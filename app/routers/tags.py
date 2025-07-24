from fastapi import APIRouter, Depends, HTTPException
from app.core.use_cases.tag_use import (
    TagUseCase,
    AddTagsToProductInput,
    RemoveTagsFromProductInput,
    ProductTagsResponse,
    AddFavoriteTagInput,
    RemoveFavoriteTagInput,
    UserFavoriteTagsResponse,
    RecommendedProductsResponse,
    ProductsByTagResponse,
    AllTagsResponse,
    CleanupResponse,
)
from app.core.factories import get_tag_use_case

router = APIRouter(prefix="/tags")

# PRODUCT TAG OPERATIONS


@router.post("/products/add", response_model=ProductTagsResponse)
def add_tags_to_product(
    input: AddTagsToProductInput, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> ProductTagsResponse:
    try:
        return tag_use_case.add_tags_to_product(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/remove", response_model=ProductTagsResponse)
def remove_tags_from_product(
    input: RemoveTagsFromProductInput,
    tag_use_case: TagUseCase = Depends(get_tag_use_case),
) -> ProductTagsResponse:
    try:
        return tag_use_case.remove_tags_from_product(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", response_model=ProductTagsResponse)
def get_product_tags(
    product_id: int, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> ProductTagsResponse:
    try:
        return tag_use_case.get_product_tags(product_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products", response_model=ProductsByTagResponse)
def get_products_by_tag(
    tag_name: str, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> ProductsByTagResponse:
    try:
        return tag_use_case.get_products_by_tag(tag_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# USER FAVORITE TAG OPERATIONS


@router.post("/users/favorites", response_model=UserFavoriteTagsResponse)
def add_favorite_tag(
    input: AddFavoriteTagInput, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> UserFavoriteTagsResponse:
    try:
        return tag_use_case.add_favorite_tag(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/favorites", response_model=UserFavoriteTagsResponse)
def remove_favorite_tag(
    input: RemoveFavoriteTagInput, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> UserFavoriteTagsResponse:
    try:
        return tag_use_case.remove_favorite_tag(input)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/favorites", response_model=UserFavoriteTagsResponse)
def get_user_favorite_tags(
    tag_use_case: TagUseCase = Depends(get_tag_use_case),
) -> UserFavoriteTagsResponse:
    try:
        return tag_use_case.get_user_favorite_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/recommendations", response_model=RecommendedProductsResponse)
def get_recommended_products(
    limit: int = 10, tag_use_case: TagUseCase = Depends(get_tag_use_case)
) -> RecommendedProductsResponse:
    try:
        return tag_use_case.get_recommended_products(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# UTILITY OPERATIONS


@router.get("/", response_model=AllTagsResponse)
def get_all_tags(
    tag_use_case: TagUseCase = Depends(get_tag_use_case),
) -> AllTagsResponse:
    try:
        return tag_use_case.get_all_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup", response_model=CleanupResponse)
def cleanup_unused_tags(
    tag_use_case: TagUseCase = Depends(get_tag_use_case),
) -> CleanupResponse:
    try:
        return tag_use_case.cleanup_unused_tags()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
