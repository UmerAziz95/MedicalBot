"""
API routes for the web application
"""

import os
import time
import traceback
import uuid
from flask import request, jsonify, render_template_string, session, url_for
from processors.speech_handler import SpeechHandler

# Fix import to use the module
import processors.image_processor
from web.templates.index import HTML_TEMPLATE
from web.swagger import SWAGGER_UI_TEMPLATE, get_openapi_spec
from config.settings import MAX_RETRIEVED_CHUNKS

def register_routes(app):
    """Register all routes for the application"""
    
    # Initialize system function for all routes
    def init_system():
        return app.initialize_system(app)
    
    @app.route('/')
    def index():
        """Serve the main UI"""
        # Initialize a session if none exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/status')
    def get_status():
        """Get system status"""
        try:
            rag, setup = init_system()
            info = setup.get_database_info()
            
            # Test API connection
            api_connected = rag.llm_client.test_connection()
            
            # Get session info if available
            session_info = {}
            if 'session_id' in session:
                session_id = session['session_id']
                # Get conversation history
                history = rag.get_conversation_history(session_id)
                messages_count = len(history.strip().split("\n\n")) if history else 0
                session_info = {
                    "id": session_id,
                    "messages_count": messages_count
                }
            
            return jsonify({
                "document_count": info.get('document_count', 0),
                "unique_documents": info.get('unique_documents', 0),
                "sources": info.get('sources', []),
                "api_connected": api_connected,
                "file_upload_support": True,  # Indicate file upload support
                "supported_formats": ["pdf", "png", "jpg", "jpeg", "bmp", "gif"],
                "session": session_info
            })
        except Exception as e:
            print(f"Status API error: {e}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    @app.route('/api/query', methods=['POST'])
    def query_rag():
        """Process a query with or without a file"""
        try:
            # Ensure we have a session
            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())
                
            session_id = session['session_id']
            
            question = request.form.get('question', '').strip()
            prompt_type = request.form.get('prompt_type', 'basic')
            file = request.files.get('file', None)
            
            # Special case: allow empty question if file is provided
            if not question and not file:
                return jsonify({"error": "Question or file is required"}), 400
            
            # Track timing
            start_time = time.time()
            
            # Check if file is empty
            if file and file.filename:
                # Get file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size == 0:
                    return jsonify({
                        "answer": "The uploaded file appears to be empty.",
                        "error": "Empty file",
                        "query_time": time.time() - start_time,
                        "chunks_found": 0
                    }), 400
                
                # Check if it's an image file
                ext = os.path.splitext(file.filename)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    # Process image directly using the module function with session
                    rag, _ = init_system()
                    # Get conversation history
                    conversation_history = rag.get_conversation_history(session_id)
                    
                    # Process the image
                    result = processors.image_processor.ImageProcessor.process_image(
                        file, question, prompt_type, conversation_history
                    )
                    
                    # Ensure we have a valid response (never return "couldn't generate")
                    answer = result.get("answer", "")
                    if not answer or "couldn't generate a response" in answer.lower():
                        # Use fallback mechanism
                        answer = rag._ensure_valid_response(answer, question, prompt_type)
                        result["answer"] = answer
                    
                    # Add to conversation history if successful
                    if 'error' not in result:
                        rag.add_to_conversation_history(
                            question if question else f"[Uploaded image: {file.filename}]",
                            result.get("answer", ""),
                            session_id
                        )
                        rag.save_conversation(session_id)
                    
                    return jsonify({
                        "answer": result.get("answer", "No answer generated"),
                        "file_processed": True,
                        "query_time": time.time() - start_time,
                        "chunks_found": 0,
                        "error": result.get("error", None)
                    })
            
            # For all other cases (text-only queries or non-image files), use the enhanced RAG system
            rag, _ = init_system()
            result = rag.query(
                question, 
                prompt_type=prompt_type, 
                file_object=file,
                session_id=session_id
            )

            # Simple final quality check
            if not result.get("answer") or len(result.get("answer", "").strip()) < 10:
                print("Emergency fallback: Empty response detected in routes.py")
                medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", 
                                   "condition", "symptom", "treatment", "drug", "patient", 
                                   "nurse", "therapy", "medical", "clinical", "diagnosis", 
                                   "surgery", "organ", "body", "anatomy", "nursing"]
                
                if any(keyword in question.lower() for keyword in medical_keywords):
                    result["answer"] = "This appears to be a medical question. While I don't have specific information about this in my database, I'd recommend consulting with a healthcare professional for accurate information about this medical topic."
                else:
                    result["answer"] = "I am a medical bot and can only assist with medical-related topics."
            
            return jsonify({
                "answer": result.get("answer", "No answer generated"),
                "chunks_found": result.get("chunks_found", 0),
                "file_processed": result.get("file_processed", False),
                "query_time": time.time() - start_time,
                "error": result.get("error", None)
            })
            
        except Exception as e:
            print(f"Query API error: {e}")
            print(traceback.format_exc())
            
            # Try to generate a fallback response
            try:
                rag, _ = init_system()
                
                # Define medical keywords here too for safety
                medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", "condition", 
                                  "symptom", "treatment", "drug", "patient", "nurse", "therapy", "medical",
                                  "clinical", "diagnosis", "surgery", "organ", "body", "anatomy", "nursing"]
                
                # Check if this is a medical question
                is_medical_question = any(keyword in question.lower() for keyword in medical_keywords)
                
                if is_medical_question:
                    fallback_answer = rag._ensure_valid_response("", question, prompt_type)
                    return jsonify({
                        "answer": fallback_answer if fallback_answer else f"Error processing query: {str(e)}",
                        "error": str(e),
                        "query_time": time.time() - start_time,
                        "chunks_found": 0
                    })
                else:
                    return jsonify({
                        "answer": "I am a medical bot and can only assist with medical-related topics.",
                        "error": str(e),
                        "query_time": time.time() - start_time,
                        "chunks_found": 0
                    })
            except:
                return jsonify({
                    "answer": f"Error processing query: {str(e)}",
                    "error": str(e),
                    "query_time": 0,
                    "chunks_found": 0
                }), 500

    @app.route('/api/v2/medical-query', methods=['POST'])
    def api_query_v2():
        """JSON-first API that wraps the medical RAG flow with explicit disclaimer handling"""
        try:
            payload = request.get_json(silent=True) or {}
            question = (payload.get("query") or payload.get("question") or "").strip()
            include_history = payload.get("include_history", True)
            disclaimer = payload.get("disclaimer")
            k = int(payload.get("k", MAX_RETRIEVED_CHUNKS))
            tenant_id = payload.get("tenant_id")
            workspace_id = payload.get("workspace_id")
            prior_chat_history = payload.get("prior_chat_history")
            external_knowledge_instructions = payload.get("external_knowledge_instructions")

            if not question:
                return jsonify({"success": False, "error": "Query text is required."}), 400

            # Resolve session (allow clients to pass their own ID)
            session_id = payload.get("session_id") or session.get("session_id") or str(uuid.uuid4())
            session['session_id'] = session_id

            rag, _ = init_system()
            result = rag.api_query(
                question,
                session_id=session_id,
                k=k,
                include_history=include_history,
                disclaimer=disclaimer,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                prior_chat_history=prior_chat_history,
                external_knowledge_instructions=external_knowledge_instructions
            )

            return jsonify(result), (200 if result.get("success") else 400)
        except Exception as e:
            print(f"API v2 query error: {e}")
            print(traceback.format_exc())
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/openapi.json')
    def openapi_spec():
        """Serve OpenAPI specification for the Medical Bot API"""
        spec = get_openapi_spec()
        return jsonify(spec)

    @app.route('/api/docs')
    def swagger_docs():
        """Render Swagger UI powered by the generated OpenAPI spec"""
        spec_url = url_for('openapi_spec', _external=False)
        return render_template_string(SWAGGER_UI_TEMPLATE, spec_url=spec_url)

    @app.route('/api/upload', methods=['POST'])
    def upload_document():
        """Upload and process a document"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            # 100MB limit
            if file_size > 100 * 1024 * 1024:
                return jsonify({"error": "File too large (max 100MB)"}), 400
            
            # Get file extension
            ext = os.path.splitext(file.filename)[1].lower()
            
            # Check if extension is supported
            supported_extensions = ['.pdf', '.txt', '.docx', '.md']
            if ext not in supported_extensions:
                return jsonify({"error": f"Unsupported file format: {ext}. Please use PDF, TXT, DOCX, or MD."}), 400
            
            # Save file temporarily
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, file.filename)
            
            file.save(temp_path)

            tenant_id = request.form.get("tenant_id") or request.args.get("tenant_id")
            workspace_id = request.form.get("workspace_id") or request.args.get("workspace_id")
            
            try:
                # Process file
                rag, setup = init_system()
                result = setup.add_document(
                    temp_path,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id
                )
                
                return jsonify({
                    "success": result.get("success", False),
                    "chunks_added": result.get("chunks_added", 0),
                    "file": file.filename,
                    "error": result.get("error", None)
                })
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            
        except Exception as e:
            print(f"Upload error: {e}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
            
    @app.route('/api/clear-history', methods=['POST'])
    def clear_conversation_history():
        """Clear the current conversation history"""
        try:
            if 'session_id' in session:
                session_id = session['session_id']
                rag, _ = init_system()
                success = rag.delete_conversation(session_id)
                
                # Create a new session
                session['session_id'] = str(uuid.uuid4())
                
                return jsonify({
                    "success": success,
                    "message": "Conversation history cleared",
                    "new_session_id": session['session_id']
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "No active session"
                }), 400
                
        except Exception as e:
            print(f"Clear history error: {e}")
            return jsonify({"error": str(e)}), 500
        
    # Add this endpoint within the register_routes function
    @app.route('/api/tts', methods=['POST'])
    def text_to_speech():
        """Convert text to speech and return audio data"""
        try:
            text = request.json.get('text', '')
            lang = request.json.get('lang', 'en')
            
            if not text:
                return jsonify({"error": "No text provided"}), 400
            
            # Limit text length to prevent abuse
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            # Convert text to speech
            result = SpeechHandler.text_to_speech(text, lang)
            
            if result["success"]:
                return jsonify(result)
            else:
                return jsonify({"error": result.get("error", "Unknown error")}), 500
                
        except Exception as e:
            print(f"TTS API error: {e}")
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 500
