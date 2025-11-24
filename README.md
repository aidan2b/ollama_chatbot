Ollama LangChain WebSocket

Simple FastAPI server that integrates LangChain with Ollama and streams token-by-token LLM responses over WebSockets. Includes a minimal browser UI for real-time interaction and endpoints to list and pull Ollama models.
Features

    WebSocket streaming of tokens for low-latency responses
    Endpoints: list available Ollama models, pull a model
    Lightweight HTML UI for testing in-browser

Requirements

    Python 3.8+
    Ollama CLI installed and configured

Quickstart

    Clone the repo and enter the directory.
    (Optional) Create a .env file in the project root for any environment variables.
    Run:

Code

    python3 your_script.py

    Open http://localhost:8000 in your browser, select a model, and connect.

Endpoints

    GET /models — list available Ollama models
    POST /pull/{model_name} — pull a model via Ollama CLI
    WebSocket /ws/{model_name} — open a streaming chat connection

Notes

    The server will attempt to install missing Python dependencies if not present.
    Ensure the Ollama daemon/CLI is running and accessible.
