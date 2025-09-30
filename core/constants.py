from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))