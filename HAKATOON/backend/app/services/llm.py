import os
import json
from dataclasses import dataclass

try:
    import google.generativeai as genai
except Exception:
    genai = None

# Mantenemos la estructura original para no romper webhook.py
@dataclass(frozen=True)
class IntentResult:
    intent: str
    target_status: str | None = None

class LLMIntentExtractor:
    def __init__(self) -> None:
        self._client_ready = False
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key and genai is not None:
            try:
                # Configuramos Gemini en lugar de OpenAI
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-1.5-flash"))
                self._client_ready = True
            except Exception:
                self._client_ready = False

    def extract(self, text: str) -> IntentResult:
        text_norm = (text or "").strip()
        
        if not self._client_ready:
            return self._extract_mock(text_norm)
            
        # --- EL CEREBRO AGRÍCOLA (AGROCAPITAL & FIRA) ---
        prompt = f"""
        Eres un asistente inteligente especializado exclusivamente en procesos de financiamiento rural, agropecuario y empresarial relacionados con AgroCapital y las condiciones de operación de FIRA.

        Tu función en este proceso es leer el mensaje del cliente, extraer su intención y clasificarlo para el CRM. 

        REGLAS DE NEGOCIO:
        1. SOLO debes procesar temas relacionados con: financiamiento, créditos, FIRA, actividades agropecuarias, capital de trabajo, inversión fija y requisitos.
        2. NO proceses temas personales, política, médicos, ni ajenos al negocio.
        3. Debes validar la prioridad según la actividad, destino del crédito, monto y ubicación.
        Opciones de 'intent' válidas para clasificar:
        - "cotizacion_credito" (Pide simulación de crédito, montos o tasas).
        - "validacion_fira" (Pregunta por requisitos, elegibilidad o reglas de FIRA).
        - "seguimiento" (Envía documentos o pregunta por el estatus de su trámite).
        - "fuera_de_contexto" (Pregunta por cosas que no son financiamiento rural).
        - "fuera_de_contexto" (Pregunta por cosas que no son financiamiento rural).

        Opciones de 'target_status' válidas para el CRM:
        - "Precalificacion" (Es un lead nuevo preguntando si aplica para el crédito).
        - "Lead Calificado" (Ya tiene claro qué quiere financiar, ej. compra de maquinaria o capital de trabajo).
        - "Rechazado/No Aplica" (Es un mensaje fuera de contexto o de un sector no elegible).

        Mensaje del cliente: "{text_norm}"
        
        Devuelve ÚNICAMENTE un JSON válido con esta estructura exacta (sin texto extra ni formato markdown):
        {{"intent": "la_intencion", "target_status": "el_status"}}
        """
        
        try:
            response = self._model.generate_content(prompt)
            # Limpiamos la respuesta por si la IA le pone marcas de código (```json)
            respuesta_limpia = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(respuesta_limpia)
            
            return IntentResult(
                intent=data.get("intent", "otro"),
                target_status=data.get("target_status", "Lead Nuevo")
            )
        except Exception:
            return self._extract_mock(text_norm)
            
    def _extract_mock(self, text: str) -> IntentResult:
        # Lógica de respaldo si la API falla
        text_lower = text.lower()
        if "cotizac" in text_lower or "precio" in text_lower:
            return IntentResult(intent="cotizacion", target_status="Lead Nuevo")
        return IntentResult(intent="otro", target_status="Contactado")

# Instanciamos la clase para que webhook.py pueda importarla (línea clave)
intent_extractor = LLMIntentExtractor()


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(prog="python -m app.services.llm")
    parser.add_argument("text", nargs="?", help="Mensaje del cliente (si no se pasa, se lee de stdin)")
    args = parser.parse_args()

    text = args.text
    if text is None:
        text = sys.stdin.read().strip()

    result = intent_extractor.extract(text)
    print(json.dumps({"intent": result.intent, "target_status": result.target_status}, ensure_ascii=False))


if __name__ == "__main__":
    main()
