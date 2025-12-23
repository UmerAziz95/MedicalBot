"""
Main entry point for the Medical RAG system
"""

import os
import sys
from core.rag_system import RAGSystem
from config.settings import PDF_FILE_PATH


def main():
    """Main function to demonstrate the RAG system"""
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Display system information
    print("\n" + "="*60)
    print("         MEDICAL RAG SYSTEM")
    print("="*60)
    
    system_info = rag.get_system_info()
    print(f"📊 System Info:")
    print(f"   - Documents in DB: {system_info['vector_database'].get('document_count', 'Unknown')}")
    print(f"   - OpenAI API Status: {'✅ Connected' if system_info['openai_api_connected'] else '❌ Not Connected'}")
    print(f"   - Chunk Size: {system_info['chunk_size']}")
    print(f"   - Max Retrieved Chunks: {system_info['max_retrieved_chunks']}")
    
    # Load and process PDF
    print(f"\n📚 Loading PDF: {PDF_FILE_PATH}")
    success = rag.load_and_process_pdf(PDF_FILE_PATH)
    
    if not success:
        print("❌ Failed to load PDF. Please check the file path and try again.")
        return
    
    # Test questions
    test_questions = [
        "What is transcultural nursing?",
        "What are the symptoms of COVID-19?",
        "How to manage patient care?",
        "What are the key principles of medical ethics?"
    ]
    
    print(f"\n🤖 Running test queries...")
    
    # Process each question
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*10} Question {i} {'='*10}")
        # Using medical prompt type for better medical responses
        answer = rag.query(question, prompt_type="medical")
    
    print(f"\n{'='*60}")
    print("🎉 Demo completed successfully!")
    print("="*60)


def interactive_mode():
    """Interactive mode for asking custom questions"""
    
    rag = RAGSystem()
    
    print("\n" + "="*60)
    print("         INTERACTIVE RAG SYSTEM")
    print("="*60)
    print("Commands:")
    print("  - Type 'load <filepath>' to load a PDF")
    print("  - Type 'clear' to clear the database")
    print("  - Type 'info' to see system information")
    print("  - Type 'exit' to quit")
    print("  - Type any question to query the system")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
                
            elif user_input.lower() == 'clear':
                rag.clear_database()
                
            elif user_input.lower() == 'info':
                info = rag.get_system_info()
                print(f"📊 System Information:")
                for key, value in info.items():
                    print(f"   {key}: {value}")
                    
            elif user_input.lower().startswith('load '):
                file_path = user_input[5:].strip()
                rag.load_and_process_pdf(file_path)
                
            elif user_input:
                # Regular query
                prompt_types = ["basic", "medical", "detailed"]
                print("\nSelect prompt type:")
                for i, pt in enumerate(prompt_types, 1):
                    print(f"  {i}. {pt}")
                
                try:
                    choice = input("Enter choice (1-3, or press Enter for basic): ").strip()
                    if choice == "":
                        prompt_type = "basic"
                    else:
                        prompt_type = prompt_types[int(choice) - 1]
                except:
                    prompt_type = "basic"
                
                answer = rag.query(user_input, prompt_type=prompt_type)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    # Create necessary directories
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()