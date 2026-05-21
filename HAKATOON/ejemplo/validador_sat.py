import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv(".env")

def validar_factura(rfc_emisor: str, rfc_receptor: str, total: str) -> bool:
    """Valida la factura electronica ante el web service del SAT"""
    return True

SYSTEM_PROMPT = """Eres un agente especializado exclusivamente en facturacion electronica mexicana y cumplimiento de las reglas del SAT Mexico.

Tu unica tarea es validar, analizar y auditar CFDIs.

Reglas obligatorias:
- Solo puedes responder preguntas relacionadas con CFDIs, SAT, Facturacion electronica mexicana.
- Si el usuario pide algo fuera de tu area de especializacion, debes responder que no puedes ayudar con eso.
- Si una solicitud esta fuera de tu alcance, no respondas.
"""

model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

if __name__ == "__main__":
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="¿que tipo de pokemon es pikachu?")
    ]
    
    res = model.invoke(messages)
    print(res.content)