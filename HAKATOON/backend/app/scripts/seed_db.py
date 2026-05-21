import random

from sqlalchemy import select

import app.models
from app.db.session import SessionLocal, engine
from app.models.base import Base
from app.models.customer import Customer
from app.models.product import Product
from app.models.prospect import Prospect


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing_products = db.scalar(select(Product.id))
        if existing_products is None:
            _seed_products(db)
        existing_customers = db.scalar(select(Customer.id))
        if existing_customers is None:
            _seed_customers(db)


def _seed_products(db) -> None:
    products = [
        Product(
            sku="TR-100",
            name="Tractor Andino 100HP",
            category="tractor",
            description="Tractor versátil para cultivos medianos y trabajo en pendientes moderadas.",
            tech_specs="Potencia: 100 HP\nTransmisión: 12F/12R\nConsumo: 7.5 L/h\nTracción: 4x4",
            price=52000.0,
        ),
        Product(
            sku="TR-150",
            name="Tractor Andino 150HP",
            category="tractor",
            description="Tractor de alto torque para preparación de suelo y arrastre de implementos pesados.",
            tech_specs="Potencia: 150 HP\nTransmisión: 16F/16R\nConsumo: 9.8 L/h\nTracción: 4x4",
            price=74000.0,
        ),
        Product(
            sku="TR-80",
            name="Tractor Valle 80HP",
            category="tractor",
            description="Tractor compacto para labores de precisión en parcelas pequeñas y medianas.",
            tech_specs="Potencia: 80 HP\nTransmisión: 8F/8R\nConsumo: 5.9 L/h\nTracción: 4x2",
            price=39000.0,
        ),
        Product(
            sku="FZ-NPK-20-20-20",
            name="Fertilizante NPK 20-20-20 (50kg)",
            category="fertilizante",
            description="Fertilizante balanceado para etapas vegetativas y de desarrollo en múltiples cultivos.",
            tech_specs="N: 20%\nP2O5: 20%\nK2O: 20%\nDosis típica: 150-250 kg/ha",
            price=34.5,
        ),
        Product(
            sku="FZ-UREA-46",
            name="Urea 46% (50kg)",
            category="fertilizante",
            description="Fuente concentrada de nitrógeno para mejorar crecimiento y vigor del cultivo.",
            tech_specs="N: 46%\nAplicación: fraccionada\nDosis típica: 80-200 kg/ha",
            price=28.0,
        ),
        Product(
            sku="FZ-DAP-18-46",
            name="DAP 18-46 (50kg)",
            category="fertilizante",
            description="Fosfatado de arranque para fortalecer raíces y establecimiento temprano.",
            tech_specs="N: 18%\nP2O5: 46%\nDosis típica: 80-180 kg/ha",
            price=31.0,
        ),
    ]
    db.add_all(products)
    db.commit()


def _seed_customers(db) -> None:
    random.seed(7)
    names = ["AgroFinca Los Olivos", "Cooperativa San Miguel", "Hacienda El Trigal", "Campos del Sur", "Agroexport Andina"]
    for i, name in enumerate(names, start=1):
        hectares = float(random.choice([25, 45, 60, 120, 250, 400]))
        purchases_count = int(random.choice([0, 1, 2, 4, 6, 10]))
        total_spent = float(purchases_count * random.choice([900, 1200, 2000, 5000]) + hectares * random.choice([80, 120, 150]))
        phone = f"+51900000{i:03d}"
        customer = Customer(
            name=name,
            phone=phone,
            hectares=hectares,
            purchases_count=purchases_count,
            total_spent=total_spent,
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        prospect = Prospect(customer_id=customer.id, status="new", lead_score=0.0)
        db.add(prospect)
        db.commit()


if __name__ == "__main__":
    main()
