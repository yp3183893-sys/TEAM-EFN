from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.product import Product


@dataclass(frozen=True)
class RAGHit:
    product_id: int
    sku: str
    name: str
    score: float
    context: str


class InMemoryRAG:
    def __init__(self) -> None:
        self._vectorizer = None
        self._matrix = None
        self._hits: list[RAGHit] = []

    def rebuild_from_db(self) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        with SessionLocal() as db:
            products = list(db.scalars(select(Product)).all())

        docs: list[str] = []
        meta: list[tuple[int, str, str]] = []
        for p in products:
            doc = f"{p.name}\n{p.category}\n{p.description}\n{p.tech_specs}"
            docs.append(doc)
            meta.append((p.id, p.sku, p.name))

        if not docs:
            self._vectorizer = TfidfVectorizer(stop_words=None)
            self._matrix = self._vectorizer.fit_transform([""])
            self._hits = []
            return

        self._vectorizer = TfidfVectorizer(stop_words=None)
        self._matrix = self._vectorizer.fit_transform(docs)
        self._hits = [RAGHit(product_id=m[0], sku=m[1], name=m[2], score=0.0, context=docs[i]) for i, m in enumerate(meta)]

    def answer(self, question: str, top_k: int | None = None) -> tuple[str, list[RAGHit]]:
        if self._vectorizer is None or self._matrix is None:
            self.rebuild_from_db()

        from sklearn.metrics.pairwise import cosine_similarity

        k = top_k or settings.rag_top_k
        q_vec = self._vectorizer.transform([question])
        sims = cosine_similarity(q_vec, self._matrix)[0]
        ranked = sorted(range(len(sims)), key=lambda i: float(sims[i]), reverse=True)[: max(1, int(k))]

        hits: list[RAGHit] = []
        for idx in ranked:
            base = self._hits[idx]
            hits.append(
                RAGHit(
                    product_id=base.product_id,
                    sku=base.sku,
                    name=base.name,
                    score=float(sims[idx]),
                    context=base.context,
                )
            )

        if not hits or hits[0].score <= 0.0:
            return "No encontré información suficiente en el catálogo. ¿Qué producto (SKU o nombre) te interesa?", hits

        top = hits[0]
        reply = (
            f"Según el catálogo, {top.name} (SKU {top.sku}) tiene estas referencias técnicas relevantes:\n"
            f"{self._extract_snippet(top.context, question)}"
        )
        return reply, hits

    def _extract_snippet(self, context: str, question: str) -> str:
        lines = [ln.strip() for ln in context.splitlines() if ln.strip()]
        q = question.lower()
        scored: list[tuple[int, str]] = []
        for ln in lines:
            overlap = sum(1 for w in q.split() if w and w in ln.lower())
            scored.append((overlap, ln))
        scored.sort(key=lambda t: t[0], reverse=True)
        top_lines = [t[1] for t in scored[:4] if t[0] > 0] or lines[:4]
        return "\n".join(top_lines)


rag_store = InMemoryRAG()
