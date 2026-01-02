"""Main application entry point for the chatbot."""

from __future__ import annotations

import logging
from pathlib import Path

import gradio as gr

from chatbot.cache import cache
from chatbot.config import ModelConfig, ui_config
from chatbot.persistence import conversation_history, persistence
from chatbot.services.llm import check_ollama_connection, refresh_model_config
from chatbot.ui.chat import chat, clear_chat, get_model_info
from chatbot.ui.theme import CUSTOM_CSS, theme

logger = logging.getLogger(__name__)


# Conversation history functions
def update_conversation_list() -> gr.Dropdown:
    """Update the conversation list dropdown with available conversations."""
    conversations = conversation_history.list_conversations()
    choices = [
        f"{conv['title']} ({conv['id']}) - {conv['message_count']} messages"
        for conv in conversations
    ]
    return gr.Dropdown(choices=choices, value=choices[0] if choices else None)


def save_current_conversation(
    history: list[dict[str, str]], model_name: str, system_prompt: str
) -> tuple[str, str]:
    """Save the current conversation."""
    if not history:
        return "❌ No conversation to save", "No conversation selected"

    conversation_id = conversation_history.generate_conversation_id()

    # Extract title from first user message or use default
    title = "Untitled Conversation"
    for msg in history:
        if msg.get("role") == "user" and msg.get("content"):
            title = (
                msg["content"][:30] + "..."
                if len(msg["content"]) > 30
                else msg["content"]
            )
            break

    metadata = {
        "title": title,
        "model": model_name,
        "system_prompt": system_prompt if system_prompt else "Default",
    }

    conversation_history.save_conversation(conversation_id, history, metadata)

    # Update conversation list
    update_conversation_list()

    return f"✅ Saved conversation: {title}", f"Saved: {title} ({conversation_id})"


def load_selected_conversation(selected: str) -> tuple[list[dict[str, str]], str]:
    """Load the selected conversation."""
    if not selected:
        return [], "❌ No conversation selected"

    # Extract conversation ID from the dropdown text
    try:
        conversation_id = selected.split("(")[1].split(")")[0].strip()
        conversation_data = conversation_history.load_conversation(conversation_id)

        # Note: System prompt update removed to avoid scope issues
        # The conversation history is still loaded successfully

        return (
            conversation_data["history"],
            f"📝 Loaded: {conversation_data.get('metadata', {}).get('title', 'Untitled')}",
        )
    except Exception as e:
        return [], f"❌ Error loading conversation: {str(e)}"


def delete_selected_conversation(selected: str) -> str:
    """Delete the selected conversation."""
    if not selected:
        return "❌ No conversation selected"

    try:
        conversation_id = selected.split("(")[1].split(")")[0].strip()
        success = conversation_history.delete_conversation(conversation_id)

        if success:
            # Update conversation list
            update_conversation_list()
            return f"🗑️ Deleted conversation"
        else:
            return "❌ Conversation not found"
    except Exception as e:
        return f"❌ Error deleting conversation: {str(e)}"


def search_conversations(query: str) -> gr.Dropdown:
    """Search conversations by query."""
    if query.strip():
        conversations = conversation_history.search_conversations(query.strip())
        choices = [
            f"{conv['title']} ({conv['id']}) - {conv['message_count']} messages"
            for conv in conversations
        ]
        return gr.Dropdown(choices=choices, value=choices[0] if choices else None)
    else:
        return update_conversation_list()


def export_selected_conversation(selected: str) -> str:
    """Export the selected conversation."""
    if not selected:
        return "❌ No conversation selected"

    try:
        conversation_id = selected.split("(")[1].split(")")[0].strip()
        export_path = conversation_history.export_conversation(conversation_id)
        return f"📤 Exported conversation to: {export_path}"
    except Exception as e:
        return f"❌ Error exporting conversation: {str(e)}"


def export_all_conversations() -> str:
    """Export all conversations."""
    try:
        export_path = conversation_history.export_all_conversations()
        return f"📤 Exported all conversations to: {export_path}"
    except Exception as e:
        return f"❌ Error exporting all conversations: {str(e)}"


def show_import_dialog() -> gr.File:
    """Show the import file dialog."""
    return gr.File(visible=True)


def import_conversation_file(uploaded_file) -> str:
    """Import a conversation from uploaded file."""
    if not uploaded_file:
        return "❌ No file selected"

    try:
        # Save the uploaded file temporarily
        import_path = Path("temp_import.json")
        with open(import_path, "wb") as f:
            f.write(uploaded_file)

        # Import the conversation
        conversation_id = conversation_history.import_conversation(import_path)

        # Clean up
        import_path.unlink()

        # Update conversation list
        update_conversation_list()

        return f"📥 Imported conversation: {conversation_id}"
    except Exception as e:
        return f"❌ Error importing conversation: {str(e)}"


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


def show_prompt_info() -> str:
    """Show information about the current system prompt.

    Returns:
        Formatted string with prompt information.
    """
    info = persistence.get_prompt_info()
    last_updated = info["last_updated"] or "Never"

    # Format date nicely - handle both old ISO format and new date format
    if last_updated and last_updated != "Never":
        if "T" in last_updated:  # Old ISO format
            last_updated = last_updated.split("T")[0]  # Extract just the date part
        # New format is already just the date

    return f"📝 Last updated: {last_updated}"


# Note: Conversation history functions are defined at the module level above


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
                    "⚙️ System Prompt",
                    open=False,
                    elem_classes=["system-prompt-accordion"],
                ):
                    system_prompt = gr.Textbox(
                        value=persistence.load_system_prompt(),
                        placeholder="Define the assistant's behavior and personality...",
                        lines=4,
                        show_label=False,
                        max_lines=8,
                    )

                    with gr.Row():
                        save_prompt_btn = gr.Button(
                            "💾 Save System Prompt",
                            size="sm",
                            elem_classes=["save-prompt-button"],
                        )

                    # Last updated display under system prompt
                    prompt_status = gr.Markdown(
                        show_prompt_info(),
                        elem_classes=["prompt-status"],
                    )

                # Conversation history section
                with gr.Accordion(
                    "💬 Conversation History",
                    open=False,
                    elem_classes=["conversation-history-accordion"],
                ):
                    # Search box for conversations
                    with gr.Row():
                        conversation_search = gr.Textbox(
                            placeholder="🔍 Search conversations...",
                            show_label=False,
                            elem_classes=["conversation-search"],
                        )
                        search_btn = gr.Button(
                            "🔍 Search",
                            size="sm",
                            elem_classes=["search-button"],
                        )

                    # Conversation list dropdown
                    conversation_list = gr.Dropdown(
                        choices=[],
                        label="Saved Conversations",
                        elem_classes=["conversation-list"],
                    )

                    # Conversation management buttons
                    with gr.Row():
                        save_conversation_btn = gr.Button(
                            "💾 Save Current",
                            size="sm",
                            elem_classes=["save-conversation-button"],
                        )
                        load_conversation_btn = gr.Button(
                            "📥 Load Selected",
                            size="sm",
                            elem_classes=["load-conversation-button"],
                        )
                        delete_conversation_btn = gr.Button(
                            "🗑️ Delete Selected",
                            size="sm",
                            elem_classes=["delete-conversation-button"],
                        )

                    # Export/Import buttons
                    with gr.Row():
                        export_conversation_btn = gr.Button(
                            "📤 Export Selected",
                            size="sm",
                            elem_classes=["export-conversation-button"],
                        )
                        export_all_btn = gr.Button(
                            "📤 Export All",
                            size="sm",
                            elem_classes=["export-all-button"],
                        )
                        import_conversation_btn = gr.Button(
                            "📥 Import Conversation",
                            size="sm",
                            elem_classes=["import-conversation-button"],
                        )

                    # File upload for import
                    import_file = gr.File(
                        label="Select file to import",
                        file_types=[".json"],
                        visible=False,
                        elem_classes=["import-file"],
                    )

                    # Conversation info display
                    conversation_info = gr.Markdown(
                        "No conversation selected",
                        elem_classes=["conversation-info"],
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

        # Save system prompt when it changes
        def save_system_prompt(prompt: str) -> str:
            persistence.save_system_prompt(prompt)
            return f"✅ System prompt saved to {persistence.get_prompt_info()['file_path']}"

        system_prompt.change(
            save_system_prompt,
            inputs=[system_prompt],
            outputs=[model_status],
        )

        # Connect save button
        save_prompt_btn.click(
            save_system_prompt,
            inputs=[system_prompt],
            outputs=[model_status],
        )

        # Update prompt status when system prompt changes
        def update_prompt_status(prompt: str) -> str:
            return show_prompt_info()

        system_prompt.change(
            update_prompt_status,
            inputs=[system_prompt],
            outputs=[prompt_status],
        )

        # Connect conversation history buttons
        save_conversation_btn.click(
            save_current_conversation,
            inputs=[chatbot, model_dropdown, system_prompt],
            outputs=[model_status, conversation_info],
        )

        load_conversation_btn.click(
            load_selected_conversation,
            inputs=[conversation_list],
            outputs=[chatbot, conversation_info],
        )

        delete_conversation_btn.click(
            delete_selected_conversation,
            inputs=[conversation_list],
            outputs=[conversation_info],
        )

        # Update conversation list on app load
        app.load(
            update_conversation_list,
            outputs=[conversation_list],
        )

        # Connect conversation buttons
        search_btn.click(
            search_conversations,
            inputs=[conversation_search],
            outputs=[conversation_list],
        )

        conversation_search.submit(
            search_conversations,
            inputs=[conversation_search],
            outputs=[conversation_list],
        )

        save_conversation_btn.click(
            save_current_conversation,
            inputs=[chatbot, model_dropdown, system_prompt],
            outputs=[model_status, conversation_info],
        )

        load_conversation_btn.click(
            load_selected_conversation,
            inputs=[conversation_list],
            outputs=[chatbot, conversation_info],
        )

        delete_conversation_btn.click(
            delete_selected_conversation,
            inputs=[conversation_list],
            outputs=[conversation_info],
        )

        export_conversation_btn.click(
            export_selected_conversation,
            inputs=[conversation_list],
            outputs=[conversation_info],
        )

        export_all_btn.click(
            export_all_conversations,
            outputs=[conversation_info],
        )

        import_conversation_btn.click(
            show_import_dialog,
            outputs=[import_file],
        )

        import_file.change(
            import_conversation_file,
            inputs=[import_file],
            outputs=[conversation_info],
        )

        # Update conversation list on app load
        app.load(
            update_conversation_list,
            outputs=[conversation_list],
        )

        # Connect refresh models button
        refresh_models_btn.click(
            refresh_models,
            outputs=[model_dropdown, model_status],
        )

        # Connect clear cache button
        def clear_cache() -> str:
            cache.clear()
            stats = cache.get_cache_stats()
            return f"✅ Cache cleared. LLM cache: {stats['llm_cache']['size']}/{stats['llm_cache']['max_size']}, Response cache: {stats['response_cache']['size']}/{stats['response_cache']['max_size']}"

        clear_cache_btn.click(
            clear_cache,
            outputs=[model_status],
        )

        # Connect conversation buttons (functions are defined at module level)
        search_btn.click(
            search_conversations,
            inputs=[conversation_search],
            outputs=[conversation_list],
        )

        conversation_search.submit(
            search_conversations,
            inputs=[conversation_search],
            outputs=[conversation_list],
        )

        save_conversation_btn.click(
            save_current_conversation,
            inputs=[chatbot, model_dropdown, system_prompt],
            outputs=[model_status, conversation_info],
        )

        load_conversation_btn.click(
            load_selected_conversation,
            inputs=[conversation_list],
            outputs=[chatbot, conversation_info],
        )

        delete_conversation_btn.click(
            delete_selected_conversation,
            inputs=[conversation_list],
            outputs=[conversation_info],
        )

        export_conversation_btn.click(
            export_selected_conversation,
            inputs=[conversation_list],
            outputs=[conversation_info],
        )

        export_all_btn.click(
            export_all_conversations,
            outputs=[conversation_info],
        )

        import_conversation_btn.click(
            show_import_dialog,
            outputs=[import_file],
        )

        import_file.change(
            import_conversation_file,
            inputs=[import_file],
            outputs=[conversation_info],
        )

        # Update conversation list on app load
        app.load(
            update_conversation_list,
            outputs=[conversation_list],
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
        server_port=7864,
        share=False,
        show_error=True,
        theme=theme,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    main()
