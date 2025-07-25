from pydantic import BaseModel
from typing import Union, Optional


class InfoIntention(BaseModel):
    """
    Use this when requesting information about products by name.
    The LLM should complete incomplete product names based on available products.
    Supports both single and multiple product requests.
    """

    product_names: list[str]
    completed_product_names: Optional[list[str]] = None


class ComboIntention(BaseModel):
    """
    Use this when the user wants to buy a combo of products by tag, brand, or product types.
    Supports price filtering and multiple product type requests.
    """

    tag: Optional[str] = None
    brand: Optional[str] = None
    product_types: Optional[list[str]] = None
    price_filter: Optional[str] = (
        None  # "cheapest", "most_expensive", "budget", "premium"
    )
    max_price: Optional[float] = None


class UserIntention(BaseModel):
    intention: Union[InfoIntention, ComboIntention]
