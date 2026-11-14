from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session as flask_session
from repositories.product_repository import ProductRepository

product_bp = Blueprint("product_bp", __name__, url_prefix="/admin/products")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask_session.get("admin_id") and not flask_session.get("employee_id"):
            return redirect(url_for("views_bp.signin", tipo="employee"))
        return f(*args, **kwargs)
    return decorated_function


@product_bp.route("/")
@admin_required
def list_products():
    products = ProductRepository.list_all()
    return render_template("admin/products/list.html", products=products)


@product_bp.route("/new", methods=["GET", "POST"])
@admin_required
def create_product():
    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "price": request.form.get("price"),
            "description": request.form.get("description"),
            "image_url": request.form.get("image_url"),
            "active": "active" in request.form,
        }
        ok, result = ProductRepository.create(data)
        if ok:
            return redirect(url_for("product_bp.list_products"))
        return render_template("admin/products/form.html", product=None, error=result)

    return render_template("admin/products/form.html", product=None, error=None)


@product_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    product = ProductRepository.find_by_id(product_id)
    if not product:
        return redirect(url_for("product_bp.list_products"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name"),
            "category": request.form.get("category"),
            "price": request.form.get("price"),
            "description": request.form.get("description"),
            "image_url": request.form.get("image_url"),
            "active": "active" in request.form,
        }
        ok, result = ProductRepository.update(product_id, data)
        if ok:
            return redirect(url_for("product_bp.list_products"))
        return render_template("admin/products/form.html", product=data, error=result)

    return render_template("admin/products/form.html", product=product, error=None)


@product_bp.route("/<int:product_id>/delete", methods=["POST"])
@admin_required
def delete_product(product_id):
    ProductRepository.delete(product_id)
    return redirect(url_for("product_bp.list_products"))