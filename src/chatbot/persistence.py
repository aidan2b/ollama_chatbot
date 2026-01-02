"""Persistence module for system prompts and other user preferences."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from chatbot.settings import settings

logger = logging.getLogger(__name__)


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
