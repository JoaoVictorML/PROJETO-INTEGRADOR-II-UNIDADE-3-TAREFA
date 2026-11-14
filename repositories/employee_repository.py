from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from models.Geral import Session
from models.Employee import Employee


class EmployeeRepository:

    @staticmethod
    def list_all():
        with Session() as db:
            employees = db.query(Employee).order_by(Employee.fullname).all()
            return [e.to_dict() for e in employees]

    @staticmethod
    def find_by_id(employee_id: int):
        with Session() as db:
            emp = db.get(Employee, employee_id)
            return emp.to_dict() if emp else None

    @staticmethod
    def authenticate(email: str, password: str):
        email_clean = (email or "").strip().lower()
        with Session() as db:
            emp = db.query(Employee).filter(
                func.lower(Employee.email) == email_clean,
                Employee.active == True
            ).first()
            if emp and check_password_hash(emp.password, password):
                return emp.to_dict()
            return None

    @staticmethod
    def create(data: dict):
        fullname = (data.get("fullname") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = (data.get("password") or "").strip()

        if not fullname or not email or not password:
            return False, "Nome, e-mail e senha são obrigatórios."

        with Session() as db:
            exists = db.query(Employee).filter(func.lower(Employee.email) == email).first()
            if exists:
                return False, "Já existe um funcionário cadastrado com este e-mail."

            emp = Employee(
                fullname=fullname,
                email=email,
                phone=(data.get("phone") or "").strip() or None,
                role=(data.get("role") or "Atendente").strip(),
                password=generate_password_hash(password),
                active=bool(data.get("active", True)),
            )
            db.add(emp)
            db.commit()
            db.refresh(emp)
            return True, emp.to_dict()

    @staticmethod
    def update(employee_id: int, data: dict):
        fullname = (data.get("fullname") or "").strip()
        email = (data.get("email") or "").strip().lower()
        new_password = (data.get("password") or "").strip()

        if not fullname or not email:
            return False, "Nome e e-mail são obrigatórios."

        with Session() as db:
            emp = db.get(Employee, employee_id)
            if not emp:
                return False, "Funcionário não encontrado."

            conflict = db.query(Employee).filter(
                func.lower(Employee.email) == email,
                Employee.id != employee_id
            ).first()
            if conflict:
                return False, "Este e-mail já está em uso por outro funcionário."

            emp.fullname = fullname
            emp.email = email
            emp.phone = (data.get("phone") or "").strip() or None
            emp.role = (data.get("role") or "Atendente").strip()
            emp.active = bool(data.get("active", True))

            if new_password:
                emp.password = generate_password_hash(new_password)

            db.commit()
            db.refresh(emp)
            return True, emp.to_dict()

    @staticmethod
    def delete(employee_id: int) -> bool:
        with Session() as db:
            emp = db.get(Employee, employee_id)
            if not emp:
                return False
            db.delete(emp)
            db.commit()
            return True