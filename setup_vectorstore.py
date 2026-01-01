from sunbeam_rag_simple import SunbeamRAG  # Changed import

if __name__ == "__main__":
    print("Setting up Sunbeam RAG system...")
    
    rag = SunbeamRAG()
    rag.load_data_to_vectorstore()
    
    print("\n✓ Setup complete! Vector store is ready.")
    
    print("\nTesting with a sample query...")
    result = rag.query("What internship programs are available?", max_results=5)
    print(f"\nAnswer: {result['answer']}")