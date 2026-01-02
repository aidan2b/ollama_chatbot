"""Ollama Chat - A sleek interface for local LLM conversations."""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "hex"

from chatbot.app import create_app, main
from chatbot.config import ModelConfig
from chatbot.settings import settings

__all__ = [
    "create_app",
    "main",
    "ModelConfig",
    "settings",
]
