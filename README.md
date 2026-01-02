# Ollama Chatbot

A feature-rich chatbot interface built with Gradio and LangChain for interacting with Ollama models.

## Requirements

- Python 3.8+
- Ollama running locally

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Create a .env file from the example
cp .env.example .env
```

## Usage

```bash
python run.py
```

The application will start on `http://localhost:7860`

## Features

### Core Features
- 🤖 **Chat with local Ollama models** - Full conversation interface
- 🎛️ **Custom system prompts** - Define assistant behavior and personality
- 🔄 **Dynamic model loading** - Automatically fetch available models from Ollama
- 📋 **Model selection** - Choose from available local models
- 💬 **Conversation history** - Maintain chat context

### Advanced Features
- ⚡ **LLM instance caching** ✅ - Improved performance with cached model instances
- 🔄 **Model refresh** ✅ - Manual refresh of available models
- 🧹 **Cache management** ✅ - Clear cache when needed
- 🛡️ **Input sanitization** ✅ - Basic security for user inputs
- 📊 **Model information** ✅ - Detailed model info and capabilities
- 💾 **System prompt persistence** ✅ - Save and load system prompts between sessions
- 💬 **Conversation history persistence** ✅ - Save and load chat conversations

### UI/UX Enhancements
- 🎨 **Loading indicators** ✅ - Visual feedback during model responses
- 📱 **Responsive design** ✅ - Works on different screen sizes
- 🔄 **Real-time updates** ✅ - Model info updates automatically
- 🎯 **Error handling** ✅ - User-friendly error messages
- 📋 **Sidebar reorganization** ✅ - Cleaner layout with better organization

### Upcoming Features
- 💬 **Conversation history persistence** - Save and load chat conversations
- ⏱️ **Rate limiting** - Prevent abuse and manage resources
- ⚙️ **Model parameter controls** - Adjust temperature, top_p, etc.
- 👥 **Multi-user support** - Multiple users and sessions
- 🔐 **Authentication** - Secure access to the application

## Configuration

The application supports configuration via environment variables or `.env` file:

```env
# Ollama Server Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=120

# Application Configuration
APP_TITLE="Ollama Chat"
APP_DESCRIPTION="A sleek interface for local LLM conversations"
CHAT_HEIGHT=550
MAX_MESSAGE_LENGTH=10000
MAX_SYSTEM_PROMPT_LENGTH=5000

# Cache Configuration
CACHE_SIZE=100
CACHE_TTL=3600
```

## Development

### Testing

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Sort imports
isort src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Architecture

- **Config Management**: Pydantic-based settings with environment variable support
- **Caching**: LLM instance and response caching for performance
- **Error Handling**: Comprehensive error handling and user feedback
- **Security**: Input sanitization and validation
- **UI**: Gradio-based responsive interface

## Roadmap

### ✅ Completed
- [x] Add comprehensive configuration system with .env support
- [x] Implement dynamic model loading from Ollama API
- [x] Add LLM instance caching for better performance
- [x] Enhance error handling and user feedback
- [x] Add loading indicators and UI improvements
- [x] Implement system prompt persistence
- [x] Reorganize sidebar for better UX
- [x] Add conversation history persistence

### 🚀 In Progress
- [ ] Add conversation search and filtering
- [ ] Implement export/import functionality
- [ ] Add model parameter controls (temperature, top_p, etc.)
- [ ] Implement rate limiting
=======
### ✅ Completed
- [x] Add comprehensive configuration system with .env support
- [x] Implement dynamic model loading from Ollama API
- [x] Add LLM instance caching for better performance
- [x] Enhance error handling and user feedback
- [x] Add loading indicators and UI improvements
- [x] Implement system prompt persistence
- [x] Reorganize sidebar for better UX
- [x] Add conversation history persistence

### 🚀 In Progress
- [ ] Add conversation search and filtering
- [ ] Implement export/import functionality
- [ ] Add model parameter controls (temperature, top_p, etc.)
- [ ] Implement rate limiting
=======
### ✅ Completed
- [x] Add conversation history persistence
- [x] Implement rate limiting
- [x] Add model parameter controls (temperature, top_p, etc.)

### 🚀 In Progress
- [ ] Add conversation search and filtering
- [ ] Implement export/import functionality

### 📋 Planned
- [ ] Support for multiple users/sessions
- [ ] Add authentication
- [ ] Implement model downloading/pulling
- [ ] Add model performance metrics
- [ ] Add conversation search and filtering
- [ ] Implement export/import functionality
