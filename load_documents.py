"""
Enhanced Dynamic Document Loader - Better progress tracking and file support
"""
import os
import sys
import time
import threading
from pathlib import Path
import humanize  # Install with: pip install humanize

# Add project root to path if needed
sys.path.append(os.path.abspath('.'))

from core.rag_system import RAGSystem
from scripts.setup_documents import DocumentSetup

# File type mappings
SUPPORTED_EXTENSIONS = {
    '.pdf': 'PDF Document',
    '.txt': 'Text File',
    '.docx': 'Word Document',
    '.doc': 'Word Document (Legacy)',
    '.md': 'Markdown',
    '.rtf': 'Rich Text Format',
    '.csv': 'CSV Data',
    '.json': 'JSON Data',
    '.html': 'HTML Document'
}

class ProgressTracker:
    """Track and display processing progress"""
    
    def __init__(self, total_files):
        self.total_files = total_files
        self.processed_files = 0
        self.successful = 0
        self.failed = 0
        self.start_time = time.time()
        self.current_file = None
        self.current_file_size = 0
        self.current_file_start = 0
        self._stop_event = threading.Event()
        self._progress_thread = None
        
    def start_file(self, filepath):
        """Start tracking a new file"""
        self.current_file = os.path.basename(filepath)
        self.current_file_size = os.path.getsize(filepath)
        self.current_file_start = time.time()
        
        # Start progress animation in a separate thread
        self._stop_event.clear()
        self._progress_thread = threading.Thread(target=self._animate_progress)
        self._progress_thread.daemon = True
        self._progress_thread.start()
    
    def finish_file(self, success):
        """Mark current file as finished"""
        # Stop the progress animation
        if self._progress_thread:
            self._stop_event.set()
            self._progress_thread.join()
        
        self.processed_files += 1
        if success:
            self.successful += 1
        else:
            self.failed += 1
        
        # Clear the progress line
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()
        
    def _animate_progress(self):
        """Animate progress indicator"""
        animation = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        idx = 0
        
        while not self._stop_event.is_set():
            elapsed = time.time() - self.current_file_start
            progress = min(100, int((elapsed / max(1, elapsed)) * 100))
            
            # Create progress bar
            progress_bar = self._get_progress_bar(progress)
            
            # Print status
            status = f"\r{animation[idx]} Processing: {self.current_file} {progress_bar} {elapsed:.1f}s"
            sys.stdout.write(status)
            sys.stdout.flush()
            
            idx = (idx + 1) % len(animation)
            time.sleep(0.1)
    
    def _get_progress_bar(self, percent):
        """Generate a text progress bar"""
        width = 20
        filled = int(width * percent / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percent}%"
    
    def print_summary(self):
        """Print summary of processing"""
        total_time = time.time() - self.start_time
        print("\n========== PROCESSING SUMMARY ==========")
        print(f"Total time: {total_time:.1f} seconds")
        print(f"Files processed: {self.processed_files} of {self.total_files}")
        print(f"Successful: {self.successful}")
        print(f"Failed: {self.failed}")
        if self.successful > 0:
            print(f"Average time per successful file: {total_time/self.successful:.1f} seconds")
        print("========================================")

def get_file_info(filepath):
    """Get formatted file information"""
    size = os.path.getsize(filepath)
    mod_time = os.path.getmtime(filepath)
    extension = os.path.splitext(filepath)[1].lower()
    file_type = SUPPORTED_EXTENSIONS.get(extension, "Unknown")
    
    return {
        "name": os.path.basename(filepath),
        "path": filepath,
        "size": size,
        "size_human": humanize.naturalsize(size),
        "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time)),
        "extension": extension,
        "type": file_type
    }

def main():
    print("\n📚 ========== ENHANCED DOCUMENT LOADER ==========")
    
    # Initialize components
    doc_setup = DocumentSetup()
    
    # Check if documents are already loaded
    db_info = doc_setup.get_database_info()
    print(f"Current document count: {db_info.get('document_count', 0)} chunks")
    
    # Ask if user wants to clear existing documents
    if db_info.get('document_count', 0) > 0:
        print("\nDocuments already exist in the database.")
        print("Do you want to clear existing documents before loading new ones? (y/n)")
        choice = input().lower()
        if choice == 'y':
            print("Clearing existing documents...")
            doc_setup.vector_store.clear_collection()
            print("✅ Database cleared")
    
    # Define document directories to check
    doc_directories = [
        "./static/documents/",
        "./data/documents/",
    ]
    
    # Print current directory for debugging
    print(f"Current directory: {os.path.abspath('.')}")
    
    # Find all documents in the specified directories
    all_documents = []
    for directory in doc_directories:
        if os.path.exists(directory) and os.path.isdir(directory):
            print(f"\n📁 Scanning directory: {directory}")
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    # Check file extension
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in SUPPORTED_EXTENSIONS:
                        file_info = get_file_info(filepath)
                        all_documents.append(file_info)
                        print(f"  📄 Found: {filename} ({file_info['size_human']}, {file_info['type']})")
    
    if not all_documents:
        print("\n❌ No documents found in the searched directories")
        print("Would you like to create the static/documents directory? (y/n)")
        choice = input().lower()
        if choice == 'y':
            os.makedirs("static/documents", exist_ok=True)
            print("✅ Created static/documents directory")
            print("Please copy your documents to this directory and run this script again.")
        return
    
    # Sort documents by size (process smaller files first for quick wins)
    all_documents.sort(key=lambda x: x['size'])
    
    # Process all found documents
    print(f"\n🔄 Found {len(all_documents)} documents to process")
    print(f"Total size: {humanize.naturalsize(sum(doc['size'] for doc in all_documents))}")
    print("Processing will begin in 3 seconds... Press Ctrl+C to cancel")
    time.sleep(3)
    
    # Initialize progress tracker
    progress = ProgressTracker(len(all_documents))
    
    for i, file_info in enumerate(all_documents):
        filepath = file_info['path']
        file_name = file_info['name']
        
        print(f"\n[{i+1}/{len(all_documents)}] 📄 {file_name} ({file_info['size_human']}, {file_info['type']})")
        
        # Start tracking progress
        progress.start_file(filepath)
        
        try:
            result = doc_setup.add_document(filepath)
            if result:
                progress.finish_file(True)
                print(f"  ✅ Success - Processed in {time.time() - progress.current_file_start:.2f} seconds")
            else:
                progress.finish_file(False)
                print(f"  ❌ Failed to process document - No content extracted")
        except Exception as e:
            progress.finish_file(False)
            print(f"  ❌ Error: {str(e)}")
    
    # Show processing summary
    progress.print_summary()
    
    # Show final document count
    db_info = doc_setup.get_database_info()
    print(f"\n📊 Final document count: {db_info.get('document_count', 0)} chunks")
    
    if db_info.get('sources'):
        print("\n📝 Documents in database:")
        for i, source in enumerate(db_info.get('sources', [])):
            print(f"  {i+1}. {source}")
    
    print("\n✨ Done! You can now start your app with: python -m web.app")
    print("=================================================")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        print("Exiting...")
        sys.exit(0)