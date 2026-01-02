"""Modern theme configuration for the chatbot UI."""

from __future__ import annotations

import gradio as gr

# Color palette - Modern dark theme with accent colors
COLORS = {
    # Base colors
    "bg_darkest": "#0d1117",
    "bg_dark": "#161b22",
    "bg_medium": "#21262d",
    "bg_light": "#30363d",
    "bg_lighter": "#484f58",
    # Text colors
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "text_muted": "#6e7681",
    # Accent colors
    "accent_primary": "#58a6ff",
    "accent_primary_hover": "#79b8ff",
    "accent_success": "#3fb950",
    "accent_success_hover": "#56d364",
    "accent_warning": "#d29922",
    "accent_error": "#f85149",
    # Border colors
    "border_default": "#30363d",
    "border_muted": "#21262d",
}

# Custom CSS for enhanced styling
CUSTOM_CSS = """
/* Global styles */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* Main layout - fixed two-column structure */
.main-layout {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    gap: 1.5rem !important;
    align-items: flex-start !important;
}

.sidebar {
    flex: 0 0 280px !important;
    max-width: 280px !important;
    min-width: 280px !important;
}

.chat-area {
    flex: 1 1 auto !important;
    min-width: 800px !important;
    max-width: 800px !important;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #30363d;
    margin-bottom: 1.5rem;
}

.header-title {
    font-size: 2rem;
    font-weight: 600;
    color: #e6edf3;
    margin: 0;
    letter-spacing: -0.02em;
}

.header-subtitle {
    font-size: 0.95rem;
    color: #8b949e;
    margin-top: 0.5rem;
}

/* Chat container */
.chat-container {
    border-radius: 12px;
    overflow: hidden;
}

/* Thinking block styling */
.thinking-block {
    background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
    border: 1px solid #30363d;
    border-left: 3px solid #58a6ff;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.thinking-block summary {
    cursor: pointer;
    color: #58a6ff;
    font-weight: 500;
    user-select: none;
}

.thinking-block summary:hover {
    color: #79b8ff;
}

.thinking-content,
.thinking-content * {
    padding-top: 0.75rem;
    color: #8b949e !important;
    line-height: 1.6;
    white-space: pre-wrap;
}

.thinking-content p,
.thinking-content span,
.thinking-content div {
    padding-top: 0;
}

/* Input area styling */
.input-row {
    gap: 0.75rem;
    display: flex !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
    height: 70px !important;
}

.input-row > div {
    height: 100% !important;
    display: flex !important;
}

.message-input {
    flex: 1 !important;
    height: 100% !important;
}

.message-input textarea {
    border-radius: 12px !important;
    padding: 0.875rem 1rem !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    height: 100% !important;
    resize: none !important;
}

.message-input textarea:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.15) !important;
}

/* Button styling */
.send-button,
.send-button button {
    height: 100% !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.send-button:hover {
    box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
}

/* Model selector styling */
.model-selector {
    border-radius: 10px;
}

/* System prompt accordion */
.system-prompt-accordion {
    border-radius: 10px;
    margin-top: 1rem;
}

.system-prompt-accordion textarea {
    max-height: 200px;
    overflow-y: auto !important;
}

/* Action buttons */
.action-buttons {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #21262d;
}

.clear-button {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #161b22;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #484f58;
}
"""


def create_theme() -> gr.themes.Base:
    """Create and return the custom theme."""
    return gr.themes.Base(
        primary_hue=gr.themes.Color(
            c50="#ddf4ff",
            c100="#b6e3ff",
            c200="#80ccff",
            c300="#54aeff",
            c400="#218bff",
            c500="#1f6feb",
            c600="#388bfd",
            c700="#58a6ff",
            c800="#79b8ff",
            c900="#a5d6ff",
            c950="#cae8ff",
        ),
        secondary_hue=gr.themes.Color(
            c50="#f0f6fc",
            c100="#c9d1d9",
            c200="#b1bac4",
            c300="#8b949e",
            c400="#6e7681",
            c500="#484f58",
            c600="#30363d",
            c700="#21262d",
            c800="#161b22",
            c900="#0d1117",
            c950="#010409",
        ),
        neutral_hue=gr.themes.Color(
            c50="#f0f6fc",
            c100="#c9d1d9",
            c200="#b1bac4",
            c300="#8b949e",
            c400="#6e7681",
            c500="#484f58",
            c600="#30363d",
            c700="#21262d",
            c800="#161b22",
            c900="#0d1117",
            c950="#010409",
        ),
        font=gr.themes.GoogleFont("Inter"),
        font_mono=gr.themes.GoogleFont("JetBrains Mono"),
        radius_size=gr.themes.sizes.radius_md,
        spacing_size=gr.themes.sizes.spacing_md,
    ).set(
        # Background colors
        body_background_fill=COLORS["bg_darkest"],
        body_background_fill_dark=COLORS["bg_darkest"],
        body_text_color=COLORS["text_primary"],
        body_text_color_dark=COLORS["text_primary"],
        body_text_color_subdued=COLORS["text_secondary"],
        body_text_color_subdued_dark=COLORS["text_secondary"],
        # Block styling
        block_background_fill=COLORS["bg_dark"],
        block_background_fill_dark=COLORS["bg_dark"],
        block_border_color=COLORS["border_default"],
        block_border_color_dark=COLORS["border_default"],
        block_label_text_color=COLORS["text_secondary"],
        block_label_text_color_dark=COLORS["text_secondary"],
        block_title_text_color=COLORS["text_primary"],
        block_title_text_color_dark=COLORS["text_primary"],
        block_radius="12px",
        block_shadow="0 2px 8px rgba(0, 0, 0, 0.3)",
        # Input styling
        input_background_fill=COLORS["bg_medium"],
        input_background_fill_dark=COLORS["bg_medium"],
        input_border_color=COLORS["border_default"],
        input_border_color_dark=COLORS["border_default"],
        input_border_color_focus=COLORS["accent_primary"],
        input_border_color_focus_dark=COLORS["accent_primary"],
        input_placeholder_color=COLORS["text_muted"],
        input_placeholder_color_dark=COLORS["text_muted"],
        input_radius="10px",
        # Button styling
        button_primary_background_fill=COLORS["accent_primary"],
        button_primary_background_fill_hover=COLORS["accent_primary_hover"],
        button_primary_background_fill_dark=COLORS["accent_primary"],
        button_primary_background_fill_hover_dark=COLORS["accent_primary_hover"],
        button_primary_text_color="#ffffff",
        button_primary_text_color_dark="#ffffff",
        button_secondary_background_fill=COLORS["bg_light"],
        button_secondary_background_fill_hover=COLORS["bg_lighter"],
        button_secondary_background_fill_dark=COLORS["bg_light"],
        button_secondary_background_fill_hover_dark=COLORS["bg_lighter"],
        button_secondary_text_color=COLORS["text_primary"],
        button_secondary_text_color_dark=COLORS["text_primary"],
        # Border styling
        border_color_primary=COLORS["border_default"],
        border_color_primary_dark=COLORS["border_default"],
        # Panel styling
        panel_background_fill=COLORS["bg_dark"],
        panel_background_fill_dark=COLORS["bg_dark"],
        panel_border_color=COLORS["border_default"],
        panel_border_color_dark=COLORS["border_default"],
    )


# Export the theme instance
theme = create_theme()
