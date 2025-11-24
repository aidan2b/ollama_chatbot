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
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import subprocess
import json
from typing import Optional, List

try:
    from langchain_core.callbacks.base import AsyncCallbackHandler
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import BaseMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_ollama import ChatOllama
    import uvicorn
except ImportError:
    print("Installing required packages...")
    subprocess.check_call(["pip", "install", "fastapi", "uvicorn", "langchain", "langchain-core", "langchain-community", "langchain-ollama", "websockets", "--quiet"])
    from langchain_core.callbacks.base import AsyncCallbackHandler
    from langchain_core.chat_history import BaseChatMessageHistory
    from langchain_core.messages import BaseMessage
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.runnables.history import RunnableWithMessageHistory
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

# Global model storage and chat histories
models = {}
chat_histories = {}

class InMemoryChatHistory(BaseChatMessageHistory):
    """Simple in-memory chat history"""
    def __init__(self):
        self.messages: List[BaseMessage] = []

    def add_message(self, message: BaseMessage) -> None:
        self.messages.append(message)

    def clear(self) -> None:
        self.messages = []

def get_chat_history(session_id: str) -> BaseChatMessageHistory:
    """Get or create chat history for a session"""
    if session_id not in chat_histories:
        chat_histories[session_id] = InMemoryChatHistory()
    return chat_histories[session_id]

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
    html_path = Path(__file__).parent / "interface.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    else:
        return HTMLResponse(content="<h1>Error: interface.html not found</h1>", status_code=500)

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
    
@app.get("/themes.css")
async def serve_themes():
    """Serve the themes CSS file"""
    css_path = Path(__file__).parent / "themes.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    else:
        raise HTTPException(status_code=404, detail="themes.css not found")

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
    
    # Generate unique session ID for this connection
    session_id = f"{model_name}_{id(websocket)}"

    try:
        # Create fresh callback for this WebSocket connection
        callback = WebSocketCallback(websocket)
        
        # Create base model if not exists
        if model_name not in models:
            models[model_name] = ChatOllama(model=model_name)
        
        # Create prompt template with memory
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Chain with message history
        chain = prompt | models[model_name]
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_chat_history,
            input_messages_key="input",
            history_messages_key="history"
        )

        await websocket.send_json({"type": "system", "content": f"Connected to {model_name}"})
        
        # Send introduction with callback
        await websocket.send_json({"type": "start"})
        intro_prompt = "Introduce yourself briefly - your model name and capabilities."
        await chain_with_history.ainvoke(
            {"input": intro_prompt},
            config={"configurable": {"session_id": session_id}, "callbacks": [callback]}
        )
        await websocket.send_json({"type": "end"})

        while True:
            data = await websocket.receive_json()

            if data["type"] == "message":
                user_message = data["content"]
                await websocket.send_json({"type": "start"})
                
                # Invoke with conversation history and callback
                await chain_with_history.ainvoke(
                    {"input": user_message},
                    config={"configurable": {"session_id": session_id}, "callbacks": [callback]}
                )
                
                await websocket.send_json({"type": "end"})

    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        # Cleanup session history on disconnect
        if session_id in chat_histories:
            del chat_histories[session_id]
        await websocket.close()

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

if __name__ == "__main__":
    print("Starting Ollama LangChain Server...")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("\n❌ ERROR: Ollama is not running or not installed!")
        print("Please start Ollama first:")
        print("  - Run 'ollama serve' in another terminal")
        print("  - Or install from: https://ollama.com/download")
        exit(1)
    
    print("✓ Ollama detected")
    print("Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)