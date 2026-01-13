"""
RAG (Retrieval-Augmented Generation) system for enhanced query answering
"""

import os
import time
import traceback
import json
import base64
from datetime import datetime
from typing import List, Optional, Dict, Any, BinaryIO, Union

from processors.document_processor import DocumentProcessor
from core.vector_store import VectorStore
from utils.prompts import Prompts
from core.llm_client import LLMClient
from config.settings import VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP, MAX_RETRIEVED_CHUNKS

class RAGSystem:
    """
    RAG system that combines document retrieval with LLM generation
    for enhanced question answering
    """
    
    def __init__(self, max_history_length: int = 10):
        """Initialize the RAG system components"""
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore(VECTOR_DB_PATH)
        self.prompts = Prompts()
        self.llm_client = LLMClient()
        
        # Add conversation history storage
        self.conversation_histories = {}
        self.max_history_length = max_history_length
        
        # Create directories for persistence
        os.makedirs("data/conversations", exist_ok=True)
    
    def get_conversation_history(self, session_id: str = "default") -> str:
        """
        Get the formatted conversation history for a specific session
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            Formatted conversation history string
        """
        if session_id not in self.conversation_histories:
            # Try to load from disk first
            if not self.load_conversation(session_id):
                self.conversation_histories[session_id] = []
            
        history = self.conversation_histories[session_id]
        
        # Format the history as a string
        formatted_history = ""
        for entry in history:
            formatted_history += f"User: {entry['user']}\n"
            formatted_history += f"Assistant: {entry['assistant']}\n\n"
            
        return formatted_history
    
    def add_to_conversation_history(self, 
                                  question: str, 
                                  answer: str, 
                                  session_id: str = "default"):
        """
        Add a Q&A pair to the conversation history
        
        Args:
            question: User's question
            answer: Assistant's answer
            session_id: Unique identifier for the conversation session
        """
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
            
        # Add the new entry
        self.conversation_histories[session_id].append({
            "user": question,
            "assistant": answer,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if it exceeds the maximum length
        if len(self.conversation_histories[session_id]) > self.max_history_length:
            self.conversation_histories[session_id] = self.conversation_histories[session_id][-self.max_history_length:]
    
    def save_conversation(self, session_id: str = "default"):
        """Save conversation history to disk"""
        if session_id in self.conversation_histories and self.conversation_histories[session_id]:
            with open(f"data/conversations/{session_id}.json", "w") as f:
                json.dump(self.conversation_histories[session_id], f)
    
    def load_conversation(self, session_id: str = "default") -> bool:
        """Load conversation history from disk"""
        try:
            with open(f"data/conversations/{session_id}.json", "r") as f:
                self.conversation_histories[session_id] = json.load(f)
            return True
        except FileNotFoundError:
            return False
    
    def query(self, question: str, prompt_type: str = "basic", 
              file_object = None, k: int = MAX_RETRIEVED_CHUNKS,
              session_id: str = "default") -> Dict[str, Any]:
        """
        Process a query with or without RAG retrieval
        
        Args:
            question (str): The user's question
            prompt_type (str): Type of prompt to use (basic, detailed, medical)
            file_object: Optional file for direct analysis
            k (int): Number of chunks to retrieve
            session_id (str): Session identifier for conversation history
            
        Returns: 
            Dict[str, Any]: Result with answer and metadata
        """
        try: 
            # Get conversation history for this session
            conversation_history = self.get_conversation_history(session_id)
            
            # First, determine if this is a medical or non-medical question
            # Define keyword lists for fallback use and medical context enrichment
            medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", "condition",
                              "symptom", "treatment", "drug", "patient", "nurse", "therapy", "medical",
                              "clinical", "diagnosis", "surgery", "organ", "body", "anatomy", "nursing",
                              "blood", "heart", "lungs", "brain", "liver", "kidney", "ph level", "hp",
                              "immune", "diet", "nutrition", "cancer", "diabetes", "virus", "bacterial",
                              "infection", "prescription", "diagnosis", "prognosis", "chronic", "acute"]

            # Non-medical keywords list for heuristic fallback
            non_medical_keywords = ["computer", "programming", "gaming", "video game", "sports", "politics",
                                  "entertainment", "movies", "celebrity", "stock market", "finance",
                                  "cooking", "recipes", "travel", "vacation", "cars", "fashion",
                                  "technology", "crypto", "weather", "news", "music", "art", "books"]

            # Primary classification using LLM
            classification = self.llm_client.classify_query(question)
            is_medical = classification == "medical"
            is_non_medical = classification == "non-medical"

            # Fallback to keyword heuristics if LLM classification is unavailable
            if classification is None:
                is_non_medical = any(keyword in question.lower() for keyword in non_medical_keywords) and \
                                not any(keyword in question.lower() for keyword in medical_keywords)
                is_medical = any(keyword in question.lower() for keyword in medical_keywords)

            # If it's a non-medical question, return early with a polite response
            if is_non_medical:
                return {
                    "answer": "I am a medical bot and can only assist with medical-related topics.",
                    "chunks_found": 0,
                    "query_time": 0,
                    "success": True
                }
                
            # Process file queries if present
            if file_object:
                result = self._process_file_query(question, file_object, prompt_type, conversation_history)
                
                # Add the interaction to conversation history
                if result.get("success", False):
                    # Ensure we have a valid response
                    result["answer"] = self._ensure_valid_response(
                        result.get("answer", ""), 
                        question if question else f"[File uploaded: {getattr(file_object, 'filename', 'unknown')}]",
                        prompt_type
                    )
                    
                    self.add_to_conversation_history(
                        question if question else f"[File uploaded: {getattr(file_object, 'filename', 'unknown')}]",
                        result.get("answer", ""),
                        session_id
                    )
                    # Save the updated conversation
                    self.save_conversation(session_id)
                    
                return result
                
            # Handle normal text queries
            start_time = time.time()
            
            # Retrieve relevant chunks from RAG
            results = self.vector_store.search(question, k=k)
            chunks_found = len(results)
            
            print(f"Found {chunks_found} chunks for question: '{question}'")
            
            # CASE 1: Sufficient RAG context found - use it
            if chunks_found >= 2:  # At least 2 relevant chunks found
                # Combine chunks into context
                context = "\n\n".join([res["content"] for res in results])
                
                # Generate prompt with context and conversation history
                prompt = self.prompts.generate_prompt(
                    question, context, prompt_type, conversation_history
                )
                
                # Generate answer using LLM with RAG context
                answer = self.llm_client.generate_response(prompt)
                
            # CASE 2: Limited or no RAG context, but medical question - generate medical response
            elif is_medical:
                print("Insufficient RAG context for medical question, generating medical response...")
                
                # Extract key medical terms for more focused response
                medical_terms = [term for term in medical_keywords if term in question.lower()]
                medical_context = ", ".join(medical_terms) if medical_terms else "general medical knowledge"
                
                # For RAG with limited context, include whatever context we have
                if chunks_found > 0:
                    limited_context = "\n\n".join([res["content"] for res in results])
                    medical_prompt = f"""You are a knowledgeable medical assistant.
The user asked: "{question}"

I have limited information in my database that might be relevant:
{limited_context}

However, this information may be incomplete. Please provide a comprehensive, educational response about this medical topic, 
focusing on {medical_context}. Always provide factual medical information, being clear when something is general knowledge 
versus specific medical advice (which should be sought from healthcare professionals).

If the question contains unclear or uncommon terminology, interpret what the user might be asking about and provide information 
that would be most helpful, while clarifying the standard medical terms.

Question: {question}
Answer:"""
                else:
                    # No context from RAG, generate purely from LLM knowledge
                    medical_prompt = f"""You are a knowledgeable medical assistant.
The user asked: "{question}"

I don't have specific information about this in my database, but this appears to be a medical question about {medical_context}.
Please provide an educational, informative response based on general medical knowledge. Be clear, factual, and helpful.

If the question contains unclear or uncommon terminology (like non-standard abbreviations), interpret what the user might be 
asking about and provide information that would be most helpful, while clarifying the standard medical terms.

Question: {question}
Answer:"""

                # Generate medical answer
                answer = self.llm_client.generate_response(medical_prompt)
                
            # CASE 3: Fallback for ambiguous cases
            else:
                # Default to using whatever limited context we have + medical assumption
                if chunks_found > 0:
                    context = "\n\n".join([res["content"] for res in results])
                    prompt = self.prompts.generate_prompt(
                        question, context, prompt_type, conversation_history
                    )
                else:
                    prompt = self.prompts.generate_no_context_prompt(
                        question, prompt_type, conversation_history
                    )
                    
                answer = self.llm_client.generate_response(prompt)
                
            # Validate the quality of the answer
            answer_lower = answer.lower() if answer else ""
            invalid_responses = [
                "the system processed your query but couldn't generate a response",
                "i don't know",
                "i couldn't generate a response",
                "no answer generated",
                "sorry, i cannot provide a response",
                "not enough information"
            ]
            
            # If answer is empty, too short, or contains invalid phrases
            if not answer or len(answer.strip()) < 20 or any(invalid in answer_lower for invalid in invalid_responses):
                print(f"Invalid or insufficient answer detected: '{answer}'")
                
                if is_medical:
                    # Generate a better medical response
                    enhanced_prompt = f"""You are a knowledgeable medical assistant responding to: "{question}"

This appears to be a medical question, and I need to provide a helpful, educational response.
Please provide detailed, factual medical information, using proper medical terminology.
If the question uses non-standard terms or abbreviations, interpret what the user might mean and provide clarification.

For example, if someone asks about "HP levels in the body," explain that "HP" is not a standard medical abbreviation and suggest
what they might be referring to (e.g., pH levels, Helicobacter pylori, hemoglobin percentage, etc.)

Always be helpful and educational in your response.

Question: {question}
Answer:"""
                    
                    print("Generating enhanced medical response...")
                    answer = self.llm_client.generate_response(enhanced_prompt)
                else:
                    # For ambiguous non-medical questions, default to medical bot message
                    answer = "I am a medical bot and can only assist with medical-related topics."
            
            query_time = time.time() - start_time
            
            # Add the interaction to conversation history
            self.add_to_conversation_history(question, answer, session_id)
            self.save_conversation(session_id)
            
            return {
                "answer": answer,
                "chunks_found": chunks_found,
                "query_time": query_time,
                "success": True
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            print(traceback.format_exc())
            
            # Try to generate a fallback response
            try:
                # Define medical keywords here for exception handler
                medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", "condition", 
                                  "symptom", "treatment", "drug", "patient", "nurse", "therapy", "medical",
                                  "clinical", "diagnosis", "surgery", "organ", "body", "anatomy", "nursing"]
                
                # Check if likely medical question
                is_medical =True
                
                if is_medical:
                    # Final fallback for medical questions when everything else fails
                    fallback_prompt = f"""You are a medical assistant. The user asked: "{question}"
                    Please provide a brief but helpful response to this medical question."""
                    
                    try:
                        print(f"Final prompt entering passing to LLM client.generate_response() \"{fallback_prompt}\"")
                        fallback_answer = self.llm_client.generate_response(fallback_prompt)
                        return {
                            "answer": fallback_answer if fallback_answer else f"This appears to be a medical question. Please try rephrasing or ask another medical question.",
                            "chunks_found": 0,
                            "query_time": 0,
                            "success": fallback_answer != "",
                            "error": str(e)
                        }
                    except:
                        return {
                            "answer": "This appears to be a medical question, but I encountered an issue generating a response. Please try asking in a different way.",
                            "chunks_found": 0,
                            "query_time": 0,
                            "success": False,
                            "error": str(e)
                        }
                else:
                    return {
                        "answer": "I am a medical bot and can only assist with medical-related topics.",
                        "chunks_found": 0,
                        "query_time": 0,
                        "success": True
                    }
            except:
                return {
                    "answer": f"Error processing your question. Please try asking in a different way.",
                    "chunks_found": 0,
                    "query_time": 0,
                    "success": False,
                    "error": str(e)
                }

    def api_query(self, question: str, session_id: str = "default",
                 k: int = MAX_RETRIEVED_CHUNKS, include_history: bool = True,
                 disclaimer: Optional[str] = None,
                 prior_chat_history: Optional[List[Dict[str, str]]] = None,
                 external_knowledge_instructions: Optional[str] = None) -> Dict[str, Any]:
        """
        Structured API-friendly query handler that always includes a medical disclaimer
        in the LLM prompt and surfaces retrieved context and conversation history.

        Args:
            question (str): The user's question
            session_id (str): Session identifier for history tracking
            k (int): Number of RAG chunks to retrieve
            include_history (bool): Whether to include previous messages in the prompt
            disclaimer (str, optional): Custom disclaimer text to prepend to the system message

        Returns:
            Dict[str, Any]: Response payload ready for API consumption
        """
        if not question or not question.strip():
            return {
                "success": False,
                "error": "Query text is required.",
                "answer": None
            }

        # Gather conversation history if requested or supplied explicitly
        conversation_history = ""
        if prior_chat_history:
            formatted_history = ""
            for entry in prior_chat_history:
                role = entry.get("role", "user").capitalize()
                content = entry.get("content", "")
                formatted_history += f"{role}: {content}\n"
            conversation_history = formatted_history
        elif include_history:
            conversation_history = self.get_conversation_history(session_id)

        # Classify query to gate non-medical topics
        classification = self.llm_client.classify_query(question)

        # Heuristic fallback if classification fails
        if classification is None:
            medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", "condition",
                              "symptom", "treatment", "drug", "patient", "nurse", "therapy", "medical",
                              "clinical", "diagnosis", "surgery", "organ", "body", "anatomy", "nursing",
                              "blood", "heart", "lungs", "brain", "liver", "kidney", "ph level", "hp",
                              "immune", "diet", "nutrition", "cancer", "diabetes", "virus", "bacterial",
                              "infection", "prescription", "diagnosis", "prognosis", "chronic", "acute"]

            non_medical_keywords = ["computer", "programming", "gaming", "video game", "sports", "politics",
                                  "entertainment", "movies", "celebrity", "stock market", "finance",
                                  "cooking", "recipes", "travel", "vacation", "cars", "fashion",
                                  "technology", "crypto", "weather", "news", "music", "art", "books"]

            lower_question = question.lower()
            if any(keyword in lower_question for keyword in non_medical_keywords) and not any(keyword in lower_question for keyword in medical_keywords):
                classification = "non-medical"
            elif any(keyword in lower_question for keyword in medical_keywords):
                classification = "medical"
            else:
                classification = "unknown"

        is_non_medical = classification == "non-medical"

        # Retrieve RAG context
        results = self.vector_store.search(question, k=k)
        chunks_found = len(results)
        context_chunks = [res.get("content", "") for res in results]
        rag_context = "\n\n".join(context_chunks) if context_chunks else "No context retrieved from the knowledge base."

        base_disclaimer = (
            "You are MedBot, a medical information assistant. Provide educational medical information only, "
            "avoid diagnoses or treatment advice, and use a professional tone. If the user asks about a non-medical "
            "topic, respond exactly with: \"I am a medical bot and can only assist with medical-related topics.\""
        )
        disclaimer_text = f"{base_disclaimer}\n\nAdditional context: {disclaimer.strip()}" if disclaimer else base_disclaimer

        extra_instructions = external_knowledge_instructions or ""

        structured_prompt = f"""{disclaimer_text}

User Query:
{question}

Relevant RAG Chunks:
{rag_context}

Previous Chat Context:
{conversation_history if conversation_history else 'No previous messages.'}

External Knowledge Instructions:
{extra_instructions if extra_instructions else 'None provided.'}

Instructions:
- Use the provided RAG context first; if it is insufficient, rely on safe, general medical knowledge.
- Maintain continuity with the prior conversation when present.
- Be concise, clear, and educational.
- Never leave a medical question unanswered.
Answer:"""

        if is_non_medical:
            answer = "I am a medical bot and can only assist with medical-related topics."
        else:
            answer = self.llm_client.generate_response(structured_prompt)
            answer = self._ensure_valid_response(answer, question, "medical")

            # Final guard against empty responses
            if not answer or not answer.strip():
                answer = (
                    "I couldn't retrieve medical context for this question yet. "
                    "Based on general medical guidance, please consult a healthcare professional for personalized advice."
                )

            self.add_to_conversation_history(question, answer, session_id)
            self.save_conversation(session_id)

        return {
            "success": True,
            "answer": answer,
            "classification": classification or "unknown",
            "chunks_found": chunks_found,
            "session_id": session_id,
            "disclaimer": disclaimer_text,
            "conversation_history_included": include_history,
            "rag_context": rag_context,
            "context_snippets": [
                {
                    "content": res.get("content", ""),
                    "metadata": res.get("metadata", {}),
                    "similarity": res.get("similarity")
                }
                for res in results
            ]
        }
    
    def _process_no_chunks_query(self, question: str, prompt_type: str, 
                                conversation_history: str = "") -> str:
        """
        Process a query when no relevant chunks are found
        
        Args:
            question (str): The user's question
            prompt_type (str): Type of prompt to use
            conversation_history (str): Previous conversation context
            
        Returns:
            str: Generated answer
        """
        prompt = self.prompts.generate_no_context_prompt(
            question, prompt_type, conversation_history
        )
        return self.llm_client.generate_response(prompt)
    
    def _process_file_query(self, question: str, file_object: BinaryIO, 
                           prompt_type: str, conversation_history: str = "") -> Dict[str, Any]:
        """
        Process a query with a file (bypassing RAG search)
        Modified to use direct image processing capabilities
        
        Args:
            question (str): User question (can be empty)
            file_object (BinaryIO): File object for analysis
            prompt_type (str): Prompt type to use
            conversation_history (str): Previous conversation context
            
        Returns:
            Dict[str, Any]: Generated answer and metadata
        """
        start_time = time.time()
        
        print("Processing file directly (bypassing RAG)...")
        
        # Get filename if available
        filename = getattr(file_object, 'filename', 'unknown_file')
        print(f"Processing file: {filename}")
        
        try:
            # Determine file type
            ext = os.path.splitext(filename)[1].lower() if filename else ''
            
            if ext not in ['.pdf', '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                return {
                    "answer": f"Unsupported file format: {ext}. Please use PDF or image files (PNG, JPG, etc.).",
                    "file_processed": True,
                    "chunks_found": 0,
                    "query_time": time.time() - start_time,
                    "success": False,
                    "error": "Unsupported file format"
                }
            
            # Reset file pointer and read the data
            file_object.seek(0)
            file_data = file_object.read()
            
            # Create temp directory if needed
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, os.path.basename(filename))
            
            # Save the file temporarily
            with open(temp_path, 'wb') as f:
                f.write(file_data)
            
            try:
                # Process based on file type
                if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                    # For image files, use direct image processing
                    from processors.direct_image_processor import DirectImageProcessor
                    result = DirectImageProcessor.process_image(
                        file_object, question, prompt_type, self.llm_client, conversation_history
                    )
                    answer = result["answer"]
                else:
                    # For PDFs, extract text
                    file_text = self.doc_processor.load_pdf(temp_path)
                    
                    # Generate prompt based on text and conversation history
                    if question:
                        prompt = self.prompts.file_analysis_prompt(
                            file_text, question, prompt_type, conversation_history
                        )
                    else:
                        prompt = self.prompts.file_summary_prompt(
                            file_text, prompt_type, conversation_history
                        )
                    
                    # Generate response using LLM
                    print("\nGenerating response from PDF content...")
                    answer = self.llm_client.generate_response(prompt)
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
            
            # Handle empty responses
            if not answer or answer.strip() == "":
                answer = "The system processed your file but couldn't generate a response. This might be due to API limits or content restrictions."
            
            query_time = time.time() - start_time
            
            print(f"\n{'='*20} ANSWER {'='*20}")
            print(answer)
            print(f"{'='*47}")
            
            return {
                "answer": answer,
                "file_processed": True,
                "chunks_found": 0,  # No RAG chunks used
                "query_time": query_time,
                "success": True
            }
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            return {
                "answer": f"Error processing file: {str(e)}. Please try again with a different file or format.",
                "file_processed": True,
                "chunks_found": 0,
                "query_time": time.time() - start_time,
                "success": False,
                "error": str(e)
            }
    
    def add_document(self, file_path: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add a document to the RAG system
        
        Args:
            file_path (str): Path to the document file
            metadata (Dict): Optional metadata
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            start_time = time.time()
            
            # Extract text from document
            document_text = self.doc_processor.load_pdf(file_path)
            
            # Split into chunks
            chunks = self.doc_processor.chunk_text(document_text, CHUNK_SIZE, CHUNK_OVERLAP)
            
            # Generate metadata if not provided
            if metadata is None:
                metadata = {
                    "source": os.path.basename(file_path),
                    "added_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }

            # Add chunks to vector store
            for i, chunk in enumerate(chunks):
                chunk_id = f"{os.path.basename(file_path)}_{i}"
                chunk_metadata = {**metadata, "chunk_id": chunk_id, "chunk_index": i}
                self.vector_store.add_text(chunk, chunk_metadata)
            
            return {
                "success": True,
                "chunks_added": len(chunks),
                "file": os.path.basename(file_path),
                "processing_time": time.time() - start_time
            }
            
        except Exception as e:
            print(f"Error adding document: {e}")
            print(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "file": os.path.basename(file_path)
            }
    
    def clear_database(self) -> Dict[str, Any]:
        """
        Clear all documents from the vector store
        
        Returns:
            Dict[str, Any]: Result of the operation
        """
        try:
            self.vector_store.clear()
            return {"success": True, "message": "All documents cleared from vector store"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get information about the RAG system
        
        Returns:
            Dict[str, Any]: System information
        """
        try:
            vector_count = self.vector_store.count()
            llm_info = self.llm_client.get_provider_info()
            
            # Check if OpenAI API is connected
            openai_api_connected = False
            try:
                openai_api_connected = self.llm_client.test_connection()
            except:
                pass
            
            # Get active conversations count
            active_conversations = len(self.conversation_histories)
            conversation_sessions = list(self.conversation_histories.keys())
            
            return {
                "document_count": vector_count,
                "vector_database": {
                    "path": VECTOR_DB_PATH,
                    "type": self.vector_store.__class__.__name__
                },
                "llm": llm_info,
                "chunk_size": CHUNK_SIZE,
                "max_retrieved_chunks": MAX_RETRIEVED_CHUNKS,
                "openai_api_connected": openai_api_connected,
                "conversation_memory": {
                    "active_sessions": active_conversations,
                    "max_history_length": self.max_history_length,
                    "sessions": conversation_sessions[:10]  # Only show first 10 for brevity
                }
            }
        except Exception as e:
            return {"error": str(e)}
            
    def load_and_process_pdf(self, file_path: str) -> bool:
        """
        Load and process a PDF file
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
                
            result = self.add_document(file_path)
            if result["success"]:
                print(f"✅ Successfully processed {result['chunks_added']} chunks from {file_path}")
                return True
            else:
                print(f"❌ Failed to process {file_path}: {result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            return False

    def delete_conversation(self, session_id: str) -> bool:
        """
        Delete a conversation history
        
        Args:
            session_id (str): The session ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove from memory
            if session_id in self.conversation_histories:
                del self.conversation_histories[session_id]
            
            # Remove from disk
            file_path = f"data/conversations/{session_id}.json"
            if os.path.exists(file_path):
                os.remove(file_path)
                
            return True
        except Exception as e:
            print(f"Error deleting conversation: {e}")
            return False
    
    def _ensure_valid_response(self, answer: str, question: str, prompt_type: str = "basic") -> str:
        """
        Ensure we don't return empty or 'I don't know' responses for medical questions
        
        Args:
            answer: The generated answer
            question: The user's question
            prompt_type: The prompt type used
            
        Returns:
            A valid response
        """
        # Check if the answer is empty, says it couldn't generate, or is just "I don't know"
        invalid_responses = [
            "the system processed your query but couldn't generate a response",
            "i don't know",
            "i couldn't generate a response",
            "no answer generated",
            "sorry, i cannot provide a response",
            "not enough information"
        ]
        
        # Medical-related keywords to detect medical questions
        medical_keywords = ["health", "medicine", "doctor", "hospital", "disease", "condition", 
                          "symptom", "treatment", "drug", "patient", "nurse", "therapy", "medical",
                          "clinical", "diagnosis", "surgery", "organ", "body", "anatomy", "nursing",
                          "hp level", "human body", "blood", "heart", "lungs", "brain", "liver"]
                          
        # Check if this is likely a medical question
        is_medical_question = any(keyword in question.lower() for keyword in medical_keywords)
        
        answer_lower = answer.lower() if answer else ""
        
        # If empty answer or contains invalid phrases OR answer is extremely short (less than 10 chars)
        if not answer or not answer.strip() or len(answer.strip()) < 10 or any(invalid in answer_lower for invalid in invalid_responses):
            print(f"Invalid or empty answer detected: '{answer}' for question: '{question}'")
            
            if is_medical_question:
                # Generate a specific response for the medical question
                print(f"Generating medical response for: {question}")
                
                # Extract key medical terms for more specific response
                medical_terms = [term for term in medical_keywords if term in question.lower()]
                medical_context = ", ".join(medical_terms) if medical_terms else "general medical knowledge"
                
                fallback_prompt = f"""You are a medical assistant with extensive knowledge. 
The user asked the following medical question: "{question}"

You MUST provide a helpful, informative response using your {medical_context}.
Be educational and clear. Never say you don't know or can't answer.
Explain medical terminology thoroughly. Format your answer professionally.
Keep your response focused on medical information only.
If the question doesn't make complete sense medically, try to interpret what they might be asking about and provide useful information.

Question: {question}
Answer:"""

                try:
                    # Generate fallback response
                    print("\n⚠️ Generating medical fallback response...")
                    fallback_answer = self.llm_client.generate_response(fallback_prompt)
                    if fallback_answer and fallback_answer.strip():
                        print("✅ Medical fallback response generated successfully")
                        return fallback_answer
                except Exception as e:
                    print(f"❌ Error generating medical fallback: {e}")
                    # Last resort fallbacks for common medical topics
                    if "nursing" in question.lower():
                        return "Nursing is a healthcare profession focused on the care of individuals, families, and communities to help them attain, maintain, or recover optimal health and quality of life. Nurses work in various settings including hospitals, clinics, schools, homes, and research institutions, providing care, education, and support to patients."
                    elif "body" in question.lower() or "human" in question.lower():
                        return "The human body is a complex biological system with numerous interconnected parts working together to maintain life. It consists of cells, tissues, organs, and organ systems that perform specific functions necessary for survival and well-being."
                    else:
                        # Generic medical fallback
                        return "This appears to be a medical question. While I don't have specific information about this in my medical knowledge base, I'd encourage you to consult with a healthcare professional for accurate, personalized medical information."
            else:
                # For non-medical questions that got this far
                return "I am a medical bot and can only assist with medical-related topics."
        
        return answer
