# backend/api/utils.py

from io import BytesIO
from pathlib import Path

import pypdf
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError


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


def convert_image_to_webp(uploaded_file, quality=85):
    """Converts an uploaded image file to WebP and returns a new ContentFile."""
    original_name = getattr(uploaded_file, "name", "image")
    output_name = f"{Path(original_name).stem or 'image'}.webp"

    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as image:
            has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
            image = image.convert("RGBA" if has_alpha else "RGB")

            output = BytesIO()
            image.save(output, format="WEBP", quality=quality)

        return ContentFile(output.getvalue(), name=output_name)
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Invalid image uploaded; unable to convert to WebP") from exc
