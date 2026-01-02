"""Main application entry point for the chatbot."""

from __future__ import annotations

import logging

import gradio as gr

from chatbot.cache import cache
from chatbot.config import ModelConfig, ui_config
from chatbot.services.llm import check_ollama_connection, refresh_model_config
from chatbot.ui.chat import chat, clear_chat, get_model_info
from chatbot.ui.theme import CUSTOM_CSS, theme

logger = logging.getLogger(__name__)


def refresh_models() -> tuple[gr.Dropdown, str]:
    """Refresh the available models from Ollama.

    Returns:
        Updated dropdown choices and status message.
    """
    try:
        refresh_model_config()

        if ModelConfig.AVAILABLE_MODELS:
            status_msg = f"✅ Found {len(ModelConfig.AVAILABLE_MODELS)} models"
            logger.info("Models refreshed successfully")
        else:
            status_msg = "⚠️ No models found"
            logger.warning("No models found after refresh")

        return (
            gr.Dropdown(
                choices=ModelConfig.AVAILABLE_MODELS,
                value=ModelConfig.get_default_model()
                if ModelConfig.AVAILABLE_MODELS
                else None,
            ),
            get_model_info(
                ModelConfig.get_default_model()
                if ModelConfig.AVAILABLE_MODELS
                else "No model selected"
            ),
            status_msg,
        )

    except Exception as e:
        logger.exception("Error refreshing models")
        error_msg = f"❌ Error refreshing models: {type(e).__name__}"
        return (
            gr.Dropdown(choices=ModelConfig.AVAILABLE_MODELS),
            get_model_info(ModelConfig.get_default_model()),
            error_msg,
        )


def create_app() -> gr.Blocks:
    """Create and configure the Gradio application.

    Returns:
        Configured Gradio Blocks application.
    """
    with gr.Blocks(title=ui_config.title) as app:
        # Header
        gr.HTML(
            f"""
            <div class="header-container">
                <h1 class="header-title">{ui_config.title}</h1>
                <p class="header-subtitle">{ui_config.description}</p>
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

                # Model info display
                model_info = gr.Markdown(
                    get_model_info(ModelConfig.get_default_model()),
                    elem_classes=["model-info"],
                )

                # Add refresh button for models
                with gr.Row():
                    refresh_models_btn = gr.Button(
                        "🔄 Refresh Models",
                        size="sm",
                        elem_classes=["refresh-models-button"],
                    )

                # Status display for model refresh
                model_status = gr.Markdown(
                    "🔄 Click to refresh available models",
                    elem_classes=["model-status"],
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
                    clear_cache_btn = gr.Button(
                        "🧹 Clear Cache",
                        size="sm",
                        elem_classes=["clear-cache-button"],
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

        # Update model info when model changes
        model_dropdown.change(
            get_model_info,
            inputs=[model_dropdown],
            outputs=[model_info],
        )

        # Connect refresh models button
        refresh_models_btn.click(
            refresh_models,
            outputs=[model_dropdown, model_info, model_status],
        )

        # Connect clear cache button
        def clear_cache() -> str:
            cache.clear()
            return "✅ Cache cleared"

        clear_cache_btn.click(
            clear_cache,
            outputs=[model_status],
        )

    return app


def main() -> None:
    """Run the chatbot application."""
    # Check Ollama connection before starting
    is_connected, message = check_ollama_connection()
    if is_connected:
        logger.info(message)

        # Try to refresh models on startup if connected
        try:
            refresh_model_config()
            logger.info("Models refreshed on startup")
        except Exception as e:
            logger.warning("Could not refresh models on startup: %s", type(e).__name__)
    else:
        logger.warning(f"Ollama connection check failed: {message}")
        logger.warning(
            "The app will start, but chat will not work until Ollama is available."
        )

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
