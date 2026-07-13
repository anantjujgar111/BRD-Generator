from pathlib import Path

from docx import Document
from pypdf import PdfReader


def parse_document(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".txt":
        return file_path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".docx":
        return _parse_docx(file_path)
    if suffix == ".pdf":
        return _parse_pdf(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _parse_docx(file_path: Path) -> str:
    document = Document(file_path)
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n\n".join(paragraphs)


def _parse_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)
