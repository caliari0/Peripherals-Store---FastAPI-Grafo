from sqlmodel import Session
from app.core.services.stock_service import StockService
from app.core.services.tag_service import TagService
from app.models import Product
from app.core.ports.type_port import TypePort
from app.dtos import (
    RestockInput,
    SetMinStockInput,
    CreateProductInput,
    UpdateProductInput,
    DeleteProductInput,
    StockStatusResponse,
    LowStockProductResponse,
    OutOfStockProductResponse,
    SetMinStockResponse,
    RestockResponse,
    CreateProductResponse,
    UpdateProductResponse,
    DeleteProductResponse,
    ProductInStockResponse,
)


# use case for stock
class StockUseCase:
    def __init__(
        self,
        session: Session,
        stock_service: StockService,
        tag_service: TagService,
        type_adapter: TypePort,
    ):
        self.session = session
        self.stock_service = stock_service
        self.tag_service = tag_service
        self.type_adapter = type_adapter

    # creates a new product
    def create_product(self, input: CreateProductInput) -> CreateProductResponse:
        # validates input data using type functions
        if not self.type_adapter.validate_price(input.price):
            raise ValueError("Price cannot be negative or exceed maximum value")
        if not self.type_adapter.validate_quantity(input.stock_quantity):
            raise ValueError(
                "Stock quantity cannot be negative or exceed maximum value"
            )
        if not self.type_adapter.validate_quantity(input.min_stock_level):
            raise ValueError(
                "Minimum stock level cannot be negative or exceed maximum value"
            )
        if not self.type_adapter.validate_product_name(input.name):
            raise ValueError("Product name is invalid or empty")
        if not self.type_adapter.validate_product_name(input.product_type):
            raise ValueError("Product type is invalid or empty")

        # creates the product
        product = Product(
            name=input.name,
            product_type=input.product_type,
            price=input.price,
            stock_quantity=input.stock_quantity,
            min_stock_level=input.min_stock_level,
        )

        # persists the product
        self.session.add(product)
        self.session.flush()
        self.session.commit()

        # adds tags to the product if provided
        tag_names = []
        if input.tag_names:
            self.tag_service.add_tags_to_product(product.id, input.tag_names)
            tag_names = self.tag_service.get_product_tags(product.id)

        message = f"Successfully created product '{input.name}' with {input.stock_quantity} units in stock"
        return CreateProductResponse(
            id=product.id,
            name=product.name,
            product_type=product.product_type,
            price=product.price,
            stock_quantity=product.stock_quantity,
            min_stock_level=product.min_stock_level,
            tag_names=tag_names,
            message=message,
        )

    # updates an existing product
    def update_product(self, input: UpdateProductInput) -> UpdateProductResponse:
        # gets the product
        product = self.stock_service.get_product(input.product_id)

        # validates input data using type functions
        if input.price is not None and not self.type_adapter.validate_price(
            input.price
        ):
            raise ValueError("Price cannot be negative or exceed maximum value")
        if input.stock_quantity is not None and not self.type_adapter.validate_quantity(
            input.stock_quantity
        ):
            raise ValueError(
                "Stock quantity cannot be negative or exceed maximum value"
            )
        if (
            input.min_stock_level is not None
            and not self.type_adapter.validate_quantity(input.min_stock_level)
        ):
            raise ValueError(
                "Minimum stock level cannot be negative or exceed maximum value"
            )
        if input.name is not None and not self.type_adapter.validate_product_name(
            input.name
        ):
            raise ValueError("Product name is invalid or empty")
        if (
            input.product_type is not None
            and not self.type_adapter.validate_product_name(input.product_type)
        ):
            raise ValueError("Product type is invalid or empty")

        # updates provided fields
        updated_fields = []
        if input.name is not None:
            product.name = input.name
            updated_fields.append("name")
        if input.product_type is not None:
            product.product_type = input.product_type
            updated_fields.append("product type")
        if input.price is not None:
            product.price = input.price
            updated_fields.append("price")
        if input.stock_quantity is not None:
            product.stock_quantity = input.stock_quantity
            updated_fields.append("stock quantity")
        if input.min_stock_level is not None:
            product.min_stock_level = input.min_stock_level
            updated_fields.append("minimum stock level")

        # handles tag updates
        if input.tag_names is not None:
            # gets current tags (now returns List[str])
            current_tag_names = self.tag_service.get_product_tags(input.product_id)

            # removes tags that are not in the new list
            tags_to_remove = [
                tag_name
                for tag_name in current_tag_names
                if tag_name not in input.tag_names
            ]
            if tags_to_remove:
                self.tag_service.remove_tags_from_product(
                    input.product_id, tags_to_remove
                )

            # adds new tags
            new_tags = [
                tag_name
                for tag_name in input.tag_names
                if tag_name not in current_tag_names
            ]
            if new_tags:
                self.tag_service.add_tags_to_product(input.product_id, new_tags)

            updated_fields.append("tags")

        # persists changes
        self.session.add(product)
        self.session.flush()
        self.session.commit()

        # gets updated tag names
        tag_names = self.tag_service.get_product_tags(input.product_id)

        # creates message based on updated fields
        if updated_fields:
            fields_str = ", ".join(updated_fields)
            message = f"Successfully updated product {input.product_id}: {fields_str}"
        else:
            message = f"No changes made to product {input.product_id}"

        return UpdateProductResponse(
            id=product.id,
            name=product.name,
            product_type=product.product_type,
            price=product.price,
            stock_quantity=product.stock_quantity,
            min_stock_level=product.min_stock_level,
            tag_names=tag_names,
            message=message,
        )

    # deletes a product from stock
    def delete_product(self, input: DeleteProductInput) -> DeleteProductResponse:
        # gets the product
        product = self.stock_service.get_product(input.product_id)

        # checks if product has stock
        if product.stock_quantity > 0 and not input.force_delete:
            raise ValueError(
                f"Cannot delete product '{product.name}' (ID: {input.product_id}) "
                f"because it has {product.stock_quantity} units in stock. "
                f"Use force_delete=True to delete anyway."
            )

        # checks if product is in orders (relationships)
        if hasattr(product, "order_products") and product.order_products:
            if not input.force_delete:
                raise ValueError(
                    f"Cannot delete product '{product.name}' (ID: {input.product_id}) "
                    f"because it is associated with {len(product.order_products)} orders. "
                    f"Use force_delete=True to delete anyway."
                )

        # stores product information before deleting
        product_id = product.id
        product_name = product.name

        # deletes the product
        self.session.delete(product)
        self.session.commit()

        message = f"Successfully deleted product '{product_name}' (ID: {product_id})"
        return DeleteProductResponse(
            product_id=product_id, product_name=product_name, message=message
        )

    # restocks inventory
    def restock_product(self, input: RestockInput) -> RestockResponse:
        # gets the product
        product = self.stock_service.get_product(
            input.product_id
        )  # TODO remove _ from get_product

        # validates input data using type functions
        if not self.type_adapter.validate_quantity(input.quantity):
            raise ValueError(
                "Restock quantity cannot be negative or exceed maximum value"
            )

        # updates stock
        product.stock_quantity += input.quantity

        # persists changes
        self.session.add(product)
        self.session.flush()
        self.session.commit()

        message = f"Successfully restocked {input.quantity} units of product {input.product_id}"
        return RestockResponse(message=message)

    # sets minimum stock level
    def set_min_stock_level(self, input: SetMinStockInput) -> SetMinStockResponse:
        # validates input data using type functions
        if not self.type_adapter.validate_quantity(input.min_level):
            raise ValueError(
                "Minimum stock level cannot be negative or exceed maximum value"
            )

        self.stock_service.set_min_stock_level(input.product_id, input.min_level)
        self.session.commit()
        message = f"Successfully set min stock level to {input.min_level} for product {input.product_id}"
        return SetMinStockResponse(message=message)

    # returns products with stock below minimum
    def get_low_stock_products(self) -> list[LowStockProductResponse]:
        products = self.stock_service.get_low_stock_products()
        return [
            LowStockProductResponse(
                id=product.id,
                name=product.name,
                current_stock=product.stock_quantity,
                min_stock_level=product.min_stock_level,
            )
            for product in products
        ]

    # returns products with zero stock
    def get_out_of_stock_products(self) -> list[OutOfStockProductResponse]:
        products = self.stock_service.get_out_of_stock_products()
        return [
            OutOfStockProductResponse(
                id=product.id,
                name=product.name,
                current_stock=product.stock_quantity,
                min_stock_level=product.min_stock_level,
            )
            for product in products
        ]

    # returns stock status
    def get_stock_status(self, product_id: int) -> StockStatusResponse:
        status = self.stock_service.get_stock_status(product_id)
        if status is None:
            raise ValueError(f"Product {product_id} not found")
        return StockStatusResponse(**status)

    # returns all products that have stock (quantity > 0)
    def get_all_products_in_stock(self) -> list[ProductInStockResponse]:
        products = self.stock_service.get_all_products_in_stock()
        return [
            ProductInStockResponse(
                id=product.id,
                name=product.name,
                product_type=product.product_type,
                price=product.price,
                stock_quantity=product.stock_quantity,
                min_stock_level=product.min_stock_level,
            )
            for product in products
        ]
