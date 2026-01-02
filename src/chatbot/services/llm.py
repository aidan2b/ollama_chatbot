"""LLM service module for handling Ollama interactions."""

from __future__ import annotations

import logging
from collections.abc import Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from chatbot.cache import cache
from chatbot.config import ModelConfig, ollama_config

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class LLMConnectionError(Exception):
    """Raised when connection to Ollama fails."""


class LLMStreamError(Exception):
    """Raised when streaming response fails."""


class LLMModelError(Exception):
    """Raised when model-related operations fail."""


def check_ollama_connection() -> tuple[bool, str]:
    """Check if Ollama server is reachable.

    Returns:
        Tuple of (is_connected, message).
    """
    try:
        response = httpx.get(f"{ollama_config.base_url}/api/tags", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            model_count = len(data.get("models", []))
            return True, f"Connected to Ollama ({model_count} models available)"
        return False, f"Ollama returned status {response.status_code}"
    except httpx.ConnectError:
        return False, "Cannot connect to Ollama. Is the server running?"
    except httpx.TimeoutException:
        return False, "Connection to Ollama timed out"
    except Exception as e:
        logger.exception("Error checking Ollama connection")
        return False, f"Error connecting to Ollama: {type(e).__name__}"


def get_available_models() -> list[str]:
    """Fetch available models from Ollama API.

    Returns:
        List of available model names.

    Raises:
        LLMConnectionError: If connection to Ollama fails.
        LLMModelError: If there's an error fetching models.
    """
    try:
        response = httpx.get(f"{ollama_config.base_url}/api/tags", timeout=10.0)

        if response.status_code != 200:
            raise LLMModelError(f"Ollama API returned status {response.status_code}")

        data = response.json()
        models = data.get("models", [])

        # Extract model names and filter out any empty or invalid entries
        available_models = []
        for model in models:
            model_name = model.get("name", "")
            if model_name and isinstance(model_name, str):
                available_models.append(model_name)

        return available_models

    except httpx.ConnectError as e:
        logger.error("Cannot connect to Ollama server: %s", e)
        raise LLMConnectionError(
            "Cannot connect to Ollama. Is the server running?"
        ) from e
    except httpx.TimeoutException as e:
        logger.error("Connection to Ollama timed out: %s", e)
        raise LLMConnectionError("Connection to Ollama timed out") from e
    except Exception as e:
        logger.exception("Error fetching available models from Ollama")
        raise LLMModelError(f"Error fetching models: {type(e).__name__}") from e


def refresh_model_config() -> None:
    """Refresh the ModelConfig with available models from Ollama.

    This updates the ModelConfig.AVAILABLE_MODELS list with models
    that are actually available on the Ollama server.
    """
    try:
        available_models = get_available_models()

        if available_models:
            # Update the ModelConfig with available models
            ModelConfig.AVAILABLE_MODELS = available_models
            logger.info(
                "Refreshed model list with %d available models", len(available_models)
            )
        else:
            logger.warning("No models found on Ollama server")

    except LLMConnectionError:
        logger.warning("Could not refresh model list - Ollama connection failed")
    except LLMModelError:
        logger.warning("Could not refresh model list - error fetching models")
    except Exception as e:
        logger.exception("Unexpected error refreshing model list")
        logger.warning("Could not refresh model list: %s", type(e).__name__)


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
        """Get or create the LLM instance with caching."""
        # Try to get cached instance first
        cached_llm = cache.get_llm(self.model_name)
        if cached_llm is not None:
            logger.debug("Using cached LLM instance for model: %s", self.model_name)
            return cached_llm

        # Create new instance if not cached
        if self._llm is None:
            self._llm = self._create_llm()

        # Cache the instance
        cache.set_llm(self.model_name, self._llm)
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
