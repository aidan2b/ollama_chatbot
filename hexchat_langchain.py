#!/usr/bin/env python3
"""
FastAPI + LangChain Ollama Backend
WebSocket streaming for real-time responses
"""

from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import subprocess
import json
from typing import Optional

try:
    from langchain_core.callbacks.base import AsyncCallbackHandler
    from langchain_ollama import ChatOllama
    import uvicorn
except ImportError:
    print("Installing required packages...")
    subprocess.check_call(["pip", "install", "fastapi", "uvicorn", "langchain", "langchain-community", "websockets", "--quiet"])
    from langchain_core.callbacks.base import AsyncCallbackHandler
    from langchain_ollama import ChatOllama
    import uvicorn

app = FastAPI(title="Ollama LangChain API")

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model storage
models = {}

class WebSocketCallback(AsyncCallbackHandler):
    """Stream tokens to WebSocket"""
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        await self.websocket.send_json({"type": "token", "content": token})

class ModelInfo(BaseModel):
    name: str

@app.get("/")
async def root():
    """Serve the HTML interface"""
    return HTMLResponse(content=HTML_INTERFACE)

@app.get("/models")
async def list_models():
    """List available models"""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')[1:]
        models = []
        for line in lines:
            if line.strip():
                parts = line.split()
                if parts and ':' in parts[0]:
                    models.append(parts[0]) 
        return {"models": models}
    except:
        return {"models": []}

@app.post("/pull/{model_name}")
async def pull_model(model_name: str):
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        return {"status": "success", "message": f"Model {model_name} pulled successfully"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{model_name}")
async def websocket_endpoint(websocket: WebSocket, model_name: str):
    await websocket.accept()

    try:
        if model_name not in models:
            models[model_name] = ChatOllama(
                model=model_name,
                callbacks=[WebSocketCallback(websocket)]
            )

            await websocket.send_json({"type": "system", "content": f"Connected to {model_name}"})
            intro_prompt = "Introduce yourself briefly - your model name and capabilities."
            await models[model_name].ainvoke(intro_prompt)
            await websocket.send_json({"type": "end"})

        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                prompt = data["content"]
                await websocket.send_json({"type": "start"})
                await models[model_name].ainvoke(prompt)
                await websocket.send_json({"type": "end"})

    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        await websocket.close()

HTML_INTERFACE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ollama LangChain WebSocket</title>

    <!-- ⭐ Markdown Renderer -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Consolas', monospace;
            background: #0a0a0a;
            color: #e0e0e0;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #header {
            background: #1a1a1a;
            padding: 15px;
            border-bottom: 1px solid #333;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        #model-select, button {
            background: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #444;
            padding: 8px 15px;
            border-radius: 3px;
            cursor: pointer;
        }
        button:hover:not(:disabled) {
            background: #3a3a3a;
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        #status {
            margin-left: auto;
            color: #888;
        }
        #chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #0f0f0f;
        }
        .message {
            margin: 15px 0;
            line-height: 1.6;
        }
        .assistant { color: #98fb98; }
        .user { color: #87ceeb; }
        .system { color: #b19cd9; }
        .error { color: #ff6b6b; }

        pre, code {
            background: #1a1a1a !important;
            padding: 6px;
            border-radius: 4px;
            overflow-x: auto;
        }

        #input-area {
            display: flex;
            padding: 15px;
            background: #1a1a1a;
            border-top: 1px solid #333;
            gap: 10px;
        }
        #input {
            flex: 1;
            background: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #444;
            padding: 10px;
            border-radius: 3px;
            resize: none;
            font-family: inherit;
        }
    </style>
</head>
<body>

    <div id="header">
        <select id="model-select">
            <option value="">Select a model...</option>
        </select>
        <button id="connect-btn">Connect</button>
        <div id="status">Disconnected</div>
    </div>

    <div id="chat"></div>

    <div id="input-area">
        <textarea id="input" rows="2" placeholder="Type your message..." disabled></textarea>
        <button id="send-btn" disabled>Send</button>
    </div>

<script>
let ws = null;
let currentMessage = null;

const chat = document.getElementById('chat');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send-btn');
const connectBtn = document.getElementById('connect-btn');
const modelSelect = document.getElementById('model-select');
const status = document.getElementById('status');

// -------------------------------
// Markdown Rendering Chat Function
// -------------------------------

function addMessage(type, content) {
    const div = document.createElement('div');
    div.className = `message ${type}`;

    let prefix = "";
    if (type === "user") prefix = "**You:**\\n\\n";
    else if (type === "assistant") prefix = `**${modelSelect.value}:**\\n\\n`;
    else if (type === "system") prefix = "**System:**\\n\\n";

    const md = prefix + content;
    div.dataset.raw = md;
    div.innerHTML = marked.parse(md);

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

// ------------------------------

async function loadModels() {
    try {
        const response = await fetch('/models');
        const data = await response.json();
        data.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            modelSelect.appendChild(option);
        });
    } catch (e) {
        console.error('Failed to load models:', e);
    }
}

connectBtn.addEventListener('click', () => {
    const model = modelSelect.value;
    if (!model) return;

    if (ws) ws.close();

    ws = new WebSocket(`ws://localhost:8000/ws/${model}`);

    ws.onopen = () => {
        status.textContent = `Connected: ${model}`;
        status.style.color = '#98fb98';
        input.disabled = false;
        sendBtn.disabled = false;
        connectBtn.textContent = 'Reconnect';
        addMessage('system', `Connecting to ${model}...`);
        currentMessage = addMessage('assistant', '');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'token') {
            if (currentMessage) {
                currentMessage.dataset.raw += data.content;
                currentMessage.innerHTML = marked.parse(currentMessage.dataset.raw);
                chat.scrollTop = chat.scrollHeight;
            }
        } else if (data.type === 'start') {
            currentMessage = addMessage('assistant', '');
        } else if (data.type === 'end') {
            currentMessage = null;
        } else if (data.type === 'error') {
            addMessage('error', data.content);
        } else if (data.type === 'system') {
            addMessage('system', data.content);
        }
    };

    ws.onerror = () => {
        addMessage('error', 'WebSocket error');
        status.textContent = 'Error';
        status.style.color = '#ff6b6b';
    };

    ws.onclose = () => {
        status.textContent = 'Disconnected';
        status.style.color = '#888';
        input.disabled = true;
        sendBtn.disabled = true;
    };
});

sendBtn.addEventListener('click', () => {
    const message = input.value.trim();
    if (!message || !ws) return;

    addMessage('user', message);
    ws.send(JSON.stringify({ type: "message", content: message }));
    input.value = '';
});

input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
    }
});

loadModels();
</script>

</body>
</html>
'''

if __name__ == "__main__":
    print("Starting Ollama LangChain Server...")
    print("Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
