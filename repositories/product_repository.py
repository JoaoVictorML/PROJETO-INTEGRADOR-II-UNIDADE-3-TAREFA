from decimal import Decimal, InvalidOperation
from models.Geral import Session
from models.Product import Product


def _parse_price(valor):
    try:
        return Decimal(str(valor or "0").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


class ProductRepository:

    @staticmethod
    def list_all(only_active=False):
        with Session() as db:
            query = db.query(Product)
            if only_active:
                query = query.filter(Product.active == True)
            return [p.to_dict() for p in query.order_by(Product.category, Product.name).all()]

    @staticmethod
    def find_by_id(product_id: int):
        with Session() as db:
            product = db.get(Product, product_id)
            return product.to_dict() if product else None

    @staticmethod
    def create(data: dict):
        name = (data.get("name") or "").strip()
        price = _parse_price(data.get("price"))

        if not name:
            return False, "O nome do produto é obrigatório."
        if price is None or price <= 0:
            return False, "Informe um preço válido maior que zero."

        with Session() as db:
            product = Product(
                name=name,
                description=(data.get("description") or "").strip() or None,
                price=price,
                category=(data.get("category") or "Hambúrgueres").strip(),
                image_url=(data.get("image_url") or "").strip() or None,
                active=bool(data.get("active", True)),
            )
            db.add(product)
            db.commit()
            db.refresh(product)
            return True, product.to_dict()

    @staticmethod
    def update(product_id: int, data: dict):
        name = (data.get("name") or "").strip()
        price = _parse_price(data.get("price"))

        if not name:
            return False, "O nome do produto é obrigatório."
        if price is None or price <= 0:
            return False, "Informe um preço válido maior que zero."

        with Session() as db:
            product = db.get(Product, product_id)
            if not product:
                return False, "Produto não encontrado."

            product.name = name
            product.description = (data.get("description") or "").strip() or None
            product.price = price
            product.category = (data.get("category") or "Hambúrgueres").strip()
            product.image_url = (data.get("image_url") or "").strip() or None
            product.active = bool(data.get("active", True))

            db.commit()
            db.refresh(product)
            return True, product.to_dict()

    @staticmethod
    def delete(product_id: int) -> bool:
        with Session() as db:
            product = db.get(Product, product_id)
            if not product:
                return False
            db.delete(product)
            db.commit()
            return True