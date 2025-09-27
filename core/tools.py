from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

import pdfplumber
import re


load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


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
            "successful": True,
            "response": response.text
        }
    except Exception as e:
        return {
            "successful": False,
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
            "successful": True,
            "response": response.text
        }
    except Exception as e:
        return {
            "successful": False,
            "error": str(e)
        }


def generateReport(candidate_json, questions_json):
    """
    Generates a textual report for the candidate combining resume info and interview questions.

    Args:
        candidate_json (dict): Extracted candidate info from resume.
        questions_json (dict): Generated questions.

    Returns:
        str: Formatted report text.
    """
    report_lines = []

    # Candidate basic info
    report_lines.append(f"Candidate Name: {candidate_json.get('name', 'N/A')}")
    report_lines.append(f"Email: {candidate_json.get('email', 'N/A')}")
    report_lines.append(f"Phone: {candidate_json.get('phone', 'N/A')}")
    report_lines.append(f"Experience (years): {candidate_json.get('experience_years', 'N/A')}")
    report_lines.append("")

    # Skills
    skills = candidate_json.get("skills", [])
    report_lines.append("Skills:")
    for skill in skills:
        report_lines.append(f"- {skill}")
    report_lines.append("")

    # Companies
    companies = candidate_json.get("companies", [])
    report_lines.append("Previous Companies:")
    for company in companies:
        report_lines.append(f"- {company}")
    report_lines.append("")

    # Education
    education = candidate_json.get("education", [])
    report_lines.append("Education:")
    for edu in education:
        report_lines.append(f"- {edu}")
    report_lines.append("")

    # Certifications
    certifications = candidate_json.get("certifications", [])
    report_lines.append("Certifications:")
    for cert in certifications:
        report_lines.append(f"- {cert}")
    report_lines.append("")

    # Languages
    languages = candidate_json.get("languages", [])
    report_lines.append("Languages:")
    for lang in languages:
        report_lines.append(f"- {lang}")
    report_lines.append("")

    # Interview Questions
    report_lines.append("Generated Interview Questions:")
    for idx, q in enumerate(questions_json.get("questions", []), 1):
        report_lines.append(f"{idx}. {q}")
    
    return "\n".join(report_lines)


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
        return {
            'successful': True,
            'response': response.text
        }
    except Exception as e:
        return {
            'successful': False,
            'error': str(e)
        }
