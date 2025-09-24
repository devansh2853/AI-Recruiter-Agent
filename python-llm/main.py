from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

from resumeTools import extractResume
from DocUtils import createGoogleDoc

import json
import re

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

resume = """
John Doe
Email: john.doe@example.com
Phone: +1-555-123-4567

Professional Summary:
Software engineer with 5 years of experience in full-stack development. Proficient in Python, Node.js, React, and cloud technologies (AWS, GCP).

Work Experience:
- Software Engineer, TechCorp, 2019-2022
  Worked on backend APIs, database optimization, and deployment pipelines.
- Junior Developer, WebSolutions, 2017-2019
  Assisted in developing frontend features and API integration.

Education:
- B.Tech in Computer Science, University of California, 2013-2017

Certifications:
- AWS Certified Solutions Architect
- Google Cloud Professional Data Engineer

Skills:
Python, Node.js, React, AWS, GCP, SQL, Docker, Kubernetes

Languages:
English, Spanish
"""

raw_text = extractResume(resume, composio, client).text

if raw_text.startswith("```"):
        raw_text = re.sub(r"^```json", "", raw_text)
        raw_text = re.sub(r"^```", "", raw_text)
        raw_text = re.sub(r"```$", "", raw_text)
        raw_text = raw_text.strip()
doc_text = json.loads(raw_text)
print(doc_text)

