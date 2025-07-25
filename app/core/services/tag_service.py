from sqlmodel import Session, select
from app.models import Tag, Product, ProductTag


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

    # UTILITY OPERATIONS

    # gets all tags that exist (used by products or users)
    def get_all_existing_tags(self) -> list[str]:
        # Fix: Get all tags and extract their names
        tags = self.session.exec(select(Tag).order_by(Tag.name)).all()
        return [tag.name for tag in tags]

    # removes unused tags (tags not used by any products)
    def cleanup_unused_tags(self) -> int:
        # find tags that are not used by any products
        used_tag_ids = set()

        # get tags used by products
        product_tag_ids = self.session.exec(select(ProductTag.tag_id)).all()
        used_tag_ids.update(product_tag_ids)

        # delete unused tags
        unused_tags = self.session.exec(
            select(Tag).where(Tag.id.not_in(used_tag_ids))
        ).all()

        for tag in unused_tags:
            self.session.delete(tag)

        self.session.commit()
        return len(unused_tags)
