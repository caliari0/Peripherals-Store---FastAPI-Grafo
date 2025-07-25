from pydantic import BaseModel, Field
from typing import Optional


# STOCK DTOs


class RestockInput(BaseModel):
    product_id: int
    quantity: int


class SetMinStockInput(BaseModel):
    product_id: int
    min_level: int


class CreateProductInput(BaseModel):
    name: str
    product_type: str
    price: float
    stock_quantity: int = 0
    min_stock_level: int = 5
    tag_names: list[str] = []


class UpdateProductInput(BaseModel):
    product_id: int
    name: Optional[str] = None
    product_type: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock_level: Optional[int] = None
    tag_names: Optional[list[str]] = None


class DeleteProductInput(BaseModel):
    product_id: int
    force_delete: bool = False


class StockStatusResponse(BaseModel):
    product_id: int
    name: str
    current_stock: int
    min_stock_level: int
    is_low_stock: bool
    is_out_of_stock: bool


class LowStockProductResponse(BaseModel):
    id: int
    name: str
    current_stock: int
    min_stock_level: int


class OutOfStockProductResponse(BaseModel):
    id: int
    name: str
    current_stock: int
    min_stock_level: int


class SetMinStockResponse(BaseModel):
    message: str


class RestockResponse(BaseModel):
    message: str


class CreateProductResponse(BaseModel):
    id: int
    name: str
    product_type: str
    price: float
    stock_quantity: int
    min_stock_level: int
    tag_names: list[str]
    message: str


class UpdateProductResponse(BaseModel):
    id: int
    name: str
    product_type: str
    price: float
    stock_quantity: int
    min_stock_level: int
    tag_names: list[str]
    message: str


class DeleteProductResponse(BaseModel):
    product_id: int
    product_name: str
    message: str


class ProductInStockResponse(BaseModel):
    id: int
    name: str
    product_type: str
    price: float
    stock_quantity: int
    min_stock_level: int


# TAG DTOs


class AddTagsToProductInput(BaseModel):
    product_id: int
    tag_names: list[str]


class RemoveTagsFromProductInput(BaseModel):
    product_id: int
    tag_names: list[str]


class ProductTagsResponse(BaseModel):
    product_id: int
    tag_names: list[str]


class ProductsByTagResponse(BaseModel):
    tag_name: str
    products: list[dict]  # Simplified product info


class AllTagsResponse(BaseModel):
    tags: list[str]


class CleanupResponse(BaseModel):
    message: str
    removed_count: int


# SALES DTOs


class SimpleSaleRequest(BaseModel):
    user_id: int = Field(..., description="ID of the user making the purchase")
    product_ids: str = Field(
        ..., description="Comma-separated product IDs (e.g., '1,2,3')"
    )
    quantities: str = Field(
        ..., description="Comma-separated quantities (e.g., '2,1,3')"
    )

    class Config:
        json_schema_extra = {
            "example": {"user_id": 1, "product_ids": "1,3,5", "quantities": "2,1,3"}
        }


class SaleResponse(BaseModel):
    order_id: int
    user_id: int
    total_price: float
    invoice: str
    products_sold: list[dict]


class SaleResult(BaseModel):
    order_id: int
    user_id: int
    total_price: float
    invoice: str
    products_sold: list[dict]


# CHAT DTOs


class ComboProductResponse(BaseModel):
    name: str
    price: float
    type: str
    brand: str


class ComboResponse(BaseModel):
    products: list[ComboProductResponse]
    total_price: float
    debug_info: dict


class ProductInfoResponse(BaseModel):
    id: int
    name: str
    type: str
    brand: str
    price: float
    stock_quantity: int
    min_stock_level: int
    tags: list[str]


class ProductInfoResponseWithDebug(BaseModel):
    products: list[ProductInfoResponse]
    debug_info: dict
