"""Persistence module for system prompts, conversation history, and other user preferences."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from chatbot.settings import settings

logger = logging.getLogger(__name__)


class ConversationHistoryPersistence:
    """Handle persistence of conversation history to file."""

    def __init__(self, history_dir: str | Path | None = None) -> None:
        """Initialize the conversation history persistence system.

        Args:
            history_dir: Directory to store conversation history. If None, uses default.
        """
        if history_dir is None:
            self.history_dir = Path("conversation_history")
        else:
            self.history_dir = Path(history_dir)

        # Ensure directory exists
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Ensure the history directory exists."""
        self.history_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Conversation history directory: %s", self.history_dir)

    def _get_history_file_path(self, conversation_id: str) -> Path:
        """Get the file path for a specific conversation.

        Args:
            conversation_id: Unique identifier for the conversation.

        Returns:
            Path to the conversation file.
        """
        return self.history_dir / f"{conversation_id}.json"

    def save_conversation(
        self,
        conversation_id: str,
        history: list[dict[str, str]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Save a conversation to file.

        Args:
            conversation_id: Unique identifier for the conversation.
            history: List of message dictionaries (role, content).
            metadata: Optional metadata about the conversation.
        """
        conversation_data = {
            "id": conversation_id,
            "history": history,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": "1.0",
        }

        try:
            file_path = self._get_history_file_path(conversation_id)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            logger.info("Saved conversation %s to %s", conversation_id, file_path)
        except Exception as e:
            logger.error("Error saving conversation %s: %s", conversation_id, e)
            raise

    def load_conversation(self, conversation_id: str) -> dict[str, Any]:
        """Load a conversation from file.

        Args:
            conversation_id: Unique identifier for the conversation.

        Returns:
            Dictionary with conversation data.

        Raises:
            FileNotFoundError: If conversation doesn't exist.
        """
        file_path = self._get_history_file_path(conversation_id)

        if not file_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update last accessed time
            data["last_accessed"] = datetime.now().isoformat()
            self._save_conversation_data(data)  # Save updated metadata

            logger.info("Loaded conversation %s from %s", conversation_id, file_path)
            return data
        except json.JSONDecodeError:
            logger.error("Invalid JSON in conversation file: %s", file_path)
            raise ValueError(f"Invalid conversation data: {file_path}")
        except Exception as e:
            logger.error("Error loading conversation %s: %s", conversation_id, e)
            raise

    def _save_conversation_data(self, data: dict[str, Any]) -> None:
        """Save conversation data back to file.

        Args:
            data: Conversation data to save.
        """
        file_path = self._get_history_file_path(data["id"])
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_conversations(self) -> list[dict[str, Any]]:
        """List all saved conversations.

        Returns:
            List of conversation metadata.
        """
        conversations = []

        if not self.history_dir.exists():
            return conversations

        for file_path in self.history_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                conversations.append(
                    {
                        "id": data.get("id", file_path.stem),
                        "title": data.get("metadata", {}).get("title", "Untitled"),
                        "created_at": data.get("created_at", "Unknown"),
                        "updated_at": data.get("updated_at", "Unknown"),
                        "message_count": len(data.get("history", [])),
                    }
                )
            except Exception as e:
                logger.warning("Error reading conversation file %s: %s", file_path, e)

        # Sort by updated_at (newest first)
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations

    def search_conversations(self, query: str) -> list[dict[str, Any]]:
        """Search conversations by title or content.

        Args:
            query: Search term to filter conversations.

        Returns:
            List of matching conversation metadata.
        """
        if not query:
            return self.list_conversations()

        return self.list_conversations(query=query)

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.

        Args:
            conversation_id: Unique identifier for the conversation.

        Returns:
            True if deleted, False if not found.
        """
        file_path = self._get_history_file_path(conversation_id)

        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            logger.info("Deleted conversation %s", conversation_id)
            return True
        except Exception as e:
            logger.error("Error deleting conversation %s: %s", conversation_id, e)
            return False

    def generate_conversation_id(self) -> str:
        """Generate a unique conversation ID.

        Returns:
            Unique conversation ID.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"conv_{timestamp}"

    def export_conversation(
        self, conversation_id: str, export_path: str | Path | None = None
    ) -> str:
        """Export a conversation to a JSON file.

        Args:
            conversation_id: ID of conversation to export.
            export_path: Optional path to export to. If None, uses downloads folder.

        Returns:
            Path to the exported file.
        """
        try:
            conversation_data = self.load_conversation(conversation_id)

            # Set export path
            if export_path is None:
                export_dir = Path("exports")
                export_dir.mkdir(parents=True, exist_ok=True)
                export_path = export_dir / f"{conversation_id}_export.json"
            else:
                export_path = Path(export_path)
                export_path.parent.mkdir(parents=True, exist_ok=True)

            # Add export metadata
            conversation_data["exported_at"] = datetime.now().isoformat()
            conversation_data["export_source"] = "Ollama Chatbot"

            # Write to file
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)

            logger.info("Exported conversation %s to %s", conversation_id, export_path)
            return str(export_path)
        except Exception as e:
            logger.error("Error exporting conversation %s: %s", conversation_id, e)
            raise

    def import_conversation(self, import_path: str | Path) -> str:
        """Import a conversation from a JSON file.

        Args:
            import_path: Path to the file to import.

        Returns:
            ID of the imported conversation.
        """
        try:
            import_path = Path(import_path)

            # Read the file
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Generate new conversation ID
            conversation_id = self.generate_conversation_id()

            # Ensure required fields
            required_data = {
                "id": conversation_id,
                "history": data.get("history", []),
                "metadata": data.get("metadata", {}),
                "created_at": data.get("created_at", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "imported_from": str(import_path),
                "imported_at": datetime.now().isoformat(),
            }

            # Save the conversation
            self.save_conversation(
                conversation_id, required_data["history"], required_data["metadata"]
            )

            logger.info(
                "Imported conversation from %s as %s", import_path, conversation_id
            )
            return conversation_id
        except Exception as e:
            logger.error("Error importing conversation from %s: %s", import_path, e)
            raise

    def export_all_conversations(self, export_path: str | Path | None = None) -> str:
        """Export all conversations to a ZIP file.

        Args:
            export_path: Optional path for the ZIP file. If None, uses exports folder.

        Returns:
            Path to the exported ZIP file.
        """
        try:
            import zipfile
            from io import BytesIO

            # Set export path
            if export_path is None:
                export_dir = Path("exports")
                export_dir.mkdir(parents=True, exist_ok=True)
                export_path = (
                    export_dir
                    / f"all_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                )
            else:
                export_path = Path(export_path)
                export_path.parent.mkdir(parents=True, exist_ok=True)

            # Create ZIP file
            with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add each conversation
                for file_path in self.history_dir.glob("*.json"):
                    zipf.write(file_path, file_path.name)

            logger.info("Exported all conversations to %s", export_path)
            return str(export_path)
        except Exception as e:
            logger.error("Error exporting all conversations: %s", e)
            raise


class SystemPromptPersistence:
    """Handle persistence of system prompts to file."""

    def __init__(self, file_path: str | Path | None = None) -> None:
        """Initialize the persistence system.

        Args:
            file_path: Path to the persistence file. If None, uses default.
        """
        if file_path is None:
            # Use a file in the user's config directory or project root
            self.file_path = Path("system_prompt.json")
        else:
            self.file_path = Path(file_path)

        # Ensure the file exists
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the persistence file exists with default content."""
        if not self.file_path.exists():
            default_content = {
                "system_prompt": "You are a helpful AI assistant.",
                "version": "1.0",
                "last_updated": None,
            }
            self._write_file(default_content)
            logger.info("Created new system prompt file at %s", self.file_path)

    def _read_file(self) -> dict[str, Any]:
        """Read the persistence file.

        Returns:
            Dictionary with persistence data.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON in %s, creating new file", self.file_path)
            self._ensure_file_exists()
            return self._read_file()
        except Exception as e:
            logger.error("Error reading persistence file: %s", e)
            self._ensure_file_exists()
            return self._read_file()

    def _write_file(self, data: dict[str, Any]) -> None:
        """Write data to the persistence file.

        Args:
            data: Dictionary with data to write.
        """
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug("Saved system prompt to %s", self.file_path)
        except Exception as e:
            logger.error("Error writing persistence file: %s", e)

    def load_system_prompt(self) -> str:
        """Load the saved system prompt.

        Returns:
            The saved system prompt text.
        """
        data = self._read_file()
        return data.get("system_prompt", "You are a helpful AI assistant.")

    def save_system_prompt(self, prompt: str) -> None:
        """Save a system prompt.

        Args:
            prompt: The system prompt text to save.
        """
        data = self._read_file()
        data["system_prompt"] = prompt
        data["last_updated"] = self._get_current_timestamp()
        self._write_file(data)

    def _get_current_timestamp(self) -> str:
        """Get current date as simple date string.

        Returns:
            Current date string in YYYY-MM-DD format.
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d")

    def get_prompt_info(self) -> dict[str, Any]:
        """Get information about the saved system prompt.

        Returns:
            Dictionary with prompt information.
        """
        data = self._read_file()
        return {
            "prompt": data.get("system_prompt", ""),
            "last_updated": data.get("last_updated", "Never"),
            "file_path": str(self.file_path),
        }


# Global persistence instance
persistence = SystemPromptPersistence()
conversation_history = ConversationHistoryPersistence()


if __name__ == "__main__":
    # Test the persistence system
    print("Testing system prompt persistence...")

    # Test loading
    prompt = persistence.load_system_prompt()
    print(f"Loaded prompt: {prompt}")

    # Test saving
    persistence.save_system_prompt(
        "You are a helpful AI assistant that remembers preferences."
    )
    print("Saved new prompt")

    # Test info
    info = persistence.get_prompt_info()
    print(f"Prompt info: {info}")
