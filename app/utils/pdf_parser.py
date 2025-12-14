##############################################################################
# File: 🚀 pdf_parser.py — Your PDF → Text Extractor
# PDF ingestion backbone of your entire knowledge ingestion pipeline.
# PDFs are the #1 format companies use for:
# - Warranty policies
# - Refund policies
# - Product manuals
# - Troubleshooting guides
# - Internal SOPs
# - Legal terms
# So this tiny file has huge strategic impact on your RAG accuracy.
# 
# 🎯 Why This Approach Works Well for RAG
# ✔ 1. It’s simple and reliable

# Most support PDFs are “born-digital,” meaning they contain a real text layer → PyPDF2 works great.
# ✔ 2. Page separation preserved through “\n”
# Your chunker uses natural boundaries to split logically.
# ✔ 3. Good performance
# PyPDF2 is lightweight and dependency-light.
# ✔ 4. Perfect feeding mechanism for your chunker + embeddings
# The downstream pipeline expects plain text — this delivers that.
from typing import List
from PyPDF2 import PdfReader


def extract_text_from_pdf(path: str) -> str:
    # ✔ 1. Load the PDF
    # PyPDF2 reads the entire file and loads page objects.
    reader = PdfReader(path)
    texts: List[str] = []
    # ✔ 2. Iterate through every page
    # This ensures no content is missed, even in multi-page manuals.
    for page in reader.pages:
        # ✔ 3. Extract text per page
        # - extract_text() returns raw text from the PDF’s text layer
        # - If a page has no extractable text → returns None → fallback to empty string
        # This prevents runtime errors.
        txt = page.extract_text() or ""
        
        # ✔ 4. Combine all text
        texts.append(txt)
    return "\n".join(texts)


"""
⚠️ Important Limitation (Common in Real PDFs)
Not your fault — PyPDF2 has a known limitation:
❌ It cannot extract text from scanned PDFs
If the PDF contains an image of text (like a scanned document), extract_text() returns None.
Those documents come out empty.
This is typical in:
- HR scanned policies
- Old manuals
- Vendor contracts
- Photocopied SOPs
✔ How to upgrade later (optional)
Use OCR:
- pytesseract + pdf2image
- PyMuPDF (fitz) — better text extraction + positional info
- Unstructured + OCR pipelines
But you do NOT need this for your current project unless your PDFs are image-based.
"""

"""
💡 Optional Enhancements (Only if Needed)
1️⃣ Extract metadata (author, title, keywords)
Useful for analytics.

2️⃣ Extract page numbers / header markers
Then your LLM can cite page numbers.

3️⃣ Remove extra whitespace or line breaks
Some PDFs produce weird formatting.

4️⃣ Use PyMuPDF instead of PyPDF2
Better accuracy, more robust extractor.
"""