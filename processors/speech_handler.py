"""
Speech handling module for text-to-speech and speech-to-text functionality
"""

import os
import base64
import tempfile
from typing import Dict, Any, Optional

# Import text-to-speech library - using gTTS as it's widely available
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    print("Warning: gTTS not installed. Text-to-speech functionality will be limited.")

class SpeechHandler:
    """Handler for speech-related functionality"""
    
    @staticmethod
    def text_to_speech(text: str, lang: str = 'en') -> Dict[str, Any]:
        """
        Convert text to speech and return as base64 encoded audio
        
        Args:
            text (str): Text to convert to speech
            lang (str): Language code (default: 'en')
            
        Returns:
            Dict: Result with audio data or error
        """
        if not GTTS_AVAILABLE:
            return {
                "success": False,
                "error": "Text-to-speech functionality requires gTTS. Please install with: pip install gtts"
            }
            
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_path = temp_audio.name
            
            # Generate speech using gTTS
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_path)
            
            # Read the generated audio file
            with open(temp_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Encode audio data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return {
                "success": True,
                "audio_data": audio_base64,
                "audio_type": "audio/mp3",
                "text": text
            }
            
        except Exception as e:
            print(f"Error in text-to-speech conversion: {e}")
            return {
                "success": False,
                "error": str(e)
            }