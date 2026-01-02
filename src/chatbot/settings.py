"""Application settings using Pydantic for configuration management."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class OllamaSettings(BaseSettings):
    """Configuration for Ollama connection."""

    model_config = SettingsConfigDict(
        env_prefix="OLLAMA_",
        env_file=".env",
        extra="ignore",
    )

    base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama server",
    )
    timeout: int = Field(
        default=120,
        description="Timeout in seconds for Ollama requests",
        ge=10,
        le=600,
    )

    @field_validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """Validate that base_url starts with http:// or https://."""
        if not v.startswith(("http://", "https://")):
            logger.warning(
                f"OLLAMA_BASE_URL should start with http:// or https://, got '{v}'. "
                "Using default: http://localhost:11434"
            )
            return "http://localhost:11434"
        return v.rstrip("/")


class AppSettings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    title: str = Field(
        default="Ollama Chat",
        description="Application title",
    )
    description: str = Field(
        default="A sleek interface for local LLM conversations",
        description="Application description",
    )
    chat_height: int = Field(
        default=550,
        description="Height of chat area in pixels",
        ge=300,
        le=1000,
    )
    max_message_length: int = Field(
        default=10000,
        description="Maximum length of user messages",
        ge=100,
        le=50000,
    )
    max_system_prompt_length: int = Field(
        default=5000,
        description="Maximum length of system prompts",
        ge=100,
        le=10000,
    )


class CacheSettings(BaseSettings):
    """Cache configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        env_file=".env",
        extra="ignore",
    )

    size: int = Field(
        default=100,
        description="Maximum number of items in cache",
        ge=10,
        le=1000,
    )
    ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
        ge=300,
        le=86400,
    )


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        extra="ignore",
    )

    url: str = Field(
        default="sqlite:///chatbot.db",
        description="Database connection URL",
    )
    enable_history: bool = Field(
        default=False,
        description="Enable conversation history persistence",
    )


class SecuritySettings(BaseSettings):
    """Security configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        env_file=".env",
        extra="ignore",
    )

    max_requests_per_minute: int = Field(
        default=60,
        description="Maximum requests per minute per user",
        ge=10,
        le=1000,
    )
    enable_input_sanitization: bool = Field(
        default=True,
        description="Enable input sanitization for security",
    )


class Settings(BaseSettings):
    """Main application settings container."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    ollama: OllamaSettings = Field(default_factory=OllamaSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    # Global settings instance
    _instance: ClassVar[Settings | None] = None

    @classmethod
    def get_instance(cls) -> Settings:
        """Get singleton instance of settings."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Initialize settings
settings = Settings.get_instance()


if __name__ == "__main__":
    # Print current configuration for debugging
    print("Current Configuration:")
    print(f"Ollama Base URL: {settings.ollama.base_url}")
    print(f"App Title: {settings.app.title}")
    print(f"Cache Size: {settings.cache.size}")
    print(f"Database Enabled: {settings.database.enable_history}")
