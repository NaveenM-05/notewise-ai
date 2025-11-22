import google.generativeai as genai
import json
import fitz # PyMuPDF
import os
from dotenv import load_dotenv
import re 
import time

# --- 1. Setup ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ CRITICAL WARNING: GEMINI_API_KEY is missing from .env")

genai.configure(api_key=GEMINI_API_KEY)

# MODIFIED: Use 'models/gemini-flash-latest'
# This model allows ~15 requests per minute (much better than Pro's 2 RPM)
model = genai.GenerativeModel('models/gemini-flash-latest') 

# --- 2. Helper Functions ---

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extracts raw text from a PDF file in memory."""
    try:
        text = ""
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        print(f"✅ Extracted {len(text)} characters from PDF.")
        return text
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return ""

def clean_json_string(text: str) -> str:
    """Cleans AI response to ensure it is valid JSON."""
    text = re.sub(r"^```json\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return text

def retry_with_backoff(func, *args, retries=3, delay=5):
    """
    Helper to retry AI calls if they hit a rate limit (429).
    """
    for i in range(retries):
        try:
            return func(*args)
        except Exception as e:
            if "429" in str(e):
                print(f"⚠️ Rate limit hit. Waiting {delay}s before retry {i+1}/{retries}...")
                time.sleep(delay)
                delay *= 2 
            else:
                raise e
    return None

# --- 3. Core AI Functions ---

def generate_syllabus(text: str):
    """Phase 1: The Architect."""
    print("--- 1. THE ARCHITECT: Analyzing PDF Structure ---")
    
    prompt = f"""
    Analyze the following academic text. Break it down into distinct, key sub-topics.
    For each topic, assign a 'complexity_score' (1 to 5).
    
    Return the result STRICTLY as a JSON list of objects. 
    Format: [{{"topic": "Topic Name", "complexity": 3, "context": "Brief summary"}}]
    
    Text Context (First 15000 chars):
    {text[:15000]}
    """
    
    try:
        # Use the model directly here since it's just one call
        response = model.generate_content(prompt)
        
        if not response.text:
            print("❌ AI Response blocked or empty.")
            return []
            
        cleaned_text = clean_json_string(response.text)
        syllabus = json.loads(cleaned_text)
        print(f"✅ Successfully extracted {len(syllabus)} topics.")
        
        # Limit to 5 topics for a good demo balance
        return syllabus[:5] 
        
    except Exception as e:
        print(f"❌ Error in generate_syllabus: {e}")
        return []

def generate_content_for_topic(topic_data: dict):
    """
    Phase 2: The Miner.
    Generates specific flashcards and questions for a single topic.
    """
    topic = topic_data['topic']
    complexity = topic_data['complexity']
    context = topic_data['context']
    
    print(f"--- 2. THE MINER: Digging into '{topic}' ---")
    
    time.sleep(4) 
    
    num_cards = min(max(2, complexity * 2), 10)
    
    prompt = f"""
    You are an educational AI.
    Topic: {topic}
    Context: {context}
    
    Generate exactly:
    1. {num_cards} Flashcards (question, answer).
    2. 1 Multiple-Choice Quiz Question (question, 4 options, correct_answer).
    3. 1 Application Scenario (scenario, ideal_response).
    
    Return STRICTLY as a JSON object with keys: "flashcards", "quiz", "arena".
    IMPORTANT: The "options" for the quiz must be a simple LIST of strings, NOT a dictionary with keys "A", "B", etc.
    Example Options: ["Paris", "London", "Berlin", "Madrid"]
    """
    
    def _call_ai():
        response = model.generate_content(prompt)
        cleaned_text = clean_json_string(response.text)
        return json.loads(cleaned_text)

    try:
        data = retry_with_backoff(_call_ai)
        
        if not data:
            print(f"❌ Skipped topic '{topic}' due to errors.")
            return None

        # --- CRITICAL FIX: SANITIZE QUIZ OPTIONS ---
        if 'quiz' in data and data['quiz']:
            quiz = data['quiz']
            options = quiz.get('options')
            
            # If AI returns a dict like {"A": "Val1", "B": "Val2"}, convert to list
            if isinstance(options, dict):
                print(f"⚠️ Converting quiz dictionary options to list for topic: {topic}")
                quiz['options'] = list(options.values())
            
            # If correct_answer is a Key like "A", try to fix it (optional but helpful)
            # For now, we just ensure options is a list.
        # -------------------------------------------

        # Tag the data
        for item in data.get('flashcards', []): 
            item['tag'] = topic
            
        if 'quiz' in data and data['quiz']: 
            data['quiz']['tag'] = topic
            
        if 'arena' in data and data['arena']: 
            data['arena']['related_topic_tag'] = topic
            
        return data
        
    except Exception as e:
        print(f"❌ Error generating content for {topic}: {e}")
        return None
