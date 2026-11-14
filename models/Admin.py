from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from models.Geral import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    position = Column(String(100), nullable=False, default="Administrador")
    salario = Column(Numeric(10, 2), nullable=False, default=0)
    phone = Column(String(20), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    data_created = Column(DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "position": self.position,
            "salario": float(self.salario or 0),
            "phone": self.phone,
            "active": self.active,
            "data_created": self.data_created.strftime("%d/%m/%Y %H:%M") if self.data_created else None,
        }