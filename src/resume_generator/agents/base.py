from abc import ABC, abstractmethod
from os import getenv
from typing import Any

from langchain.schema import HumanMessage, SystemMessage
from langchain_core.language_models import BaseLLM
from pydantic import SecretStr

from resume_generator.observability import get_langfuse_callback


class BaseAgent(ABC):
    def __init__(self, llm: BaseLLM | None = None):
        if llm:
            self.llm = llm
            return
        api_key = getenv("OPENAI_API_KEY")
        ollama_model = getenv("OLLAMA_MODEL")

        callbacks = []
        langfuse_callback = get_langfuse_callback()
        if langfuse_callback:
            callbacks.append(langfuse_callback)

        if api_key:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=getenv("OPENAI_MODEL", "openai/gpt-5-mini"),
                api_key=SecretStr(api_key),
                base_url=getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"),
                callbacks=callbacks,
            )
        elif ollama_model:
            from langchain_ollama.llms import OllamaLLM

            reason = getenv("OLLAMA_REASONING", "n").lower() in ["y", "yes", "true", "1"]
            self.llm = OllamaLLM(model=ollama_model, callbacks=callbacks, reasoning=reason)
        else:
            raise ValueError("No valid LLM configuration found. Please set OPENAI_API_KEY or OLLAMA_MODEL.")

    def create_prompt(self, system_message: str, user_message: str) -> list:
        return [
            SystemMessage(content=system_message),
            HumanMessage(content=user_message),
        ]

    @abstractmethod
    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        pass
