from fastapi import APIRouter, Depends
from app.core.factories import get_llm_adapter, get_formatter_adapter
from app.core.workflows.intention import IntentionWorkflow
from app.database import get_db
from app.models import Product
from sqlmodel import select
from app.adapters.instructor_adapter import InstructorAdapter
from app.adapters.jinja2_adapter import Jinja2Adapter
from app.core.services.tag_service import TagService
from app.core.workflows.intention_models import InfoIntention
from app.dtos import ComboProductResponse, ProductInfoResponse


router = APIRouter(prefix="/chat")


async def get_available_tags() -> list[str]:
    """Get all available tags from the database"""
    session = next(get_db())
    tag_service = TagService(session)
    return tag_service.get_all_existing_tags()


async def get_product(product_name: str) -> ProductInfoResponse:
    session = next(get_db())
    product = session.exec(select(Product).where(Product.name == product_name)).first()

    if product:
        # Get tags for the product
        tag_service = TagService(session)
        tags = tag_service.get_product_tags(product.id)

        return ProductInfoResponse(
            id=product.id,
            name=product.name,
            type=product.type,
            brand=product.brand,
            price=product.price,
            stock_quantity=product.stock_quantity,
            min_stock_level=product.min_stock_level,
            tags=tags,
        )
    return None


async def get_combo(brand: str = None, tag: str = None) -> list[ComboProductResponse]:
    session = next(get_db())

    if brand:
        # Get products by brand that are in stock
        products = list(
            session.exec(
                select(Product).where(
                    Product.brand == brand, Product.stock_quantity > 0
                )
            ).all()
        )
    elif tag:
        # Get products by tag that are in stock
        tag_service = TagService(session)
        try:
            all_products = tag_service.get_products_by_tag(tag)
            # Filter for products in stock
            products = [p for p in all_products if p.stock_quantity > 0]
        except ValueError:
            # Tag doesn't exist, return empty list
            print(f"Warning: Tag '{tag}' not found in database")
            products = []
    else:
        products = []

    # Return only name, price, and type
    return [
        ComboProductResponse(name=product.name, price=product.price, type=product.type)
        for product in products
    ]


@router.post("/")
async def chat(
    message: str,
    llm_adapter: InstructorAdapter = Depends(get_llm_adapter),
    formatter_adapter: Jinja2Adapter = Depends(get_formatter_adapter),
):
    intention_workflow = IntentionWorkflow(llm_adapter, formatter_adapter)
    nodes = await intention_workflow.run(message, get_product, get_combo)

    for node in nodes:
        if node.output is not None:
            if isinstance(node.output, ProductInfoResponse):
                # Single product selected (InfoIntention) - display all info
                print("Product Information:")
                print(f"  ID: {node.output.id}")
                print(f"  Name: {node.output.name}")
                print(f"  Type: {node.output.type}")
                print(f"  Brand: {node.output.brand}")
                print(f"  Price: ${node.output.price:.2f}")
                print(f"  Stock Quantity: {node.output.stock_quantity}")
                print(f"  Min Stock Level: {node.output.min_stock_level}")
                print(f"  Tags: {', '.join(node.output.tags)}")

                # Stock status
                if node.output.stock_quantity == 0:
                    print("  Status: Out of Stock")
                elif node.output.stock_quantity < node.output.min_stock_level:
                    print("  Status: Low Stock")
                else:
                    print("  Status: In Stock")

            elif isinstance(node.output, list):
                # Multiple products selected (ComboIntention)
                if node.output:  # Check if list is not empty
                    print(f"Selected Products ({len(node.output)} items):")
                    for product in node.output:
                        print(
                            f"  - {product.name} | Price: ${product.price:.2f} | Type: {product.type}"
                        )
                else:
                    print("No products found matching the criteria.")
                    # Provide helpful feedback about available tags
                    available_tags = await get_available_tags()
                    print(f"Available tags: {', '.join(available_tags)}")
            else:
                print(f"Node output: {node.output}")

    # Check if product name was completed by LLM
    for node in nodes:
        if (
            hasattr(node, "output")
            and node.output
            and hasattr(node.output, "intention")
        ):
            if isinstance(node.output.intention, InfoIntention):
                if (
                    node.output.intention.completed_product_name
                    and node.output.intention.completed_product_name
                    != node.output.intention.product_name
                ):
                    print(
                        f"\nNote: Completed '{node.output.intention.product_name}' to '{node.output.intention.completed_product_name}'"
                    )


@router.get("/tags")
async def get_tags():
    """Get all available tags for debugging and validation"""
    return {"available_tags": await get_available_tags()}
