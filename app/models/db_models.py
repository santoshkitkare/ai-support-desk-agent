##############################################################################
# File: 🚀 db_models.py — Your Knowledge + Conversation Database Schema
# This file is your database blueprint, the foundation under EVERYTHING your Support Agent does.
# Documents, chunks, conversations, messages — all persistent memory comes from here.
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean

Base = declarative_base()

#📄 1. Document Table
# ✔ Stores metadata for each uploaded file
# Fields include:
# - id
# - filename
# - absolute path
# - file type (pdf/docx/txt/etc.)
# - created timestamp
#
# ✔ Relationship:
# chunks = relationship("DocumentChunk", cascade="all, delete-orphan")
#
# This means:
# - If a document is deleted → all its chunks auto-delete
# - Ensures DB integrity
# - Prevents orphan chunks polluting your RAG index
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, docx, csv, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

# 🧩 2. DocumentChunk Table
# ✔ Each row = one chunk from ingestion
# Contains:
# - chunk_id
# - document_id
# - chunk_index (ordering!)
# - content (raw text)
# - timestamp
# Why it's important:
# - chunk_index preserves original document order
# - FAISS stores vectors by chunk_id
# - Chat service reconstructs context using these rows
# - Allows UI to show which file + chunk were used
# Clean relational design:
#   document = relationship("Document", back_populates="chunks")
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  # order within document
    content = Column(Text, nullable=False)

    # For debugging / retrieval metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")

# 💬 3. Conversation Table
# ✔ One row per UI session
# session_id ties all messages from one browser/session.
# ✔ Optional user_name
# Future-proof for login-based SaaS version.
# ✔ Cascade delete on messages
# Deleting a conversation wipes all messages cleanly.
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # UUID from frontend
    user_name = Column(String, nullable=True)  # optional if you support auth later
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

# 🗣️ 4. Message Table
# ✔ Each message stored with:
# - conversation_id
# - role ("user" or "assistant")
# - content
# - timestamp
# Drives:
# - History retrieval
# - Analytics
# - Debug logs
# - Conversation replay
# Indexes:
# - Message.id is indexed → fast ordering
# - conversation_id leverages foreign key constraint
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
    
"""
🤓 Suggested (Optional) Improvements
None of these are required, but useful when scaling:
1️⃣ Add updated_at timestamps
Good for auditing.
2️⃣ Track “embedding_model_version” per document
If you later switch models (BGE → OpenAI → Instructor), you won’t mix embeddings.
3️⃣ Add doc_type or tags for filtering documents
Useful for enterprise support where you may have categories:
refund policies
installment agreements
warranty docs
4️⃣ Add soft-delete flag instead of hard delete
Enterprises prefer "disabled" docs over deletion.
"""