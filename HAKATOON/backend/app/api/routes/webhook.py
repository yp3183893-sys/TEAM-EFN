import re
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.message import Message
from app.models.product import Product
from app.schemas.webhook import WebhookMessageIn, WebhookMessageOut
from app.services.crm import crm_service
from app.services.lead_scoring import lead_scorer
from app.services.llm import intent_extractor
from app.services.rag import rag_store


router = APIRouter(prefix="", tags=["webhook"])


@router.post("/webhook", response_model=WebhookMessageOut)
def webhook(payload: WebhookMessageIn, db: Session = Depends(get_db)) -> WebhookMessageOut:
    customer = crm_service.get_or_create_customer(db, phone=payload.sender_phone, name=payload.sender_name)
    prospect = crm_service.get_or_create_prospect(db, customer_id=customer.id)

    hectares = _extract_hectares(payload.text)
    if hectares is not None and hectares >= 0:
        customer.hectares = float(hectares)
        db.add(customer)
        db.commit()
        db.refresh(customer)

    intent = intent_extractor.extract(payload.text)
    if intent.intent in {"create_prospect"}:
        prospect = crm_service.update_prospect_status(db, customer_id=customer.id, status=intent.target_status or "new", last_intent=intent.intent)
    elif intent.intent in {"update_prospect_status", "request_quote"} and intent.target_status:
        prospect = crm_service.update_prospect_status(db, customer_id=customer.id, status=intent.target_status, last_intent=intent.intent)
    else:
        prospect.last_intent = intent.intent
        prospect.updated_at = datetime.utcnow()
        db.add(prospect)
        db.commit()
        db.refresh(prospect)

    lead_score = lead_scorer.predict_probability(customer)
    prospect.lead_score = lead_score
    db.add(prospect)
    db.commit()
    db.refresh(prospect)

    if intent.intent == "product_tech_question":
        reply, _ = rag_store.answer(payload.text)
    elif intent.intent == "request_quote":
        reply = _build_quick_quote(db, payload.text)
    else:
        reply = _default_reply(customer_name=customer.name, lead_score=lead_score)

    msg = Message(
        customer_id=customer.id,
        channel=payload.channel,
        text=payload.text,
        intent=intent.intent,
        response=reply,
    )
    db.add(msg)
    db.commit()

    return WebhookMessageOut(reply=reply, intent=intent.intent, prospect_status=prospect.status, lead_score=lead_score)


def _extract_hectares(text: str) -> float | None:
    lower = (text or "").lower()
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ha|hectareas|hectáreas)\b", lower)
    if not m:
        return None
    raw = m.group(1).replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def _build_quick_quote(db: Session, text: str) -> str:
    lower = (text or "").lower()
    if "tractor" in lower:
        products = list(db.scalars(select(Product).where(Product.category == "tractor").limit(3)).all())
    elif "fertiliz" in lower or "npk" in lower:
        products = list(db.scalars(select(Product).where(Product.category == "fertilizante").limit(3)).all())
    else:
        products = list(db.scalars(select(Product).limit(3)).all())

    if not products:
        return "No tengo productos cargados para cotizar todavía. Primero seed-ea el catálogo y vuelve a intentar."

    lines = ["Cotización rápida (referencial):"]
    for p in products:
        lines.append(f"- {p.name} (SKU {p.sku}): ${p.price:,.2f}")
    lines.append("Si me confirmas cantidad y ubicación, preparo una cotización formal.")
    return "\n".join(lines)


def _default_reply(customer_name: str, lead_score: float) -> str:
    score_txt = f"{lead_score * 100:.0f}%"
    return (
        f"Gracias, {customer_name}. Para ayudarte más rápido:\n"
        "1) ¿Cuántas hectáreas trabajas? (ej: 120 ha)\n"
        "2) ¿Qué te interesa: tractores o fertilizantes?\n"
        f"Lead score actual: {score_txt}"
    )
