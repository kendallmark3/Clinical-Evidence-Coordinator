from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

def extract_text(data: bytes) -> str:
    """Return the text layer of a PDF, or "" if it has none or cannot be read."""
    try:
        reader = PdfReader(BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except (PdfReadError, ValueError):
        return ""
