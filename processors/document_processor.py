"""
Document processing utilities for RAG system
"""

import os
import tempfile
import io
from typing import List, BinaryIO, Dict
import traceback

# Import conditionally to handle environments without these dependencies
try:
    from pypdf import PdfReader
except ImportError:
    print("Warning: pypdf not installed. PDF processing will be unavailable.")
    PdfReader = None

try:
    from PIL import Image
except ImportError:
    print("Warning: PIL not installed. Image processing will be unavailable.")
    Image = None


class DocumentProcessor:
    """Handle document loading and text extraction for various formats"""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        """
        Load PDF and extract all text
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from PDF
        """
        if PdfReader is None:
            return "Error: PDF processing is unavailable. Please install pypdf."
        
        try:
            reader = PdfReader(file_path)
            text = ""
            
            # Check if PDF is encrypted
            if reader.is_encrypted:
                try:
                    # Try empty password first
                    reader.decrypt('')
                except:
                    return "Error: Cannot process encrypted PDF. Please provide an unencrypted document."
            
            # Check if there are pages
            if len(reader.pages) == 0:
                return "The PDF file appears to be empty (contains no pages)."
            
            # Extract text from each page
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num}: {e}")
            
            # If we couldn't extract meaningful text, return a message
            if not text or len(text.strip()) < 50:
                return f"""
This PDF appears to contain mostly images, scanned content, or limited text.
For better results, the file will be processed directly by the AI.
"""
            
            return text
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            print(traceback.format_exc())
            return f"Error loading PDF: {str(e)}"
    
    @staticmethod
    def extract_text_from_image(image_path: str) -> str:
        """
        Instead of OCR, return a message indicating direct API processing
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Message about direct processing
        """
        # For image files, we'll bypass OCR and return a message
        try:
            if Image is None:
                return "Image will be processed directly by the AI."
            
            # Get basic image info
            image = Image.open(image_path)
            width, height = image.size
            file_size = os.path.getsize(image_path) / 1024  # KB
            
            return f"""
This is an image file ({width}x{height} pixels).
Rather than extracting text with OCR, the image will be processed directly by the AI.
Please ask specific questions about what you see in the image.
"""
        except Exception as e:
            print(f"Error handling image: {e}")
            return "Image will be processed directly by the AI."
    
    @staticmethod
    def extract_text_from_file(file_object: BinaryIO) -> str:
        """
        Extract text from various file formats or prepare for direct processing
        
        Args:
            file_object (BinaryIO): File object
            
        Returns:
            str: Extracted text or message about direct processing
        """
        # Get file extension if possible
        filename = getattr(file_object, 'filename', '')
        if filename:
            ext = os.path.splitext(filename)[1].lower()
        else:
            ext = ''  # Unknown extension
        
        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_path = temp_file.name
        
        try:
            # Save file content to temp file
            file_object.seek(0)  # Reset file pointer
            temp_file.write(file_object.read())
            temp_file.close()
            
            # Extract text based on file type
            if ext in ['.pdf']:
                return DocumentProcessor.load_pdf(temp_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                return DocumentProcessor.extract_text_from_image(temp_path)
            else:
                return f"Unsupported file format: {ext}. Supported formats are PDF and common image formats."
                
        except Exception as e:
            print(f"Error extracting text: {e}")
            print(traceback.format_exc())
            return f"Error extracting text: {str(e)}"
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text (str): Text to be chunked
            chunk_size (int): Size of each chunk
            overlap (int): Overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        # Handle error messages that were returned instead of actual text
        if text.startswith("Error:"):
            return [text]
            
        chunks = []
        start = 0
        
        # If text is very short, just return it as one chunk
        if len(text) < chunk_size * 1.5:
            return [text]
            
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:  # skip empty chunks
                chunks.append(chunk)
            start += chunk_size - overlap
            
        return chunks


# For backwards compatibility
PDFProcessor = DocumentProcessor