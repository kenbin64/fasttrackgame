#!/usr/bin/env python3
"""
ButterflyFX AI Substrate - Dimensional Intelligence Layer

Wraps embedded AI (Ollama, OpenAI, local models) in the 7-level helix paradigm.
AI cognition is mapped to dimensional levels:

    Level 6: MEANING    → Intent understanding, goal inference
    Level 5: VOLUME     → Context aggregation, memory integration  
    Level 4: PLANE      → Response generation (primary INVOKE level)
    Level 3: WIDTH      → Pattern matching, semantic similarity
    Level 2: LINE       → Token relationships, attention
    Level 1: POINT      → Token identity, embeddings
    Level 0: VOID       → Pre-prompt, null state

Communication Protocols:
    - SYNC:  Blocking request/response (traditional)
    - ASYNC: Non-blocking with callback
    - STREAM: Token-by-token streaming
    - SPIRAL: Multi-turn with level navigation

Copyright (c) 2026 ButterflyFX. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable, Generator, Union
from enum import Enum, auto
from abc import ABC, abstractmethod
import json
import time
import hashlib
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, Future

# ═══════════════════════════════════════════════════════════════════════════════
# DIMENSIONAL CONSTANTS - Fibonacci-aligned cognitive levels
# ═══════════════════════════════════════════════════════════════════════════════

class CognitiveLevel(Enum):
    """7-level cognitive helix - AI reasoning mapped to dimensions."""
    VOID = 0        # F(0)=0 - Pre-activation, null state
    POINT = 1       # F(1)=1 - Token identity, embeddings
    LINE = 2        # F(2)=1 - Token relationships, attention patterns
    WIDTH = 3       # F(3)=2 - Semantic similarity, pattern matching
    PLANE = 4       # F(4)=3 - Response generation (INVOKE level)
    VOLUME = 5      # F(5)=5 - Context aggregation, memory
    WHOLE = 6       # F(6)=8 - Intent/meaning understanding

# Fibonacci weights for each level
FIBONACCI = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8}

class CommProtocol(Enum):
    """Communication protocols for AI interaction."""
    SYNC = auto()      # Blocking request/response
    ASYNC = auto()     # Non-blocking with Future
    STREAM = auto()    # Token-by-token generator
    SPIRAL = auto()    # Multi-turn with level navigation


# ═══════════════════════════════════════════════════════════════════════════════
# COGNITIVE TOKENS - AI thoughts as dimensional tokens
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CognitiveToken:
    """
    A thought-unit in the dimensional AI substrate.
    
    τ = (content, level, signature, metadata)
    
    - content: The actual text/embedding/response
    - level: Cognitive dimension (0-6)
    - signature: SHA-256 identity hash
    - metadata: Contextual information (model, latency, etc.)
    """
    content: Any
    level: CognitiveLevel
    signature: str = field(default="")
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        if not self.signature:
            content_str = str(self.content) if not isinstance(self.content, str) else self.content
            self.signature = hashlib.sha256(
                f"{content_str}:{self.level.value}:{self.timestamp}".encode()
            ).hexdigest()[:16]
    
    def __hash__(self):
        return hash(self.signature)
    
    def __eq__(self, other):
        if not isinstance(other, CognitiveToken):
            return False
        return self.signature == other.signature
    
    def spiral_up(self) -> 'CognitiveToken':
        """Elevate token to higher cognitive level."""
        new_level = min(self.level.value + 1, 6)
        return CognitiveToken(
            content=self.content,
            level=CognitiveLevel(new_level),
            metadata={**self.metadata, "elevated_from": self.level.value},
            timestamp=time.time()
        )
    
    def spiral_down(self) -> 'CognitiveToken':
        """Reduce token to lower cognitive level."""
        new_level = max(self.level.value - 1, 0)
        return CognitiveToken(
            content=self.content,
            level=CognitiveLevel(new_level),
            metadata={**self.metadata, "reduced_from": self.level.value},
            timestamp=time.time()
        )


# ═══════════════════════════════════════════════════════════════════════════════
# MESSAGE TYPES - Structured communication
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Message:
    """A message in the AI conversation substrate."""
    role: str  # "system", "user", "assistant"
    content: str
    level: CognitiveLevel = CognitiveLevel.PLANE
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class Conversation:
    """Multi-turn conversation as dimensional spiral."""
    messages: List[Message] = field(default_factory=list)
    current_level: CognitiveLevel = CognitiveLevel.PLANE
    context_window: int = 4096
    
    def add(self, role: str, content: str, level: Optional[CognitiveLevel] = None):
        """Add message at current or specified level."""
        self.messages.append(Message(
            role=role,
            content=content,
            level=level or self.current_level
        ))
    
    def spiral_up(self):
        """Move conversation to higher abstraction."""
        if self.current_level.value < 6:
            self.current_level = CognitiveLevel(self.current_level.value + 1)
    
    def spiral_down(self):
        """Move conversation to more specific level."""
        if self.current_level.value > 0:
            self.current_level = CognitiveLevel(self.current_level.value - 1)
    
    def to_messages(self) -> List[Dict[str, str]]:
        """Export as standard message format."""
        return [m.to_dict() for m in self.messages]
    
    def token_estimate(self) -> int:
        """Rough token count (4 chars ≈ 1 token)."""
        return sum(len(m.content) // 4 for m in self.messages)


# ═══════════════════════════════════════════════════════════════════════════════
# AI BACKEND INTERFACE - Pluggable model providers
# ═══════════════════════════════════════════════════════════════════════════════

class AIBackend(ABC):
    """Abstract interface for AI model backends."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous generation."""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Streaming token generation."""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding vector (Level 1 operation)."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier."""
        pass


class OllamaBackend(AIBackend):
    """Ollama local model backend (Phi-3, Mistral, etc.)."""
    
    def __init__(self, model: str = "phi3:mini", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._session = None
    
    @property
    def name(self) -> str:
        return f"ollama:{self.model}"
    
    def _ensure_session(self):
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
            except ImportError:
                raise RuntimeError("requests library required: pip install requests")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Synchronous generation via Ollama API."""
        self._ensure_session()
        
        response = self._session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("response", "")
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Streaming generation via Ollama API."""
        self._ensure_session()
        
        response = self._session.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                **kwargs
            },
            stream=True,
            timeout=120
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
                if data.get("done", False):
                    break
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat completion via Ollama API."""
        self._ensure_session()
        
        response = self._session.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                **kwargs
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings via Ollama."""
        self._ensure_session()
        
        response = self._session.post(
            f"{self.base_url}/api/embeddings",
            json={
                "model": self.model,
                "prompt": text
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("embedding", [])


class OpenAIBackend(AIBackend):
    """OpenAI API backend (GPT-4, GPT-3.5, etc.)."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self._client = None
    
    @property
    def name(self) -> str:
        return f"openai:{self.model}"
    
    def _ensure_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                import os
                self._client = OpenAI(api_key=self.api_key or os.getenv("OPENAI_API_KEY"))
            except ImportError:
                raise RuntimeError("openai library required: pip install openai")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate via OpenAI completions."""
        self._ensure_client()
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content or ""
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """Streaming generation via OpenAI."""
        self._ensure_client()
        
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **kwargs
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings via OpenAI."""
        self._ensure_client()
        
        response = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding


class MockBackend(AIBackend):
    """Mock backend for testing without real AI."""
    
    def __init__(self, responses: Optional[Dict[str, str]] = None):
        self.responses = responses or {}
        self.call_count = 0
    
    @property
    def name(self) -> str:
        return "mock:test"
    
    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        # Check for exact match first
        if prompt in self.responses:
            return self.responses[prompt]
        # Default response
        return f"[Mock response #{self.call_count} for: {prompt[:50]}...]"
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        response = self.generate(prompt, **kwargs)
        for word in response.split():
            yield word + " "
    
    def embed(self, text: str) -> List[float]:
        # Return deterministic pseudo-embedding based on text hash
        h = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in h[:128]]


# ═══════════════════════════════════════════════════════════════════════════════
# AI SUBSTRATE - Dimensional intelligence layer
# ═══════════════════════════════════════════════════════════════════════════════

class AISubstrate:
    """
    ButterflyFX AI Substrate - Intelligence as dimensional manifold.
    
    S = (M, T, R) where:
        M = Cognitive manifold (7-level helix)
        T = Token space (thoughts, responses, embeddings)
        R = Relations (conversation threads, context links)
    
    Supports multiple communication protocols:
        - SYNC: Blocking request/response
        - ASYNC: Non-blocking with Future
        - STREAM: Token-by-token generator  
        - SPIRAL: Multi-turn with level navigation
    """
    
    def __init__(self, backend: Optional[AIBackend] = None):
        self.backend = backend or MockBackend()
        self.state: tuple[int, int] = (0, 4)  # (spiral, level) - start at PLANE
        self.conversations: Dict[str, Conversation] = {}
        self.token_cache: Dict[str, CognitiveToken] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._callbacks: Dict[str, Callable] = {}
    
    @property
    def level(self) -> CognitiveLevel:
        return CognitiveLevel(self.state[1])
    
    @property
    def spiral(self) -> int:
        return self.state[0]
    
    # ─────────────────────────────────────────────────────────────────────────
    # HELIX OPERATORS - Navigate cognitive dimensions
    # ─────────────────────────────────────────────────────────────────────────
    
    def spiral_up(self) -> CognitiveLevel:
        """Ascend to higher cognitive abstraction."""
        s, l = self.state
        if l < 6:
            self.state = (s, l + 1)
        else:
            # Wrap to next spiral
            self.state = (s + 1, 1)
        return self.level
    
    def spiral_down(self) -> CognitiveLevel:
        """Descend to more specific cognition."""
        s, l = self.state
        if l > 0:
            self.state = (s, l - 1)
        elif s > 0:
            # Wrap to previous spiral
            self.state = (s - 1, 6)
        return self.level
    
    def set_level(self, level: Union[int, CognitiveLevel]) -> CognitiveLevel:
        """Jump to specific cognitive level."""
        if isinstance(level, CognitiveLevel):
            level = level.value
        self.state = (self.state[0], max(0, min(6, level)))
        return self.level
    
    # ─────────────────────────────────────────────────────────────────────────
    # SYNC PROTOCOL - Blocking request/response
    # ─────────────────────────────────────────────────────────────────────────
    
    def invoke(self, prompt: str, **kwargs) -> CognitiveToken:
        """
        Primary INVOKE operation - synchronous generation.
        
        Materializes thought at current cognitive level.
        """
        start = time.time()
        response = self.backend.generate(prompt, **kwargs)
        latency = time.time() - start
        
        token = CognitiveToken(
            content=response,
            level=self.level,
            metadata={
                "model": self.backend.name,
                "latency_ms": int(latency * 1000),
                "prompt_chars": len(prompt),
                "response_chars": len(response)
            }
        )
        
        # Cache by signature
        self.token_cache[token.signature] = token
        return token
    
    def ask(self, question: str, context: Optional[str] = None, **kwargs) -> str:
        """Simplified invoke - returns string directly."""
        prompt = question
        if context:
            prompt = f"Context: {context}\n\nQuestion: {question}"
        return self.invoke(prompt, **kwargs).content
    
    # ─────────────────────────────────────────────────────────────────────────
    # ASYNC PROTOCOL - Non-blocking with Future
    # ─────────────────────────────────────────────────────────────────────────
    
    def invoke_async(self, prompt: str, callback: Optional[Callable] = None, **kwargs) -> Future:
        """
        Async INVOKE - returns Future, optionally calls back on completion.
        """
        def _generate():
            token = self.invoke(prompt, **kwargs)
            if callback:
                callback(token)
            return token
        
        return self.executor.submit(_generate)
    
    # ─────────────────────────────────────────────────────────────────────────
    # STREAM PROTOCOL - Token-by-token generation
    # ─────────────────────────────────────────────────────────────────────────
    
    def invoke_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Streaming INVOKE - yields tokens as they're generated.
        
        Useful for real-time display of AI responses.
        """
        yield from self.backend.generate_stream(prompt, **kwargs)
    
    def invoke_stream_collected(self, prompt: str, **kwargs) -> CognitiveToken:
        """Stream but collect into single token at end."""
        chunks = []
        start = time.time()
        
        for chunk in self.invoke_stream(prompt, **kwargs):
            chunks.append(chunk)
        
        response = "".join(chunks)
        latency = time.time() - start
        
        return CognitiveToken(
            content=response,
            level=self.level,
            metadata={
                "model": self.backend.name,
                "latency_ms": int(latency * 1000),
                "streamed": True,
                "chunk_count": len(chunks)
            }
        )
    
    # ─────────────────────────────────────────────────────────────────────────
    # SPIRAL PROTOCOL - Multi-turn conversation with level navigation
    # ─────────────────────────────────────────────────────────────────────────
    
    def conversation(self, conv_id: str = "default") -> Conversation:
        """Get or create a conversation thread."""
        if conv_id not in self.conversations:
            self.conversations[conv_id] = Conversation()
        return self.conversations[conv_id]
    
    def chat(self, message: str, conv_id: str = "default", **kwargs) -> CognitiveToken:
        """
        SPIRAL protocol - multi-turn chat with context.
        
        Maintains conversation history and current cognitive level.
        """
        conv = self.conversation(conv_id)
        conv.add("user", message)
        
        # Build chat completion
        if hasattr(self.backend, 'chat'):
            start = time.time()
            response = self.backend.chat(conv.to_messages(), **kwargs)
            latency = time.time() - start
        else:
            # Fallback to generate with context
            context = "\n".join(f"{m.role}: {m.content}" for m in conv.messages[-10:])
            token = self.invoke(context, **kwargs)
            response = token.content
            latency = token.metadata.get("latency_ms", 0) / 1000
        
        conv.add("assistant", response)
        
        return CognitiveToken(
            content=response,
            level=conv.current_level,
            metadata={
                "model": self.backend.name,
                "latency_ms": int(latency * 1000),
                "turn": len(conv.messages) // 2,
                "conv_id": conv_id
            }
        )
    
    def spiral_chat(self, message: str, direction: str = "up", conv_id: str = "default") -> CognitiveToken:
        """Chat with automatic level navigation."""
        conv = self.conversation(conv_id)
        
        if direction == "up":
            conv.spiral_up()
            prefix = "[Abstracting...] "
        elif direction == "down":
            conv.spiral_down()
            prefix = "[Specifying...] "
        else:
            prefix = ""
        
        return self.chat(prefix + message, conv_id)
    
    # ─────────────────────────────────────────────────────────────────────────
    # LEVEL OPERATIONS - Cognitive dimension specific
    # ─────────────────────────────────────────────────────────────────────────
    
    def embed(self, text: str) -> CognitiveToken:
        """
        Level 1 (POINT) operation - generate embedding vector.
        
        Projects text into vector space for similarity/retrieval.
        """
        embedding = self.backend.embed(text)
        
        return CognitiveToken(
            content=embedding,
            level=CognitiveLevel.POINT,
            metadata={
                "model": self.backend.name,
                "dimensions": len(embedding),
                "text_chars": len(text)
            }
        )
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Level 3 (WIDTH) operation - semantic similarity.
        
        Computes cosine similarity between embeddings.
        """
        import math
        
        emb1 = self.embed(text1).content
        emb2 = self.embed(text2).content
        
        # Cosine similarity
        dot = sum(a * b for a, b in zip(emb1, emb2))
        mag1 = math.sqrt(sum(a * a for a in emb1))
        mag2 = math.sqrt(sum(b * b for b in emb2))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
    
    def understand_intent(self, text: str) -> CognitiveToken:
        """
        Level 6 (WHOLE) operation - extract meaning/intent.
        
        Elevates to highest cognitive level for goal inference.
        """
        self.set_level(CognitiveLevel.WHOLE)
        
        prompt = f"""Analyze the following text and extract the core intent/meaning.
Return a JSON object with:
- "intent": primary goal or purpose
- "entities": key subjects/objects mentioned
- "action": what should happen
- "context": relevant background

Text: {text}

JSON:"""
        
        return self.invoke(prompt)
    
    # ─────────────────────────────────────────────────────────────────────────
    # UTILITY METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_token(self, signature: str) -> Optional[CognitiveToken]:
        """Retrieve cached token by signature (O(1))."""
        return self.token_cache.get(signature)
    
    def clear_cache(self):
        """Clear token cache."""
        self.token_cache.clear()
    
    def reset_conversation(self, conv_id: str = "default"):
        """Reset a conversation thread."""
        if conv_id in self.conversations:
            del self.conversations[conv_id]
    
    def status(self) -> Dict[str, Any]:
        """Get substrate status."""
        return {
            "state": self.state,
            "level": self.level.name,
            "spiral": self.spiral,
            "backend": self.backend.name,
            "cached_tokens": len(self.token_cache),
            "conversations": list(self.conversations.keys())
        }


# ═══════════════════════════════════════════════════════════════════════════════
# AI KERNEL - High-level operations
# ═══════════════════════════════════════════════════════════════════════════════

class AIKernel:
    """
    ButterflyFX AI Kernel - Unified AI interface.
    
    Wraps AISubstrate with convenient high-level operations.
    """
    
    def __init__(self, backend: Union[str, AIBackend] = "mock"):
        if isinstance(backend, str):
            backend = self._create_backend(backend)
        self.substrate = AISubstrate(backend)
    
    def _create_backend(self, backend_spec: str) -> AIBackend:
        """Create backend from spec string."""
        if backend_spec == "mock":
            return MockBackend()
        elif backend_spec.startswith("ollama:"):
            model = backend_spec.split(":", 1)[1]
            return OllamaBackend(model=model)
        elif backend_spec == "ollama":
            return OllamaBackend()
        elif backend_spec.startswith("openai:"):
            model = backend_spec.split(":", 1)[1]
            return OpenAIBackend(model=model)
        elif backend_spec == "openai":
            return OpenAIBackend()
        else:
            raise ValueError(f"Unknown backend: {backend_spec}")
    
    # Quick operations
    def ask(self, question: str, context: Optional[str] = None) -> str:
        """Simple Q&A."""
        return self.substrate.ask(question, context)
    
    def chat(self, message: str) -> str:
        """Multi-turn chat."""
        return self.substrate.chat(message).content
    
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Streaming generation."""
        return self.substrate.invoke_stream(prompt)
    
    def embed(self, text: str) -> List[float]:
        """Get embedding vector."""
        return self.substrate.embed(text).content
    
    def similar(self, text1: str, text2: str) -> float:
        """Compute similarity."""
        return self.substrate.similarity(text1, text2)
    
    # Dimensional operations
    def spiral_up(self):
        """Move to higher abstraction."""
        return self.substrate.spiral_up()
    
    def spiral_down(self):
        """Move to more specific."""
        return self.substrate.spiral_down()
    
    @property
    def level(self) -> str:
        """Current cognitive level name."""
        return self.substrate.level.name


# ═══════════════════════════════════════════════════════════════════════════════
# COMMUNICATION CHANNELS - External interfaces
# ═══════════════════════════════════════════════════════════════════════════════

class AIChannel:
    """
    Communication channel for AI substrate.
    
    Provides WebSocket, HTTP, and Unix socket interfaces.
    """
    
    def __init__(self, kernel: AIKernel):
        self.kernel = kernel
        self.message_queue = queue.Queue()
        self._running = False
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and return response.
        
        Message format:
        {
            "protocol": "sync|async|stream|spiral",
            "action": "ask|chat|embed|spiral_up|spiral_down|status",
            "payload": { ... }
        }
        """
        protocol = message.get("protocol", "sync")
        action = message.get("action", "ask")
        payload = message.get("payload", {})
        
        try:
            if action == "ask":
                result = self.kernel.ask(
                    payload.get("question", ""),
                    payload.get("context")
                )
                return {"status": "ok", "result": result}
            
            elif action == "chat":
                result = self.kernel.chat(payload.get("message", ""))
                return {"status": "ok", "result": result}
            
            elif action == "embed":
                result = self.kernel.embed(payload.get("text", ""))
                return {"status": "ok", "result": result}
            
            elif action == "spiral_up":
                level = self.kernel.spiral_up()
                return {"status": "ok", "level": level.name}
            
            elif action == "spiral_down":
                level = self.kernel.spiral_down()
                return {"status": "ok", "level": level.name}
            
            elif action == "status":
                return {"status": "ok", "result": self.kernel.substrate.status()}
            
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def start_http(self, host: str = "localhost", port: int = 8765):
        """Start HTTP server for AI channel."""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        channel = self
        
        class AIHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                message = json.loads(body)
                
                response = channel.handle_message(message)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        server = HTTPServer((host, port), AIHandler)
        print(f"AI Channel listening on http://{host}:{port}")
        self._running = True
        server.serve_forever()


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI for AI Substrate testing."""
    import sys
    
    print("═" * 60)
    print("ButterflyFX AI Substrate - Dimensional Intelligence")
    print("═" * 60)
    
    # Test with mock backend
    kernel = AIKernel("mock")
    
    print(f"\nBackend: {kernel.substrate.backend.name}")
    print(f"Level: {kernel.level}")
    
    # Test sync invoke
    print("\n--- SYNC Protocol ---")
    response = kernel.ask("What is the meaning of life?")
    print(f"Response: {response}")
    
    # Test spiral navigation
    print("\n--- Spiral Navigation ---")
    print(f"Current: {kernel.level}")
    kernel.spiral_up()
    print(f"After spiral_up: {kernel.level}")
    kernel.spiral_down()
    kernel.spiral_down()
    print(f"After 2x spiral_down: {kernel.level}")
    
    # Test chat
    print("\n--- SPIRAL Protocol (Chat) ---")
    kernel.chat("Hello!")
    response = kernel.chat("What did I just say?")
    print(f"Chat response: {response}")
    
    # Test embedding
    print("\n--- Embedding (Level 1) ---")
    emb = kernel.embed("ButterflyFX dimensional computing")
    print(f"Embedding dims: {len(emb)}")
    
    # Test similarity
    print("\n--- Similarity (Level 3) ---")
    sim = kernel.similar("cat", "dog")
    print(f"Similarity(cat, dog): {sim:.4f}")
    
    print("\n--- Status ---")
    print(kernel.substrate.status())
    
    print("\n✓ AI Substrate operational!")
    
    # If Ollama available, test it
    if "--ollama" in sys.argv:
        print("\n" + "=" * 60)
        print("Testing Ollama Backend")
        print("=" * 60)
        
        try:
            ollama_kernel = AIKernel("ollama:phi3:mini")
            response = ollama_kernel.ask("What is 2+2?")
            print(f"Ollama response: {response}")
        except Exception as e:
            print(f"Ollama test failed: {e}")


if __name__ == "__main__":
    main()
