from app.models import User, Product, Order, OrderProduct
from sqlmodel import Session, select


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def get_products(self, product_ids: list[int]) -> list[Product]:
        products = list(
            self.session.exec(select(Product).where(Product.id.in_(product_ids))).all()
        )
        if not products:
            raise ValueError(f"Products with ids {product_ids} not found")
        return products

    def create_order(self, user_id: int) -> Order:
        return Order(user_id=user_id)

    def create_order_product(self, order_id: int, product_id: int, quantity: int):
        return OrderProduct(order_id=order_id, product_id=product_id, quantity=quantity)

    def calculate_price(
        self, user: User, product_map: list[tuple[Product, int]]
    ) -> float:
        total_price = sum(
            [product.price * quantity for product, quantity in product_map]
        )
        if user.is_member:
            return total_price * 0.7
        return total_price

    def generate_invoice(
        self,
        order: Order,
        product_map: list[tuple[Product, int]],
        user: User = None,
    ):
        """Generate a formatted invoice for the given products and quantities."""
        if not product_map:
            raise ValueError("Product map cannot be empty")

        invoice_lines = []
        invoice_lines.append("=" * 50)
        invoice_lines.append("INVOICE")
        invoice_lines.append("=" * 50)

        if order.id:
            invoice_lines.append(f"Order ID: {order.id}")

        # Show member discount info if applicable
        if user and user.is_member:
            invoice_lines.append("Customer: MEMBER (30% discount applied)")
        elif user:
            invoice_lines.append("Customer: Regular Customer")

        invoice_lines.append("")
        invoice_lines.append(f"{'Product':<20} {'Qty':<8} {'Price':<10} {'Total':<10}")
        invoice_lines.append("-" * 50)

        total_amount = 0
        discount_amount = 0

        for product, quantity in product_map:
            original_price = product.price
            line_total = original_price * quantity

            # Apply member discount if applicable
            if user and user.is_member:
                discounted_price = original_price * 0.7
                discounted_line_total = discounted_price * quantity
                discount_amount += line_total - discounted_line_total

                invoice_lines.append(
                    f"{product.name:<20} {quantity:<8} ${discounted_price:<9.2f} ${discounted_line_total:<9.2f}"
                )
                invoice_lines.append(
                    f"{'':<20} {'':<8} {'(was $' + f'{original_price:.2f})':<10} {'':<10}"
                )
            else:
                invoice_lines.append(
                    f"{product.name:<20} {quantity:<8} ${original_price:<9.2f} ${line_total:<9.2f}"
                )

            total_amount += line_total

        invoice_lines.append("-" * 50)

        if user and user.is_member and discount_amount > 0:
            invoice_lines.append(f"{'SUBTOTAL':<38} ${total_amount:<9.2f}")
            invoice_lines.append(
                f"{'MEMBER DISCOUNT (30%)':<38} -${discount_amount:<8.2f}"
            )
            invoice_lines.append(f"{'FINAL TOTAL':<38} ${order.final_price:<9.2f}")
        else:
            invoice_lines.append(f"{'TOTAL':<38} ${total_amount:<9.2f}")

        invoice_lines.append("=" * 50)

        return "\n".join(invoice_lines)
