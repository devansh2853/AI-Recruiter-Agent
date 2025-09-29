from core.constants import composio, client
from core.tools import extractResume, cleanLLMJson, parsePDF, generateQuestions, generateReport, createGoogleDoc, sendMail

import json
import sys
import os


class RecruiterAgent:
    def __init__(self):
        self.composio = composio
        self.client = client
    def handleResume(self, resume_path, userId):

        #Parse PDF text from file
        pdf_text = parsePDF(resume_path)

        #Extract Candidate Info using LLM
        resumeLLMCall = extractResume(pdf_text, self.composio, self.client)
        if not resumeLLMCall['successful']:
            return {
                "successful": False,
                "error": f"Unable to extract Resume: ${resumeLLMCall['error']}"
            }

        extracted_resume = resumeLLMCall['response']

        #Clean the LLM Response
        cleaned_resume = cleanLLMJson(extracted_resume)

        #Get Candidate Dictionary
        candidate_json = json.loads(cleaned_resume)

        #Generate Questions using LLM
        questionsLLMCall = generateQuestions(candidate_json, self.composio, self.client)
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

        #Print Question
        print("These are the generated questions: \n")
        for question in questions_json['questions']:
            print(question)
            print("\n")


        #Generate the Report
        doc_text = generateReport(candidate_json, questions_json)


        #Create the Google Document of the candidate's report using the LLM
        doc_creation = createGoogleDoc(doc_text, f"{candidate_json['name']} Report", self.composio, self.client, userId)
        if not doc_creation['successful']:
            return {
                'successful': False,
                'error': f"Unable to create doc because of the following error: {doc_creation['error']}"
            }
        print(f"A google document containing the report of the candidate {candidate_json['name']} has been created")

        cleaned_doc = cleanLLMJson(doc_creation['response'])
        doc_link_json = json.loads(cleaned_doc)

        recipient_email = input("Who do you me to mail the report to? (example@gmail.com): ").strip()

        mail = sendMail(candidate_json, doc_link_json['link'], recipient_email, self.composio, userId)
        if not mail['successful']:
            return {
                'successful': False,
                'error': f"Unable to send mail because of the following error: {mail['error']}"
            }
        
        print("Mail Sent")

        if not doc_creation['successful']:
            return {
                'successful': False,
                'error': f"Unable to create doc because of the following error: {doc_creation['error']}"
            }
        return {
            'successful': True,
            'candidate': candidate_json['name']
        }


    
