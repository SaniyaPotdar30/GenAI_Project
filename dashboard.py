import streamlit as st
import os
import requests
from dotenv import load_dotenv
from sunbeam_rag_simple import SunbeamRAG

load_dotenv()

GROQ_MODELS = ["llama-3.3-70b-versatile"]
LM_STUDIO_MODELS = ["phi-3-mini-4k-instruct", "llama-3.2-1b-instruct"]
GEMINI_MODELS = ["gemini-2.5-flash"]

def call_llm_with_provider(prompt, provider, model):
    """Call different LLM providers with the same prompt"""
    
    if provider == "Groq":
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    
    elif provider == "LM Studio":
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 300
            }
        )
        return response.json()["choices"][0]["message"]["content"]
    
    elif provider == "Gemini":
        # For Gemini, we'll use langchain
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3
        )
        response = llm.invoke(prompt)
        return response.content

def dashboard():
    st.success(f"Welcome {st.session_state.username} 🎉")
    st.title("📚 Sunbeam GenAI Chatbot")

    # Initialize RAG system (always in background)
    if "rag" not in st.session_state:
        with st.spinner("Loading knowledge base..."):
            st.session_state.rag = SunbeamRAG()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "provider" not in st.session_state:
        st.session_state.provider = "Groq"

    if "model" not in st.session_state:
        st.session_state.model = GROQ_MODELS[0]

    # ================= SIDEBAR ==================
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        st.caption("Model & Chat Settings")

        st.divider()

        with st.expander("🤖 Model Settings", expanded=True):
            provider = st.radio(
                "Choose LLM Provider",
                ["Groq", "LM Studio", "Gemini"],
                horizontal=True
            )

            if provider == "Groq":
                model = st.selectbox("Groq Models", GROQ_MODELS)
            elif provider == "LM Studio":
                model = st.selectbox("LM Studio Models", LM_STUDIO_MODELS)
            else:
                model = st.selectbox("Gemini Models", GEMINI_MODELS)
            
            st.caption("📚 RAG retrieval always active")

        st.divider()

        with st.expander("💬 Chat Settings", expanded=True):
            show_history = st.toggle("Show Chat History", value=True)

            if show_history:
                message_limit = st.slider(
                    "Context Window (Last N messages)",
                    2, 20, 6, 2
                )
            else:
                message_limit = 0

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🧹 Clear Chat"):
                    st.session_state.messages = []
                    st.toast("Chat cleared", icon="🗑️")
                    st.rerun()

            with col2:
                if st.button("🚪 Logout"):
                    st.session_state.clear()
                    st.rerun()

    # Update provider/model in session
    if provider != st.session_state.provider or model != st.session_state.model:
        st.session_state.provider = provider
        st.session_state.model = model
        st.toast(f"Switched to {provider} - {model}", icon="⚡")

    # =============== CHAT DISPLAY ===============
    
    display_messages = (
       st.session_state.messages[-message_limit:]
       if show_history else st.session_state.messages
    )

    for msg in display_messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
               st.markdown(f"**You:** {msg['content']}")
        else:
            with st.chat_message("assistant"):
               st.markdown(f"🤖 {msg['content']}")

    # =============== USER INPUT ===============
    user_input = st.chat_input("Ask about Sunbeam Institute...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(f"**You:** {user_input}")

        with st.chat_message("assistant"):
            with st.spinner(f"Thinking using {st.session_state.provider}..."):
                import re
                question_lower = user_input.lower().strip()
                
                # 1. Contact queries (EXACT match)
                contact_keywords = ['email', 'contact', 'phone', 'number', 'address', 'reach']
                is_contact_query = any(kw in question_lower for kw in contact_keywords)
                # But NOT if asking about course/program contact details
                is_about_program = any(word in question_lower for word in ['course', 'program', 'internship', 'precat'])
                
                if is_contact_query and not is_about_program:
                    similar_docs = st.session_state.rag.vs.find_similar_documents(user_input, 5)
                    context = "\n\n".join([doc["document"] for doc in similar_docs])
                    
                    emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', context)))
                    phones = list(set(re.findall(r'[\+\d][\d\-\(\)\s]{8,}[\d]', context)))
                    
                    reply = "📧 Email: " + ", ".join(emails) if emails else ""
                    if phones:
                        reply += ("\n" if reply else "") + "📞 Phone: " + ", ".join(phones[:2])
                    if not emails and not phones:
                        reply = "Contact info not found. Visit: https://www.sunbeaminfo.in/contact-us"
                
                # 2. Fee queries (SPECIFIC handler)
                elif any(kw in question_lower for kw in ['fee', 'fees', 'cost', 'price', 'charge']) and any(kw in question_lower for kw in ['internship', 'course', 'program', 'precat', 'mern', 'genai', 'java', 'python']):
                    # Get more documents for fee queries
                    similar_docs = st.session_state.rag.vs.find_similar_documents(user_input, 15)
                    context = "\n\n".join([doc["document"] for doc in similar_docs])
                    
                    # Enhanced prompt specifically for fees
                    prompt = f"""You are a helpful assistant for Sunbeam Institute. Answer ONLY about fees.

Question: {user_input}

Context from Sunbeam's database:
{context}

CRITICAL INSTRUCTIONS:
1. Search the context for "Fees (Rs.)" or fee amounts
2. Look for patterns like "4000/-/-" or "25000" or "Rs. 15000"
3. If you find ANY fee amount in the context, state it clearly
4. Format: "The fees for [course/program] is ₹[amount]"
5. If fees vary by duration/batch, mention that
6. If NO fees found in context, say "I don't have specific fee information for this program. Please contact Sunbeam directly."

Answer with ONLY the fee information:"""
                    
                    reply = call_llm_with_provider(prompt, st.session_state.provider, st.session_state.model)
                
                # 3. List ALL internship programs (VERY SPECIFIC)
                elif question_lower in [
                    'list internship programs',
                    'list all internship programs', 
                    'what are the internship programs',
                    'what internship programs are available',
                    'show all internship programs',
                    'give me internship programs',
                    'all internship programs'
                ]:
                    programs = st.session_state.rag.get_all_internship_programs()
                    if programs:
                        reply = "**Internship programs at Sunbeam:**\n\n"
                        for i, p in enumerate(programs, 1):
                            reply += f"{i}. **{p['technology']}** - {p['location']}\n"
                        reply += f"\n📚 Total: {len(programs)} programs available"
                    else:
                        reply = "No internship programs found."
                
                # 4. List ALL modular courses (VERY SPECIFIC)
                elif question_lower in [
                    'list all courses',
                    'list courses',
                    'what are the courses',
                    'what courses are available',
                    'show all courses',
                    'give me the list of all the courses',
                    'all courses',
                    'list all modular courses',
                    'what are the modular courses',
                    'give me the list of all the courses at sunbeam'
                ]:
                    all_docs = st.session_state.rag.vs.get_all_documents()
                    courses = []
                    seen = set()
                    
                    for doc in all_docs:
                        metadata = doc.get('metadata', {})
                        if metadata.get('page') == 'modular_courses' and metadata.get('section_type') == 'course_detail':
                            course_name = metadata.get('course_name', '')
                            if course_name and course_name not in seen and course_name != 'Unknown':
                                seen.add(course_name)
                                duration = metadata.get('duration', 'N/A')
                                courses.append({'name': course_name, 'duration': duration})
                    
                    if courses:
                        reply = "**Modular Courses at Sunbeam:**\n\n"
                        for i, course in enumerate(sorted(courses, key=lambda x: x['name']), 1):
                            reply += f"{i}. **{course['name']}** - Duration: {course['duration']}\n"
                        reply += f"\n📚 Total: {len(courses)} courses available"
                    else:
                        reply = "I couldn't find the complete course list. Please visit https://www.sunbeaminfo.in/modular-courses for details."
                
                # 5. Everything else - Use RAG + LLM (SMART ANSWERS)
                else:
                    # Determine how many documents to retrieve
                    if any(kw in question_lower for kw in ['all', 'every', 'list']):
                        num_docs = 10
                    else:
                        num_docs = 6
                    
                    similar_docs = st.session_state.rag.vs.find_similar_documents(user_input, num_docs)
                    context = "\n\n".join([doc["document"] for doc in similar_docs])
                    
                    prompt = f"""You are a helpful assistant for Sunbeam Institute.

Question: {user_input}

Context from Sunbeam's database:
{context}

Instructions:
- For greetings or casual chat, respond naturally and friendly
- For questions about Sunbeam courses/programs/fees/schedules, use the context to give accurate, specific answers
- Extract exact details like fees, duration, schedule, dates from the context
- Search carefully for "Fees (Rs.)", "Duration", "Start Date", "Time" in the context
- If asking about a specific course/program, give details about THAT course only
- Be conversational and helpful
- Keep answers to 2-4 sentences unless listing multiple items
- If information is not in context, say you don't have that specific information

Answer:"""
                    
                    # Call the selected LLM provider
                    reply = call_llm_with_provider(prompt, st.session_state.provider, st.session_state.model)
                
                st.markdown(f"🤖 {reply}")

        st.session_state.messages.append({"role": "assistant", "content": reply})