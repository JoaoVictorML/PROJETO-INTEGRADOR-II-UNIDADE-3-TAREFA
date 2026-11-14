from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from models.Geral import Base


class Employee(Base):
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    phone = Column(String(20), nullable=True)
    role = Column(String(60), nullable=False, default="Atendente")
    password = Column(String(255), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    data_created = Column(DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "phone": self.phone or "",
            "role": self.role,
            "active": self.active,
            "data_created": self.data_created.strftime("%d/%m/%Y %H:%M") if self.data_created else None,
        }