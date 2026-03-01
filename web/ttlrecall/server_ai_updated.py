#!/usr/bin/env python3
"""
TTL Recall API Server with Real AI Integration
Supports multiple AI providers with automatic fallback
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import time
import requests
import sys

app = Flask(__name__)
CORS(app)

# Memory storage (simple in-memory for now)
conversation_memory = {}

def log(message):
    """Log to stderr so it shows in journalctl"""
    print(message, file=sys.stderr, flush=True)

def call_openai(prompt, api_key, conversation_id=None):
    """Call OpenAI API"""
    if not api_key:
        return None, "OpenAI API key not provided"
    
    messages = conversation_memory.get(conversation_id, [])
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_message = result["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": ai_message})
            conversation_memory[conversation_id] = messages[-10:]
            return ai_message, None
        else:
            error_msg = f"OpenAI API error: {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
            except:
                error_msg += f" - {response.text}"
            return None, error_msg
    except Exception as e:
        return None, f"OpenAI error: {str(e)}"

def call_gemini(prompt, api_key, conversation_id=None):
    """Call Google Gemini API"""
    if not api_key:
        log("[GEMINI] No API key provided")
        return None, "Gemini API key not provided"
    
    log(f"[GEMINI] Calling API with key length: {len(api_key)}")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"}, json=data, timeout=30)
        
        log(f"[GEMINI] Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            log(f"[GEMINI] Success! Response keys: {list(result.keys())}")
            ai_message = result["candidates"][0]["content"]["parts"][0]["text"]
            return ai_message, None
        else:
            error_msg = f"Gemini API error: {response.status_code}"
            try:
                error_data = response.json()
                log(f"[GEMINI] Error response: {error_data}")
                error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
            except:
                error_msg += f" - {response.text}"
            log(f"[GEMINI] {error_msg}")
            return None, error_msg
    except Exception as e:
        log(f"[GEMINI] Exception: {str(e)}")
        return None, f"Gemini error: {str(e)}"

def generate_intelligent_stub(prompt):
    """Generate a more intelligent stub response"""
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
        return "Hello! I'm TTL Recall, an AI with perfect memory. I'm currently in demo mode. To unlock full AI capabilities, click the Settings button and add your OpenAI or Gemini API key. What would you like to know?"
    
    if any(word in prompt_lower for word in ["who are you", "what are you"]):
        return "I'm TTL Recall - an AI system with perfect memory. I'm running in demo mode right now. Add your API key in Settings to enable full AI capabilities with OpenAI or Gemini!"
    
    if any(word in prompt_lower for word in ["help", "what can you do"]):
        return "I can help you with:\n• 💬 Intelligent conversations (with perfect memory)\n• 🎤 Voice commands and responses\n• 🎨 Image generation\n• 🎬 Video creation\n\n⚙️ Click Settings to add your API key and unlock full AI power!"
    
    return f"I understand: '{prompt}'. I'm in demo mode. Click the Settings button (⚙️) in the top right to add your OpenAI or Gemini API key for full AI capabilities!"

def get_ai_response(prompt, api_key=None, provider="auto", conversation_id=None):
    """Get AI response with automatic fallback"""
    
    log(f"[AI] Request - Provider: {provider}, API Key: {'Yes' if api_key else 'No'}")
    
    # Try with provided API key first
    if api_key:
        if provider == "gemini":
            log("[AI] Trying Gemini...")
            response, error = call_gemini(prompt, api_key, conversation_id)
            if response:
                log("[AI] Gemini success!")
                return response, "gemini"
            log(f"[AI] Gemini failed: {error}")
        
        if provider == "openai":
            log("[AI] Trying OpenAI...")
            response, error = call_openai(prompt, api_key, conversation_id)
            if response:
                log("[AI] OpenAI success!")
                return response, "openai"
            log(f"[AI] OpenAI failed: {error}")
    
    # Fallback to environment variables
    env_openai_key = os.environ.get("OPENAI_API_KEY", "")
    if env_openai_key:
        response, error = call_openai(prompt, env_openai_key, conversation_id)
        if response:
            return response, "openai"
    
    env_gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if env_gemini_key:
        response, error = call_gemini(prompt, env_gemini_key, conversation_id)
        if response:
            return response, "gemini"
    
    # Fallback to intelligent stub
    log("[AI] Falling back to stub")
    return generate_intelligent_stub(prompt), "stub"

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "ttlrecall-api",
        "version": "2.0.0"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    conversation_id = data.get("conversation_id", "default")
    
    # Get API key from headers
    api_key = request.headers.get("X-API-Key", "")
    provider = request.headers.get("X-Provider", "auto")
    
    key_info = f"Yes (len={len(api_key)})" if api_key else "No"
    log(f"[CHAT] Request - Provider: {provider}, API Key: {key_info}")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    
    response, used_provider = get_ai_response(prompt, api_key, provider, conversation_id)
    
    log(f"[CHAT] Response - Provider used: {used_provider}")
    
    return jsonify({
        "response": response,
        "provider": used_provider,
        "cached": False,
        "conversation_id": conversation_id
    })

@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.json
    prompt = data.get("prompt", "")
    conversation_id = data.get("conversation_id", "default")
    
    api_key = request.headers.get("X-API-Key", "")
    provider = request.headers.get("X-Provider", "auto")
    
    def generate():
        response, used_provider = get_ai_response(prompt, api_key, provider, conversation_id)
        words = response.split()
        for word in words:
            yield f"data: {json.dumps({'content': word + ' ', 'provider': used_provider})}\n\n"
            time.sleep(0.05)
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream")

@app.route("/api/image/generate", methods=["POST"])
def generate_image():
    data = request.json
    prompt = data.get("prompt", "")
    return jsonify({
        "url": "https://via.placeholder.com/1024x1024?text=Image+Generation+Coming+Soon",
        "provider": "placeholder",
        "prompt": prompt
    })

@app.route("/api/video/generate", methods=["POST"])
def generate_video():
    data = request.json
    prompt = data.get("prompt", "")
    return jsonify({
        "job_id": "placeholder-" + str(int(time.time())),
        "status": "processing",
        "prompt": prompt
    })

@app.route("/api/video/status/<job_id>", methods=["GET"])
def video_status(job_id):
    return jsonify({
        "status": "completed",
        "url": "https://www.w3schools.com/html/mov_bbb.mp4",
        "progress": 100
    })

if __name__ == "__main__":
    log("=" * 60)
    log("TTL Recall API Server v2.0")
    log("=" * 60)
    log("Accepts API keys via X-API-Key header")
    log("Supports: OpenAI, Gemini")
    log("=" * 60)
    log("Running on http://0.0.0.0:8081")
    log("=" * 60)
    
    app.run(host="0.0.0.0", port=8081)
