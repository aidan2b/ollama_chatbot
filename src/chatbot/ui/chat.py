"""Chat handler for the Gradio UI."""

from __future__ import annotations

import logging
from collections.abc import Generator

from chatbot.config import ModelConfig
from chatbot.services.llm import (
    LLMConnectionError,
    LLMService,
    LLMStreamError,
    build_messages,
)
from chatbot.ui.components import format_error_message, format_response_with_thinking

logger = logging.getLogger(__name__)


def chat(
    message: str,
    history: list[dict[str, str]],
    model_name: str,
    system_prompt: str,
) -> Generator[list[dict[str, str]], None, None]:
    """Process a chat message and stream the response.

    Args:
        message: The user's message.
        history: The chat history.
        model_name: The name of the model to use.
        system_prompt: Optional system prompt.

    Yields:
        Updated chat history with streaming response.
    """
    if not message or not message.strip():
        yield history
        return

    message = message.strip()

    new_history = [*history, {"role": "user", "content": message}]

    try:
        llm_service = LLMService(model_name)
        messages = build_messages(history, message, system_prompt)

        for response in llm_service.stream_response(messages):
            display_content = format_response_with_thinking(
                response.content,
                response.thinking if response.thinking else None,
            )
            yield [*new_history, {"role": "assistant", "content": display_content}]

    except LLMConnectionError as e:
        logger.exception("Connection error")
        error_msg = format_error_message(
            f"Could not connect to Ollama. Please ensure the Ollama server is running. Details: {e}"
        )
        yield [*new_history, {"role": "assistant", "content": error_msg}]

    except LLMStreamError as e:
        logger.exception("Streaming error")
        error_msg = format_error_message(
            f"An error occurred while generating the response. Details: {e}"
        )
        yield [*new_history, {"role": "assistant", "content": error_msg}]

    except Exception as e:
        logger.exception("Unexpected error in chat")
        error_msg = format_error_message(f"An unexpected error occurred. Details: {e}")
        yield [*new_history, {"role": "assistant", "content": error_msg}]


def clear_chat() -> tuple[list, str]:
    """Clear the chat history.

    Returns:
        Empty history and empty message input.
    """
    return [], ""


def get_model_info(model_name: str) -> str:
    """Get information about the selected model.

    Args:
        model_name: The name of the model.

    Returns:
        Model information string.
    """
    supports_reasoning = ModelConfig.supports_reasoning(model_name)
    reasoning_badge = " | Reasoning" if supports_reasoning else ""
    return f"**{model_name}**{reasoning_badge}"
