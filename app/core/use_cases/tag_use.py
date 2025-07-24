from sqlmodel import Session
from app.core.services.tag_service import TagService
from app.dtos import (
    AddTagsToProductInput,
    RemoveTagsFromProductInput,
    ProductTagsResponse,
    ProductsByTagResponse,
    AddFavoriteTagInput,
    RemoveFavoriteTagInput,
    UserFavoriteTagsResponse,
    RecommendedProductsResponse,
    AllTagsResponse,
    CleanupResponse,
)


class TagUseCase:
    def __init__(self, session: Session, tag_service: TagService):
        self.session = session
        self.tag_service = tag_service

    # PRODUCT TAG OPERATIONS

    def add_tags_to_product(self, input: AddTagsToProductInput) -> ProductTagsResponse:
        # Validate input
        if not input.tag_names:
            raise ValueError("Tag names cannot be empty")

        # Call service methods directly - let exceptions bubble up
        new_tags = self.tag_service.add_tags_to_product(
            input.product_id, input.tag_names
        )

        return ProductTagsResponse(product_id=input.product_id, tag_names=new_tags)

    def remove_tags_from_product(
        self, input: RemoveTagsFromProductInput
    ) -> ProductTagsResponse:
        # Validate input
        if not input.tag_names:
            raise ValueError("Tag names cannot be empty")

        # Call service methods directly - let exceptions bubble up
        self.tag_service.remove_tags_from_product(input.product_id, input.tag_names)
        remaining_tags = self.tag_service.get_product_tags(input.product_id)

        return ProductTagsResponse(
            product_id=input.product_id, tag_names=remaining_tags
        )

    def get_product_tags(self, product_id: int) -> ProductTagsResponse:
        # Call service methods directly - let exceptions bubble up
        tag_names = self.tag_service.get_product_tags(product_id)
        return ProductTagsResponse(product_id=product_id, tag_names=tag_names)

    def get_products_by_tag(self, tag_name: str) -> ProductsByTagResponse:
        # Validate input
        if not tag_name or not tag_name.strip():
            raise ValueError("Tag name cannot be empty")

        # Call service methods directly - let exceptions bubble up
        products = self.tag_service.get_products_by_tag(tag_name.strip())
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "product_type": p.product_type,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
            }
            for p in products
        ]

        return ProductsByTagResponse(tag_name=tag_name, products=product_list)

    # USER FAVORITE TAG OPERATIONS

    def add_favorite_tag(self, input: AddFavoriteTagInput) -> UserFavoriteTagsResponse:
        # Validate input

        if not input.tag_name or not input.tag_name.strip():
            raise ValueError("Tag name cannot be empty")

        # Call service methods directly - let exceptions bubble up
        self.tag_service.add_favorite_tag(input.user_id, input.tag_name.strip())
        favorite_tags = self.tag_service.get_user_favorite_tags(input.user_id)

        return UserFavoriteTagsResponse(
            user_id=input.user_id, favorite_tags=favorite_tags
        )

    def remove_favorite_tag(
        self, input: RemoveFavoriteTagInput
    ) -> UserFavoriteTagsResponse:
        # Validate input

        if not input.tag_name or not input.tag_name.strip():
            raise ValueError("Tag name cannot be empty")

        # Call service methods directly - let exceptions bubble up
        success = self.tag_service.remove_favorite_tag(
            input.user_id, input.tag_name.strip()
        )
        if not success:
            raise ValueError(
                f"Favorite tag '{input.tag_name}' not found for user {input.user_id}"
            )

        favorite_tags = self.tag_service.get_user_favorite_tags(input.user_id)
        return UserFavoriteTagsResponse(
            user_id=input.user_id, favorite_tags=favorite_tags
        )

    def get_user_favorite_tags(self, user_id: int) -> UserFavoriteTagsResponse:
        # Validate input

        # Call service methods directly - let exceptions bubble up
        favorite_tags = self.tag_service.get_user_favorite_tags(user_id)
        return UserFavoriteTagsResponse(user_id=user_id, favorite_tags=favorite_tags)

    def get_recommended_products(
        self, user_id: int, limit: int = 10
    ) -> RecommendedProductsResponse:
        # Validate input

        if limit <= 0:
            raise ValueError("Limit must be positive")
        if limit > 100:
            limit = 100  # Cap limit to prevent abuse

        # Call service methods directly - let exceptions bubble up
        products = self.tag_service.get_recommended_products(user_id, limit)
        product_list = [
            {
                "id": p.id,
                "name": p.name,
                "product_type": p.product_type,
                "price": p.price,
                "stock_quantity": p.stock_quantity,
            }
            for p in products
        ]

        return RecommendedProductsResponse(user_id=user_id, products=product_list)

    # UTILITY OPERATIONS

    def get_all_tags(self) -> AllTagsResponse:
        # Call service methods directly - let exceptions bubble up
        tags = self.tag_service.get_all_existing_tags()
        return AllTagsResponse(tags=tags)

    def cleanup_unused_tags(self) -> CleanupResponse:
        # Call service methods directly - let exceptions bubble up
        removed_count = self.tag_service.cleanup_unused_tags()
        return CleanupResponse(
            message=f"Successfully removed {removed_count} unused tags",
            removed_count=removed_count,
        )
