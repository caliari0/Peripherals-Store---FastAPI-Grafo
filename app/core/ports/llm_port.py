from abc import ABC, abstractmethod

from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# classe abstrata pra portas LLM
class LLMPort(ABC):
    @abstractmethod
    async def asend(
        self,
        messages: list[dict[str, str]],
        response_model: Type[T],
    ) -> T:
        """
        Envia uma mensagem para o LLM assincronamente e retorna uma resposta estruturada.
        """
        pass
