# Ollama Chatbot

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

The script installs missing packages automatically on first run: 
- fastapi
- uvicorn
- langchain, langchain-community
- langchain-ollama
- websockets
- dotenv

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

### 3. Add a `.env` file (WIP - Features comings...)

### 4. Run the server

``` bash
python chatbot.py
```

You should see:

    Starting Ollama LangChain Server...
    Access at: http://localhost:8000

### 5. Start chatting

Go to http://localhost:8000, and wait for introductory message, then start chatting!
