from fastapi import APIRouter, Depends, HTTPException
from app.core.use_cases.sales_use import SalesUseCase
from app.core.factories import get_sales_use_case
from app.dtos import SimpleSaleRequest, SaleResponse

router = APIRouter(prefix="/sale")


@router.post("/", response_model=SaleResponse)
async def sell_products(
    request: SimpleSaleRequest,
    sales_use_case: SalesUseCase = Depends(get_sales_use_case),
):
    try:
        # Parse product IDs and quantities
        try:
            product_ids = [
                int(pid.strip())
                for pid in request.product_ids.split(",")
                if pid.strip()
            ]
            quantities = [
                int(qty.strip()) for qty in request.quantities.split(",") if qty.strip()
            ]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Product IDs and quantities must be comma-separated numbers",
            )

        # Validate that we have the same number of products and quantities
        if len(product_ids) != len(quantities):
            raise HTTPException(
                status_code=400,
                detail="Number of product IDs must match number of quantities",
            )

        # Validate that quantities are positive
        if any(qty <= 0 for qty in quantities):
            raise HTTPException(
                status_code=400, detail="All quantities must be positive numbers"
            )

        # Process the sale
        result = sales_use_case.simple_sale(
            user_id=request.user_id, product_ids=product_ids, quantities=quantities
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sale failed: {str(e)}")


# Get available products for purchase
@router.get("/products")
async def get_available_products(
    sales_use_case: SalesUseCase = Depends(get_sales_use_case),
):
    """Get all products that are in stock for purchase"""
    try:
        return sales_use_case.get_available_products()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
