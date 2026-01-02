"""Chat handler for the Gradio UI."""

from __future__ import annotations

import logging
from collections.abc import Generator

from chatbot.config import ModelConfig, ui_config
from chatbot.services.llm import (
    LLMConnectionError,
    LLMModelError,
    LLMService,
    LLMStreamError,
    build_messages,
)
from chatbot.ui.components import (
    format_error_message,
    format_response_with_thinking,
    get_loading_indicator,
)

logger = logging.getLogger(__name__)

# Maximum length for system prompts (characters)
MAX_SYSTEM_PROMPT_LENGTH = 5000


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent potential security issues.

    Args:
        text: Input text to sanitize.

    Returns:
        Sanitized text.
    """
    if not text:
        return text

    # Basic sanitization - remove potentially harmful content
    # while preserving most formatting and content

    # Remove script tags and other potentially dangerous HTML
    sanitized = text.replace("<script", "&lt;script")
    sanitized = sanitized.replace("</script", "&lt;/script")

    # Remove excessive whitespace and control characters
    sanitized = " ".join(sanitized.split())

    # Limit maximum length to prevent DoS attacks
    max_length = 20000  # Higher than UI limits for safety
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning("Input truncated due to excessive length")

    return sanitized


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

    # Input sanitization
    message = sanitize_input(message)
    if system_prompt:
        system_prompt = sanitize_input(system_prompt)

    # Validate message length
    if len(message) > ui_config.max_message_length:
        error_msg = format_error_message(
            f"Message too long. Maximum {ui_config.max_message_length:,} characters allowed."
        )
        yield [*history, {"role": "assistant", "content": error_msg}]
        return

    # Validate system prompt length
    if system_prompt and len(system_prompt) > ui_config.max_system_prompt_length:
        error_msg = format_error_message(
            f"System prompt too long. Maximum {ui_config.max_system_prompt_length:,} characters allowed."
        )
        yield [*history, {"role": "assistant", "content": error_msg}]
        return

    new_history = [*history, {"role": "user", "content": message}]

    # Show loading indicator immediately
    loading_history = [
        *new_history,
        {"role": "assistant", "content": get_loading_indicator()},
    ]
    yield loading_history

    try:
        llm_service = LLMService(model_name)
        messages = build_messages(history, message, system_prompt)

        for response in llm_service.stream_response(messages):
            display_content = format_response_with_thinking(
                response.content,
                response.thinking if response.thinking else None,
            )
            yield [*new_history, {"role": "assistant", "content": display_content}]

    except LLMConnectionError:
        logger.exception("Connection error")
        error_msg = format_error_message(
            "Could not connect to Ollama. Please ensure the Ollama server is running."
        )
        yield [*new_history, {"role": "assistant", "content": error_msg}]

    except LLMStreamError as e:
        logger.exception("Streaming error: %s", e)
        error_msg = format_error_message(
            f"Streaming error: {str(e)}. Please try again."
        )
        yield [*new_history, {"role": "assistant", "content": error_msg}]

    except LLMModelError as e:
        logger.exception("Model error: %s", e)
        error_msg = format_error_message(
            f"Model error: {str(e)}. The selected model may not be available."
        )
        yield [*new_history, {"role": "assistant", "content": error_msg}]

    except Exception as e:
        logger.exception("Unexpected error in chat: %s", e)
        error_msg = format_error_message(
            f"Unexpected error: {type(e).__name__}. Please try again."
        )
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

    # Check if model is in the available models list
    is_available = model_name in ModelConfig.AVAILABLE_MODELS
    availability_badge = " | Available" if is_available else " | Not Available"

    return f"**{model_name}**{reasoning_badge}{availability_badge}"


def get_model_details(model_name: str) -> dict[str, str]:
    """Get detailed information about a model.

    Args:
        model_name: The name of the model.

    Returns:
        Dictionary with model details.
    """
    return {
        "name": model_name,
        "supports_reasoning": str(ModelConfig.supports_reasoning(model_name)),
        "is_available": str(model_name in ModelConfig.AVAILABLE_MODELS),
        "description": "Local LLM model running on Ollama",
    }
