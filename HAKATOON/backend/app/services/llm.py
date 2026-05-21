import json
import re
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class IntentResult:
    intent: str
    target_status: str | None = None


class LLMIntentExtractor:
    def __init__(self) -> None:
        self._client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self._client = None

    def extract(self, text: str) -> IntentResult:
        text_norm = (text or "").strip()
        if self._client is None:
            return self._extract_mock(text_norm)
        try:
            return self._extract_openai(text_norm)
        except Exception:
            return self._extract_mock(text_norm)

    def _extract_mock(self, text: str) -> IntentResult:
        lower = text.lower()
        if re.search(r"\b(cotiz|cotiza|cotización|precio|presupuesto)\b", lower):
            return IntentResult(intent="request_quote", target_status="quoted")
        if re.search(r"\b(ficha|especific|potencia|hp|rendimiento|dosis|npk|compatibilidad)\b", lower):
            return IntentResult(intent="product_tech_question")
        if re.search(r"\b(quiero comprar|compra|cerrar|pedido|orden)\b", lower):
            return IntentResult(intent="update_prospect_status", target_status="qualified")
        if re.search(r"\b(llamar|visita|reunión|agendar|contactar)\b", lower):
            return IntentResult(intent="update_prospect_status", target_status="contacted")
        if re.search(r"\b(soy|me llamo)\b", lower) or re.search(r"\b(nuevo|primera vez)\b", lower):
            return IntentResult(intent="create_prospect", target_status="new")
        return IntentResult(intent="general")

    def _extract_openai(self, text: str) -> IntentResult:
        prompt = {
            "role": "user",
            "content": (
                "Clasifica la intención del mensaje de un cliente B2B agrícola.\n"
                "Devuelve SOLO JSON estricto con campos: intent, target_status.\n"
                "intent en {create_prospect, request_quote, product_tech_question, update_prospect_status, general}.\n"
                "target_status en {new, contacted, qualified, quoted, won, lost} o null.\n"
                f"Mensaje: {text}"
            ),
        }
        resp = self._client.chat.completions.create(
            model=settings.openai_model,
            messages=[prompt],
            temperature=0,
        )
        content = (resp.choices[0].message.content or "").strip()
        data = json.loads(content)
        intent = str(data.get("intent") or "general")
        target_status = data.get("target_status")
        if target_status is not None:
            target_status = str(target_status)
        return IntentResult(intent=intent, target_status=target_status)


intent_extractor = LLMIntentExtractor()
