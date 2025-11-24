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

if __name__ == "__main__":
    print("Starting Ollama LangChain Server...")
    print("Access at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)