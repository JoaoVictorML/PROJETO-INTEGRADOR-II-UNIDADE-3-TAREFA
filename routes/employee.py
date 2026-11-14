from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session as flask_session
from repositories.employee_repository import EmployeeRepository

employee_bp = Blueprint("employee_bp", __name__, url_prefix="/admin/employees")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("admin_id"):
            return redirect(url_for("views_bp.signin", tipo="admin"))
        return f(*args, **kwargs)
    return decorated_function


@employee_bp.route("/")
@admin_required
def list_employees():
    employees = EmployeeRepository.list_all()
    return render_template("admin/employees/list.html", employees=employees)


@employee_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create_employee():
    if request.method == "POST":
        data = {
            "fullname": request.form.get("fullname"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "role": request.form.get("role"),
            "password": request.form.get("password"),
            "active": "active" in request.form,
        }
        ok, result = EmployeeRepository.create(data)
        if ok:
            return redirect(url_for("employee_bp.list_employees"))
        return render_template("admin/employees/form.html", employee=None, error=result)

    return render_template("admin/employees/form.html", employee=None, error=None)


@employee_bp.route("/<int:employee_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_employee(employee_id):
    employee = EmployeeRepository.find_by_id(employee_id)
    if not employee:
        return redirect(url_for("employee_bp.list_employees"))

    if request.method == "POST":
        data = {
            "fullname": request.form.get("fullname"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "role": request.form.get("role"),
            "password": request.form.get("password"),
            "active": "active" in request.form,
        }
        ok, result = EmployeeRepository.update(employee_id, data)
        if ok:
            return redirect(url_for("employee_bp.list_employees"))
        return render_template("admin/employees/form.html", employee=data, error=result)

    return render_template("admin/employees/form.html", employee=employee, error=None)


@employee_bp.route("/<int:employee_id>/delete", methods=["POST"])
@admin_required
def delete_employee(employee_id):
    EmployeeRepository.delete(employee_id)
    return redirect(url_for("employee_bp.list_employees"))