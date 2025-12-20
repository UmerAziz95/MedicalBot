"""
LLM Client module for RAG system
Handles interactions with various language models
"""

import os
import json
import requests
from typing import Dict, Any, Optional
import traceback

from config.settings import OPENAI_API_KEY, OPENAI_MODEL

class LLMClient:
    """Client for interacting with language models"""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        Initialize LLM client
        
        Args:
            provider (str): LLM provider (openai, ollama)
            model (str): Specific model to use
        """
        self.provider = provider.lower()
        
        # Set up OpenAI client if needed
        if self.provider == "openai":
            try:
                # Try to import new OpenAI client
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
                self.openai_version = "new"
                print("Using new OpenAI client (v1.0.0+)")
            except Exception as e:
                # Fall back to old client
                try:
                    import openai
                    openai.api_key = OPENAI_API_KEY
                    self.openai_client = openai
                    self.openai_version = "old"
                    print("Using legacy OpenAI client")
                except Exception as e2:
                    print(f"Failed to initialize OpenAI client: {e2}")
        
        # Set model
        if model:
            self.model = model
        else:
            self.model = OPENAI_MODEL
            
        # Check if model is GPT-5-nano
        self.is_gpt5_nano = "gpt-5-nano" in self.model.lower()
    
    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt (str): The input prompt
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, max_tokens)
        else:
            return f"Unsupported LLM provider: {self.provider}"

    def classify_query(self, question: str) -> Optional[str]:
        """
        Classify a query as medical or non-medical using the LLM.

        Args:
            question (str): The user's question to classify

        Returns:
            Optional[str]: "medical", "non-medical", or None if classification fails
        """
        if not question:
            return None

        if self.provider != "openai":
            return None

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a classifier that labels user questions as either medical or non-medical. "
                        "Respond with a single word: 'medical' if the primary intent is about health, medicine, "
                        "or healthcare topics; otherwise respond with 'non-medical'."
                    ),
                },
                {"role": "user", "content": question},
            ]

            token_param = "max_completion_tokens" if self.is_gpt5_nano else "max_tokens"
            kwargs = {token_param: 5}

            if self.openai_version == "new":
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )
                content = response.choices[0].message.content.strip().lower()
            else:
                response = self.openai_client.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    **kwargs,
                )
                content = response.choices[0].message["content"].strip().lower()

            normalized = content.replace("nonmedical", "non-medical")
            if normalized.startswith("non-medical") or normalized.startswith("non medical"):
                return "non-medical"
            if normalized.startswith("medical"):
                return "medical"

            return None
        except Exception as e:
            print(f"Error classifying query: {e}")
            print(traceback.format_exc())
            return None
    
    def _generate_openai(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a response using OpenAI
        
        Args:
            prompt (str): The input prompt
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        try:
            if self.openai_version == "new":
                # New client API (v1.0.0+)
                kwargs = {}
                
                # Use correct parameter based on model
                if self.is_gpt5_nano:
                    kwargs["max_completion_tokens"] = max_tokens
                else:
                    kwargs["max_tokens"] = max_tokens
                    
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    **kwargs
                )
                return response.choices[0].message.content.strip()
            else:
                # Old client API
                response = self.openai_client.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens
                )
                return response.choices[0].message["content"].strip()
                
        except Exception as e:
            print(f"Error generating response: {e}")
            print(traceback.format_exc())
            return f"Error: {str(e)}"
    
    def generate_image_response(self, prompt: str, base64_image: str, max_tokens: int = 1000) -> str:
        """
        Generate a response based on an image using vision capabilities
        
        Args:
            prompt (str): The text prompt
            base64_image (str): Base64-encoded image data
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: Generated response
        """
        try:
            if self.provider == "openai":
                # Use the configured model with vision capabilities
                if self.openai_version == "new":
                    try:
                        # Create a message with text and image
                        kwargs = {}
                        
                        # Use correct parameter based on model
                        if self.is_gpt5_nano:
                            kwargs["max_completion_tokens"] = max_tokens
                        else:
                            kwargs["max_tokens"] = max_tokens
                            
                        response = self.openai_client.chat.completions.create(
                            model=self.model,  # Use the configured model
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
                            ],
                            **kwargs
                        )
                        
                        # Check for a valid response
                        if hasattr(response, 'choices') and len(response.choices) > 0:
                            return response.choices[0].message.content.strip()
                        else:
                            return "Error: Empty response from OpenAI API"
                    
                    except Exception as e:
                        print(f"Error with vision API: {e}")
                        return f"Error processing image: {str(e)}"
                else:
                    # Old client doesn't support vision API well
                    return "Image analysis requires OpenAI client v1.0.0 or newer. Please update your OpenAI package."
            else:
                return "Image analysis is only supported with OpenAI provider. Ollama doesn't support this feature yet."
                
        except Exception as e:
            print(f"Error processing image: {e}")
            print(traceback.format_exc())
            return f"Error generating image response: {str(e)}"
    
    def test_connection(self) -> bool:
        """
        Test the connection to the LLM provider
        
        Returns:
            bool: True if connection is successful
        """
        try:
            if self.provider == "openai":
                test_prompt = "Hello, this is a test!"
                self.generate_response(test_prompt, max_tokens=10)
                return True
            else:
                return False
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current provider
        
        Returns:
            Dict[str, Any]: Provider information
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "client_version": self.openai_version if self.provider == "openai" else None
        }