from io import BytesIO

import fitz
from docx import Document


async def extract_text_from_upload(filename: str, content: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        with fitz.open(stream=content, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    if lower.endswith(".docx"):
        document = Document(BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)
    return content.decode("utf-8", errors="ignore")
