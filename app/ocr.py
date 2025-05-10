import re
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

DATE_PATTERNS = [
    r"\b(\d{1,2}[\/\.\-]\d{1,2}[\/\.\-]\d{2,4})\b", 
    r"\b(\d{4}[\/\.\-]\d{1,2}[\/\.\-]\d{1,2})\b",
]


AMOUNT_PATTERN = r"(?:TOTAL|AMOUNT|GRAND\s+TOTAL)[^\d]{0,15}(\d+[.,]\d{2})"

def pdf_to_text(pdf_path: str) -> str:
    """Convert every page of a PDF to text (simple single-thread version)."""
    pages = convert_from_path(pdf_path, dpi=300)
    full_text = []
    for page in pages:
        text = pytesseract.image_to_string(page)
        full_text.append(text)
    return "\n".join(full_text)

def parse_date(text: str):
    for pat in DATE_PATTERNS:
        m = re.search(pat, text)
        if m:
            raw = m.group(1)
            for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
                        "%Y-%m-%d", "%d.%m.%Y"):
                try:
                    return datetime.strptime(raw.replace(".", "/").replace("-", "/"), fmt)
                except ValueError:
                    continue
    return None

def parse_amount(text: str):
    m = re.search(AMOUNT_PATTERN, text, flags=re.IGNORECASE)
    if m:
        amt_str = m.group(1).replace(",", "").replace(" ", "")
        return float(amt_str)
    return None

def parse_merchant(text: str):
    for line in text.splitlines():
        line = line.strip()
        if line and "receipt" not in line.lower() and len(line) <= 60:
            return line
    return None

def extract_receipt_fields(pdf_path: str):
    text = pdf_to_text(pdf_path)
    return {
        "raw_text": text,
        "purchased_at": parse_date(text),
        "total_amount": parse_amount(text),
        "merchant_name": parse_merchant(text),
    }
