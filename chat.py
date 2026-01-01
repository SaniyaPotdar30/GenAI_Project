from sunbeam_rag_simple import SunbeamRAG

def main():
    print("=" * 60)
    print("🤖 SUNBEAM INSTITUTE CHATBOT")
    print("=" * 60)
    print("Initializing RAG system...")
    
    # Initialize RAG
    rag = SunbeamRAG()
    
    print("✓ Ready! Ask me anything about Sunbeam Institute.")
    print("(Type 'exit' or 'quit' to stop)\n")
    
    while True:
        # Get user input
        user_question = input("You: ").strip()
        
        # Check for exit commands
        if user_question.lower() in ['exit', 'quit', 'bye', 'q']:
            print("\n👋 Goodbye! Have a great day!")
            break
        
        # Skip empty questions
        if not user_question:
            continue
        
        # Get answer from RAG
        print("\n🤔 Thinking...")
        try:
            result = rag.query(user_question)
            print(f"\n🤖 Bot: {result['answer']}\n")
            print("-" * 60)
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("-" * 60)

if __name__ == "__main__":
    main()