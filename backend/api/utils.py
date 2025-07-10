# backend/api/utils.py

import pypdf
from bs4 import BeautifulSoup


def extract_pdf_text(pdf_path):
    """Extracts text from a PDF file at the given path."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""


def clean_html(html_content):
    """Strips HTML tags and returns clean text."""
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    # Get text
    text = soup.get_text()
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    return "\n".join(chunk for chunk in chunks if chunk)
