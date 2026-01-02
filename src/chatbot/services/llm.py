"""LLM service module for handling Ollama interactions."""

from __future__ import annotations

import logging
from collections.abc import Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from chatbot.config import ModelConfig, ollama_config

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class LLMConnectionError(Exception):
    """Raised when connection to Ollama fails."""


class LLMStreamError(Exception):
    """Raised when streaming response fails."""


@dataclass
class StreamResponse:
    """Response from streaming LLM."""

    content: str
    thinking: str
    is_complete: bool = False


class LLMService:
    """Service for interacting with Ollama LLMs."""

    def __init__(self, model_name: str) -> None:
        """Initialize the LLM service.

        Args:
            model_name: Name of the model to use.
        """
        self.model_name = model_name
        self._llm: ChatOllama | None = None

    @property
    def llm(self) -> ChatOllama:
        """Get or create the LLM instance."""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm

    def _create_llm(self) -> ChatOllama:
        """Create a ChatOllama instance."""
        try:
            return ChatOllama(
                model=self.model_name,
                base_url=ollama_config.base_url,
                timeout=ollama_config.timeout,
            )
        except Exception as e:
            logger.exception("Failed to create LLM instance")
            raise LLMConnectionError(f"Failed to connect to Ollama: {e}") from e

    @property
    def supports_reasoning(self) -> bool:
        """Check if current model supports reasoning."""
        return ModelConfig.supports_reasoning(self.model_name)

    def stream_response(
        self,
        messages: list[BaseMessage],
    ) -> Generator[StreamResponse, None, None]:
        """Stream a response from the LLM.

        Args:
            messages: List of messages to send.

        Yields:
            StreamResponse objects with accumulated content and thinking.
        """
        content = ""
        thinking = ""

        try:
            for chunk in self.llm.stream(messages, reasoning=self.supports_reasoning):
                if chunk.additional_kwargs.get("reasoning_content"):
                    thinking += chunk.additional_kwargs["reasoning_content"]
                content += chunk.content

                yield StreamResponse(content=content, thinking=thinking)

            yield StreamResponse(content=content, thinking=thinking, is_complete=True)

        except Exception as e:
            logger.exception("Error streaming response")
            raise LLMStreamError(f"Failed to stream response: {e}") from e


def build_messages(
    history: list[dict[str, str]],
    current_message: str,
    system_prompt: str | None = None,
) -> list[BaseMessage]:
    """Build LangChain messages from chat history.

    Args:
        history: List of message dictionaries with 'role' and 'content' keys.
        current_message: The current user message.
        system_prompt: Optional system prompt.

    Returns:
        List of LangChain message objects.
    """
    messages: list[BaseMessage] = []

    if system_prompt and system_prompt.strip():
        messages.append(SystemMessage(content=system_prompt.strip()))

    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=current_message))

    return messages
