from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def createGoogleDoc(doc_text, doc_name, composio, client):
    config = types.GenerateContentConfig(
        tools = composio.tools.get(
            user_id="devansh",
            toolkits=[
                "GOOGLEDOCS"
            ],
        )
    )
    chat = client.chats.create(model="gemini-2.0-flash", config=config)
    prompt = f"Create a new Google Doc named '{doc_name}' with the following text: {doc_text}"
    try:
        response = chat.send_message(prompt)
        return response
    except Exception as e:
        return f"Error: {str(e)}"


