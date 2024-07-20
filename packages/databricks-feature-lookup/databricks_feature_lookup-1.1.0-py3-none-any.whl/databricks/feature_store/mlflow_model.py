import inspect
import itertools
import logging
import os
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union

import mlflow
import pandas as pd
from mlflow.utils import databricks_utils

from databricks.feature_store.entities.feature_functions_for_serving import (
    FeatureFunctionsForServing,
)
from databricks.feature_store.feature_functions.feature_function_executor import (
    FeatureFunctionExecutor,
)
from databricks.feature_store.feature_lookup_version import VERSION
from databricks.feature_store.online_lookup_client import (
    OnlineLookupClient,
    is_primary_key_lookup,
    should_use_brickstore_http_gateway,
    tables_share_dynamodb_access_keys,
)
from databricks.feature_store.utils.collection_utils import LookupKeyList
from databricks.feature_store.utils.metrics_utils import (
    OVERRIDEN_FEATURE_COUNT,
    LookupClientMetrics,
    lookup_call_maybe_with_metrics,
)
from databricks.feature_store.utils.timeout_utils import (
    TOTAL_REQUEST_TIMEOUT_SECONDS,
    timeout,
)
from databricks.ml_features_common import mlflow_model_constants
from databricks.ml_features_common.entities.feature_column_info import FeatureColumnInfo
from databricks.ml_features_common.entities.feature_spec import FeatureSpec
from databricks.ml_features_common.entities.feature_tables_for_serving import (
    FeatureTablesForServing,
)
from databricks.ml_features_common.entities.on_demand_column_info import (
    OnDemandColumnInfo,
)
from databricks.ml_features_common.entities.online_feature_table import (
    OnlineFeatureTable,
    PrimaryKeyDetails,
)
from databricks.ml_features_common.protos.feature_store_serving_pb2 import DataType
from databricks.ml_features_common.utils.feature_spec_utils import (
    COLUMN_INFO_TYPE_FEATURE,
    COLUMN_INFO_TYPE_ON_DEMAND,
    COLUMN_INFO_TYPE_SOURCE,
    get_feature_execution_groups,
)
from databricks.ml_features_common.utils.uc_utils import (
    get_feature_spec_with_full_table_names,
    get_feature_spec_with_reformat_full_table_names,
)

# The provisioner of this model is expected to set an environment variable with the path to a
# feature_tables_for_serving.dat file.
FEATURE_TABLES_FOR_SERVING_FILEPATH_ENV = "FEATURE_TABLES_FOR_SERVING_FILEPATH"
# should match LOOKUP_CLIENT_INSTRUMENTATION_ENABLED_ENV in
# model-serving/model-serving-common/src/main/scala/com/databricks/mlflow/utils/serving/FeatureStoreConstants.scala
LOOKUP_CLIENT_INSTRUMENTATION_ENABLED_ENV = "LOOKUP_CLIENT_INSTRUMENTATION_ENABLED"
# should match LOOKUP_CLIENT_FEATURE_FUNCTION_EVALUATION_ENABLED_ENV in
# model-serving/model-serving-common/src/main/scala/com/databricks/mlflow/utils/serving/FeatureStoreConstants.scala
LOOKUP_CLIENT_FEATURE_FUNCTION_EVALUATION_ENABLED_ENV = (
    "LOOKUP_CLIENT_FEATURE_FUNCTION_EVALUATION_ENABLED"
)

LookupKeyType = Tuple[str, ...]
LookupKeyToFeatureColumnInfosType = Dict[LookupKeyType, List[FeatureColumnInfo]]
_logger = logging.getLogger(__name__)


class _FeatureTableMetadata:
    """
    Encapsulates metadata on a feature table, including lookup keys, feature metadata, and online
    feature table metadata.

    Feature metadata is grouped by lookup key, since different features may require different
    lookup keys (eg pickup_zip and dropoff_zip may each be used to lookup a geographic data feature
    table).
    """

    def __init__(
        self,
        feature_col_infos_by_lookup_key: LookupKeyToFeatureColumnInfosType,
        online_ft: OnlineFeatureTable,
    ):
        self.feature_col_infos_by_lookup_key = feature_col_infos_by_lookup_key
        self.online_ft = online_ft


def _load_raw_model(path):
    raw_model_path = os.path.join(path, mlflow_model_constants.RAW_MODEL_FOLDER)
    return mlflow.pyfunc.load_model(raw_model_path)


class _FeatureStoreModelWrapper:
    def __init__(self, path: str):
        print(f"Initializing feature store lookup client: {VERSION}")
        self._check_support()
        feature_tables_for_serving = self._load_feature_tables_for_serving()

        self.raw_model = _load_raw_model(path)

        # Reformat local metastore 3L tables to 2L. Non-local metastore 3L tables and 2L tables are unchanged.
        # This guarantees table name consistency between feature_spec and feature_tables_for_serving.
        # https://docs.google.com/document/d/1x_V9GshlnoAAFFCuDsXWdJVtop9MG2HWTUo5IK_1mEw
        original_feature_spec = FeatureSpec.load(path)
        # We call get_feature_spec_with_full_table_names to append the default metastore to 2L names,
        # as get_feature_spec_with_reformat_full_table_names expects full 3L table names and throws otherwise.
        # TODO (ML-26593): Consolidate this into a single function that allows either 2L/3L names.
        feature_spec_with_full_table_names = get_feature_spec_with_full_table_names(
            original_feature_spec
        )
        self.feature_spec = get_feature_spec_with_reformat_full_table_names(
            feature_spec_with_full_table_names
        )

        self.ft_metadata = self._get_ft_metadata(
            self.feature_spec, feature_tables_for_serving
        )
        self._validate_ft_metadata(self.ft_metadata)
        self.is_model_eligible_for_batch_lookup = (
            self._is_model_eligible_for_batch_lookup(self.ft_metadata)
        )

        if self.is_model_eligible_for_batch_lookup:
            self.batch_lookup_client = self._create_batch_lookup_client(
                self.ft_metadata
            )
        else:
            self.ft_to_lookup_client = self._create_lookup_clients(self.ft_metadata)

        if self._is_lookup_client_feature_function_evaluation_enabled():
            self.has_feature_functions = self._has_feature_functions(path)
            if self.has_feature_functions:
                feature_function_dir = os.path.join(
                    path, mlflow_model_constants.FEATURE_STORE_INTERNAL_DATA_DIR
                )
                feature_functions_for_serving = FeatureFunctionsForServing.load(
                    feature_function_dir
                )
                self.feature_function_executor = FeatureFunctionExecutor(
                    feature_functions_for_serving,
                    self.feature_spec.on_demand_column_infos,
                )

    def _has_feature_functions(self, path):
        feature_function_dir = os.path.join(
            path, mlflow_model_constants.FEATURE_STORE_INTERNAL_DATA_DIR
        )
        return os.path.isfile(
            os.path.join(feature_function_dir, FeatureFunctionsForServing.DATA_FILE)
        )

    # true if all feature tables using DynamoDB under same authorization (ie same region and keys)
    def _is_model_eligible_for_batch_lookup(
        self, ft_metadata: Dict[str, _FeatureTableMetadata]
    ):
        online_feature_tables = [meta.online_ft for _, meta in ft_metadata.items()]
        return (
            tables_share_dynamodb_access_keys(online_feature_tables)
            and is_primary_key_lookup(online_feature_tables)
        ) or should_use_brickstore_http_gateway(online_feature_tables)

    @staticmethod
    def _load_feature_tables_for_serving() -> FeatureTablesForServing:
        return FeatureTablesForServing.load(
            path=os.getenv(FEATURE_TABLES_FOR_SERVING_FILEPATH_ENV)
        )

    @staticmethod
    def _is_lookup_client_instrumentation_enabled() -> bool:
        # environment variables stored as string, rather than boolean
        return os.getenv(LOOKUP_CLIENT_INSTRUMENTATION_ENABLED_ENV) == "true"

    @staticmethod
    def _is_lookup_client_feature_function_evaluation_enabled() -> bool:
        return (
            os.getenv(LOOKUP_CLIENT_FEATURE_FUNCTION_EVALUATION_ENABLED_ENV) == "true"
        )

    @staticmethod
    def _check_support():
        if (
            databricks_utils.is_in_databricks_notebook()
            or databricks_utils.is_in_databricks_job()
        ):
            raise NotImplementedError(
                "Feature Store packaged models cannot be loaded with MLflow APIs. For batch "
                "inference, use FeatureStoreClient.score_batch."
            )

    @staticmethod
    def _validate_ft_metadata(ft_metadata: Dict[str, _FeatureTableMetadata]):
        for ft, meta in ft_metadata.items():
            for lookup_key in meta.feature_col_infos_by_lookup_key.keys():
                if len(lookup_key) != len(meta.online_ft.primary_keys):
                    raise Exception(
                        f"Internal error: Online feature table has primary keys "
                        f"{meta.online_ft.primary_keys}, however FeatureSpec specifies "
                        f"{len(lookup_key)} lookup_keys: {lookup_key}."
                    )

    def _create_lookup_clients(
        self, ft_metadata: Dict[str, _FeatureTableMetadata]
    ) -> Dict[str, OnlineLookupClient]:
        ft_to_lookup_client = {}
        for ft, meta in ft_metadata.items():
            ft_to_lookup_client[ft] = OnlineLookupClient(meta.online_ft)
        return ft_to_lookup_client

    def _create_batch_lookup_client(
        self, ft_metadata: Dict[str, _FeatureTableMetadata]
    ) -> Optional[OnlineLookupClient]:
        """
        Creates and returns an OnlineLookupClient for batch lookup, or None if `ft_metadata` is
        empty.
        """
        if not ft_metadata:
            return None
        online_fts = []
        for ft, meta in ft_metadata.items():
            online_fts.append(meta.online_ft)

        return OnlineLookupClient(online_fts)

    def _monitored_augment_with_materialized_features(
        self,
        df: pd.DataFrame,
        features_to_lookup: List[FeatureColumnInfo],
        partially_overridden_feature_output_names: List[str],
        *,
        output_metrics: LookupClientMetrics = None,
    ):
        augment_with_materialized_features = lookup_call_maybe_with_metrics(
            self._augment_with_materialized_features,
            output_metrics,
            measuring_e2e_latency=True,
        )

        # Add materialized features to `df`. This call does not do input column filtering, which is
        # important as Feature Functions may require inputs with include=False, so filtering must
        # be done after Feature Function execution. See _augment_with_materialized_features
        # docstring for details.
        return augment_with_materialized_features(
            df,
            features_to_lookup,
            partially_overridden_feature_output_names,
            metrics=output_metrics,
        )

    def _augment_with_on_demand_features(self, df, functions_to_apply):
        if (
            self._is_lookup_client_feature_function_evaluation_enabled()
            and self.has_feature_functions
        ):
            # Includes fully and partially overridden columns in this iteration.
            df_columns_set = set(df.columns)
            override_columns = [
                f.output_name
                for f in functions_to_apply
                if f.output_name in df_columns_set
            ]
            if override_columns:
                overrides = df[override_columns]
                # May contain partially overridden columns that will be used in later iterations.
                df_without_override_columns = df.drop(columns=override_columns)

            else:
                overrides = None
                df_without_override_columns = df

            feature_functions_df = self._compute_feature_functions(
                df_without_override_columns, functions_to_apply, overrides
            )
            return pd.concat(
                [df_without_override_columns, feature_functions_df], axis=1
            )
        return df

    # basic predict just returning predict
    def predict(self, df: pd.DataFrame, params: Optional[Dict[str, Any]] = None):
        return self._predict(df, params)

    # new method to return tuple of prediction and metrics if available
    def predict_with_metrics(
        self, df: pd.DataFrame, params: Optional[Dict[str, Any]] = None
    ):
        # if enabled, use metrics class to record metric values in child function calls
        output_metrics = None
        if self._is_lookup_client_instrumentation_enabled():
            output_metrics = LookupClientMetrics({})
        prediction = self._predict(df, params, output_metrics)
        # will add any captured metrics to output via pandas series attributes
        if output_metrics:
            return (prediction, output_metrics.get_metrics())
        else:
            return (prediction, None)

    # main predict logic
    def _predict(
        self,
        df: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None,
        output_metrics=None,
    ):
        (
            fully_overridden_feature_output_names,
            partially_overridden_feature_output_names,
        ) = self._get_overridden_feature_output_names(df)
        fully_overridden_feature_output_names_set = set(
            fully_overridden_feature_output_names
        )

        self._validate_input(
            df,
            fully_overridden_feature_output_names,
            partially_overridden_feature_output_names,
        )

        if output_metrics and len(fully_overridden_feature_output_names) > 0:
            output_metrics.increase_metric(
                OVERRIDEN_FEATURE_COUNT,
                df[fully_overridden_feature_output_names].count().sum(),
            )

        execution_groups = get_feature_execution_groups(self.feature_spec, df.columns)
        result_df = df
        for execution_group in execution_groups:
            if execution_group.type == COLUMN_INFO_TYPE_SOURCE:
                continue
            elif execution_group.type == COLUMN_INFO_TYPE_FEATURE:
                # Filter out fully overridden feature names, so they are not looked up unnecessarily
                result_df = self._monitored_augment_with_materialized_features(
                    result_df,
                    [
                        feature
                        for feature in execution_group.features
                        if feature.output_name
                        not in fully_overridden_feature_output_names_set
                    ],
                    partially_overridden_feature_output_names,
                    output_metrics=output_metrics,
                )
            elif execution_group.type == COLUMN_INFO_TYPE_ON_DEMAND:
                result_df = self._augment_with_on_demand_features(
                    result_df, execution_group.features
                )
            else:
                # This should never be visible to user.
                raise Exception(
                    "Unknown feature execution group type:", execution_group.type
                )
        output_cols = [
            ci.output_name for ci in self.feature_spec.column_infos if ci.include
        ]
        model_input_df = result_df[output_cols]
        if inspect.signature(self.raw_model.predict).parameters.get("params"):
            prediction = self.raw_model.predict(model_input_df, params=params)
        else:
            prediction = self.raw_model.predict(model_input_df)
            if params:
                _logger.warning(
                    "The model does not support passing additional "
                    "parameters to the predict function. Supplied parameters "
                    "will be ignored."
                )

        return prediction

    def _get_ft_metadata(
        self,
        feature_spec: FeatureSpec,
        fts_for_serving: FeatureTablesForServing,
    ) -> Dict[str, _FeatureTableMetadata]:
        ft_to_lookup_key_to_feature_col_infos = (
            self._group_fcis_by_feature_table_lookup_key(feature_spec)
        )
        ft_names = ft_to_lookup_key_to_feature_col_infos.keys()
        ft_to_online_ft = self._resolve_online_stores(
            feature_tables=ft_names, feature_tables_for_serving=fts_for_serving
        )

        return {
            ft: _FeatureTableMetadata(
                feature_col_infos_by_lookup_key=ft_to_lookup_key_to_feature_col_infos[
                    ft
                ],
                online_ft=ft_to_online_ft[ft],
            )
            for ft in ft_names
        }

    @staticmethod
    def _group_fcis_by_feature_table_lookup_key(
        feature_spec: FeatureSpec,
    ) -> Dict[str, LookupKeyToFeatureColumnInfosType]:
        """
        Re-organizes the provided FeatureSpec into a convenient structure for creating
        _FeatureTableMetadata objects.

        :return: Nested dictionary:
            {feature_table_name -> {lookup_key -> feature_column_infos}}
        """
        feature_table_to_lookup_key_to_fcis = defaultdict(lambda: defaultdict(list))
        for fci in feature_spec.feature_column_infos:
            feature_table_name = fci.table_name
            lookup_key = tuple(fci.lookup_key)
            feature_table_to_lookup_key_to_fcis[feature_table_name][lookup_key].append(
                fci
            )
        return feature_table_to_lookup_key_to_fcis

    def _get_overridden_feature_output_names(self, df: pd.DataFrame):
        """A feature value can be overridden in the provided DataFrame. There are two cases:
          1. The feature value is overridden for all rows in the df.
          2. The feature value is overridden for some but not all rows in the df.

        :return: Tuple<List[str], List[str]>
          (List of feature names with values that were fully overridden,
          list of feature names with values that were partially overridden)
        """
        df_columns_set = set(df.columns)
        overridden_feature_names = [
            fci.output_name
            for fci in self.feature_spec.feature_column_infos
            if fci.output_name in df_columns_set
        ]
        if len(overridden_feature_names) == 0:
            return [], []

        all_rows_overridden_idxs = df[overridden_feature_names].notna().all().values
        fully_overridden = [
            overridden_feature_names[i]
            for i in range(len(overridden_feature_names))
            if all_rows_overridden_idxs[i]
        ]
        fully_overridden_set = set(fully_overridden)
        partially_overridden = [
            name
            for name in overridden_feature_names
            if name not in fully_overridden_set
        ]
        return (fully_overridden, partially_overridden)

    def _validate_input(
        self,
        df: pd.DataFrame,
        fully_overridden_feature_output_names: List[str],
        partially_overridden_feature_output_names: List[str],
    ):
        """
        Validates:
            - df contains exactly one column per SourceDataColumnInfo
            - df contains exactly one column per lookup key and per function input that are not
                provided by intermediate lookups or functions
            - df has no NaN lookup keys
        """
        req_source_column_names = [
            col_info.name for col_info in self.feature_spec.source_data_column_infos
        ]
        lookup_key_columns = set(
            itertools.chain.from_iterable(
                [
                    col_info.lookup_key
                    for col_info in self.feature_spec.feature_column_infos
                ]
            )
        )
        function_input_binding_columns = set(
            itertools.chain.from_iterable(
                [
                    col_info.input_bindings.values()
                    for col_info in self.feature_spec.on_demand_column_infos
                ]
            )
        )

        lookup_output_columns = set(
            [ci.output_name for ci in self.feature_spec.feature_column_infos]
        )
        function_output_columns = set(
            [ci.output_name for ci in self.feature_spec.on_demand_column_infos]
        )

        # All input and output excluding source columns.
        all_input_columns = function_input_binding_columns.union(lookup_key_columns)
        all_output_columns = lookup_output_columns.union(function_output_columns)

        all_req_columns = set(req_source_column_names).union(
            all_input_columns.difference(all_output_columns)
        )
        df_column_set = set(df.columns)
        missing_columns = [c for c in all_req_columns if c not in df_column_set]

        if missing_columns:
            raise ValueError(
                f"Input is missing columns {list(missing_columns)}. "
                f"\n\tThe following columns are required: {list(all_req_columns)}."
            )

        df_column_name_counts = Counter(df.columns)
        no_dup_columns_allowed_set = set(
            list(lookup_key_columns)
            + req_source_column_names
            + fully_overridden_feature_output_names
            + partially_overridden_feature_output_names
        )
        dup_columns = [
            col
            for col, count in df_column_name_counts.items()
            if count > 1 and col in no_dup_columns_allowed_set
        ]

        if dup_columns:
            raise ValueError(
                f"Input has duplicate columns: {dup_columns}"
                f"\n\tThe following column names must be unique: {no_dup_columns_allowed_set}"
            )

        # The set of columns from the input that are required as lookup keys.
        # This set doesn't include lookup keys that can be provided by intermediate lookup or
        # function result.
        lookup_key_columns_from_input = lookup_key_columns.difference(
            all_output_columns
        )
        lookup_key_df = df[list(lookup_key_columns_from_input)]
        cols_with_nulls = lookup_key_df.columns[lookup_key_df.isnull().any()].tolist()
        if cols_with_nulls:
            raise ValueError(
                f"Failed to lookup feature values due to null values for lookup_key columns "
                f"{cols_with_nulls}. The following columns cannot contain null values: "
                f"{lookup_key_columns}"
            )

    @timeout(seconds=TOTAL_REQUEST_TIMEOUT_SECONDS)
    def _augment_with_materialized_features(
        self,
        df: pd.DataFrame,
        features_to_lookup: List[FeatureColumnInfo],
        partially_overridden_feature_output_names: List[str],
        *,
        metrics: LookupClientMetrics = None,
    ) -> pd.DataFrame:
        """
        Adds materialized features to `df`. This function does not filter out ColumnInfos with
        include=False, however it will drop any columns in `df` that are not in the FeatureSpec.
        features_to_lookup MUST NOT include any fully overridden features already in df; however,
        partially overridden features are allowed and non-overridden cells will be looked up.

        For example, a FeatureSpec may include

            - revenue:
                include: false
                source: training_data
            - cost:
                include: false
                source: training_data
            - profit:
                udf_name: prod.math.subtract
                input_bindings:
                  x: sales
                  y: cost
                source: on_demand_feature

         In this case, the DataFrame returned by this method will include columns `revenue` and
         `cost`. This is required to compute the Feature Function `profit` at a later stage.

        :param df: Pandas DataFrame provided by user as model input. This is expected to contain
        columns for each SourceColumnInfo, and for each lookup key of a FeatureColumnInfo. Columns
        with the same name as FeatureColumnInfo output_names will override those features, meaning
        they will not be queried from the online store.
        :param features_to_lookup: List of FeatureColumnInfos to lookup from the online store.
        :param partially_overridden_feature_output_names: List of feature output names that are
        partially overridden in `df`. These features will be looked up from the online store, and
        only the cells that are not overridden will be looked up.
        :return: Pandas DataFrame containing all materialized features specified in the FeatureSpec,
          including features with include=False (see example above).
        """
        # Contains lookup result columns. Does not include fully overridden columns.
        feature_dfs = []
        partially_overridden_features_count = 0
        partially_overridden_feature_output_names_set = set(
            partially_overridden_feature_output_names
        )

        pk_lists = defaultdict(lambda: defaultdict(list))
        feature_column_infos_to_lookup_dict = defaultdict(lambda: defaultdict(list))
        lookup_clients = {}

        table_names_to_lookup = {info.table_name for info in features_to_lookup}
        all_lookup_columns = {info.output_name for info in features_to_lookup}

        # Query online store(s) for feature values
        ft_meta: _FeatureTableMetadata
        for ft_name, ft_meta in self.ft_metadata.items():
            if ft_name not in table_names_to_lookup:
                continue
            if not self.is_model_eligible_for_batch_lookup:
                lookup_clients[
                    ft_meta.online_ft.online_feature_table_name
                ] = self.ft_to_lookup_client[ft_name]

            # Iterate through the lookup_keys for this feature table, each of which is used to
            # lookup a list of features
            lookup_key: LookupKeyType
            feature_column_infos: List[FeatureColumnInfo]
            for (
                lookup_key,
                feature_column_infos,
            ) in ft_meta.feature_col_infos_by_lookup_key.items():
                # Only lookup features that were specified in features_to_lookup
                feature_column_infos_to_lookup = [
                    fci
                    for fci in feature_column_infos
                    if fci.output_name in all_lookup_columns
                ]
                if len(feature_column_infos_to_lookup) == 0:
                    # All features were overridden in the input DataFrame
                    continue

                pk_lists[ft_meta.online_ft.online_feature_table_name][
                    lookup_key
                ] = self._get_primary_key_list(
                    lookup_key, ft_meta.online_ft.primary_keys, df
                )
                feature_column_infos_to_lookup_dict[
                    ft_meta.online_ft.online_feature_table_name
                ][lookup_key] = feature_column_infos_to_lookup

        # A nested defaultdict using table_name as first layer key and lookup_key as second layer
        # key. The actual inner value of the dict is of type pd.DataFrame. The structure looks like:
        # table_name: {
        #   lookup_key: DataFrame
        # }
        # TODO[ML-34263]: consider updating the default value type to match the actual usage.
        feature_values_dfs = defaultdict(lambda: defaultdict(list))
        if self.is_model_eligible_for_batch_lookup and pk_lists:
            feature_values_dfs = self._batch_lookup_and_rename_features(
                self.batch_lookup_client,
                pk_lists,
                feature_column_infos_to_lookup_dict,
                metrics=metrics,
            )
        else:
            for oft_name, pk_list_by_lookup_key in pk_lists.items():
                for lookup_key in pk_list_by_lookup_key.keys():
                    feature_values_dfs[oft_name][
                        lookup_key
                    ] = self._lookup_and_rename_features(
                        lookup_clients[oft_name],
                        pk_lists[oft_name][lookup_key],
                        feature_column_infos_to_lookup_dict[oft_name][lookup_key],
                        metrics=metrics,
                    )

        for oft_name, feature_values_df_by_lookup_key in feature_values_dfs.items():
            for (
                lookup_key,
                feature_values_df,
            ) in feature_values_df_by_lookup_key.items():
                if feature_values_df.shape[0] != df.shape[0]:
                    raise Exception(
                        f"Internal Error: Expected {df.shape[0]} rows to be looked up from feature "
                        f"table {ft_name}, but found {feature_values_df.shape[0]}"
                    )

                # If any features were partially overridden, use the override values.
                # Filter all partially overridden feature output names down to those that
                # are in the feature table currently being processed.
                partially_overridden_feats = [
                    c
                    for c in feature_values_df.columns
                    if c in partially_overridden_feature_output_names_set
                ]
                if partially_overridden_feats:
                    # add partially overriden features to override count, count() returns the number
                    # of non-NaN values per column those are the values that will get overriden
                    partially_overridden_features_count += (
                        df[partially_overridden_feats].count().sum()
                    )
                    # For each cell of overridden column, use the overridden value if provided, else
                    # the value looked up from the online store.
                    partially_overridden_feats_df = df[
                        partially_overridden_feats
                    ].combine_first(feature_values_df[partially_overridden_feats])
                    feature_values_df[
                        partially_overridden_feats
                    ] = partially_overridden_feats_df[partially_overridden_feats]

                feature_dfs.append(feature_values_df)

        feature_names_looked_up = [feat for df in feature_dfs for feat in df.columns]
        used_partial_feature_names = (
            partially_overridden_feature_output_names_set.intersection(
                set(feature_names_looked_up)
            )
        )

        # Concatenate the following DataFrames, where N is the number of rows in `df`.
        #  1. feature_dfs - List of DataFrames, one per feature table looked up from the online
        #       store, containing partially overridden columns. Each DataFrame has N rows.
        #  2. non_overridden_columns_df - columns from `df` that are not partially overriden or are
        #       not looked-up in this iteration. DataFrame with N rows.
        non_overridden_columns_df = df.drop(columns=list(used_partial_feature_names))
        augmented_features = pd.concat(
            feature_dfs + [non_overridden_columns_df],
            axis=1,
        )

        if metrics:
            metrics.increase_metric(
                OVERRIDEN_FEATURE_COUNT, partially_overridden_features_count
            )

        return augmented_features

    def _compute_feature_functions(
        self,
        ff_inputs: pd.DataFrame,
        functions_to_apply: List[OnDemandColumnInfo],
        ff_overrides: Optional[pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Executes Feature Functions specified by FeatureSpec.

        :param ff_inputs: A DataFrame containing all inputs required to evaluate Feature Functions.
          Additional columns are permitted.
        :param ff_overrides: A DataFrame containing overrides to Feature Functions. When a Feature
          Function output name is included as a column in `ff_overrides`, the function is computed
          only for rows where the override is `np.nan`.
        :return: DataFrame containing computed Feature Function columns
        """
        # TODO(ML-30619): Short-circuit Feature Function execution when overridden
        feature_function_df = self.feature_function_executor.execute_feature_functions(
            ff_inputs,
            functions_to_apply,
        )
        if ff_overrides is None:
            return feature_function_df

        ff_overrides_columns_set = set(ff_overrides.columns)
        overridden_ff_outputs = [
            odci.output_name
            for odci in functions_to_apply
            if odci.output_name in ff_overrides_columns_set
        ]
        overridden_ff_df = ff_overrides[overridden_ff_outputs]
        # As with materialized features, Feature Functions may be fully or partially
        # overridden, where a partial override means that some rows have null override value.
        # Merge the overridden values with the computed feature values:
        return overridden_ff_df.combine_first(feature_function_df)

    @staticmethod
    def _validate_lookup_key_datatype(
        df: pd.DataFrame,
        primary_keys: List[PrimaryKeyDetails],
        lookup_key: LookupKeyType,
    ):
        """
        Validates that the given keys are of the correct datatype used to look up from online store.
        It is assumed that lookup_key and primary_keys are in the same order.
        """
        dtypes_dict = df.dtypes.to_dict()
        for pk, lookup_name in zip(primary_keys, lookup_key):
            if pk.data_type == DataType.STRING and not pd.api.types.is_string_dtype(
                dtypes_dict[lookup_name]
            ):
                raise ValueError(
                    f"Provided primary keys {pk.name} is not of type string"
                )

    def _get_primary_key_list(
        self,
        lookup_key: LookupKeyType,
        primary_keys: List[PrimaryKeyDetails],
        df: pd.DataFrame,
    ) -> LookupKeyList:
        """
        :return: A list of rows where each row is a list of tuples, each tuple is (column_name, value).
            There will be a column per column in `primary_keys`, and a row per row in `df`. `lookup_key` must `primary_keys` in length.
            The order of columns in each row is the same as the order of columns in `primary_keys`.
            Note that using LookupKeyList (which uses Python lists) is faster than using pandas
            DataFrame for the majority of use cases, since pandas DataFrame is optimized for large
            number of rows and has heavy overhead for small data.
            It is assumed that lookup_key and primary_keys are in the same order.
        """
        lookup_key_columns = df[list(lookup_key)]
        self._validate_lookup_key_datatype(lookup_key_columns, primary_keys, lookup_key)
        lookup_key_dict = lookup_key_columns.to_dict("list")
        # Update the lookup_key_df column names to be those of the feature table primary
        # key columns, rather than the names of columns from the source DataFrame. This is
        # required by the lookup_features interface.
        return LookupKeyList(
            columns=[feature_pk.name for feature_pk in primary_keys],
            rows=[
                [lookup_key_dict[lookup_name][i] for lookup_name in lookup_key]
                for i in range(len(df))
            ],
        )

    def _lookup_and_rename_features(
        self,
        lookup_client: OnlineLookupClient,
        primary_key_list: LookupKeyList,
        feature_column_infos: List[FeatureColumnInfo],
        *,
        metrics: LookupClientMetrics = None,
    ) -> pd.DataFrame:
        """
        Looks up features from a single feature table, then renames them. Feature metadata is
         specified via `feature_column_infos`.
        """
        feature_names = [fci.feature_name for fci in feature_column_infos]
        feature_values = lookup_client.lookup_features(
            primary_key_list, feature_names, metrics=metrics
        )
        feature_name_to_output_name = {
            fci.feature_name: fci.output_name for fci in feature_column_infos
        }
        return feature_values.rename(feature_name_to_output_name, axis=1)

    def _batch_lookup_and_rename_features(
        self,
        batch_lookup_client: OnlineLookupClient,
        primary_key_lists: Dict[str, Dict[LookupKeyType, LookupKeyList]],
        feature_column_infos_dict: Dict[
            str, Dict[LookupKeyType, List[FeatureColumnInfo]]
        ],
        *,
        metrics: LookupClientMetrics = None,
    ) -> Dict[str, Dict[LookupKeyType, pd.DataFrame]]:
        """
        Looks up features from all the feature tables in batch, then renames them. Feature metadata
         is specified via `feature_column_infos`.
        """
        feature_names = defaultdict(lambda: defaultdict(list))
        feature_name_to_output_names = defaultdict(lambda: defaultdict(list))
        for (
            oft_name,
            feature_column_infos_by_lookup_key,
        ) in feature_column_infos_dict.items():
            for (
                lookup_key,
                feature_column_infos,
            ) in feature_column_infos_by_lookup_key.items():
                feature_names[oft_name][lookup_key] = [
                    fci.feature_name for fci in feature_column_infos
                ]
                feature_name_to_output_names[oft_name][lookup_key] = {
                    fci.feature_name: fci.output_name for fci in feature_column_infos
                }
        feature_values = batch_lookup_client.batch_lookup_features(
            primary_key_lists, feature_names, metrics=metrics
        )

        for oft_name, feature_values_by_lookup_key in feature_values.items():
            for lookup_key, _ in feature_values_by_lookup_key.items():
                feature_values[oft_name][lookup_key] = feature_values[oft_name][
                    lookup_key
                ].rename(feature_name_to_output_names[oft_name][lookup_key], axis=1)
        return feature_values

    def _resolve_online_stores(
        self,
        feature_tables: List[str],
        feature_tables_for_serving: FeatureTablesForServing,
    ) -> Dict[str, OnlineFeatureTable]:
        """
        :return: feature table name -> OnlineFeatureTable
        """
        all_fts_to_online_ft = {
            online_ft.feature_table_name: online_ft
            for online_ft in feature_tables_for_serving.online_feature_tables
        }

        missing = [ft for ft in feature_tables if ft not in all_fts_to_online_ft]
        if missing:
            raise Exception(
                f"Internal error: Online feature table information could not be found "
                f"for feature tables {missing}."
            )

        return {ft: all_fts_to_online_ft[ft] for ft in feature_tables}


def _load_pyfunc(path):
    """
    Called by ``pyfunc.load_pyfunc``.
    """
    return _FeatureStoreModelWrapper(path)
