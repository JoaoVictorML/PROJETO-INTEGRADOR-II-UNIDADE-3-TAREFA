from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session as flask_session

from repositories.admin_repository import AdminRepository

admin_bp = Blueprint("admin_bp", __name__)


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not flask_session.get("admin_id"):
            return redirect(url_for("admin_bp.admin_login"))
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin = AdminRepository.authenticate(
            request.form.get("email"),
            request.form.get("password")
        )
        if admin:
            flask_session["admin_id"] = admin["id"]
            flask_session["admin_name"] = admin["name"]
            flash(f"Bem-vindo(a), {admin['name']}!", "success")
            return redirect(url_for("admin_bp.list_admins"))
        return render_template("auth/signin.html", error="Credenciais inválidas ou usuário inativo.")
    return render_template("auth/signin.html")


@admin_bp.route("/admin/logout")
def admin_logout():
    flask_session.pop("admin_id", None)
    flask_session.pop("admin_name", None)
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("views_bp.index"))


@admin_bp.route("/admin/admins")
@admin_required
def list_admins():
    admins = AdminRepository.list_all()
    return render_template("admin/admins/list.html", admins=admins)


@admin_bp.route("/admin/admins/new", methods=["GET", "POST"])
@admin_required
def create_admin():
    if request.method == "POST":
        data = request.form.to_dict()
        data["active"] = "active" in request.form          # checkbox

        ok, result = AdminRepository.create(data)
        if ok:
            flash("Administrador criado com sucesso!", "success")
            return redirect(url_for("admin_bp.list_admins"))

        return render_template(
            "admin/admins/form.html",
            admin=data,
            error=result,
            editing=False
        )

    return render_template(
        "admin/admins/form.html",
        admin={"active": True},
        editing=False
    )


@admin_bp.route("/admin/admins/<int:admin_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_admin(admin_id):
    admin = AdminRepository.find_by_id(admin_id)
    if not admin:
        flash("Administrador não encontrado.", "error")
        return redirect(url_for("admin_bp.list_admins"))

    if request.method == "POST":
        data = request.form.to_dict()
        data["active"] = "active" in request.form

        ok, result = AdminRepository.update(admin_id, data)
        if ok:
            flash("Administrador atualizado com sucesso!", "success")
            return redirect(url_for("admin_bp.list_admins"))

        data["id"] = admin_id
        return render_template(
            "admin/admins/form.html",
            admin=data,
            error=result,
            editing=True
        )

    return render_template(
        "admin/admins/form.html",
        admin=admin,
        editing=True
    )


@admin_bp.route("/admin/admins/<int:admin_id>/delete", methods=["POST"])
@admin_required
def delete_admin(admin_id):
    # Impede que o admin logado exclua a própria conta
    if admin_id == flask_session.get("admin_id"):
        flash("Você não pode excluir a própria conta.", "error")
    elif AdminRepository.delete(admin_id):
        flash("Administrador excluído com sucesso.", "success")
    else:
        flash("Administrador não encontrado.", "error")

    return redirect(url_for("admin_bp.list_admins"))