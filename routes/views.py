import sys
import os

from flask import Blueprint, render_template, request, redirect, url_for, session as flask_session
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import current_app
from sqlalchemy import func

from models.Geral import Session
from models.User import User
from models.Admin import Admin


from controllers.UserController import cadastrar_usuario 


from repositories.admin_repository import AdminRepository
from repositories.employee_repository import EmployeeRepository
from repositories.product_repository import ProductRepository


views_bp = Blueprint('views_bp', __name__)

@views_bp.route("/")
def index():
    return redirect(url_for('views_bp.public_index'))

@views_bp.route("/public")
def public_index():
    products = ProductRepository.list_all(only_active=True)
    return render_template("public/index.html", products=products)

@views_bp.route("/about")
def about():
    return render_template("public/about_us.html")

@views_bp.route("/contact")
def contact():
    return render_template("public/contact.html")

@views_bp.route("/dashboard")
def dashboard():
    if not flask_session.get("user_id") and not flask_session.get("admin_id") and not flask_session.get("employee_id"):
        return redirect(url_for('views_bp.auth_selection'))

    if flask_session.get("admin_id") or flask_session.get("employee_id"):
        return render_template("admin/dashboard.html")

    return render_template("users/dashboard.html")

@views_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("password")

        ok, result = cadastrar_usuario(nome, email, password)
        if ok:
            flask_session["user_id"] = result["id"]
            flask_session["user_nome"] = result["nome"]
            return redirect(url_for("views_bp.dashboard"))
        return render_template("auth/signup.html", error=result)

    return render_template("auth/signup.html", error=None)

@views_bp.route("/signin", methods=["GET", "POST"])
def signin():
    # Captura se o acesso veio como 'admin' ou 'user' (padrão 'user')
    tipo = request.args.get("tipo", "user")

    if request.method == "POST":
        input_login = request.form.get("email", "").strip().lower()
        input_password = request.form.get("password", "").strip()

        # --- FLUXO DE ADMINISTRADOR ---
        if tipo == "admin":
            admin = AdminRepository.authenticate(input_login, input_password)
            if admin:
                flask_session["admin_id"] = admin["id"]
                flask_session["admin_name"] = admin["name"]
                return redirect(url_for("views_bp.dashboard"))
            return render_template("auth/signin.html", error="Credenciais de administrador inválidas ou usuário inativo.")

        # --- FLUXO DE FUNCIONÁRIO (EMPLOYEE) ---
        if tipo == "employee":
            emp = EmployeeRepository.authenticate(input_login, input_password)
            if emp:
                flask_session["employee_id"] = emp["id"]
                flask_session["employee_name"] = emp["fullname"]
                return redirect(url_for("views_bp.dashboard"))
            return render_template("auth/signin.html", error="Credenciais de funcionário inválidas ou cadastro inativo.")

        # --- FLUXO DE CLIENTE COMUM (USER) ---
        db_session = Session()
        user = db_session.query(User).filter(
            func.lower(User.login) == input_login
        ).first()
        db_session.close()

        if user and str(user.password).strip() == input_password:
            flask_session["user_id"] = user.id
            flask_session["user_nome"] = user.nome
            return redirect(url_for('views_bp.dashboard'))
        else:
            return render_template("auth/signin.html", error="Credenciais inválidas")

    return render_template("auth/signin.html")

@views_bp.route("/user/save", methods=["POST"])
def save_user():
    fullname = request.form.get("fullname")
    email = request.form.get("email")
    cpf_input = request.form.get("phone")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")
    
    sucesso, resultado = cadastrar_usuario(fullname, email, cpf_input, password, confirm_password)
    
    if sucesso:
        db_session = Session()
        user = db_session.query(User).filter(User.login == email).first()
        if user:
            flask_session["user_id"] = user.id
            flask_session["user_nome"] = user.nome
        db_session.close()
        return redirect(url_for('views_bp.dashboard'))
    else:
        return render_template("auth/signup.html", error=resultado)
    
@views_bp.route('/auth_selection')
def auth_selection(): # O nome da função deve ser este
    return render_template('auth/auth_selection.html')

@views_bp.route("/profile")
def profile():
    if "user_id" not in flask_session:
        return redirect(url_for('views_bp.signin'))
    
    db_session = Session()
    user = db_session.query(User).filter(User.id == flask_session["user_id"]).first()
    db_session.close()
    
    return render_template("admin/profile.html", user=user)


@views_bp.route("/logout")
def logout():
    flask_session.clear()
    return redirect(url_for('views_bp.index'))

@views_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_id" not in flask_session:
        return redirect(url_for('views_bp.signin'))
    
    user_id = flask_session["user_id"]
    db_session = Session()
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if user:
        db_session.delete(user)
        db_session.commit()
    
    db_session.close()
    flask_session.clear()
    return redirect(url_for('views_bp.index'))