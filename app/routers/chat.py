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
from app.dtos import (
    ComboProductResponse,
    ProductInfoResponse,
    ComboResponse,
    ProductInfoResponseWithDebug,
)


router = APIRouter(prefix="/chat")


async def get_available_tags() -> list[str]:
    """Get all available tags from the database"""
    session = next(get_db())
    tag_service = TagService(session)
    return tag_service.get_all_existing_tags()


async def get_product(product_names: list[str]) -> ProductInfoResponseWithDebug:
    session = next(get_db())
    products_info = []
    debug_info = {
        "requested_products": product_names,
        "found_products": 0,
        "not_found": [],
    }

    for product_name in product_names:
        product = session.exec(
            select(Product).where(Product.name == product_name)
        ).first()

        if product:
            # Get tags for the product
            tag_service = TagService(session)
            tags = tag_service.get_product_tags(product.id)

            products_info.append(
                ProductInfoResponse(
                    id=product.id,
                    name=product.name,
                    type=product.type,
                    brand=product.brand,
                    price=product.price,
                    stock_quantity=product.stock_quantity,
                    min_stock_level=product.min_stock_level,
                    tags=tags,
                )
            )
        else:
            debug_info["not_found"].append(product_name)

    debug_info["found_products"] = len(products_info)

    return ProductInfoResponseWithDebug(products=products_info, debug_info=debug_info)


async def get_combo(
    brand: str = None,
    tag: str = None,
    product_types: list[str] = None,
    price_filter: str = None,
    max_price: float = None,
) -> ComboResponse:
    session = next(get_db())
    debug_info = {"filters_applied": {}, "products_found": 0, "price_range": None}

    # Build query based on filters
    query = select(Product).where(Product.stock_quantity > 0)

    # Start with all products in stock
    products = list(session.exec(query).all())

    # Apply brand filter if specified
    if brand:
        products = [p for p in products if p.brand.lower() == brand.lower()]
        debug_info["filters_applied"]["brand"] = brand

    # Apply tag filter if specified
    if tag:
        # Get products by tag that are in stock
        tag_service = TagService(session)
        try:
            tag_products = tag_service.get_products_by_tag(tag)
            # Filter for products in stock and that are already in our filtered list
            tag_product_ids = {p.id for p in tag_products}
            products = [p for p in products if p.id in tag_product_ids]
            debug_info["filters_applied"]["tag"] = tag
        except ValueError:
            print(f"Warning: Tag '{tag}' not found in database")
            products = []
            debug_info["filters_applied"]["tag"] = f"{tag} (not found)"

    # Filter by product types if specified
    if product_types:
        products = [
            p
            for p in products
            if p.type.lower() in [pt.lower() for pt in product_types]
        ]
        debug_info["filters_applied"]["product_types"] = product_types

    # Apply price filtering
    if max_price:
        products = [p for p in products if p.price <= max_price]
        debug_info["filters_applied"]["max_price"] = max_price

    if price_filter:
        debug_info["filters_applied"]["price_filter"] = price_filter

        if price_filter == "cheapest":
            # For each product type, get the cheapest option
            if product_types:
                filtered_products = []
                for product_type in product_types:
                    type_products = [
                        p for p in products if p.type.lower() == product_type.lower()
                    ]
                    if type_products:
                        cheapest = min(type_products, key=lambda x: x.price)
                        filtered_products.append(cheapest)
                products = filtered_products
            else:
                # Get the cheapest product overall
                if products:
                    products = [min(products, key=lambda x: x.price)]

        elif price_filter == "most_expensive":
            # For each product type, get the most expensive option
            if product_types:
                filtered_products = []
                for product_type in product_types:
                    type_products = [
                        p for p in products if p.type.lower() == product_type.lower()
                    ]
                    if type_products:
                        most_expensive = max(type_products, key=lambda x: x.price)
                        filtered_products.append(most_expensive)
                products = filtered_products
            else:
                # Get the most expensive product overall
                if products:
                    products = [max(products, key=lambda x: x.price)]

        elif price_filter == "budget":
            # Get products under $100 (or adjust as needed)
            products = [p for p in products if p.price <= 100]

        elif price_filter == "premium":
            # Get products over $200 (or adjust as needed)
            products = [p for p in products if p.price >= 200]

    # Update debug info
    debug_info["products_found"] = len(products)
    if products:
        prices = [p.price for p in products]
        debug_info["price_range"] = {
            "min": min(prices),
            "max": max(prices),
            "total": sum(prices),
        }

    # Convert to response format
    combo_products = [
        ComboProductResponse(
            name=product.name,
            price=product.price,
            type=product.type,
            brand=product.brand,
        )
        for product in products
    ]

    total_price = sum(p.price for p in combo_products)

    return ComboResponse(
        products=combo_products, total_price=total_price, debug_info=debug_info
    )


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
            if isinstance(node.output, ProductInfoResponseWithDebug):
                # Products selected (InfoIntention) - display all info
                for i, product in enumerate(node.output.products):
                    print(f"Product {i + 1} Information:")
                    print(f"  ID: {product.id}")
                    print(f"  Name: {product.name}")
                    print(f"  Type: {product.type}")
                    print(f"  Brand: {product.brand}")
                    print(f"  Price: ${product.price:.2f}")
                    print(f"  Stock Quantity: {product.stock_quantity}")
                    print(f"  Min Stock Level: {product.min_stock_level}")
                    print(f"  Tags: {', '.join(product.tags)}")

                    # Stock status
                    if product.stock_quantity == 0:
                        print("  Status: Out of Stock")
                    elif product.stock_quantity < product.min_stock_level:
                        print("  Status: Low Stock")
                    else:
                        print("  Status: In Stock")
                    print()  # Add spacing between products

                # Debug output
                print("🔍 Debug Info:")
                print(
                    f"  Requested products: {node.output.debug_info.get('requested_products', [])}"
                )
                print(
                    f"  Found products: {node.output.debug_info.get('found_products', 0)}"
                )
                if node.output.debug_info.get("not_found"):
                    print(f"  Not found: {node.output.debug_info['not_found']}")
                print()

            elif isinstance(node.output, ComboResponse):
                # Combo products selected (ComboIntention)
                if node.output.products:  # Check if list is not empty
                    print(f"Selected Combo ({len(node.output.products)} items):")
                    print(f"Total Price: ${node.output.total_price:.2f}")
                    print()
                    for product in node.output.products:
                        print(
                            f"  - {product.name} | Price: ${product.price:.2f} | Type: {product.type} | Brand: {product.brand}"
                        )

                    # Debug output
                    print("\n🔍 Debug Info:")
                    print(
                        f"  Filters applied: {node.output.debug_info.get('filters_applied', {})}"
                    )
                    print(
                        f"  Products found: {node.output.debug_info.get('products_found', 0)}"
                    )
                    if node.output.debug_info.get("price_range"):
                        price_range = node.output.debug_info["price_range"]
                        print(
                            f"  Price range: ${price_range['min']:.2f} - ${price_range['max']:.2f}"
                        )
                else:
                    print("No products found matching the criteria.")
                    # Provide helpful feedback about available tags
                    available_tags = await get_available_tags()
                    print(f"Available tags: {', '.join(available_tags)}")
            else:
                print(f"Node output: {node.output}")

    # Check if product names were completed by LLM
    for node in nodes:
        if (
            hasattr(node, "output")
            and node.output
            and hasattr(node.output, "intention")
        ):
            if isinstance(node.output.intention, InfoIntention):
                if node.output.intention.completed_product_names:
                    for i, (original, completed) in enumerate(
                        zip(
                            node.output.intention.product_names,
                            node.output.intention.completed_product_names,
                        )
                    ):
                        if original != completed:
                            print(f"\nNote: Completed '{original}' to '{completed}'")


@router.get("/tags")
async def get_tags():
    """Get all available tags for debugging and validation"""
    return {"available_tags": await get_available_tags()}
