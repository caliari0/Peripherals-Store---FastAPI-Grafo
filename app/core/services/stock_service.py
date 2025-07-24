from sqlmodel import Session, select
from typing import Optional
from app.models import Product, OrderProduct


class StockService:
    def __init__(self, session: Session):
        self.session = session

    # gets the product
    def get_product(self, product_id: int) -> Product:
        product = self.session.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")
        return product

    def update_stock_quantity(self, product_id: int, quantity_change: int) -> None:
        # 1. gets the product
        product = self.get_product(product_id)

        # 2. updates stock
        new_quantity = product.stock_quantity + quantity_change
        if new_quantity < 0:
            raise ValueError(
                f"Insufficient stock for product {product_id}. Available: {product.stock_quantity}, requested: {-quantity_change}"
            )
        product.stock_quantity = new_quantity

    # returns all products that have stock (quantity > 0)
    def get_all_products_in_stock(self) -> list[Product]:
        statement = (
            select(Product).where(Product.stock_quantity > 0).order_by(Product.name)
        )
        return list(self.session.exec(statement))

    # returns products that are below minimum stock but not zero
    def get_low_stock_products(self) -> list[Product]:
        statement = select(Product).where(
            Product.stock_quantity <= Product.min_stock_level,
            Product.stock_quantity > 0,
        )
        return list(self.session.exec(statement))

    # returns products that are out of stock
    def get_out_of_stock_products(self) -> list[Product]:
        statement = select(Product).where(Product.stock_quantity == 0)
        return list(self.session.exec(statement))

    def set_min_stock_level(self, product_id: int, min_level: int) -> None:
        product = self.get_product(product_id)
        product.min_stock_level = min_level

    # updates stock for multiple products in an order
    def process_order_stock_update(self, order_products: list[OrderProduct]) -> None:
        for order_product in order_products:
            self.update_stock_quantity(
                order_product.product_id, -order_product.quantity
            )

    # returns stock status
    def get_stock_status(self, product_id: int) -> Optional[dict]:
        product = self.session.get(Product, product_id)
        if not product:
            return None

        return {
            "product_id": product.id,
            "name": product.name,
            "current_stock": product.stock_quantity,
            "min_stock_level": product.min_stock_level,
            "is_low_stock": product.stock_quantity <= product.min_stock_level,
            "is_out_of_stock": product.stock_quantity == 0,
        }
