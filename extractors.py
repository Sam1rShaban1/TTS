import fitz  # PyMuPDF
from docx import Document
from pptx import Presentation
import os


def extract_text(file_path: str) -> str:
    """Extract text from a document. Supports PDF, DOCX, PPTX, TXT."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext == ".pptx":
        return _extract_pptx(file_path)
    elif ext == ".txt":
        return _extract_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(path: str) -> str:
    doc = fitz.open(path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n".join(text_parts).strip()


def _extract_docx(path: str) -> str:
    doc = Document(path)
    text_parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    return "\n".join(text_parts).strip()


def _extract_pptx(path: str) -> str:
    prs = Presentation(path)
    text_parts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    if para.text.strip():
                        text_parts.append(para.text)
    return "\n".join(text_parts).strip()


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def is_scanned_pdf(text: str, threshold: int = 50) -> bool:
    """Heuristic: if extracted text is very short, likely scanned/image PDF."""
    return len(text.strip()) < threshold
