import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env")

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content("Hola, ¿estás funcionando?")
    print(f"Respuesta: {response.text}")
except Exception as e:
    print(f"Error: {e}")
