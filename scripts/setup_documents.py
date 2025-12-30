"""
Document setup script - Run this ONCE to process and store your documents
"""

import os
import sys
from pathlib import Path
from processors.document_processor import DocumentProcessor
from core.vector_store import VectorStore
from config.settings import PDF_FILE_PATH, CHUNK_SIZE, CHUNK_OVERLAP, DOCUMENTS_DIR


class DocumentSetup:
    """Handle one-time document processing and storage"""
    
    def __init__(self):
        """Initialize processors"""
        self.doc_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.processed_files = []
    
    def add_document(self, file_path: str, clear_existing: bool = False,
                    tenant_id: str | None = None) -> bool:
        """
        Process and store a single document
        
        Args:
            file_path (str): Path to the document
            clear_existing (bool): Whether to clear existing documents first
            
        Returns:
            bool: Success status
        """
        if clear_existing:
            print("🗑️ Clearing existing documents...")
            self.vector_store.clear_collection()
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        try:
            print(f"📄 Processing: {file_path}")
            
            # Extract text from document
            print("   📖 Extracting text...")
            ext = os.path.splitext(file_path)[1].lower()
            
            # Extract text based on file type
            if ext in ['.pdf']:
                text = self.doc_processor.load_pdf(file_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                text = self.doc_processor.extract_text_from_image(file_path)
            else:
                print(f"   ❌ Unsupported file format: {ext}")
                return False
            
            if not text or len(text.strip()) < 100:
                print("   ❌ No meaningful text extracted")
                return False
            
            print(f"   ✅ Extracted {len(text):,} characters")
            
            # Create chunks
            print("   ✂️ Creating chunks...")
            chunks = self.doc_processor.chunk_text(
                text, 
                chunk_size=CHUNK_SIZE, 
                overlap=CHUNK_OVERLAP
            )
            
            if not chunks:
                print("   ❌ No chunks created")
                return False
            
            print(f"   ✅ Created {len(chunks)} chunks")
            
            # Store chunks with metadata
            print("   💾 Storing in database...")
            file_name = os.path.basename(file_path)
            
            # Add metadata to chunks
            chunk_ids = []
            chunk_docs = []
            chunk_metadatas = []
            
            current_count = self.vector_store.get_collection_info().get('document_count', 0)
            
            tenant_value = tenant_id or "default_tenant"

            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_name}_{current_count + i}"
                chunk_ids.append(chunk_id)
                chunk_docs.append(chunk)
                chunk_metadatas.append({
                    "source": file_name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "tenant_id": tenant_value
                })
            
            # Store all chunks at once
            self.vector_store.collection.add(
                ids=chunk_ids,
                documents=chunk_docs,
                metadatas=chunk_metadatas
            )
            
            print(f"   ✅ Stored {len(chunks)} chunks successfully")
            
            self.processed_files.append({
                "file": file_name,
                "path": file_path,
                "chunks": len(chunks),
                "characters": len(text)
            })
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing {file_path}: {e}")
            return False
    
    def add_multiple_documents(self, file_paths: list, clear_existing: bool = False,
                               tenant_id: str | None = None) -> dict:
        """
        Process multiple documents
        
        Args:
            file_paths (list): List of file paths
            clear_existing (bool): Clear existing documents first
            
        Returns:
            dict: Processing results
        """
        results = {
            "successful": 0,
            "failed": 0,
            "total_chunks": 0,
            "files": []
        }
        
        for i, file_path in enumerate(file_paths):
            print(f"\n📋 Processing file {i+1}/{len(file_paths)}")
            
            # Only clear on first file
            should_clear = clear_existing and i == 0
            
            if self.add_document(file_path, clear_existing=should_clear,
                                 tenant_id=tenant_id):
                results["successful"] += 1
                if self.processed_files:
                    last_file = self.processed_files[-1]
                    results["total_chunks"] += last_file["chunks"]
                    results["files"].append(last_file)
            else:
                results["failed"] += 1
        
        return results
    
    def get_database_info(self) -> dict:
        """Get current database information"""
        info = self.vector_store.get_collection_info()
        
        # Try to get file information from metadata
        try:
            # Query a few documents to see what sources we have
            sample_results = self.vector_store.collection.get(
                limit=100,
                include=["metadatas"]
            )
            
            sources = set()
            if sample_results and "metadatas" in sample_results:
                for metadata in sample_results["metadatas"]:
                    if metadata and "source" in metadata:
                        sources.add(metadata["source"])
            
            info["sources"] = list(sources)
            info["unique_documents"] = len(sources)
            
        except Exception as e:
            info["sources"] = []
            info["unique_documents"] = 0
            info["metadata_error"] = str(e)
        
        return info
    
    def process_all_documents_in_folder(self, folder_path=None,
                                        tenant_id: str | None = None) -> dict:
        """
        Process all supported documents in a folder
        
        Args:
            folder_path (str): Path to the folder with documents
            
        Returns:
            dict: Processing results
        """
        if folder_path is None:
            folder_path = DOCUMENTS_DIR
            
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return {
                "error": f"Folder not found: {folder_path}",
                "successful": 0,
                "failed": 0
            }
        
        # Find all supported documents
        supported_extensions = ['.pdf', '.txt', '.docx', '.md']
        file_paths = []
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in supported_extensions:
                    file_paths.append(file_path)
        
        if not file_paths:
            return {
                "message": "No supported documents found in folder",
                "successful": 0,
                "failed": 0
            }
            
        print(f"Found {len(file_paths)} documents to process")
        return self.add_multiple_documents(
            file_paths,
            clear_existing=False,
            tenant_id=tenant_id
        )
