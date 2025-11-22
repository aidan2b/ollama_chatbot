#!/usr/bin/env python3
"""
Ollama Interface Server
Serves the HTML interface and proxies requests to avoid CORS issues
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import json
import os

class OllamaProxyHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        # Proxy POST requests to Ollama
        if self.path.startswith('/api/'):
            ollama_url = f'http://localhost:11434{self.path}'
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Forward to Ollama
            try:
                if self.path == '/api/generate' or self.path == '/api/pull':
                    # Streaming endpoints
                    response = requests.post(
                        ollama_url, 
                        data=post_data,
                        headers={'Content-Type': 'application/json'},
                        stream=True
                    )
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            self.wfile.write(chunk)
                else:
                    # Non-streaming endpoints
                    response = requests.post(
                        ollama_url,
                        data=post_data,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    self.send_response(response.status_code)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.content)
                    
            except Exception as e:
                self.send_error(500, f"Proxy error: {str(e)}")
        else:
            self.send_error(404)
    
    def do_GET(self):
        # Proxy GET requests to Ollama API
        if self.path.startswith('/api/'):
            ollama_url = f'http://localhost:11434{self.path}'
            try:
                response = requests.get(ollama_url)
                self.send_response(response.status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.content)
            except Exception as e:
                self.send_error(500, f"Proxy error: {str(e)}")
        else:
            # Serve files normally
            super().do_GET()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    port = 8888
    server = HTTPServer(('localhost', port), OllamaProxyHandler)
    
    print(f"🌐 Ollama Interface Server")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🔗 Access at: http://localhost:{port}/ollama_interface.html")
    print(f"🔧 Proxying Ollama API calls to avoid CORS")
    print(f"\nPress Ctrl+C to stop...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✨ Server stopped")