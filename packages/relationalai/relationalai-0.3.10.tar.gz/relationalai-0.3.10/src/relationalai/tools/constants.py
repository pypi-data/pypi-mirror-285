#--------------------------------------------------
# Constants
#--------------------------------------------------

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
PROFILE = None

SNOWFLAKE = "Snowflake"
AZURE = "Azure (Beta)"

AZURE_ENVS = {
    "Production": {
        "host": "azure.relationalai.com",
        "client_credentials_url": "https://login.relationalai.com/oauth/token"
    },
    "Early Access": {
        "host": "azure-ea.relationalai.com",
        "client_credentials_url": "https://login-ea.relationalai.com/oauth/token"
    },
    "Staging": {
        "host": "azure-staging.relationalai.com",
        "client_credentials_url": "https://login-staging.relationalai.com/oauth/token"
    },
    "Latest": {
        "host": "azure-latest.relationalai.com",
        "client_credentials_url": "https://login-latest.relationalai.com/oauth/token"
    },
}
