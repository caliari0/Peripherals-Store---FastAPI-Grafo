from sqlmodel import Session, select
from app.models import Tag, Product, ProductTag, User, UserFavoriteTag


class TagService:
    def __init__(self, session: Session):
        self.session = session

    # Helper: gets or creates tag by name
    def _get_tag(self, name: str) -> Tag:
        tag = self.session.exec(select(Tag).where(Tag.name == name)).first()
        if not tag:
            raise ValueError(f"Tag with name {name} not found")
        return tag

    def _create_tag(self, name: str) -> Tag:
        tag = Tag(name=name)
        self.session.add(tag)
        self.session.flush()
        return tag

    # PRODUCT TAG OPERATIONS

    # adds tags to a product (creates tags if they don't exist)
    def add_tags_to_product(self, product_id: int, tag_names: list[str]) -> list[str]:
        product = self.session.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        added_tags = []
        for tag_name in tag_names:
            tag = self._get_tag(tag_name)
            if not tag:
                tag = self._create_tag(tag_name)

            # check if product already has this tag
            existing = next(
                (pt for pt in product.tags if pt.tag_id == tag.id), None
            )  #! TODO generator > SÓ PODE ITERAR UMA VEZ, NÃO PRECISA DE LISTA

            if not existing:
                product_tag = ProductTag(product_id=product_id, tag_id=tag.id)
                self.session.add(product_tag)
                added_tags.append(tag_name)

        self.session.commit()
        return added_tags

    # removes tags from a product
    def remove_tags_from_product(self, product_id: int, tag_names: list[str]) -> int:
        removed_count = 0
        for tag_name in tag_names:
            tag = self.session.exec(select(Tag).where(Tag.name == tag_name)).first()
            if tag:
                product_tag = self.session.exec(
                    select(ProductTag).where(
                        ProductTag.product_id == product_id, ProductTag.tag_id == tag.id
                    )
                ).first()

                if product_tag:
                    self.session.delete(product_tag)
                    removed_count += 1

        self.session.commit()
        return removed_count

    # gets all tags for a product
    def get_product_tags(self, product_id: int) -> list[str]:
        # Fix: Get full Tag objects and extract names
        statement = (
            select(Tag).join(ProductTag).where(ProductTag.product_id == product_id)
        )
        tags = self.session.exec(statement).all()
        return [tag.name for tag in tags]

    # gets all products with a specific tag
    def get_products_by_tag(self, tag_name: str) -> list[Product]:
        statement = (
            select(Product).join(ProductTag).join(Tag).where(Tag.name == tag_name)
        )
        return list(self.session.exec(statement))

    # USER FAVORITE TAG OPERATIONS

    # adds a favorite tag for a user (creates tag if it doesn't exist)
    def add_favorite_tag(self, user_id: int, tag_name: str) -> str:
        user = self.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        tag = self._get_or_create_tag(tag_name)

        # check if user already has this favorite tag
        existing = self.session.exec(
            select(UserFavoriteTag).where(
                UserFavoriteTag.user_id == user_id, UserFavoriteTag.tag_id == tag.id
            )
        ).first()

        if existing:
            raise ValueError(f"User already has '{tag_name}' as a favorite tag")

        favorite_tag = UserFavoriteTag(user_id=user_id, tag_id=tag.id)
        self.session.add(favorite_tag)
        self.session.commit()
        return tag_name

    # removes a favorite tag for a user
    def remove_favorite_tag(self, user_id: int, tag_name: str) -> bool:
        tag = self.session.exec(select(Tag).where(Tag.name == tag_name)).first()
        if not tag:
            return False

        favorite_tag = self.session.exec(
            select(UserFavoriteTag).where(
                UserFavoriteTag.user_id == user_id, UserFavoriteTag.tag_id == tag.id
            )
        ).first()

        if not favorite_tag:
            return False

        self.session.delete(favorite_tag)
        self.session.commit()
        return True

    # gets all favorite tags for a user
    def get_user_favorite_tags(self, user_id: int) -> list[str]:
        # Fix: Get full Tag objects and extract names
        statement = (
            select(Tag).join(UserFavoriteTag).where(UserFavoriteTag.user_id == user_id)
        )
        tags = self.session.exec(statement).all()
        return [tag.name for tag in tags]

    # gets products recommended for a user based on their favorite tags
    def get_recommended_products(self, user_id: int, limit: int = 10) -> list[Product]:
        favorite_tags = self.get_user_favorite_tags(user_id)
        if not favorite_tags:
            return []

        # get products that have any of the user's favorite tags
        statement = (
            select(Product)
            .join(ProductTag)
            .join(Tag)
            .where(Tag.name.in_(favorite_tags))
            .distinct()
            .limit(limit)
        )
        return list(self.session.exec(statement))

    # UTILITY OPERATIONS

    # gets all tags that exist (used by products or users)
    def get_all_existing_tags(self) -> list[str]:
        # Fix: Get all tags and extract their names
        tags = self.session.exec(select(Tag).order_by(Tag.name)).all()
        return [tag.name for tag in tags]

    # removes unused tags (tags not used by any products or users)
    def cleanup_unused_tags(self) -> int:
        # find tags that are not used by any products or users
        used_tag_ids = set()

        # get tags used by products
        product_tag_ids = self.session.exec(select(ProductTag.tag_id)).all()
        used_tag_ids.update(product_tag_ids)

        # get tags used by users
        user_tag_ids = self.session.exec(select(UserFavoriteTag.tag_id)).all()
        used_tag_ids.update(user_tag_ids)

        # delete unused tags
        unused_tags = self.session.exec(
            select(Tag).where(Tag.id.not_in(used_tag_ids))
        ).all()

        for tag in unused_tags:
            self.session.delete(tag)

        self.session.commit()
        return len(unused_tags)
