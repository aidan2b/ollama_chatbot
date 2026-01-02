"""Reusable UI components for the chatbot."""

from __future__ import annotations


def get_loading_indicator() -> str:
    """Get HTML for a loading indicator.

    Returns:
        HTML string for loading indicator.
    """
    return """
    <div class="loading-indicator">
        <div class="loading-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
        <span class="loading-text">Thinking...</span>
    </div>
    <style>
    .loading-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem;
        color: #6b7280;
    }

    .loading-dots {
        display: flex;
        gap: 0.25rem;
    }

    .loading-dots span {
        width: 0.5rem;
        height: 0.5rem;
        background-color: #6b7280;
        border-radius: 50%;
        opacity: 0;
        animation: bounce 1.4s infinite ease-in-out;
    }

    .loading-dots span:nth-child(1) {
        animation-delay: -0.32s;
    }

    .loading-dots span:nth-child(2) {
        animation-delay: -0.16s;
    }

    @keyframes bounce {
        0%, 80%, 100% {
            transform: scale(0);
            opacity: 0;
        }
        40% {
            transform: scale(1);
            opacity: 1;
        }
    }
    </style>
    """


def get_typing_indicator() -> str:
    """Get HTML for a typing indicator.

    Returns:
        HTML string for typing indicator.
    """
    return """
    <div class="typing-indicator">
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    <style>
    .typing-indicator {
        display: flex;
        justify-content: flex-start;
        padding: 0.5rem;
    }

    .typing-dots {
        display: flex;
        gap: 0.2rem;
    }

    .typing-dots span {
        width: 0.4rem;
        height: 0.4rem;
        background-color: #6b7280;
        border-radius: 50%;
        opacity: 0;
        animation: typing-bounce 1.4s infinite ease-in-out;
    }

    .typing-dots span:nth-child(1) {
        animation-delay: 0s;
    }

    .typing-dots span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-dots span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing-bounce {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.3;
        }
        30% {
            transform: translateY(-0.3rem);
            opacity: 1;
        }
    }
    </style>
    """


def format_thinking_block(thinking: str) -> str:
    """Format thinking content as a collapsible block.

    Args:
        thinking: The thinking/reasoning content.

    Returns:
        HTML formatted thinking block.
    """
    return f"""<div class="thinking-block"><details><summary>Reasoning</summary><div class="thinking-content">{thinking}</div></details></div>"""


def format_response_with_thinking(response: str, thinking: str | None) -> str:
    """Format the full response with optional thinking block.

    Args:
        response: The main response content.
        thinking: Optional thinking/reasoning content.

    Returns:
        Formatted response with thinking block if present.
    """
    if thinking:
        return f"{format_thinking_block(thinking)}\n\n{response}"
    return response


def format_error_message(error: str) -> str:
    """Format an error message for display.

    Args:
        error: The error message.

    Returns:
        HTML formatted error message.
    """
    return f"""<div style="
    background: linear-gradient(135deg, #2d1f1f 0%, #3d2020 100%);
    border: 1px solid #f85149;
    border-left: 3px solid #f85149;
    border-radius: 8px;
    padding: 1rem;
    color: #f0f6fc;
">
<strong style="color: #f85149;">Error</strong>
<p style="margin: 0.5rem 0 0 0; color: #c9d1d9;">{error}</p>
</div>"""
