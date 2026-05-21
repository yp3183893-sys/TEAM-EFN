import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(".env")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
