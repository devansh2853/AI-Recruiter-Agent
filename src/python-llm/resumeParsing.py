import pdfplumber

def parse_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

pdf_path = "uploads/latest_resume.pdf"  # replace with your actual file name
parsed_text = parse_pdf(pdf_path)
print(parsed_text)