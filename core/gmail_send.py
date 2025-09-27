from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

from resumeTools import extractResume, cleanLLMJson, parsePDF, generateQuestions, generateReport
from DocUtils import createGoogleDoc

import json
import re
import sys

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

config = types.GenerateContentConfig(
        tools = composio.tools.get(
            user_id="devansh",
            toolkits=[
                "GMAIL"
            ],
        )
    )

# result = composio.tools.execute(
#     "GMAIL_SEND_EMAIL",
#     user_id="devansh",
arguments={
        "body": "Hey this is a tester mail",
        "subject": "Test",
        "recipient_email": "ishitabansal484@gmail.com"
}
# )

# print(result)

chat = client.chats.create(model="gemini-2.0-flash", config=config)
prompt = f"Send the following mail: {arguments}. Why can you not send emails and only create drafts? I have provided the tool to you"
response = chat.send_message(prompt)
print(response.text)

def sendEmail(arguments) {
    result = composio.tools.execute(
    "GMAIL_SEND_EMAIL",
    user_id="devansh",
    arguments=arguments
    )
}