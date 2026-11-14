from sqlalchemy import Column, Integer, String
from models.Geral import Base


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    login = Column(String(150), nullable=False, unique=True)
    cpf = Column(String(14), nullable=True)
    password = Column(String(150), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "login": self.login,
            "cpf": self.cpf or "",
        }