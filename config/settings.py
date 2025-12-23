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

# Vector database configuration (PostgreSQL + pgvector)
PGVECTOR_CONNECTION_URI = os.getenv(
    "PGVECTOR_CONNECTION_URI",
    "postgresql+asyncpg://postgres:faziA12#@localhost:5433/medicalbot",
)
PGVECTOR_TABLE = os.getenv("PGVECTOR_TABLE", "rag_documents")
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)
# Alias for backward compatibility with older code paths
VECTOR_DB_PATH = PGVECTOR_CONNECTION_URI

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

# No local directory is required for pgvector persistence because data
# is stored directly in PostgreSQL.