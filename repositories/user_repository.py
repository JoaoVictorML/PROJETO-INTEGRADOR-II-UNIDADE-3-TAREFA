from sqlalchemy import func
from models.Geral import Session
from models.User import User


class UserRepository:
    @classmethod
    def authenticate(cls, email, password):
        session = Session()
        try:
            email_limpo = email.strip().lower()
            user = session.query(User).filter(func.lower(User.login) == email_limpo).first()

            if not user:
                return None

            senha_banco = str(user.password).strip()
            senha_digitada = str(password).strip()

            if senha_banco == senha_digitada:
                return user
            return None
        finally:
            session.close()

    @staticmethod
    def list_all():
        with Session() as db:
            users = db.query(User).order_by(User.nome).all()
            return [u.to_dict() for u in users]

    @staticmethod
    def find_by_id(user_id: int):
        with Session() as db:
            user = db.get(User, user_id)
            return user.to_dict() if user else None

    @staticmethod
    def create(data: dict):
        nome = (data.get("nome") or "").strip()
        login = (data.get("login") or "").strip().lower()
        cpf = (data.get("cpf") or "").strip()
        password = (data.get("password") or "").strip()

        if not nome or not login or not cpf or not password:
            return False, "Nome, e-mail, CPF/telefone e senha são obrigatórios."

        with Session() as db:
            exists = db.query(User).filter(func.lower(User.login) == login).first()
            if exists:
                return False, "Já existe um cliente cadastrado com este e-mail."

            user = User()
            user.nome = nome
            user.login = login
            user.cpf = cpf
            user.password = password

            db.add(user)
            db.commit()
            db.refresh(user)
            return True, user.to_dict()

    @staticmethod
    def update(user_id: int, data: dict):
        nome = (data.get("nome") or "").strip()
        login = (data.get("login") or "").strip().lower()
        cpf = (data.get("cpf") or "").strip()
        new_password = (data.get("password") or "").strip()

        if not nome or not login or not cpf:
            return False, "Nome, e-mail e CPF/telefone são obrigatórios."

        with Session() as db:
            user = db.get(User, user_id)
            if not user:
                return False, "Cliente não encontrado."

            conflict = db.query(User).filter(
                func.lower(User.login) == login,
                User.id != user_id
            ).first()
            if conflict:
                return False, "Este e-mail já está em uso por outro cliente."

            user.nome = nome
            user.login = login
            user.cpf = cpf

            if new_password:
                user.password = new_password

            db.commit()
            db.refresh(user)
            return True, user.to_dict()

    @staticmethod
    def delete(user_id: int) -> bool:
        with Session() as db:
            user = db.get(User, user_id)
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True