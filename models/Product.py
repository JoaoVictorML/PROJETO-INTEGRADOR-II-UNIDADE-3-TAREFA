from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text
from models.Geral import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(80), nullable=False, default="Hambúrgueres")
    image_url = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    data_created = Column(DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "price": float(self.price or 0),
            "category": self.category,
            "image_url": self.image_url or "",
            "active": self.active,
            "data_created": self.data_created.strftime("%d/%m/%Y %H:%M") if self.data_created else None,
        }