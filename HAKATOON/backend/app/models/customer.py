from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    hectares: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_spent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    purchases_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    prospect: Mapped["Prospect"] = relationship(back_populates="customer", uselist=False)
    messages: Mapped[list["Message"]] = relationship(back_populates="customer")
