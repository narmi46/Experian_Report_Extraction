import pdfplumber
import re

def parse_experian_legal_suits(pdf_file):
    """
    Parse Experian PDF and return basic legal suit facts.
    For now: ONLY total legal suits count.
    """
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # Simple, robust pattern
    match = re.search(r"Legal Suits\s+(\d+)", text, re.IGNORECASE)

    legal_suits_count = int(match.group(1)) if match else 0

    return {
        "legal_suits_count": legal_suits_count
    }
