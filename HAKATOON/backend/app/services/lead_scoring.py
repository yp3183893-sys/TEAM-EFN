from __future__ import annotations

import os
import random
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.models.customer import Customer


class LeadScorer:
    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)
        self.model: Pipeline | None = None

    def load_or_train(self) -> None:
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            return
        self.model = self._train_synthetic()
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)

    def predict_probability(self, customer: Customer) -> float:
        if self.model is None:
            self.load_or_train()
        X = [[float(customer.hectares), float(customer.total_spent), float(customer.purchases_count)]]
        proba = float(self.model.predict_proba(X)[0][1])
        return max(0.0, min(1.0, proba))

    def _train_synthetic(self) -> Pipeline:
        random.seed(42)
        X: list[list[float]] = []
        y: list[int] = []
        for _ in range(600):
            hectares = max(0.0, random.gauss(80, 60))
            purchases_count = max(0, int(random.gauss(4, 3)))
            total_spent = max(0.0, random.gauss(hectares * 120 + purchases_count * 800, 3000))
            score = 0.02 * hectares + 0.00025 * total_spent + 0.35 * purchases_count
            prob = 1 / (1 + pow(2.718281828, -0.2 * (score - 8)))
            label = 1 if random.random() < prob else 0
            X.append([hectares, total_spent, float(purchases_count)])
            y.append(label)
        model = Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("clf", LogisticRegression(max_iter=500)),
            ]
        )
        model.fit(X, y)
        return model


lead_scorer = LeadScorer(model_path=os.getenv("LEAD_MODEL_PATH", settings.lead_model_path))
