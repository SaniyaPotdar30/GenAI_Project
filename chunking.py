from langchain_core.documents import Document
import json
import re

def simple_chunk_text(text, chunk_size=800, overlap=100):
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def create_doc(content, page, type, url, source, **extra):
    return Document(
        page_content=content,
        metadata={"page": page, "section_type": type, "url": url, "source": source, **extra}
    )

def chunk_sections(sections, page, url, source):
    docs = []
    for s in sections:
        title, content = s.get('title', ''), s.get('content', '').strip()
        if not content:
            continue
        chunks = chunk_text_if_large(title, content)
        for i, chunk in enumerate(chunks):
            extra = {"chunk_index": i, "total_chunks": len(chunks)} if len(chunks) > 1 else {}
            docs.append(create_doc(f"{title}\n\n{chunk}", page, "accordion", url, source, section_title=title, **extra))
    return docs

def chunk_text_if_large(title, content, max_size=1000):
    return [content] if len(f"{title}\n\n{content}") <= max_size else simple_chunk_text(content)

def chunk_about_us_data(data):
    docs = []
    url = data.get('url', 'https://www.sunbeaminfo.in/about-us')
    if main := data.get('main_description', '').strip():
        docs.append(create_doc(f"About Sunbeam Institute\n\n{main}", "about-us", "main_description", url, "sunbeam_about_us"))
    docs.extend(chunk_sections(data.get('accordion_sections', []), "about-us", url, "sunbeam_about_us"))
    return docs

def chunk_internship_data(data):
    docs = []
    url = "https://sunbeaminfo.in/internship"
    if main := data.get('main_description', '').strip():
        docs.append(create_doc(f"About Sunbeam Internship\n\n{main}", "internship", "main_description", url, "sunbeam_internship"))
    docs.extend(chunk_sections(data.get('accordion_sections', []), "internship", url, "sunbeam_internship"))
    
    for p in data.get('programs', []):
        text = f"Internship Program\n\nTechnology: {p.get('Technology', 'N/A')}\nAim: {p.get('Aim', 'N/A')}\nPrerequisite: {p.get('Prerequisite', 'N/A')}\nLearning: {p.get('Learning', 'N/A')}\nLocation: {p.get('Location', 'N/A')}"
        docs.append(create_doc(text, "internship", "program", url, "sunbeam_internship", technology=p.get('Technology', 'N/A'), location=p.get('Location', 'N/A')))
    
    if batches := data.get('batches', []):
        text = "Internship Batches Schedule\n\n" + "\n\n".join([f"Batch: {b.get('Batch', 'N/A')}\nDuration: {b.get('Batch Duration', 'N/A')}\nStart Date: {b.get('Start Date', 'N/A')}\nEnd Date: {b.get('End Date', 'N/A')}\nTime: {b.get('Time', 'N/A')}\nFees: {b.get('Fees (Rs.)', 'N/A')}" for b in batches])
        docs.append(create_doc(text, "internship", "batch_schedule", url, "sunbeam_internship", total_batches=len(batches)))
    return docs

def chunk_precat_data(data):
    return chunk_sections(data.get('accordion_sections', []), "pre-cat", "https://www.sunbeaminfo.in/pre-cat", "sunbeam_precat")

def chunk_modular_courses_list(data):
    docs = []
    url = "https://www.sunbeaminfo.in/modular-courses-home"
    courses = data if isinstance(data, list) else data.get('courses', [])
    if not courses:
        return docs
    
    overview = "Sunbeam Modular Courses\n\n" + "\n".join([f"• {c.get('course_name', 'N/A')} - Duration: {c.get('duration', 'N/A')}" for c in courses])
    docs.append(create_doc(overview, "modular_courses", "courses_overview", url, "sunbeam_modular_courses", total_courses=len(courses)))
    
    for c in courses:
        text = f"Course: {c.get('course_name', 'Unknown')}\nDuration: {c.get('duration', 'N/A')}"
        if link := c.get('link', ''):
            if link != 'N/A':
                text += f"\nMore Information: {link}"
        docs.append(create_doc(text, "modular_courses", "course_detail", link if link != 'N/A' else url, "sunbeam_modular_courses", course_name=c.get('course_name', 'Unknown'), duration=c.get('duration', 'N/A')))
    return docs

def chunk_mcq_course_data(data):
    docs = []
    name = data.get('course_name', 'Mastering MCQs')
    url = data.get('url', 'https://www.sunbeaminfo.in/modular-courses.php?mdid=57')
    
    if info := data.get('basic_info', {}):
        text = f"Course: {name}\n\n" + "\n".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in info.items() if k != 'course_name'])
        docs.append(create_doc(text, "modular_courses", "course_basic_info", url, "sunbeam_mcq_course", course_name=name))
    
    for s in data.get('sections', []):
        if not (content := s.get('content', '').strip()):
            continue
        title = s.get('title', '')
        chunks = chunk_text_if_large(f"{name} - {title}", content)
        for i, chunk in enumerate(chunks):
            extra = {"chunk_index": i, "total_chunks": len(chunks)} if len(chunks) > 1 else {}
            docs.append(create_doc(f"{name} - {title}\n\n{chunk}", "modular_courses", "course_section", url, "sunbeam_mcq_course", course_name=name, section_title=title, **extra))
    return docs

def chunk_contact_data(data):
    docs = []
    url = data.get('url', 'https://www.sunbeaminfo.in/contact-us')
    if text := data.get('full_text', ''):
        docs.append(create_doc(f"Contact Information - Sunbeam Institute\n\n{text}", "contact", "main_content", url, "sunbeam_contact"))
    if emails := data.get('emails', []):
        docs.append(create_doc("Sunbeam Institute Email Addresses:\n\n" + "\n".join(emails), "contact", "emails", url, "sunbeam_contact"))
    if phones := data.get('phones', []):
        docs.append(create_doc("Sunbeam Institute Phone Numbers:\n\n" + "\n".join(phones), "contact", "phones", url, "sunbeam_contact"))
    return docs

def chunk_all_scraped_data(file_paths):
    all_docs = []
    chunkers = {'about_us': chunk_about_us_data, 'internship': chunk_internship_data, 'precat': chunk_precat_data, 'modular_courses': chunk_modular_courses_list, 'mcq_course': chunk_mcq_course_data, 'contact': chunk_contact_data}
    
    for page_type, file_path in file_paths.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if chunker := chunkers.get(page_type):
                docs = chunker(data)
                all_docs.extend(docs)
                print(f"✓ {page_type}: {len(docs)} chunks")
        except FileNotFoundError:
            print(f"⚠ {file_path} not found")
        except Exception as e:
            print(f"❌ {page_type}: {e}")
    
    print(f"\n✓ Total: {len(all_docs)} chunks\n")
    return all_docs

if __name__ == "__main__":
    file_paths = {'about_us': 'about_us_data.json', 'internship': 'internship_complete_data.json', 'precat': 'precat_data.json', 'modular_courses': 'modular_courses_data.json', 'mcq_course': 'mastering_mcqs_data.json', 'contact': 'contact_data.json'}
    docs = chunk_all_scraped_data(file_paths)
    print(docs)