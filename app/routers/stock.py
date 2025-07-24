from fastapi import APIRouter, Depends, HTTPException
from app.core.use_cases.stock_use import (
    StockUseCase,
    RestockInput,
    SetMinStockInput,
    CreateProductInput,
    UpdateProductInput,
    DeleteProductInput,
    StockStatusResponse,
    LowStockProductResponse,
    OutOfStockProductResponse,
    ProductInStockResponse,  # Add this import
    SetMinStockResponse,
    RestockResponse,
    CreateProductResponse,
    UpdateProductResponse,
    DeleteProductResponse,
)
from app.core.factories import get_stock_use_case

router = APIRouter(prefix="/stock")


# creates a new product
@router.post("/products")
def create_product(
    request: CreateProductInput,
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> CreateProductResponse:
    try:
        return stock_use_case.create_product(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# updates an existing product
@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    request: UpdateProductInput,
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> UpdateProductResponse:
    try:
        # Ensure the product_id in the path matches the request
        request.product_id = product_id
        return stock_use_case.update_product(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# deletes a product
@router.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    force_delete: bool = False,
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> DeleteProductResponse:
    try:
        request = DeleteProductInput(product_id=product_id, force_delete=force_delete)
        return stock_use_case.delete_product(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# returns products with stock below minimum
@router.get("/low-stock")
def get_low_stock_products(
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> list[LowStockProductResponse]:
    try:
        return stock_use_case.get_low_stock_products()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# returns products with zero stock
@router.get("/out-of-stock")
def get_out_of_stock_products(
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> list[OutOfStockProductResponse]:
    try:
        return stock_use_case.get_out_of_stock_products()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# restocks inventory
@router.post("/restock")
def restock_product(
    request: RestockInput, stock_use_case: StockUseCase = Depends(get_stock_use_case)
) -> RestockResponse:
    try:
        return stock_use_case.restock_product(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# sets minimum stock level
@router.post("/set-min-level")
def set_min_stock_level(
    request: SetMinStockInput,
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> SetMinStockResponse:
    try:
        return stock_use_case.set_min_stock_level(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# returns stock status
@router.get("/status/{product_id}")
def get_stock_status(
    product_id: int, stock_use_case: StockUseCase = Depends(get_stock_use_case)
) -> StockStatusResponse:
    try:
        status = stock_use_case.get_stock_status(product_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# gets all products in stock
@router.get("/products/in-stock", response_model=list[ProductInStockResponse])
def get_all_products_in_stock(
    stock_use_case: StockUseCase = Depends(get_stock_use_case),
) -> list[ProductInStockResponse]:
    try:
        return stock_use_case.get_all_products_in_stock()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
