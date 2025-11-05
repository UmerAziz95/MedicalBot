"""
Standalone image processor module for direct integration
"""

import os
import base64
import time
import traceback
from io import BytesIO

# Import OpenAI client
from openai import OpenAI
from config.settings import OPENAI_API_KEY, OPENAI_MODEL

class ImageProcessor:
    """
    Handles direct processing of images with GPT-5-nano vision capabilities
    This class is designed to be used directly from the web app
    """
    
    @staticmethod
    def process_image(file_object, question=None, prompt_type="basic", conversation_history=""):
        """
        Process an image file with GPT-5-nano
        
        Args:
            file_object: File-like object with the image
            question (str): Optional question about the image
            prompt_type (str): Type of analysis (basic, detailed, medical)
            conversation_history (str): Previous conversation context
            
        Returns:
            dict: Processing result
        """
        start_time = time.time()
        
        try:
            # Get filename if available
            filename = getattr(file_object, 'filename', 'unknown_file')
            print(f"Processing image: {filename}")
            
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
            
            # Reset file pointer and read the data
            file_object.seek(0)
            image_data = file_object.read()
            
            # Create OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Add conversation history if available
            history_context = ""
            if conversation_history:
                history_context = f"\n\nPrevious conversation history:\n{conversation_history}\n\nPlease maintain consistency with any relevant information from the previous conversation."
            
            # Create appropriate prompt based on type
            if question:
                if prompt_type == "medical":
                    prompt = f"You are a medical expert analyzing this image. Please examine the image carefully and answer the following question: {question}{history_context}\n\nIf the question is medical in nature but not clearly visible in the image, use your general medical knowledge to respond. Only say 'I am a medical bot and can only assist with medical-related topics' if the question is completely unrelated to medicine or healthcare."
                elif prompt_type == "detailed":
                    prompt = f"Please provide a detailed analysis of this image and answer the following question with thorough explanations: {question}{history_context}\n\nIf the question is medical in nature but not clearly visible in the image, use your general medical knowledge to respond. Only say 'I am a medical bot and can only assist with medical-related topics' if the question is completely unrelated to medicine or healthcare."
                else:
                    prompt = f"Please analyze this image and answer: {question}{history_context}\n\nIf the question is medical in nature but not clearly visible in the image, use your general medical knowledge to respond. Only say 'I am a medical bot and can only assist with medical-related topics' if the question is completely unrelated to medicine or healthcare."
            else:
                if prompt_type == "medical":
                    prompt = f"You are a medical expert. Please analyze this image and provide a detailed description of any medical content visible.{history_context}"
                elif prompt_type == "detailed":
                    prompt = f"Please provide a comprehensive and detailed analysis of everything visible in this image, focusing on any medical or health-related aspects if present.{history_context}"
                else:
                    prompt = f"Please describe what you see in this image, focusing on any medical or health-related aspects if present.{history_context}"
            
            print(f"Processing with prompt: {prompt}")
            
            # Send API request - WITHOUT any token parameters that might cause issues
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
                # No token parameters to avoid compatibility issues
            )
            
            # Get result
            answer = response.choices[0].message.content
            
            if not answer or answer.strip() == "":
                answer = "The system processed your image but couldn't generate a response. This might be due to API limits or content restrictions."
            
            print(f"\n{'='*20} ANSWER {'='*20}")
            print(answer)
            print(f"{'='*47}")
            
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