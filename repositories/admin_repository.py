from decimal import Decimal, InvalidOperation
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from models.Geral import Session
from models.Admin import Admin


def _parse_salario(valor):
    try:
        return Decimal(str(valor or "0").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class AdminRepository:

    @staticmethod
    def list_all():
        with Session() as db:
            return [a.to_dict() for a in db.query(Admin).order_by(Admin.name).all()]

    @staticmethod
    def find_by_id(admin_id: int):
        with Session() as db:
            admin = db.get(Admin, admin_id)
            return admin.to_dict() if admin else None

    @staticmethod
    def create(data: dict):
        """
        Retorna (True, dict) em caso de sucesso
        ou (False, mensagem_de_erro) em caso de falha.
        """
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        salario = _parse_salario(data.get("salario"))

        if not name or not email or not password:
            return False, "Nome, e-mail e senha são obrigatórios."
        if len(password) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."
        if salario is None or salario < 0:
            return False, "Salário inválido."

        with Session() as db:
            admin = Admin(
                name=name,
                email=email,
                password=generate_password_hash(password),
                position=(data.get("position") or "Administrador").strip(),
                salario=salario,
                phone=(data.get("phone") or "").strip() or None,
                active=bool(data.get("active", True)),
            )
            db.add(admin)
            try:
                db.commit()
                db.refresh(admin)
            except IntegrityError:
                db.rollback()
                return False, "Já existe um administrador com esse e-mail."
            return True, admin.to_dict()

    @staticmethod
    def update(admin_id: int, data: dict):
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        salario = _parse_salario(data.get("salario"))
        password = data.get("password") or ""

        if not name or not email:
            return False, "Nome e e-mail são obrigatórios."
        if salario is None or salario < 0:
            return False, "Salário inválido."
        if password and len(password) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        with Session() as db:
            admin = db.get(Admin, admin_id)
            if not admin:
                return False, "Administrador não encontrado."

            admin.name = name
            admin.email = email
            admin.position = (data.get("position") or "Administrador").strip()
            admin.salario = salario
            admin.phone = (data.get("phone") or "").strip() or None
            admin.active = bool(data.get("active", True))

            if password:  # só atualiza a senha se o usuário digitou algo
                admin.password = generate_password_hash(password)

            try:
                db.commit()
                db.refresh(admin)
            except IntegrityError:
                db.rollback()
                return False, "Já existe um administrador com esse e-mail."
            return True, admin.to_dict()

    @staticmethod
    def delete(admin_id: int) -> bool:
        with Session() as db:
            admin = db.get(Admin, admin_id)
            if not admin:
                return False
            db.delete(admin)
            db.commit()
            return True

    @staticmethod
    def authenticate(email: str, password: str):
        """
        Retorna o dict do admin se as credenciais estiverem corretas
        e o usuário estiver ativo. Caso contrário retorna None.
        """
        email = (email or "").strip().lower()
        print("DEBUG LOGIN -> Email digitado:", repr(email))
        print("DEBUG LOGIN -> Senha digitada:", repr(password))

        with Session() as db:
            admin = db.query(Admin).filter(func.lower(Admin.email) == email).first()
            print("DEBUG LOGIN -> Admin encontrado no banco:", admin)
            if admin:
                print("DEBUG LOGIN -> Active:", admin.active)
                print("DEBUG LOGIN -> Hash no banco:", admin.password)
                print("DEBUG LOGIN -> Senha bateu?:", check_password_hash(admin.password, password or ""))

            if admin and admin.active and check_password_hash(admin.password, password or ""):
                return admin.to_dict()
        return None