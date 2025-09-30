from constants import composio


gmail_auth_config = composio.auth_configs.create(
    toolkit="GMAIL",
    options = {
    'type': "use_composio_managed_auth",
    'auth_scheme': "OAUTH2",
    }
)

print("AUTHCFG_GMAIL=", gmail_auth_config.id)

docs_auth_config = composio.auth_configs.create(
    toolkit="GOOGLEDOCS",
    options = {
        'type': 'use_composio_managed_auth',
        'auth_scheme': "OAUTH2",
    }
)

print("AUTHCFG_GDOCS=", docs_auth_config.id)

