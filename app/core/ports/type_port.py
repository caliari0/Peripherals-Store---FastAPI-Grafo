from typing import TypeVar, Type, Any, Callable, Dict, Optional
from pydantic import BaseModel

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=BaseModel)


class TypePort:
    """Port interface for type validation and conversion operations."""
    
    def validate_type(self, value: Any, expected_type: Type[T]) -> bool:
        """Validate if a value matches the expected type."""
        raise NotImplementedError
    
    def convert_type(self, value: Any, target_type: Type[T]) -> T:
        """Convert a value to the target type."""
        raise NotImplementedError
    
    def register_type_function(self, type_name: str, validator: Callable, converter: Callable) -> None:
        """Register custom type functions."""
        raise NotImplementedError
    
    def get_type_function(self, type_name: str) -> tuple[Callable, Callable]:
        """Get registered type functions."""
        raise NotImplementedError
    
    def validate_model(self, data: Dict[str, Any], model_class: Type[ModelType]) -> ModelType:
        """Validate and create a Pydantic model instance."""
        raise NotImplementedError
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input."""
        raise NotImplementedError
    
    def validate_price(self, value: float) -> bool:
        """Validate price values."""
        raise NotImplementedError
    
    def validate_quantity(self, value: int) -> bool:
        """Validate quantity values."""
        raise NotImplementedError
    
    def validate_product_name(self, value: str) -> bool:
        """Validate product name format."""
        raise NotImplementedError 