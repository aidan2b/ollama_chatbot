"""Configuration module for the chatbot application."""

from __future__ import annotations

import logging
from typing import ClassVar

from chatbot.settings import settings

logger = logging.getLogger(__name__)


class ModelConfig:
    """Configuration for available models."""

    AVAILABLE_MODELS: ClassVar[list[str]] = [
        "deepseek-r1:14b",
        "ministral-3:14b",
        "devstral-small-2:latest",
    ]

    REASONING_MODELS: ClassVar[set[str]] = {"deepseek-r1:14b"}

    @classmethod
    def get_default_model(cls) -> str:
        """Get the default model."""
        return cls.AVAILABLE_MODELS[0]

    @classmethod
    def supports_reasoning(cls, model_name: str) -> bool:
        """Check if a model supports reasoning/thinking."""
        return model_name in cls.REASONING_MODELS


# Use settings from the new settings system
ollama_config = settings.ollama
ui_config = settings.app
model_config = ModelConfig()
