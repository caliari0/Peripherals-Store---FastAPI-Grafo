from pydantic import BaseModel
from typing import Union, Optional


class InfoIntention(BaseModel):
    """
    Use this when requesting information about a product by name.
    The LLM should complete incomplete product names based on available products.
    """

    product_name: str
    completed_product_name: Optional[str] = None


class ComboIntention(BaseModel):
    """
    Use this when the user wants to buy a combo of products by tag.
    """

    tag: str


class UserIntention(BaseModel):
    intention: Union[InfoIntention, ComboIntention]
