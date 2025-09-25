from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

import pdfplumber

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def parsePDF(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def cleanLLMJson(raw_text):
    # re.sub(r"\(cid:\d+\)", "", raw_text)
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```json", "", raw_text)
        raw_text = re.sub(r"^```", "", raw_text)
        raw_text = re.sub(r"```$", "", raw_text)
        raw_text = raw_text.strip()
    return raw_text


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
        return {
            "successfull": True,
            "response": response.text
        }
    except Exception as e:
        return {
            "successfull": False,
            "error": str(e)
        }


def generateQuestions(candidate_json, composio, client):
    config = types.GenerateContentConfig(
        tools = []
    )
    chat = client.chats.create(model="gemini-2.0-flash", config=config)
    prompt = f"""
    You are an experienced technical recruiter. Based on the candidate's profile below, generate a set of 10 interview questions**.

    Candidate profile (JSON):
    {candidate_json}

    Guidelines for questions:
    - Mix technical and behavioral questions.
    - Tailor them to the candidate's skills, past experience, and education.
    - Keep questions open-ended, not yes/no.
    - Questions should be concise and professional.
    - Output as a JSON list of strings only. Use this structure exactly:

    {{
        "questions": [
            "Question 1?",
            "Question 2?",
            "Question 3?"
        ]
    }}
    """
    try:
        response = chat.send_message(prompt)
        return {
            "successfull": True,
            "response": response.text
        }
    except Exception as e:
        return {
            "successfull": False,
            "error": str(e)
        }


def generateReport(candidate_json, questions_json):
    return ""