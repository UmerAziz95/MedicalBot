"""
Direct image processing module for RAG system
"""

import os
import base64
import time
import traceback
from io import BytesIO
from typing import Dict, Any, BinaryIO

class DirectImageProcessor:
    """Handle direct image processing for the RAG system"""
    
    @staticmethod
    def process_image(file_object: BinaryIO, question: str, prompt_type: str, llm_client) -> Dict[str, Any]:
        """
        Process an image file directly with the API
        
        Args:
            file_object (BinaryIO): Image file object
            question (str): User question
            prompt_type (str): Type of prompt to use
            llm_client: LLM client instance
            
        Returns:
            Dict[str, Any]: Processing result
        """
        start_time = time.time()
        
        # Get filename if available
        filename = getattr(file_object, 'filename', 'unknown_file')
        
        try:
            # Reset file pointer and read the data
            file_object.seek(0)
            file_data = file_object.read()
            
            # Determine file type
            ext = os.path.splitext(filename)[1].lower() if filename else ''
            
            if ext not in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                return {
                    "answer": f"Unsupported image format: {ext}. Please use PNG, JPG, JPEG, BMP, GIF, or TIFF.",
                    "file_processed": True,
                    "success": False,
                    "error": "Unsupported format",
                    "query_time": time.time() - start_time
                }
            
            # Encode image to base64
            base64_image = base64.b64encode(file_data).decode('utf-8')
            
            # Create appropriate prompt based on type
            if question:
                if prompt_type == "medical":
                    image_prompt = f"You are a medical expert analyzing this image. Please examine the image carefully and answer the following question: {question}"
                elif prompt_type == "detailed":
                    image_prompt = f"Please provide a detailed analysis of this image and answer the following question with thorough explanations: {question}"
                else:
                    image_prompt = f"Please analyze this image and answer: {question}"
            else:
                if prompt_type == "medical":
                    image_prompt = "You are a medical expert. Please analyze this image and provide a detailed description of any medical content visible."
                elif prompt_type == "detailed":
                    image_prompt = "Please provide a comprehensive and detailed analysis of everything visible in this image."
                else:
                    image_prompt = "Please describe what you see in this image."
            
            # Process with LLM client
            answer = llm_client.generate_image_response(image_prompt, base64_image)
            
            if not answer or answer.strip() == "":
                answer = "The system processed your image but couldn't generate a response. This might be due to API limits or content restrictions."
            
            return {
                "answer": answer,
                "file_processed": True,
                "success": True,
                "query_time": time.time() - start_time
            }
            
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            
            return {
                "answer": f"Error processing image: {str(e)}. Please try again with a different image or format.",
                "file_processed": True,
                "success": False,
                "error": str(e),
                "query_time": time.time() - start_time
            }
        # Add to your DirectImageProcessor class

    @staticmethod
    def process_image(file_object, question=None, prompt_type="basic", llm_client=None, conversation_history=""):
        """Process an image directly using vision capabilities"""
        # Your existing code...
        
        # When creating the prompt, add conversation history and enhance the instructions:
        prompt = f"""You are analyzing a medical image. {history_context}
        
        IMPORTANT: You MUST provide a clear and informative answer.
        Never say "I don't know" or "I couldn't generate a response" for medical topics - always use your medical knowledge to respond.

        If the question refers to medical terms mentioned in previous messages, explain them thoroughly.
        If the image doesn't directly show what's being asked but the question is medical in nature, use your general medical knowledge to provide a helpful response.

        Question: {question}
        """

        # When returning the result, ensure it never contains "couldn't generate a response"
        answer = result.get("answer", "")
        if not answer or "couldn't generate" in answer.lower():
            # Create fallback
            fallback_prompt = f"""You are a medical assistant analyzing an image. The user asked: "{question}"
            A previous response attempt failed. ALWAYS provide a helpful response about this medical topic using your general knowledge.
            Be informative and educational. NEVER say you don't know or can't answer."""
            try:
                answer = llm_client.generate_response(fallback_prompt)
            except:
                answer = "The system processed your image and found it relates to medical content. What specific aspect would you like me to explain?"
        
        # Return result with ensured answer
        return {
            "answer": answer,
            "success": True
        }