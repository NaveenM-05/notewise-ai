import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("--- Available Generative Models ---")
for m in genai.list_models():
  # Check if the model supports the 'generateContent' method
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
print("---------------------------------")