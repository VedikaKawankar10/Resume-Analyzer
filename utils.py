import pdfplumber
import fitz  # PyMuPDF
from fpdf import FPDF
import datetime
import os
import re

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    return text.strip()

def extract_text_from_txt(file):
    return file.read().decode("utf-8")


def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def clean_text(text):
    # Replace common problematic characters with safe ones
    replacements = {
        '–': '-', '—': '-',  # dashes
        '“': '"', '”': '"', '‘': "'", '’': "'",
        '•': '-', '→': '->',
        '©': '(c)', '®': '(R)', '™': '(TM)'
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Remove any characters outside basic ASCII range
    return re.sub(r'[^\x00-\x7F]+', '', text)


def save_to_pdf(result, jd_text, resume_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Clean all input text
    jd_text = clean_text(jd_text)
    resume_text = clean_text(resume_text)
    match_score = result.get('match_score', 'N/A')
    matched_skills = ', '.join(result.get('matched_skills', []))
    missing_skills = ', '.join(result.get('missing_skills', []))

    pdf.cell(0, 10, txt="Resume vs Job Description Analysis", ln=True, align='C')
    pdf.ln(10)

    pdf.multi_cell(0, 10, txt=f"Match Score: {match_score}%")
    pdf.multi_cell(0, 10, txt=f"Skills Matched: {matched_skills}")
    pdf.multi_cell(0, 10, txt=f"Missing Skills: {missing_skills}")
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, txt="Job Description:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=jd_text)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(0, 10, txt="Resume:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=resume_text)

    file_path = "resume_analysis_report.pdf"
    pdf.output(file_path)
    return file_path