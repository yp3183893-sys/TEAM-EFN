from pydantic import BaseModel, Field


class WebhookMessageIn(BaseModel):
    channel: str = Field(default="whatsapp", examples=["whatsapp", "telegram", "webhook"])
    sender_phone: str = Field(examples=["+51999999999"])
    sender_name: str | None = None
    text: str


class WebhookMessageOut(BaseModel):
    reply: str
    intent: str
    prospect_status: str
    lead_score: float
