from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


# tag
class Tag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    # relationships
    products: list["ProductTag"] = Relationship(back_populates="tag")
    user_favorites: list["UserFavoriteTag"] = Relationship(back_populates="tag")


# user
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default="")
    is_member: bool = Field(default=False)

    # relationships
    orders: list["Order"] = Relationship(back_populates="user")
    favorite_tags: list["UserFavoriteTag"] = Relationship(back_populates="user")


# user favorite tags (many-to-many relationship)
class UserFavoriteTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    tag_id: int = Field(foreign_key="tag.id")

    # relationships
    user: "User" = Relationship(back_populates="favorite_tags")
    tag: "Tag" = Relationship(back_populates="user_favorites")


# order products
class OrderProduct(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(default=None, foreign_key="order.id")
    product_id: int = Field(default=None, foreign_key="product.id")
    quantity: int = Field(default=0)

    order: "Order" = Relationship(back_populates="order_products")
    product: "Product" = Relationship(back_populates="order_products")


# product tags (many-to-many relationship)
class ProductTag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    tag_id: int = Field(foreign_key="tag.id")

    # relationships
    product: "Product" = Relationship(back_populates="tags")
    tag: "Tag" = Relationship(back_populates="products")


# product
class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default="")
    type: str = Field(default="")
    brand: str = Field(default="")
    price: float = Field(default=0.0)
    stock_quantity: int = Field(default=0)
    min_stock_level: int = Field(default=5)

    # relationships
    order_products: list["OrderProduct"] = Relationship(back_populates="product")
    tags: list["ProductTag"] = Relationship(back_populates="product")


# order
class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    final_price: float | None = Field(default=None)
    date: datetime = Field(default=datetime.now())

    user: "User" = Relationship(back_populates="orders")
    order_products: list["OrderProduct"] = Relationship(back_populates="order")
