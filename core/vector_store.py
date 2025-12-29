"""
Vector database operations using ChromaDB
"""

import chromadb
from typing import List, Dict, Any, Optional
from config.settings import COLLECTION_NAME, CHROMA_DB_PATH


class VectorStore:
    """Handle vector database operations"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize ChromaDB client and collection
        
        Args:
            db_path (str, optional): Path to the ChromaDB directory
        """
        # Use provided path or default from config
        path_to_use = db_path if db_path is not None else CHROMA_DB_PATH
        
        # Use persistent client with a specific path
        self.client = chromadb.PersistentClient(path=path_to_use)
        self.collection_name = COLLECTION_NAME
        self.collection = None
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure collection exists and is accessible"""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(self.collection_name)
            print(f"✅ Connected to existing collection: {self.collection_name}")
        except:
            try:
                # Create new collection if it doesn't exist
                self.collection = self.client.create_collection(self.collection_name)
                print(f"✅ Created new collection: {self.collection_name}")
            except:
                # Use get_or_create as fallback
                self.collection = self.client.get_or_create_collection(self.collection_name)
                print(f"✅ Got or created collection: {self.collection_name}")
    
    def store_chunks(self, chunks: List[str]) -> None:
        """
        Store text chunks in the vector database
        
        Args:
            chunks (List[str]): List of text chunks to store
        """
        print(f"Storing {len(chunks)} chunks in vector database...")
        
        for i, chunk in enumerate(chunks):
            print(f"Storing chunk {i+1}/{len(chunks)}")
            print(f"Preview: {chunk[:100]}...")
            
            self.collection.add(
                ids=[str(i)],
                documents=[chunk]
            )
        print("✅ All chunks stored successfully!")
    
    def query_similar_chunks(self, question: str, n_results: int = 3) -> List[str]:
        """
        Query the vector database for similar chunks
        
        Args:
            question (str): User question
            n_results (int): Number of similar chunks to retrieve
            
        Returns:
            List[str]: List of similar text chunks
        """
        # Ensure collection exists before querying
        self._ensure_collection_exists()
        
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results,
                include=["documents"]
            )
            
            retrieved_chunks = results["documents"][0] if results["documents"] else []
            print(f"Retrieved {len(retrieved_chunks)} relevant chunks")
            
            return retrieved_chunks
            
        except Exception as e:
            print(f"Error querying collection: {e}")
            # Try to recreate collection
            self._ensure_collection_exists()
            return []
    
    def search(self, query: str, k: int = 3, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents (compatibility method)
        
        Args:
            query (str): Query string
            k (int): Number of results to return
            where (Dict[str, Any], optional): Metadata filter (e.g., tenant_id/workspace_id)
            
        Returns:
            List[Dict[str, Any]]: List of document data with similarity scores
        """
        # Ensure collection exists
        self._ensure_collection_exists()
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=k,
                include=["documents", "metadatas", "distances"],
                where=where or None
            )
            
            formatted_results = []
            if results and "documents" in results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] and i < len(results["metadatas"][0]) else {}
                    distance = results["distances"][0][i] if "distances" in results and results["distances"] and i < len(results["distances"][0]) else None
                    
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "similarity": 1.0 - (distance or 0) if distance is not None else None
                    })
            
            print(f"Found {len(formatted_results)} matching documents")
            return formatted_results
        
        except Exception as e:
            print(f"Error searching collection: {e}")
            return []
    
    def add_text(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add a single text chunk with metadata
        
        Args:
            text (str): Text content
            metadata (Dict[str, Any]): Associated metadata
            
        Returns:
            str: ID of the added document
        """
        # Generate a unique ID
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Store document
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )
        
        return doc_id
    
    def clear(self) -> None:
        """Clear all data from the collection"""
        return self.clear_collection()
    
    def clear_collection(self) -> None:
        """Clear all data from the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            print("✅ Collection cleared successfully!")
        except Exception as e:
            print(f"Note: Collection may not exist: {e}")
        
        # Recreate the collection
        self._ensure_collection_exists()
    
    def count(self) -> int:
        """Get the number of documents in the collection"""
        try:
            return self.collection.count()
        except:
            return 0
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection"""
        try:
            count = self.collection.count()
            return {
                "name": COLLECTION_NAME,
                "document_count": count
            }
        except Exception as e:
            return {"error": str(e)}
