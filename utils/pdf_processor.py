"""
utils/pdf_processor.py
Handles PDF reading, text extraction, and chunking.
"""

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdfs(files):
    """
    Reads uploaded PDF files, extracts text page by page,
    splits into overlapping chunks, and returns metadata.

    Returns:
        all_chunks  - list of text strings
        meta        - list of dicts with {source, page}
        total_pages - int
        full_text   - raw concatenated text for DNA analysis
    """
    all_chunks, meta = [], []
    total_pages = 0
    full_text = ""

    for file in files:
        pdf = PdfReader(file)
        total_pages += len(pdf.pages)

        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += text + "\n"

            if text.strip():
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=600,
                    chunk_overlap=80
                )
                chunks = splitter.split_text(text)
                for chunk in chunks:
                    all_chunks.append(chunk)
                    meta.append({"source": file.name, "page": i + 1})

    return all_chunks, meta, total_pages, full_text
