"""
Enhanced Flask Web API for Medical RAG System UI
Modern UI with improved usability and visual design
"""
import base64
import os
import time
import traceback
from pathlib import Path
from io import BytesIO
import secrets

from flask import Flask, request, jsonify, render_template_string, send_from_directory, session
from flask_cors import CORS
from openai import OpenAI

# Import RAG components
from core.rag_system import RAGSystem
from scripts.setup_documents import DocumentSetup
import processors.image_processor
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from web.routes import register_routes

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)
    
    # Set up a secret key for sessions
    app.secret_key = secrets.token_hex(16)
    
    # Increase max content length to 16MB
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Initialize RAG system and document setup
    app.rag_system = None
    app.document_setup = None
    
    # Register routes
    register_routes(app)
    
    # Create necessary directories
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("data/conversations", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("temp_uploads", exist_ok=True)
    
    return app

def initialize_system(app):
    """Initialize RAG system lazily"""
    if app.rag_system is None:
        app.rag_system = RAGSystem()
        app.document_setup = DocumentSetup()
    return app.rag_system, app.document_setup

# Create app
app = create_app()
app.initialize_system = initialize_system

if __name__ == '__main__':
    print("🚀 Starting MedIntelligence RAG System")
    print("=" * 50)
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)