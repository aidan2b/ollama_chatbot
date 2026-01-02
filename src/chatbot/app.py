"""Main application entry point for the chatbot."""

from __future__ import annotations

import logging

import gradio as gr

from chatbot.config import ModelConfig, ui_config
from chatbot.ui.chat import chat, clear_chat
from chatbot.ui.theme import CUSTOM_CSS, theme

logger = logging.getLogger(__name__)


def create_app() -> gr.Blocks:
    """Create and configure the Gradio application.

    Returns:
        Configured Gradio Blocks application.
    """
    with gr.Blocks(title=ui_config.app_title) as app:
        # Header
        gr.HTML(
            f"""
            <div class="header-container">
                <h1 class="header-title">{ui_config.app_title}</h1>
                <p class="header-subtitle">{ui_config.app_description}</p>
            </div>
            """
        )

        # Main layout using HTML/CSS grid
        with gr.Row(elem_classes=["main-layout"]):
            # Sidebar
            with gr.Column(elem_classes=["sidebar"], min_width=280):
                # Model selection
                model_dropdown = gr.Dropdown(
                    choices=ModelConfig.AVAILABLE_MODELS,
                    value=ModelConfig.get_default_model(),
                    label="Model",
                    interactive=True,
                    elem_classes=["model-selector"],
                )

                # System prompt
                with gr.Accordion(
                    "System Prompt",
                    open=False,
                    elem_classes=["system-prompt-accordion"],
                ):
                    system_prompt = gr.Textbox(
                        placeholder="Define the assistant's behavior and personality...",
                        lines=4,
                        show_label=False,
                        max_lines=8,
                    )

            # Chat area
            with gr.Column(elem_classes=["chat-area"]):
                # Chat display
                chatbot = gr.Chatbot(
                    label="Conversation",
                    height=ui_config.chat_height,
                    elem_classes=["chat-container"],
                    layout="panel",
                )

                # Input area
                with gr.Row(elem_classes=["input-row"]):
                    msg = gr.Textbox(
                        placeholder="Type your message...",
                        show_label=False,
                        scale=9,
                        max_lines=5,
                        elem_classes=["message-input"],
                        autofocus=True,
                    )
                    submit_btn = gr.Button(
                        "Send",
                        scale=1,
                        variant="primary",
                        min_width=80,
                        elem_classes=["send-button"],
                    )

                # Action buttons
                with gr.Row(elem_classes=["action-buttons"]):
                    clear_btn = gr.Button(
                        "Clear Conversation",
                        size="sm",
                        elem_classes=["clear-button"],
                    )

        # Submit handlers
        submit_inputs = [msg, chatbot, model_dropdown, system_prompt]

        msg.submit(
            chat,
            inputs=submit_inputs,
            outputs=[chatbot],
        ).then(
            lambda: "",
            outputs=[msg],
        )

        submit_btn.click(
            chat,
            inputs=submit_inputs,
            outputs=[chatbot],
        ).then(
            lambda: "",
            outputs=[msg],
        )

        clear_btn.click(
            clear_chat,
            outputs=[chatbot, msg],
        )

    return app


def main() -> None:
    """Run the chatbot application."""
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        theme=theme,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    main()
