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
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import fitz  # PyMuPDF
# from typing import Optional, Any # MODIFIED: Added 'Any'
# import os
# import json
# from dotenv import load_dotenv
# import google.generativeai as genai

# # --- 1. Setup and Configuration ---

# # Load environment variables from the .env file
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure the Gemini API client
# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
# genai.configure(api_key=GEMINI_API_KEY)

# # Initialize the generative model
# model = genai.GenerativeModel('gemini-pro-latest')

# # Initialize the FastAPI app
# app = FastAPI(title="NoteWise AI")

# # --- 2. CORS Middleware ---
# # This allows your frontend (running on localhost:5173) to talk to your backend
# origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- 3. The API Endpoint ---

# @app.post("/api/generate")
# # MODIFIED: Changed 'Optional[UploadFile]' to 'Any' to handle empty file fields gracefully
# async def generate(text: Optional[str] = Form(None), file: Any = File(None)):
    
#     extracted_text = ""

#     # Part A: Extract text from either the PDF file or the text form field
#     # MODIFIED: Added 'isinstance' check to ensure 'file' is a real upload
#     if isinstance(file, UploadFile) and file.filename:
#         if file.content_type != "application/pdf":
#             raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        
#         pdf_content = await file.read()
#         try:
#             with fitz.open(stream=pdf_content, filetype="pdf") as doc:
#                 for page in doc:
#                     extracted_text += page.get_text()
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    
#     elif text:
#         extracted_text = text
        
#     else:
#         raise HTTPException(status_code=400, detail="No input provided. Please provide either text or a PDF file.")

#     if not extracted_text.strip():
#         raise HTTPException(status_code=400, detail="Input text is empty.")

#     # Part B: Call the Gemini API with the extracted text
#     try:
#         prompt = f"""
#         Based on the following text, generate a list of 5 to 7 question-and-answer flashcards.
#         Return the response as a valid JSON array of objects, where each object has a "question" key and an "answer" key.
#         Do not include any other text, explanations, or markdown formatting like ```json outside of the JSON array itself.

#         Text:
#         ---
#         {extracted_text}
#         ---
#         """
        
#         # Call the Gemini API
#         response = model.generate_content(prompt)
        
#         # The AI's response is a string that should be a JSON array. We need to parse it.
#         raw_text_response = response.text
        
#         # Clean up the response to find the start '[' and end ']' of the JSON array
#         start = raw_text_response.find('[')
#         end = raw_text_response.rfind(']') + 1
        
#         if start == -1 or end == 0:
#             raise ValueError("Could not find a valid JSON array in the AI's response.")
            
#         json_str = raw_text_response[start:end]
        
#         # Parse the extracted string into a Python list
#         flashcards_list = json.loads(json_str)
        
#         return {"flashcards": flashcards_list}

#     except Exception as e:
#         # Handle potential errors from the API call or JSON parsing
#         raise HTTPException(status_code=500, detail=f"An error occurred with the AI model: {e}")