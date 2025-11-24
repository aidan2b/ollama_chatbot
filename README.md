# Ollama LangChain WebSocket Chatbot

A lightweight, real-time chatbot server built using **FastAPI**,
**LangChain**, and **Ollama**, featuring **WebSocket streaming** for
token-by-token responses and a built-in **browser UI** with Markdown
rendering.

This backend allows you to chat with any locally installed Ollama model
(e.g., `llama3`, `mistral`, `phi3`, etc.) through a responsive web
interface.

------------------------------------------------------------------------

## 🚀 Features

-   FastAPI backend with REST + WebSocket support\
-   Real-time streaming of tokens using WebSockets\
-   LangChain `ChatOllama` integration\
-   Automatic Markdown rendering in the frontend\
-   Model auto-loading & on-demand pulling\
-   Custom lightweight HTML/JS Chat UI\
-   CORS enabled for easy client integration

------------------------------------------------------------------------

## 📦 Requirements

### System

-   Python 3.9+

-   Ollama installed: https://ollama.com/download\

-   At least one model pulled locally:

    ``` bash
    ollama pull llama3
    ```

### Python Dependencies

The script installs missing packages automatically on first run: -
fastapi\
- uvicorn\
- langchain, langchain-community\
- langchain-ollama\
- websockets\
- python-dotenv

------------------------------------------------------------------------

## 🛠️ Setup & Installation

### 1. Clone the repository

``` bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. (Optional) Create a virtual environment

``` bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Add a `.env` file (optional)

    OPENAI_API_KEY=...
    OTHER_ENV=...

### 4. Run the server

``` bash
python chatbot.py
```

You should see:

    Starting Ollama LangChain Server...
    Access at: http://localhost:8000

------------------------------------------------------------------------

## 💬 Using the Web Interface

Visit:\
👉 **http://localhost:8000/**

You'll find a full chat UI featuring:

-   Model selector (auto-populated from `ollama list`)
-   Connect/reconnect button
-   Live Markdown-rendered messages
-   Streaming token output
-   Error reporting

### Keyboard shortcuts

-   **Enter** = Send\
-   **Shift + Enter** = New line

------------------------------------------------------------------------

## 🔌 API Endpoints

### GET /

Returns the built-in HTML chat interface.

------------------------------------------------------------------------

### GET /models

Lists available local Ollama models.

``` json
{
  "models": ["llama3", "mistral", "phi3"]
}
```

------------------------------------------------------------------------

### POST /pull/{model_name}

Pulls a model from the Ollama registry.

``` bash
POST /pull/llama3
```

------------------------------------------------------------------------

### WS /ws/{model_name}

WebSocket endpoint for real-time chat.

Incoming message:

``` json
{
  "type": "message",
  "content": "Hello!"
}
```

Event types: - `system`\
- `token`\
- `start`\
- `end`\
- `error`

------------------------------------------------------------------------

## 🧩 How It Works

### LangChain Integration

Each model uses:

``` python
ChatOllama(
    model=model_name,
    callbacks=[WebSocketCallback(websocket)]
)
```

### Token Streaming

``` json
{ "type": "token", "content": "..." }
```

### Model Persistence

``` python
models = {}
```

------------------------------------------------------------------------

## 📁 Project Structure

    chatbot.py      # Main backend server + HTML UI
    .env            # Optional environment variables

------------------------------------------------------------------------

## 🧪 Example CURL Usage

### List models

``` bash
curl http://localhost:8000/models
```

### Pull a model

``` bash
curl -X POST http://localhost:8000/pull/llama3
```

------------------------------------------------------------------------

## 🙌 Contributing

Feel free to submit issues, pull requests, or feature suggestions.

------------------------------------------------------------------------

## 📄 License

MIT
