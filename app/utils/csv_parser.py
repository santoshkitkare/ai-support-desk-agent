##############################################################################
# File: 🚀 csv_parser.py — The CSV → Text Converter for Your RAG Pipeline
# it plays a big strategic role in making your ingestion system flexible and enterprise-ready.
# Most RAG projects choke on CSV files because they treat them like PDFs or DOCX.
# But support teams often keep knowledge in CSVs:
# - product SKUs
# - troubleshooting steps
# - price lists
# - serial number mappings
# - warranty clauses
# - FAQ exports from Zendesk/Hubspot
# Your CSV parser handles this beautifully.
#
# 🎯 Why This Is a Great Approach for RAG
# ✔ 1. Keeps row structure intact
# " | " separator preserves data relationships.
#
# ✔ 2. Makes CSV documents searchable
# After chunking + embedding, FAISS can retrieve:
# matching SKUs
# troubleshooting rows
# service procedures
# configuration tables
#
# ✔ 3. Plays well with reranker + LLM
# Chunk structure becomes:
# [Snippet X | Doc: product_specs.csv | ...]
# ProductID | Feature1 | Feature2 | ...
# The LLM can easily reason about it.
#
# ✔ 4. Avoids issues with complex tables
# No multi-column formatting nightmares.
# No HTML tables.
# No need for advanced parsing.
# This is practical engineering.
import pandas as pd


def extract_text_from_csv(path: str) -> str:
    # 1️⃣ Load the CSV into pandas
    # Automatically handles:
    # - commas
    # - quoted cells
    # - numeric columns
    # - booleans
    # - missing values
    df = pd.read_csv(path)
    
    # 2️⃣ Convert entire dataframe to string
    # This ensures:
    # No NaN/float formatting issues
    # No type errors during join
    # Everything becomes text for embeddings
    # Simple: flatten all cells into text
    
    # 3️⃣ Convert each row → a single textual line
    # This turns CSV rows into something like:
    #   ProductID123 | Black Refrigerator | Cooling issue | Steps: Reset thermostat...
    
    # 4️⃣ Flatten entire CSV into one plain-text document
    # This gives you a text block ready for:
    # - chunking
    # - embedding
    # - FAISS indexing
    return "\n".join(
        df.astype(str).apply(lambda row: " | ".join(row.values), axis=1).tolist()
    )


"""
🔥 What You Could Add Later (Optional Enhancements)
These are not necessary, but worth considering if CSVs become large or structured.
1️⃣ Include column headers
Right now you're only extracting values.
You might want:
    ProductID | Name | Issue | Steps
    123 | Freezer | Cooling issue | Reset thermostat...
Add simply:
    header = " | ".join(df.columns)
    rows = ...
    return header + "\n" + rows
    
2️⃣ Handle very large CSVs in chunks
If CSV has >100k rows, loading entire file can be slow.
Use chunked pandas:
    pd.read_csv(path, chunksize=10000)

3️⃣ Normalize whitespace
Some CSVs include stray newlines inside fields.

4️⃣ Replace pipes with another separator if needed
If the data itself uses “|”, consider using:
    \t (tab)
    |||
    custom delimiter

5️⃣ Add data-type tags for LLM interpretability
E.g. [ProductID=123] [Category=Electronics] [Issue=Cooling]
This makes LLM responses even sharper.
"""