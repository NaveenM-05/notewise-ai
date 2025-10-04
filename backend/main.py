from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# --- 1. Setup and Configuration ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro-latest')
app = FastAPI(title="NoteWise AI")

# --- 2. CORS Middleware ---
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. The API Endpoint (File Upload Only) ---
@app.post("/api/generate")
async def generate(file: UploadFile = File(...)): # The '...' makes the file a required field
    
    extracted_text = ""

    # Part A: Extract text from the PDF file
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
    
    pdf_content = await file.read()
    try:
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                extracted_text += page.get_text()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="The PDF appears to be empty or contains no text.")

    # Part B: Call the Gemini API
    try:
        prompt = f"""
        Based on the following text, generate a list of 5 to 7 question-and-answer flashcards.
        Return the response as a valid JSON array of objects, where each object has a "question" key and an "answer" key.
        Do not include any other text, explanations, or markdown formatting like ```json outside of the JSON array itself.

        Text:
        ---
        {extracted_text}
        ---
        """
        
        response = model.generate_content(prompt)
        raw_text_response = response.text
        
        start = raw_text_response.find('[')
        end = raw_text_response.rfind(']') + 1
        
        if start == -1 or end == 0:
            raise ValueError("Could not find a valid JSON array in the AI's response.")
            
        json_str = raw_text_response[start:end]
        flashcards_list = json.loads(json_str)
        
        return {"flashcards": flashcards_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred with the AI model: {e}")
