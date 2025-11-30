import os
import json
import re
import time
import random
import uuid
import requests
import fitz  # PyMuPDF
from dotenv import load_dotenv
from hashlib import sha256

# Optional: official Google client (used when available)
try:
    import google.generativeai as genai
except Exception:
    genai = None

# --- 1. Setup ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash") # Updated default to Flash for speed
AI_OFFLINE = os.getenv("AI_OFFLINE", "false").lower() in ("1", "true", "yes")

if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY is not set. Set it in your .env for real AI calls.")

# configure the official client if present
if genai and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print("⚠️ genai.configure failed:", e)

# --- Helpers to inspect available models (debugging) ---
def list_available_models(api_key=None, use_v1beta=True):
    version = "v1beta" if use_v1beta else "v1"
    url = f"https://generativelanguage.googleapis.com/{version}/models"
    if api_key:
        url += f"?key={api_key}"
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        models = [m.get("name") for m in data.get("models", [])] if isinstance(data, dict) else data
        return models
    except Exception as e:
        print("⚠️ Could not list models:", e)
        return None

# --- Lazy model getter with helpful diagnostics ---
_MODEL_OBJ = None

def get_model():
    global _MODEL_OBJ
    if AI_OFFLINE:
        raise RuntimeError("AI_OFFLINE is enabled")
    if _MODEL_OBJ is not None:
        return _MODEL_OBJ
    if not genai:
        raise RuntimeError("google.generativeai client not installed or importable.")
    try:
        print(f"Initializing model: {GEMINI_MODEL}")
        _MODEL_OBJ = genai.GenerativeModel(GEMINI_MODEL)
        return _MODEL_OBJ
    except Exception as e:
        print("⚠️ Model instantiation failed:", e)
        models = list_available_models(GEMINI_API_KEY)
        if models:
            print("Available models (sample):", models[:40])
        else:
            print("No model list available (couldn't reach API or API key missing).")
        raise

# --- Utility functions ---
def extract_text_from_pdf(pdf_content: bytes) -> str:
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

def repair_json(json_str: str) -> str:
    if not json_str:
        return ""
    json_str = re.sub(r"^```(?:json)?\s*", "", json_str.strip())
    json_str = re.sub(r"\s*```$", "", json_str.strip())
    replacements = {
        r"\Omega": r"\\Omega",
        r"\times": r"\\times",
        r"\le": r"\\le",
        r"\ge": r"\\ge",
        r"\frac": r"\\frac",
    }
    for old, new in replacements.items():
        if old in json_str and new not in json_str:
            json_str = json_str.replace(old, new)
    json_str = json_str.replace('\\\\', '@@DOUBLE_BACKSLASH@@')
    json_str = json_str.replace('\\"', '@@QUOTE@@')
    json_str = json_str.replace('\\n', '@@NEWLINE@@')
    json_str = json_str.replace('\\t', '@@TAB@@')
    json_str = json_str.replace('\\/', '@@SLASH@@')
    json_str = json_str.replace('\\b', '@@BACKSPACE@@')
    json_str = json_str.replace('\\f', '@@FORMFEED@@')
    json_str = json_str.replace('\\r', '@@RETURN@@')
    json_str = json_str.replace('\\', '\\\\')
    json_str = json_str.replace('@@DOUBLE_BACKSLASH@@', '\\\\')
    json_str = json_str.replace('@@QUOTE@@', '\\"')
    json_str = json_str.replace('@@NEWLINE@@', '\\n')
    json_str = json_str.replace('@@TAB@@', '\\t')
    json_str = json_str.replace('@@SLASH@@', '\\/')
    json_str = json_str.replace('@@BACKSPACE@@', '\\b')
    json_str = json_str.replace('@@FORMFEED@@', '\\f')
    json_str = json_str.replace('@@RETURN@@', '\\r')
    return json_str

def retry_with_backoff(func, *args, retries=3, delay=5):
    for i in range(retries):
        try:
            return func(*args)
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg:
                print(f"⚠️ Rate limit hit. Waiting {delay}s before retry {i+1}/{retries}...")
                time.sleep(delay)
                delay *= 2
                continue
            if "500" in error_msg or "internal" in error_msg:
                print("⚠️ AI Internal Error. Retrying...")
                time.sleep(2)
                continue
            raise
    return None

def text_hash(s: str) -> str:
    return sha256(s.strip().lower().encode()).hexdigest()

# --- Core AI functions ---
def generate_syllabus(text: str):
    print("--- 1. THE ARCHITECT: Analyzing PDF Structure ---")
    if not text:
        print("⚠️ No text provided to generate_syllabus.")
        return []
    if AI_OFFLINE:
        print("⚠️ AI_OFFLINE enabled — returning mock syllabus")
        return [
            {"topic": "Mock: Introduction", "complexity": 1, "context": "Offline fallback"},
            {"topic": "Mock: Key Concepts", "complexity": 2, "context": "Offline fallback"}
        ]
    prompt = f"""
Analyze the following academic text. Break it down into distinct, key sub-topics.
For each topic, assign a 'complexity' (1-5) and provide a short context summary.

Return STRICTLY as a JSON list of objects:
[{{"topic":"Topic Name","complexity":3,"context":"Brief summary"}}]

Text Context (truncated to 20000 chars):
{text[:20000]}
"""
    try:
        def _call():
            model = get_model()
            return model.generate_content(prompt)
        response = retry_with_backoff(_call)
        if not response:
            print("❌ No response from model after retries.")
            return []
        text_out = ""
        try:
            if hasattr(response, "text") and response.text:
                text_out = response.text
            elif hasattr(response, "generations"):
                gens = getattr(response, "generations")
                if isinstance(gens, (list, tuple)) and len(gens) > 0:
                    text_out = getattr(gens[0], "text", "") or str(gens[0])
            else:
                text_out = str(response)
        except Exception:
            text_out = str(response)
        if not text_out.strip():
            print("❌ AI returned empty text.")
            return []
        cleaned = repair_json(text_out)
        try:
            syllabus = json.loads(cleaned)
        except Exception as e:
            print("⚠️ JSON parsing failed after repair:", e)
            m = re.search(r"(\[.*\])", cleaned, flags=re.S)
            if m:
                try:
                    syllabus = json.loads(m.group(1))
                except Exception as e2:
                    print("⚠️ Fallback parsing failed:", e2)
                    return []
            else:
                return []
        print(f"✅ Successfully extracted {len(syllabus)} topics.")
        return syllabus[:8]
    except Exception as e:
        msg = str(e)
        print(f"❌ Error in generate_syllabus: {msg}")
        if "not found" in msg.lower() or "is not found" in msg.lower() or "404" in msg:
            print("⚠️ Model not available or doesn't support this method. Returning mock syllabus for development.")
            models = list_available_models(GEMINI_API_KEY)
            if models:
                print("Available models (sample):", models[:30])
            return [
                {"topic": "Fallback: Introduction", "complexity": 1, "context": "Model unavailable, dev fallback."},
                {"topic": "Fallback: Topics Overview", "complexity": 2, "context": "Model unavailable, dev fallback."}
            ]
        return []

def generate_content_for_topic(topic_data: dict):
    topic = topic_data.get('topic', 'Unknown Topic')
    complexity = int(topic_data.get('complexity', 2))
    context = topic_data.get('context', "")
    print(f"--- 2. THE MINER: Digging into '{topic}' ---")
    num_cards = min(max(3, complexity * 2), 12)
    prompt = f"""
You are an expert tutor.
Topic: {topic}
Context: {context}

Generate exactly:
1. {num_cards} Flashcards (question, answer).
2. 1 Multiple-Choice Quiz Question (question, 4 options, correct_answer).
3. 1 Application Scenario (scenario, ideal_response).

Return STRICTLY as a JSON object with keys: "flashcards", "quiz", "arena".
"""
    def _call_ai():
        model = get_model()
        return model.generate_content(prompt)
    try:
        response = retry_with_backoff(_call_ai)
        if not response:
            print(f"❌ Skipped topic '{topic}' due to empty AI response.")
            return None
        response_text = ""
        try:
            if hasattr(response, "text") and response.text:
                response_text = response.text
            elif hasattr(response, "generations"):
                gens = getattr(response, "generations")
                if isinstance(gens, (list, tuple)) and len(gens) > 0:
                    response_text = getattr(gens[0], "text", "") or str(gens[0])
            else:
                response_text = str(response)
        except Exception:
            response_text = str(response)
        cleaned = repair_json(response_text)
        try:
            data = json.loads(cleaned)
        except Exception as e:
            print("⚠️ Failed to parse topic content JSON:", e)
            m = re.search(r"(\{.*\})", cleaned, flags=re.S)
            if m:
                try:
                    data = json.loads(m.group(1))
                except Exception as e2:
                    print("⚠️ Fallback parse failed:", e2)
                    return None
            else:
                return None
        if isinstance(data, dict) and 'quiz' in data and data['quiz']:
            quiz = data['quiz']
            options = quiz.get('options')
            if isinstance(options, dict):
                quiz['options'] = list(options.values())
        for item in data.get('flashcards', []):
            item.setdefault('tag', topic)
        if 'quiz' in data and data['quiz']:
            data['quiz'].setdefault('tag', topic)
        if 'arena' in data and data['arena']:
            data['arena'].setdefault('related_topic_tag', topic)
        return data
    except Exception as e:
        print(f"❌ Error generating content for {topic}: {e}")
        return None

# --- NEW: generate_arena_questions_for_set (session generation) ---
def generate_arena_questions_for_set(study_set, generation_kwargs: dict):
    """
    Generate `num_questions` application scenarios for the study_set.
    Returns list of dicts: {"scenario":..., "ideal_response":..., "meta":{...}}
    """
    # Defensive defaults
    num_questions = int(generation_kwargs.get("num_questions", 1))
    temperature = float(generation_kwargs.get("temperature", 0.8))
    top_p = float(generation_kwargs.get("top_p", 0.95))
    seed = generation_kwargs.get("random_seed", str(uuid.uuid4()))

    # Determine topic(s) to focus on. If study_set has related topics, prefer them.
    topics = []
    try:
        if hasattr(study_set, "title") and study_set.title:
            topics.append(study_set.title)
        # if your StudySet stores saved topics/sections, add them:
        if hasattr(study_set, "topics"):
            for t in getattr(study_set, "topics") or []:
                if isinstance(t, dict):
                    topics.append(t.get("topic") or t.get("title"))
                else:
                    topics.append(str(t))
    except Exception:
        topics = [getattr(study_set, "title", "General")]

    if not topics:
        topics = ["General"]

    out = []
    for i in range(num_questions):
        variant_label = random.choice(["A", "B", "C", "D", "E", "F"])
        topic_focus = topics[i % len(topics)]
        prompt = f"""
You are an expert evaluator creating an application scenario for learners.
Session seed: {seed}
Variant: {variant_label}
Study set title: {getattr(study_set, 'title', 'Untitled')}
Topic focus: {topic_focus}

Create 1 application scenario and an ideal model response. The scenario should be moderately challenging and require applying knowledge from the topic. Keep the JSON compact.

Return EXACTLY one JSON object like:
{{"scenario":"...","ideal_response":"..."}}
"""
        # Call model with attempt to use temperature/top_p if supported
        try:
            model = get_model()
            # Many SDKs accept keyword params for sampling; if not, fallback
            try:
                response = model.generate_content(prompt, generation_config=genai.types.GenerationConfig(temperature=temperature, top_p=top_p))
            except TypeError:
                response = model.generate_content(prompt)
        except Exception as e:
            print("⚠️ generate_arena_questions_for_set model call failed:", e)
            # fallback: try a simpler call or return placeholder
            try:
                if genai:
                    model = get_model()
                    response = model.generate_content(prompt)
                else:
                    response = None
            except Exception as e2:
                print("⚠️ Secondary attempt failed:", e2)
                response = None

        if not response:
            # fallback placeholder
            out.append({
                "scenario": f"Placeholder scenario (variant {variant_label}) on {topic_focus}",
                "ideal_response": "Model unavailable — placeholder ideal response.",
                "meta": {"variant": variant_label, "seed": seed}
            })
            continue

        # Extract response text defensively
        text_out = ""
        try:
            if hasattr(response, "text") and response.text:
                text_out = response.text
            elif hasattr(response, "generations"):
                gens = getattr(response, "generations")
                if isinstance(gens, (list, tuple)) and len(gens) > 0:
                    text_out = getattr(gens[0], "text", "") or str(gens[0])
            else:
                text_out = str(response)
        except Exception:
            text_out = str(response)

        cleaned = repair_json(text_out)
        data = None
        try:
            data = json.loads(cleaned)
        except Exception:
            m = re.search(r"(\{.*\})", cleaned, flags=re.S)
            if m:
                try:
                    data = json.loads(m.group(1))
                except Exception:
                    data = None
        if not data:
            # fallback to using first 1000 chars of output as scenario
            out.append({
                "scenario": text_out[:1000],
                "ideal_response": "",
                "meta": {"variant": variant_label, "seed": seed}
            })
            continue

        scenario = data.get("scenario") or data.get("prompt") or data.get("problem") or ""
        ideal = data.get("ideal_response") or data.get("ideal") or data.get("answer") or ""
        out.append({"scenario": scenario, "ideal_response": ideal, "meta": {"variant": variant_label, "seed": seed, "topic": topic_focus}})

    return out

# --- NEW FEATURES: QUIZ REGENERATION & ARENA GRADING ---

def generate_quiz_from_context(context_text: str, num_questions: int = 5):
    """
    Generates dynamic MCQ quiz questions based on provided text (e.g. Flashcards).
    """
    print(f"--- 3. THE EXAMINER: Creating {num_questions} new questions ---")
    prompt = f"""
    You are a strict exam setter.
    Create {num_questions} multiple-choice questions based ONLY on the following context.
    
    CONTEXT:
    {context_text[:15000]}
    
    OUTPUT FORMAT (JSON ARRAY ONLY):
    [
      {{
        "question": "The question text?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option B"
      }}
    ]
    """
    
    def _call():
        model = get_model()
        return model.generate_content(prompt)

    try:
        response = retry_with_backoff(_call)
        if not response:
            return []
        
        text_out = response.text if hasattr(response, 'text') else str(response)
        cleaned = repair_json(text_out)
        return json.loads(cleaned)
    except Exception as e:
        print(f"Quiz Gen Error: {e}")
        return []

def grade_arena_submission(scenario: str, user_response: str):
    """
    Grades the user's open-ended response against the scenario.
    Returns JSON: { "score": 85, "feedback": "Good job, but you missed..." }
    """
    print("--- 4. THE GRADER: Assessing Arena Submission ---")
    prompt = f"""
    You are an expert professor. Grade this student's answer.
    
    SCENARIO: {scenario}
    STUDENT ANSWER: {user_response}
    
    Task:
    1. Assign a score from 0 to 100 based on accuracy, completeness, and reasoning.
    2. Provide 1 sentence of constructive feedback.
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "score": 85,
        "feedback": "Your logic was sound, but you forgot to mention X."
    }}
    """
    
    def _call():
        model = get_model()
        return model.generate_content(prompt)

    try:
        response = retry_with_backoff(_call)
        if not response:
            return {"score": 0, "feedback": "AI Grading unavailable."}
            
        text_out = response.text if hasattr(response, 'text') else str(response)
        cleaned = repair_json(text_out)
        return json.loads(cleaned)
    except Exception as e:
        print(f"Grading Error: {e}")
        return {"score": 0, "feedback": "AI Grading failed. Please try again."}