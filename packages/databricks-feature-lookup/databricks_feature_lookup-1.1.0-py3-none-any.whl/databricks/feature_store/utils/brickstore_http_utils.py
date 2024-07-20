"""
Utils/constants for brickstore HTTP gateway feature lookups.
"""

# Mount folder for served model secrets.
SECRET_MOUNT_LOCATION = "/var/credentials-secret"

# File name within secret mount file containing oauth token.
BRICKSTORE_OAUTH_TOKEN_FILE_NAME = "brickstore-feature-lookup"
BRICKSTORE_OAUTH_TOKEN_FILE_PATH = (
    SECRET_MOUNT_LOCATION + "/" + BRICKSTORE_OAUTH_TOKEN_FILE_NAME
)
