"""Text extraction and manipulation utilities for resume processing."""

import io
import re
from typing import List, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

import nltk


def extract_pdf_text_and_meta(file_bytes: bytes) -> Tuple[str, int, bool]:
    """Extracts raw text, page count, and scanned status from PDF bytes.
    
    Returns:
        (extracted_text, page_count, is_scanned_or_empty)
    """
    if pdfplumber is None:
        raise RuntimeError("PDF support is unavailable. Install pdfplumber in requirements.txt.")

    pages_text: List[str] = []
    page_count = 0

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

    combined_text = "\n".join(pages_text).strip()
    is_empty_or_scanned = len(combined_text.strip()) < 50 and page_count > 0

    return combined_text, page_count, is_empty_or_scanned


def normalize_heading(line: str) -> str:
    """Normalizes a section heading for alias matching."""
    # Remove leading bullets, numbering (e.g. '1. Experience'), and symbols
    line = re.sub(r"^[\d\.\-\*\•\–\>\:\s]+", "", line)
    # Strip trailing punctuation like colons
    line = re.sub(r"[:\-_]+$", "", line)
    # Remove non-alpha and multi-spaces
    line = re.sub(r"[^a-zA-Z\s]", " ", line)
    return " ".join(line.lower().split())


def split_sentences(text: str) -> List[str]:
    """Splits text into sentences using NLTK or regex fallback."""
    try:
        sentences = nltk.tokenize.sent_tokenize(text)
    except Exception:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    return [s for s in sentences if len(s.strip()) > 3]


def tokenize_words(text: str) -> List[str]:
    """Tokenizes alphanumeric words from text."""
    return re.findall(r"\b[A-Za-z0-9+#.-]+\b", text)
