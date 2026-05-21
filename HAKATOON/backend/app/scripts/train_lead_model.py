from __future__ import annotations

from pathlib import Path

import joblib
from sqlalchemy import select
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.prospect import Prospect


def main() -> None:
    X: list[list[float]] = []
    y: list[int] = []

    with SessionLocal() as db:
        rows = db.execute(select(Customer, Prospect).join(Prospect, Prospect.customer_id == Customer.id)).all()
        for customer, prospect in rows:
            X.append([float(customer.hectares), float(customer.total_spent), float(customer.purchases_count)])
            label = 1 if (prospect.status in {"won"} or customer.total_spent > 25000 or customer.purchases_count >= 6) else 0
            y.append(label)

    if len(X) < 10:
        return

    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=500)),
        ]
    )
    model.fit(X, y)

    out = Path(settings.lead_model_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out)


if __name__ == "__main__":
    main()
