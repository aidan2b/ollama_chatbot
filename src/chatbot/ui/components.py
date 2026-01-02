"""Reusable UI components for the chatbot."""

from __future__ import annotations


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
