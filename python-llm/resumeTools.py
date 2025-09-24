from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def extractResume(resume, composio, client):
    config = types.GenerateContentConfig(
        tools = []
    )
    chat = client.chats.create(model="gemini-2.0-flash", config=config)
    
    prompt = f"""
    You are a recruitment assistant. Extract the following information from the resume text below:

    Required fields:
    - Full Name
    - Email
    - Phone number
    - Total experience (in years)
    - Skills
    - Previous companies
    - Education
    - Certifications
    - Languages

    Output format: JSON only. Use this structure exactly:

    {{
        "name": "",
        "email": "",
        "phone": "",
        "experience_years": "",
        "skills": [],
        "companies": [],
        "education": [],
        "certifications": [],
        "languages": []
    }}

    Resume text:
    \"\"\"
    {resume}
    \"\"\"
    """

    try:
        response = chat.send_message(prompt)
        return response
    except Exception as e:
        return f"Error: {str(e)}"