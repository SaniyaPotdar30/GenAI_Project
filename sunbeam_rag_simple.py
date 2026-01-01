import requests
import json
import re
import os
from dotenv import load_dotenv
from sunbeam_vectorstore import SunbeamVectorStore
from chunking import chunk_all_scraped_data

load_dotenv()

class SunbeamRAG:
    def __init__(self):
        self.base_url = "http://127.0.0.1:1234/v1"
        self.vs = SunbeamVectorStore("chroma_db", self.embed_query, self.embed_documents)
    
    def embed_query(self, text):
        """Uses Nomic Embed from LM Studio (LOCAL)"""
        response = requests.post(
            f"{self.base_url}/embeddings",
            json={
                "input": text,
                "model": "text-embedding-nomic-embed-text-v1.5"
            }
        )
        return response.json()["data"][0]["embedding"]
    
    def embed_documents(self, texts):
        """Uses Nomic Embed from LM Studio (LOCAL)"""
        try:
            response = requests.post(
                f"{self.base_url}/embeddings",
                json={
                    "input": texts,
                    "model": "text-embedding-nomic-embed-text-v1.5"
                }
            )
            result = response.json()
            if "data" not in result:
                return [self.embed_query(text) for text in texts]
            return [item["embedding"] for item in result["data"]]
        except Exception as e:
            return [self.embed_query(text) for text in texts]
    
    def call_llm(self, prompt):
        """Uses Groq LLaMA 70B (CLOUD - SMART & FAST)"""
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    
    def load_data_to_vectorstore(self):
        file_paths = {
            'about_us': 'data/about_us_data.json',
            'internship': 'data/internship_complete_data.json',
            'precat': 'data/precat_data.json',
            'modular_courses': 'data/modular_courses_data.json',
            'mcq_course': 'data/mastering_mcqs_data.json',
            'contact': 'data/contact_data.json'
        }
        docs = chunk_all_scraped_data(file_paths)
        print(f"Loading {len(docs)} documents...")
        
        documents = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        doc_ids = [f"doc_{i}" for i in range(len(docs))]
        
        success = self.vs.add_documents(documents, metadatas, doc_ids)
        print(f"✓ Loaded {len(docs)} documents!" if success else "❌ Failed")
        return success
    
    def get_all_internship_programs(self):
        all_docs = self.vs.get_all_documents()
        programs = []
        seen = set()
        
        for doc in all_docs:
            metadata = doc.get('metadata', {})
            if metadata.get('section_type') == 'program' and metadata.get('page') == 'internship':
                tech = metadata.get('technology', 'Unknown')
                loc = metadata.get('location', 'Unknown')
                key = f"{tech}|{loc}"
                if key not in seen and tech != 'N/A':
                    seen.add(key)
                    programs.append({'technology': tech, 'location': loc})
        return programs
    
    def query(self, question: str, max_results=None):
        question_lower = question.lower().strip()
        
        list_keywords = ['what are', 'list', 'all', 'available', 'programs', 'courses', 'which']
        is_list_question = any(kw in question_lower for kw in list_keywords)
        
        # Contact queries (keep this - it's more accurate than LLM extraction)
        contact_keywords = ['email', 'contact', 'phone', 'number', 'address', 'reach']
        if any(kw in question_lower for kw in contact_keywords):
            similar_docs = self.vs.find_similar_documents(question, 5)
            context = "\n\n".join([doc["document"] for doc in similar_docs])
            
            emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', context)))
            phones = list(set(re.findall(r'[\+\d][\d\-\(\)\s]{8,}[\d]', context)))
            
            answer = "📧 Email: " + ", ".join(emails) if emails else ""
            if phones:
                answer += ("\n" if answer else "") + "📞 Phone: " + ", ".join(phones[:2])
            if not emails and not phones:
                answer = "Contact info not found. Visit: https://www.sunbeaminfo.in/contact-us"
            
            return {"answer": answer, "sources": similar_docs}
        
        # Internship programs (keep this - more reliable than LLM)
        if is_list_question and 'internship' in question_lower and 'program' in question_lower:
            programs = self.get_all_internship_programs()
            if programs:
                answer = "Internship programs at Sunbeam:\n\n" + "\n".join([f"{i}. {p['technology']} - {p['location']}" for i, p in enumerate(programs, 1)])
                return {"answer": answer, "sources": [], "total_programs": len(programs)}
        
        # For everything else (including greetings), use the LLM
        max_results = max_results or (8 if is_list_question else 4)
        similar_docs = self.vs.find_similar_documents(question, max_results)
        context = "\n\n".join([doc["document"] for doc in similar_docs])
        
        # Smart prompt that handles both casual and technical questions
        prompt = f"""You are a helpful assistant for Sunbeam Institute.

Question: {question}

Context (use only if relevant to the question):
{context}

Instructions:
- For greetings or casual chat, respond naturally and friendly
- For questions about Sunbeam, use the context to give accurate 2-3 sentence answers
- Be conversational and helpful

Answer:"""
        
        answer = self.call_llm(prompt)
        return {"answer": answer, "sources": similar_docs}
    
    def get_vector_store(self):
        return self.vs