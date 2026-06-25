import re


def extract_pdf_pages(pdf_path):
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF extraction. Install it with: pip install PyMuPDF") from exc

    pages = []
    with pymupdf.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page": page_index, "text": normalize_text(text)})
    return pages


def chunk_pages(pages, chunk_size=1200, overlap=180):
    chunks = []
    for page in pages:
        words = page["text"].split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            content = " ".join(words[start:end]).strip()
            if content:
                chunks.append({"page": page["page"], "content": content})
            if end == len(words):
                break
            start = max(end - overlap, start + 1)
    return chunks


def normalize_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()
