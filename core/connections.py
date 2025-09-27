from core.constants import composio, client
from dotenv import load_dotenv
import os
import json
load_dotenv()

gmail_auth_config_id = os.getenv('AUTHCFG_GMAIL')
docs_auth_config_id = os.getenv('AUTHCFG_GDOCS')


CONNECTIONS_FILE = "connections.json"


def authenticate_gmail(user_id: str):
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=gmail_auth_config_id,
    )
    print(
        f"Visit this URL to authenticate Gmail: {connection_request.redirect_url}"
    )
    # This will wait for the auth flow to be completed
    connection_request.wait_for_connection(timeout=300)
    return connection_request.id

def authenticate_docs(user_id: str):
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=docs_auth_config_id,
    )
    print(
        f"Visit this URL to authenticate Google Docs: {connection_request.redirect_url}"
    )
    # This will wait for the auth flow to be completed
    connection_request.wait_for_connection(timeout=300)
    return connection_request.id


def saveuser(userId, gmail:bool, docs:bool):
    """Save connections to file."""
    user = {
        "userId": userId,
        "gmail": gmail,
        "docs": docs
    }
    with open(CONNECTIONS_FILE, "w") as f:
        json.dump(user, f, indent=2)

def getuser():
    if os.path.exists(CONNECTIONS_FILE):
        with open(CONNECTIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}
