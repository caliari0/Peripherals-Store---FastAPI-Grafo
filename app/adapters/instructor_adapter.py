from typing import Type, TypeVar

import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel, SecretStr

from app.core.ports.llm_port import LLMPort

T = TypeVar("T", bound=BaseModel)


class InstructorAdapter(LLMPort):
    """
    Instructor implementation of the LLM port.
    """

    def __init__(self, model: str | None = None):
        # Use Ollama with qwen2.5:3b by default
        self.model = model or "qwen2.5:3b"
        self.base_url = "http://localhost:11434/v1"  # Ollama API endpoint
        self.api_key = SecretStr("ollama")  # Ollama doesn't require a real API key

        openai_client = AsyncOpenAI(
            api_key=self.api_key.get_secret_value(),
            base_url=self.base_url,
        )
        self.client = instructor.from_openai(
            client=openai_client, model=instructor.Mode.JSON
        )

    async def asend(
        self,
        messages: list[dict[str, str]],
        response_model: Type[T],
    ) -> T:
        """
        Sends a message to the LLM asynchronously and returns a structured response.
        """
        model_args = dict(
            model=self.model,
            messages=messages,
            response_model=response_model,
        )

        return await self.client.chat.completions.create(**model_args)  # type: ignore
