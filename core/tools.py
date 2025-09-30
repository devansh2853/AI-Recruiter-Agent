from core.constants import composio, client
from google.genai import types
import pdfplumber
import re



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

    If the input is not a valid resume follow this JSON Output structure exactly:
    {{
        "name": "invalid"
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


def generateQuestions(candidate_json, composio, client):
    config = types.GenerateContentConfig(
        tools = []
    )
    chat = client.chats.create(model="gemini-2.0-flash", config=config)
    prompt = f"""
    You are an experienced technical recruiter. Based on the candidate's skill set below, generate exact 1 question; either a technical or behavioral question based on the candidate's skills. **.

    Candidate profile (JSON):
    {candidate_json}

    Guidelines for question:
    - Tailor them to the candidate's skills, past experience, and education.
    - Keep questions open-ended, not yes/no.
    - Question should be concise and professional.
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


def createGoogleDoc(doc_text, doc_name, composio, client, userId):
    config = types.GenerateContentConfig(
        tools = composio.tools.get(
            user_id=userId,
            toolkits=[
                "GOOGLEDOCS"
            ],
        )
    )
    chat = client.chats.create(model="gemini-2.0-flash", config=config)
    prompt = f"""Create a new Google Doc named '{doc_name}' with the following text: {doc_text}.
    Please format the doc using Markdown conventions:
        - # for main heading
        - ## for subheadings
        - **bold** for important labels
    Return the link of the google document. Return it in the form of a JSON Object. Follow this structure exactly:
    {{
        "link": "document link"
    }}
    """
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


def sendMail(candidate_json, doc_link, recipient_email, composio, userId):
    highlights = []
    if "experience_years" in candidate_json:
        highlights.append(f"{candidate_json['experience_years']} years of experience")
    if "skills" in candidate_json and candidate_json["skills"]:
        highlights.append(f"Skilled in {', '.join(candidate_json['skills'][:5])}")  # just top 3
      
    summary_text = "\n".join(f"- {h}" for h in highlights)

    key_highlights = f"Key Highlights: \n \n {summary_text}"

    mail_body = f"""
    Hello,
    Please find the candidate report for {candidate_json['name']} attached below.

    {key_highlights}

    You can access the full report here: {doc_link}

    Best,
    AI Recruiter Agent
    """
    arguments={
        "body": mail_body,
        "subject": f"{candidate_json['name']} Report",
        "recipient_email": recipient_email  
    }
    try:
        result = composio.tools.execute(
        "GMAIL_SEND_EMAIL",
        user_id=userId,
        arguments=arguments
        )
        return {
            'successful': True,
            'response': result
        }
    except Exception as e:
        return {
            'successful': False,
            'error': str(e)
        }


def generateReport(candidate_json, questions_json):
    """
    Generates a Markdown-formatted report for the candidate combining resume info and interview questions.
    This will create headings and lists suitable for Google Docs or Markdown rendering.

    Args:
        candidate_json (dict): Extracted candidate info from resume.
        questions_json (dict): Generated questions.

    Returns:
        str: Formatted report text with Markdown headings.
    """
    report_lines = []

    # Main Heading
    report_lines.append(f"# {candidate_json.get('name', 'N/A')} Report\n")

    # Candidate Info
    report_lines.append("## Candidate Information")
    report_lines.append(f"- **Email:** {candidate_json.get('email', 'N/A')}")
    report_lines.append(f"- **Phone:** {candidate_json.get('phone', 'N/A')}")
    report_lines.append(f"- **Experience (years):** {candidate_json.get('experience_years', 'N/A')}\n")

    # Skills
    skills = candidate_json.get("skills", [])
    if skills:
        report_lines.append("## Skills")
        for skill in skills:
            report_lines.append(f"- {skill}")
        report_lines.append("")

    # Previous Companies
    companies = candidate_json.get("companies", [])
    if companies:
        report_lines.append("## Previous Companies")
        for company in companies:
            report_lines.append(f"- {company}")
        report_lines.append("")

    # Education
    education = candidate_json.get("education", [])
    if education:
        report_lines.append("## Education")
        for edu in education:
            report_lines.append(f"- {edu}")
        report_lines.append("")

    # Certifications
    certifications = candidate_json.get("certifications", [])
    if certifications:
        report_lines.append("## Certifications")
        for cert in certifications:
            report_lines.append(f"- {cert}")
        report_lines.append("")

    # Languages
    languages = candidate_json.get("languages", [])
    if languages:
        report_lines.append("## Languages")
        for lang in languages:
            report_lines.append(f"- {lang}")
        report_lines.append("")

    # Interview Questions
    questions = questions_json.get("questions", [])
    if questions:
        report_lines.append("## Generated Interview Questions")
        for idx, q in enumerate(questions, 1):
            report_lines.append(f"{idx}. {q}")

    return "\n".join(report_lines)


def isValidMail(email: str) -> bool:
    """Basic regex validation for email address."""
    regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(regex, email) is not None

