import pytesseract
from pdf2image import convert_from_path
from docx import Document

def extract_text_from_pdf(file_path):
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image) + "\n"
    return text

def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

