from sunbeam_rag_simple import SunbeamRAG

class RAGWrapper:
    """Wrapper to make SunbeamRAG compatible with langchain LLM interface"""
    
    def __init__(self):
        self.rag = SunbeamRAG()
    
    def invoke(self, messages):
        """Makes RAG compatible with langchain's invoke() method"""
        # Extract the last user message
        user_message = ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
            elif isinstance(msg, str):
                user_message = msg
                break
        
        # Get answer from RAG
        result = self.rag.query(user_message)
        
        # Return in langchain format
        class Response:
            def __init__(self, content):
                self.content = content
        
        return Response(result['answer'])