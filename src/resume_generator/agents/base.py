from abc import ABC, abstractmethod
from os import getenv
from typing import Any

from langchain.schema import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


class BaseAgent(ABC):
    def __init__(self, llm: BaseLLM | None = None):
        if llm:
            self.llm = llm
            return
        api_key = getenv("OPENAI_API_KEY")

        if api_key is None:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it to use the OpenAI API.")

        self.llm = ChatOpenAI(
            model=getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=SecretStr(api_key),
            base_url=getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        )

    def create_prompt(self, system_message: str, user_message: str) -> list:
        return [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

    @abstractmethod
    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        pass
