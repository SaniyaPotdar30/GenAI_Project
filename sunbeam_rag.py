from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from sunbeam_vectorstore import SunbeamVectorStore
from chunking import chunk_all_scraped_data

class SunbeamRAG:
    def __init__(self):
        # Initialize LLM (using your LM Studio setup)
        self.llm = init_chat_model(
            "llama-3.2-1b-instruct",
            model_provider="openai",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio",
        )
        
        # Initialize embeddings (using your LM Studio setup)
        self.emb = init_embeddings(
            "text-embedding-nomic-embed-text-v1.5",
            provider="openai",
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio",
            check_embedding_ctx_length=False
        )
        
        # Initialize vector store
        self.vs = SunbeamVectorStore(
            "chroma_db",  # Your chroma DB directory
            self.emb.embed_query,
            self.emb.embed_documents
        )
    
    def load_data_to_vectorstore(self):
        """Load all scraped and chunked data into vector store."""
        file_paths = {
            'about_us': 'about_us_data.json',
            'internship': 'internship_complete_data.json',
            'precat': 'precat_data.json',
            'modular_courses': 'modular_courses_data.json',
            'mcq_course': 'mastering_mcqs_data.json'
        }
        
        # Get all chunked documents
        docs = chunk_all_scraped_data(file_paths)
        
        print(f"Loading {len(docs)} documents into vector store...")
        
        # Prepare data for vector store
        documents = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        doc_ids = [f"doc_{i}" for i in range(len(docs))]
        
        # Add to vector store
        success = self.vs.add_documents(documents, metadatas, doc_ids)
        
        if success:
            print(f"✓ Successfully loaded {len(docs)} documents!")
        else:
            print("❌ Failed to load documents")
        
        return success
    
    def query(self, question: str, max_results=3):
        """Query the RAG system."""
        # Find similar documents
        similar_docs = self.vs.find_similar_documents(question, max_results)
        
        # Build context from similar documents
        context = "\n\n".join([doc["document"] for doc in similar_docs])
        
        # Create prompt
        prompt = f"""Based on the following information about Sunbeam Institute, answer the question.

Context:
{context}

Question: {question}

Answer in simple English:"""
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        return {
            "answer": response.content,
            "sources": similar_docs
        }
    
    def get_vector_store(self):
        """Get the vector store instance."""
        return self.vs