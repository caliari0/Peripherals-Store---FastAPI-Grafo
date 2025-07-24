from typing import TypeVar, Type, Any, Callable, Dict, Optional
from pydantic import BaseModel, ValidationError
import re
from app.core.ports.type_port import TypePort

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=BaseModel)


class TypeAdapter(TypePort):
    """Concrete implementation of TypePort with e-commerce specific type functions."""
    
    def __init__(self):
        self._type_functions: Dict[str, tuple[Callable, Callable]] = {}
        self._register_default_functions()
    
    def _register_default_functions(self):
        """Register default type functions for common e-commerce types."""
        # Price validation and conversion
        self.register_type_function(
            "price",
            self._validate_price,
            self._convert_price
        )
        
        # Quantity validation and conversion
        self.register_type_function(
            "quantity", 
            self._validate_quantity,
            self._convert_quantity
        )
        
        # Product name validation and conversion
        self.register_type_function(
            "product_name",
            self._validate_product_name,
            self._convert_product_name
        )
        
        # Email validation and conversion
        self.register_type_function(
            "email",
            self._validate_email,
            self._convert_email
        )
    
    def validate_type(self, value: Any, expected_type: Type[T]) -> bool:
        """Validate if a value matches the expected type."""
        try:
            if expected_type == str:
                return isinstance(value, str)
            elif expected_type == int:
                return isinstance(value, int) or (isinstance(value, str) and value.isdigit())
            elif expected_type == float:
                return isinstance(value, float) or (isinstance(value, str) and self._is_float(value))
            elif expected_type == bool:
                return isinstance(value, bool) or value in ['true', 'false', '1', '0', True, False]
            else:
                return isinstance(value, expected_type)
        except Exception:
            return False
    
    def convert_type(self, value: Any, target_type: Type[T]) -> T:
        """Convert a value to the target type."""
        try:
            if target_type == str:
                return str(value)
            elif target_type == int:
                return int(value)
            elif target_type == float:
                return float(value)
            elif target_type == bool:
                if isinstance(value, str):
                    return value.lower() in ['true', '1']
                return bool(value)
            else:
                return target_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot convert {value} to {target_type.__name__}: {str(e)}")
    
    def register_type_function(self, type_name: str, validator: Callable, converter: Callable) -> None:
        """Register custom type functions."""
        self._type_functions[type_name] = (validator, converter)
    
    def get_type_function(self, type_name: str) -> tuple[Callable, Callable]:
        """Get registered type functions."""
        if type_name not in self._type_functions:
            raise ValueError(f"Type function '{type_name}' not registered")
        return self._type_functions[type_name]
    
    def validate_model(self, data: Dict[str, Any], model_class: Type[ModelType]) -> ModelType:
        """Validate and create a Pydantic model instance."""
        try:
            return model_class(**data)
        except ValidationError as e:
            raise ValueError(f"Model validation failed: {str(e)}")
    
    def sanitize_string(self, value: str, max_length: Optional[int] = None) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove leading/trailing whitespace
        sanitized = value.strip()
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Apply max length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def validate_price(self, value: float) -> bool:
        """Validate price values."""
        return isinstance(value, (int, float)) and value >= 0 and value <= 999999.99
    
    def validate_quantity(self, value: int) -> bool:
        """Validate quantity values."""
        return isinstance(value, int) and value >= 0 and value <= 999999
    
    def validate_product_name(self, value: str) -> bool:
        """Validate product name format."""
        if not isinstance(value, str):
            return False
        
        sanitized = self.sanitize_string(value)
        return (
            len(sanitized) >= 1 and 
            len(sanitized) <= 100 and
            re.match(r'^[a-zA-Z0-9\s\-_\.]+$', sanitized) is not None
        )
    
    # Private helper methods for default type functions
    def _validate_price(self, value: Any) -> bool:
        """Internal price validator."""
        return self.validate_price(value)
    
    def _convert_price(self, value: Any) -> float:
        """Internal price converter."""
        converted = self.convert_type(value, float)
        if not self.validate_price(converted):
            raise ValueError(f"Invalid price value: {value}")
        return round(converted, 2)
    
    def _validate_quantity(self, value: Any) -> bool:
        """Internal quantity validator."""
        return self.validate_quantity(value)
    
    def _convert_quantity(self, value: Any) -> int:
        """Internal quantity converter."""
        converted = self.convert_type(value, int)
        if not self.validate_quantity(converted):
            raise ValueError(f"Invalid quantity value: {value}")
        return converted
    
    def _validate_product_name(self, value: Any) -> bool:
        """Internal product name validator."""
        return self.validate_product_name(value)
    
    def _convert_product_name(self, value: Any) -> str:
        """Internal product name converter."""
        converted = self.convert_type(value, str)
        sanitized = self.sanitize_string(converted, 100)
        if not self.validate_product_name(sanitized):
            raise ValueError(f"Invalid product name: {value}")
        return sanitized
    
    def _validate_email(self, value: Any) -> bool:
        """Internal email validator."""
        if not isinstance(value, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, value) is not None
    
    def _convert_email(self, value: Any) -> str:
        """Internal email converter."""
        converted = self.convert_type(value, str)
        sanitized = self.sanitize_string(converted, 255).lower()
        if not self._validate_email(sanitized):
            raise ValueError(f"Invalid email format: {value}")
        return sanitized
    
    def _is_float(self, value: str) -> bool:
        """Check if a string can be converted to float."""
        try:
            float(value)
            return True
        except ValueError:
            return False 