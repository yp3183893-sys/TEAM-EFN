from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.webhook import router as webhook_router
from app.db.session import engine
from app.models.base import Base
import app.models
from app.services.lead_scoring import lead_scorer
from app.services.rag import rag_store


def create_app() -> FastAPI:
    api = FastAPI(title="Agro B2B Sales Agent (MVP)", version="0.1.0")

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.include_router(health_router)
    api.include_router(webhook_router)

    @api.on_event("startup")
    def _startup() -> None:
        Base.metadata.create_all(bind=engine)
        lead_scorer.load_or_train()
        rag_store.rebuild_from_db()

    return api


app = create_app()
