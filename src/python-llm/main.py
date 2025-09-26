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

load_dotenv()

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"), provider=GeminiProvider())

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def handleResume(resume_path):

    #Parse PDF text from file
    pdf_text = parsePDF(resume_path)

    #Extract Candidate Info using LLM
    resumeLLMCall = extractResume(pdf_text, composio, client)
    if not resumeLLMCall['successful']:
        return {
            "successful": False,
            "error": "Unable to extract Resume"
        }

    extracted_resume = resumeLLMCall['response']

    #Clean the LLM Response
    cleaned_resume = cleanLLMJson(extracted_resume)

    #Get Candidate Dictionary
    candidate_json = json.loads(cleaned_resume)

    #Generate Questions using LLM
    questionsLLMCall = generateQuestions(candidate_json, composio, client)
    if not questionsLLMCall['successful']: 
        return {
            'successful': False,
            'error': f"Unable to Generate questions because of the following error: {questionsLLMCall['error']}"
        }
    questions = questionsLLMCall['response']

    #Clean the LLM questions response
    cleaned_questions = cleanLLMJson(questions)

    #Generate questions dictionary
    questions_json = json.loads(cleaned_questions)

    #Generate the Report
    doc_text = generateReport(candidate_json, questions_json)

    #Create the Google Document of the candidate's report using the LLM
    doc_creation = createGoogleDoc(doc_text, f"{candidate_json['name']} Report", composio, client)
    if not doc_creation['successful']:
        return {
            'successful': False,
            'error': f"Unable to create doc because of the following error: {doc_creation['error']}"
        }
    return {
        'successful': True,
    }


    
handle = handleResume('uploads/latest_resume.pdf')
print(handle)