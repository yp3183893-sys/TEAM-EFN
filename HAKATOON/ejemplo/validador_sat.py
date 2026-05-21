"""
Crear un primer agente que valide las facturas ante el
SAT.

uv add langchain-google-genai
uv add langchain-openai


1) Hacer el agente solo. SIN CAPACIDADES O TOOLS
2) Agregarle la tool `validar_cfdi_sat` para validar CFDI/SAT
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from tools import validar_cfdi_sat

load_dotenv(".env")

SYSTEM_PROMPT = """
Eres un agente enterprise especializado exclusivamente en facturación electrónica mexicana y cumplimiento fiscal del SAT.

Tu única responsabilidad es validar, analizar y auditar CFDI.

REGLAS OBLIGATORIAS:

- SOLO puedes responder preguntas relacionadas con CFDI, SAT, facturación electrónica, validaciones fiscales y cumplimiento tributario mexicano.
- Si el usuario pide algo fuera de ese dominio, debes rechazar la solicitud.
- Nunca generes código, recetas, traducciones, contenido creativo o programación que no esté directamente relacionada con CFDI/SAT.
- Nunca inventes información faltante.
- Prioriza exactitud normativa y trazabilidad.

Si una solicitud está fuera de alcance responde EXACTAMENTE:

"Solicitud fuera del alcance del agente especializado en CFDI/SAT."
"""

model = init_chat_model(model="google_genai:gemini-1.5-flash-lite", temperature=0)

agent = create_agent(model, tools=[validar_cfdi_sat], system_prompt=SYSTEM_PROMPT)

if __name__ == "__main__":
    res = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """El UUID de mi factura es 9E5386EF-2D41-45EE-A982-17F1F405F273,
                    rfc_emisor=NWM9709244W4,
                    rfc_receptor="EIRL830903450",
                    total="345.300000",
                    uuid="9E5386EF-2D41-45EE-A982-17F1F405F271"
                    """,
                }
            ]
        }
    )

    print(res["messages"][-1].content)