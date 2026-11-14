from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session as flask_session
from repositories.user_repository import UserRepository

user_bp = Blueprint("user_bp", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("admin_id"):
            return redirect(url_for("views_bp.signin", tipo="admin"))
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("user_id"):
            return redirect(url_for("views_bp.signin", tipo="user"))
        return f(*args, **kwargs)
    return decorated_function


# --- ÁREA DO PRÓPRIO CLIENTE (EDITAR CONTA) ---
@user_bp.route("/users/profile", methods=["GET", "POST"])
@user_required
def my_profile():
    user_id = flask_session["user_id"]
    user = UserRepository.find_by_id(user_id)
    if not user:
        flask_session.clear()
        return redirect(url_for("views_bp.signin", tipo="user"))

    if request.method == "POST":
        data = {
            "nome": request.form.get("nome"),
            "login": request.form.get("login"),
            "cpf": request.form.get("cpf"),
            "password": request.form.get("password"),
        }
        ok, result = UserRepository.update(user_id, data)
        if ok:
            flask_session["user_nome"] = result["nome"]
            return render_template("users/profile.html", user=result, success="Dados atualizados com sucesso!", error=None)
        return render_template("users/profile.html", user=data, success=None, error=result)

    return render_template("users/profile.html", user=user, success=None, error=None)


# --- ÁREA ADMINISTRATIVA (CRUD COMPLETO DE CLIENTES) ---
@user_bp.route("/admin/users/")
@admin_required
def list_users():
    users = UserRepository.list_all()
    return render_template("admin/users/list.html", users=users)


@user_bp.route("/admin/users/new", methods=["GET", "POST"])
@admin_required
def create_user():
    if request.method == "POST":
        data = {
            "nome": request.form.get("nome"),
            "login": request.form.get("login"),
            "cpf": request.form.get("cpf"),
            "password": request.form.get("password"),
        }
        ok, result = UserRepository.create(data)
        if ok:
            return redirect(url_for("user_bp.list_users"))
        return render_template("admin/users/form.html", user=None, error=result)

    return render_template("admin/users/form.html", user=None, error=None)


@user_bp.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = UserRepository.find_by_id(user_id)
    if not user:
        return redirect(url_for("user_bp.list_users"))

    if request.method == "POST":
        data = {
            "nome": request.form.get("nome"),
            "login": request.form.get("login"),
            "cpf": request.form.get("cpf"),
            "password": request.form.get("password"),
        }
        ok, result = UserRepository.update(user_id, data)
        if ok:
            return redirect(url_for("user_bp.list_users"))
        return render_template("admin/users/form.html", user=data, error=result)

    return render_template("admin/users/form.html", user=user, error=None)


@user_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    UserRepository.delete(user_id)
    return redirect(url_for("user_bp.list_users"))