"""
Configuration file for RAG system
"""

import os

# OpenAI API Configuration
OPENAI_API_KEY = "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"
OPENAI_MODEL = "gpt-5-nano"  # Fixed model name - gpt-5-nano doesn't exist yet

# Ollama Configuration (for local models)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"

# Choose your LLM provider
LLM_PROVIDER = "openai"  # Options: "openai", "ollama"

# Text Processing Configuration
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ChromaDB Configuration
COLLECTION_NAME = "rag_documents"
CHROMA_DB_PATH = "./data/chroma_db"
# Add this line to ensure compatibility with modules that expect VECTOR_DB_PATH
VECTOR_DB_PATH = CHROMA_DB_PATH  # Alias for backward compatibility

# RAG Configuration
MAX_RETRIEVED_CHUNKS = 3
MAX_TOKENS = 1000

# Static Files and Documents
STATIC_DIR = "./static"
DOCUMENTS_DIR = os.path.join(STATIC_DIR, "documents")
PDF_FILE_PATH = os.path.join(DOCUMENTS_DIR, "medical_book.pdf")
PDF_FOLDER = DOCUMENTS_DIR  # Updated folder for multiple documents

# Document Processing Settings
SUPPORTED_EXTENSIONS = [".pdf", ".txt", ".md", ".docx"]
MAX_FILE_SIZE_MB = 100

# Performance Settings
BATCH_SIZE = 10
MAX_CONTEXT_LENGTH = 4000

# Logging
LOG_LEVEL = "INFO"
ENABLE_PERFORMANCE_LOGGING = True

# Directories - Create if they don't exist
DATA_DIR = "./data"
LOGS_DIR = "./logs"

# Create directories if they don't exist
for directory in [PDF_FOLDER, DATA_DIR, LOGS_DIR, STATIC_DIR]:
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

# Create chroma_db directory
if CHROMA_DB_PATH and not os.path.exists(CHROMA_DB_PATH):
    os.makedirs(CHROMA_DB_PATH, exist_ok=True)
    print(f"Created directory: {CHROMA_DB_PATH}")