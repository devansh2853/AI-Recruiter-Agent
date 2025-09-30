from core.constants import composio, client
from dotenv import load_dotenv
import os
import json
load_dotenv()

gmail_auth_config_id = os.getenv('AUTHCFG_GMAIL')
docs_auth_config_id = os.getenv('AUTHCFG_GDOCS')


CONNECTIONS_FILE = "connections.json"


def authenticate_gmail(user_id: str):
    user = getuser()
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=gmail_auth_config_id,
    )
    print(
        f"Visit this URL to authenticate Gmail: {connection_request.redirect_url}"
    )
    try:
        # This will wait for the auth flow to be completed
        connection_request.wait_for_connection(timeout=300)
        if user.get("gmail_connection_id", False):
            composio.connected_accounts.delete(user.get("gmail_connection_id"))
    except Exception as e:
        try:
            composio.connected_accounts.delete(connection_request.id)
        except Exception as f:
            pass
        retry = input("⏱ Gmail authentication timed out. Would you like to try again?(y/n) \n").strip()
        if retry.lower() == 'y':
            return authenticate_gmail(user_id)
        else: 
            return 0
        
    return connection_request.id


def authenticate_docs(user_id: str):
    user = getuser()
    connection_request = composio.connected_accounts.initiate(
        user_id=user_id,
        auth_config_id=docs_auth_config_id,
    )
    print(
        f"Visit this URL to authenticate Google Docs: {connection_request.redirect_url}"
    )
    try:
        # This will wait for the auth flow to be completed
        connection_request.wait_for_connection(timeout=300)
        if user.get("doc_connection_id", False):
            composio.connected_accounts.delete(user.get("doc_connection_id"))
    except Exception as e:
        try:
            composio.connected_accounts.delete(connection_request.id)
        except Exception as f:
            pass
        retry = input("⏱ Google Docs authentication timed out. Would you like to try again?(y/n) \n").strip()
        if retry.lower() == 'y':
            return authenticate_docs(user_id)
        else: 
            return 0
        
    return connection_request.id



def saveuser(userId, gmail=False, docs=False, gmail_con_id=0, doc_con_id=0):
    """Save or update connections without overwriting the other."""
    user = getuser() or {}
    user.update({
        "userId": userId,
        "gmail": gmail or user.get("gmail", False),
        "docs": docs or user.get("docs", False),
        "gmail_connection_id": gmail_con_id or user.get("gmail_connection_id", False),
        "doc_connection_id": doc_con_id or user.get("doc_connection_id", False),
    })
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

  