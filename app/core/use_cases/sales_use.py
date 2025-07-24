from sqlmodel import Session
from app.models import User, Order, OrderProduct
from app.core.services.order_service import OrderService
from app.core.services.setup_service import SetupService
from app.core.services.stock_service import StockService
from app.core.ports.type_port import TypePort
from app.dtos import SaleResult
from datetime import datetime


class SalesUseCase:
    def __init__(
        self,
        session: Session,
        order_service: OrderService,
        setup_service: SetupService,
        stock_service: StockService,
        type_adapter: TypePort,
    ):
        self.session = session
        self.order_service = order_service
        self.setup_service = setup_service
        self.stock_service = stock_service
        self.type_adapter = type_adapter

    def simple_sale(
        self, user_id: int, product_ids: list[int], quantities: list[int]
    ) -> SaleResult:
        try:
            # Validate inputs using type functions
            if not self.type_adapter.validate_quantity(user_id):
                raise ValueError("Invalid user ID")

            for quantity in quantities:
                if not self.type_adapter.validate_quantity(quantity):
                    raise ValueError(f"Invalid quantity: {quantity}")

            # 1. Get or create user
            user = self.setup_service.get_user(user_id, None)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # 2. Get all products
            products = self.order_service.get_products(product_ids)
            if len(products) != len(product_ids):
                found_ids = [p.id for p in products]
                missing_ids = [pid for pid in product_ids if pid not in found_ids]
                raise ValueError(f"Products not found: {missing_ids}")

            # 3. Create order
            order = Order(user_id=user.id, date=datetime.now())
            self.session.add(order)
            self.session.flush()  # Get order ID

            # 4. Create order products and update stock
            order_products = []
            product_map = []
            total_price = 0.0

            for product, quantity in zip(products, quantities):
                # Check stock availability with improved error message
                if product.stock_quantity < quantity:
                    raise ValueError(
                        f"Insufficient stock for product ID {product.id} '{product.name}'. Available: {product.stock_quantity}, requested: {quantity}"
                    )

                # Create order product
                order_product = OrderProduct(
                    order_id=order.id, product_id=product.id, quantity=quantity
                )
                self.session.add(order_product)
                order_products.append(order_product)

                # Update stock
                product.stock_quantity -= quantity
                self.session.add(product)

                # Calculate price
                unit_price = product.price
                item_total = unit_price * quantity
                total_price += item_total

                product_map.append((product, quantity))

            # 5. Set final price (apply member discount if applicable)
            if user.is_member:
                total_price *= 0.7  # 30% discount for members

            order.final_price = total_price
            self.session.add(order)

            # 6. Commit all changes
            self.session.commit()

            # 7. Generate invoice
            invoice = self._generate_simple_invoice(order, product_map, user)

            # 8. Return result
            return SaleResult(
                order_id=order.id,
                user_id=user.id,
                total_price=total_price,
                invoice=invoice,
                products_sold=[
                    {
                        "product_id": product.id,
                        "name": product.name,
                        "quantity": quantity,
                        "unit_price": product.price,
                        "total": product.price * quantity,
                    }
                    for product, quantity in product_map
                ],
            )

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Sale failed: {str(e)}")

    def get_available_products(self) -> list[dict]:
        """Get all products that are in stock"""
        try:
            products = self.stock_service.get_all_products_in_stock()
            return [
                {
                    "id": product.id,
                    "name": product.name,
                    "product_type": product.product_type,
                    "price": product.price,
                    "stock_quantity": product.stock_quantity,
                    "min_stock_level": product.min_stock_level,
                }
                for product in products
            ]
        except Exception as e:
            raise ValueError(f"Failed to get available products: {str(e)}")

    def _generate_simple_invoice(
        self, order: Order, product_map: list[tuple], user: User
    ) -> str:
        """Generate a simple text invoice"""
        invoice_lines = []
        invoice_lines.append("=" * 50)
        invoice_lines.append("INVOICE")
        invoice_lines.append("=" * 50)
        invoice_lines.append(f"Order ID: {order.id}")
        invoice_lines.append(f"Date: {order.date.strftime('%Y-%m-%d %H:%M:%S')}")
        invoice_lines.append(f"Customer: {user.name} (ID: {user.id})")
        invoice_lines.append(f"Member: {'Yes' if user.is_member else 'No'}")
        invoice_lines.append("-" * 50)
        invoice_lines.append("ITEMS:")
        invoice_lines.append("-" * 50)

        subtotal = 0.0
        for product, quantity in product_map:
            unit_price = product.price
            item_total = unit_price * quantity
            subtotal += item_total
            invoice_lines.append(f"{product.name} (ID: {product.id})")
            invoice_lines.append(
                f"  {quantity} x ${unit_price:.2f} = ${item_total:.2f}"
            )

        invoice_lines.append("-" * 50)
        if user.is_member:
            invoice_lines.append(f"Subtotal: ${subtotal:.2f}")
            discount = subtotal * 0.3
            invoice_lines.append(f"Member Discount (30%): -${discount:.2f}")

        invoice_lines.append(f"TOTAL: ${order.final_price:.2f}")
        invoice_lines.append("=" * 50)
        invoice_lines.append("Thank you for your purchase!")
        invoice_lines.append("=" * 50)

        return "\n".join(invoice_lines)

    # Keep the old method for backward compatibility
    def create_order(self, input) -> str:
        # This is kept for backward compatibility but simplified
        try:
            user = self.setup_service.get_user(input.user_id, input.name)
            products = self.order_service.get_products(
                [p.product_id for p in input.products]
            )

            order = Order(user_id=user.id, date=datetime.now())
            self.session.add(order)
            self.session.flush()

            product_map = []
            for product, input_product in zip(products, input.products):
                if product.stock_quantity < input_product.quantity:
                    raise ValueError(
                        f"Insufficient stock for product ID {product.id} '{product.name}'. Available: {product.stock_quantity}, requested: {input_product.quantity}"
                    )

                order_product = OrderProduct(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=input_product.quantity,
                )
                self.session.add(order_product)

                product.stock_quantity -= input_product.quantity
                self.session.add(product)

                product_map.append((product, input_product.quantity))

            total_price = sum(product.price * qty for product, qty in product_map)
            if user.is_member:
                total_price *= 0.7

            order.final_price = total_price
            self.session.commit()

            return self._generate_simple_invoice(order, product_map, user)

        except Exception as e:
            self.session.rollback()
            raise ValueError(f"Order creation failed: {str(e)}")
