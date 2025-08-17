from abc import ABC, abstractmethod
from os import getenv
from typing import Any, Dict, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLLM


class BaseAgent(ABC):
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm or ChatOpenAI(
            model=getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=getenv("OPENAI_API_KEY"),
            base_url=getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
        )

    def create_prompt(self, system_message: str, user_message: str) -> list:
        return [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass
