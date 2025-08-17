from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLLM
from langchain.schema import HumanMessage, SystemMessage
from typing import Any, Dict, Optional
import os


class BaseAgent(ABC):
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm or self._get_default_llm()

    def _get_default_llm(self) -> BaseLLM:
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        except ImportError:
            raise ImportError(
                "Please install langchain-openai: uv add langchain-openai"
            )

    def create_prompt(self, system_message: str, user_message: str) -> list:
        return [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass
