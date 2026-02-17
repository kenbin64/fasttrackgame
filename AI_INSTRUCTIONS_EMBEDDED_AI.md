# AI INSTRUCTIONS: ButterflyFX Embedded AI Substrate

## Overview

The AI Substrate (`helix/ai_substrate.py`) implements dimensional AI cognition for ButterflyFX. It wraps embedded language models (Ollama, OpenAI, local models) in the 7-level helix paradigm, treating AI reasoning as navigation through cognitive dimensions.

## Cognitive Level Mapping

AI operations map to the dimensional helix:

| Level | Name | Fibonacci | AI Operation |
|-------|------|-----------|--------------|
| 0 | VOID | 0 | Pre-activation, null state |
| 1 | POINT | 1 | Token embeddings (identity) |
| 2 | LINE | 1 | Attention patterns (relationships) |
| 3 | WIDTH | 2 | Semantic similarity (patterns) |
| 4 | PLANE | 3 | Response generation (INVOKE) |
| 5 | VOLUME | 5 | Context aggregation (memory) |
| 6 | WHOLE | 8 | Intent understanding (meaning) |

## Communication Protocols

### SYNC Protocol
Blocking request/response. Traditional AI interaction.

```python
from helix.ai_substrate import AIKernel

kernel = AIKernel("ollama:phi3:mini")
response = kernel.ask("What is ButterflyFX?")
```

### ASYNC Protocol  
Non-blocking with Future. For parallel operations.

```python
future = kernel.substrate.invoke_async("Complex question...", 
    callback=lambda t: print(f"Done: {t.content}"))
# Continue other work...
result = future.result()  # Block when needed
```

### STREAM Protocol
Token-by-token streaming. For real-time display.

```python
for token in kernel.stream("Tell me a story"):
    print(token, end="", flush=True)
```

### SPIRAL Protocol
Multi-turn conversation with level navigation.

```python
kernel.chat("Hello!")
kernel.spiral_up()  # Move to abstraction
response = kernel.chat("What's the big picture?")
kernel.spiral_down()  # Move to specifics
response = kernel.chat("Give me details")
```

## Core Classes

### CognitiveToken
A thought-unit in the dimensional substrate.

```python
τ = (content, level, signature, metadata)
```

- `content`: The response/embedding/thought
- `level`: CognitiveLevel (0-6)
- `signature`: SHA-256 identity hash
- `metadata`: Model info, latency, etc.

### AISubstrate
The dimensional intelligence layer.

```python
S = (M, T, R) where:
    M = Cognitive manifold (7-level helix)
    T = Token space (thoughts, responses)
    R = Relations (conversation threads)
```

### AIKernel
High-level interface wrapping AISubstrate.

```python
kernel = AIKernel("ollama:phi3:mini")
kernel.ask(question)       # Quick Q&A
kernel.chat(message)       # Multi-turn
kernel.embed(text)         # Get vector
kernel.spiral_up()         # Navigate up
kernel.spiral_down()       # Navigate down
```

## Backend Configuration

### Ollama (Recommended for Local)
```python
from helix.ai_substrate import AIKernel, OllamaBackend

# Simple
kernel = AIKernel("ollama:phi3:mini")

# Custom
backend = OllamaBackend(
    model="mistral:7b",
    base_url="http://localhost:11434"
)
kernel = AIKernel(backend)
```

### OpenAI (Cloud)
```python
# Using environment variable OPENAI_API_KEY
kernel = AIKernel("openai:gpt-4o-mini")

# Or explicit
from helix.ai_substrate import OpenAIBackend
backend = OpenAIBackend(
    model="gpt-4o",
    api_key="sk-..."
)
```

### Mock (Testing)
```python
from helix.ai_substrate import MockBackend

backend = MockBackend(responses={
    "What is 2+2?": "4"
})
kernel = AIKernel(backend)
```

## Level-Specific Operations

### Level 1 (POINT) - Embeddings
```python
# Generate embedding vector
token = kernel.substrate.embed("ButterflyFX")
vector = token.content  # List[float]
```

### Level 3 (WIDTH) - Similarity
```python
# Semantic similarity
sim = kernel.similar("cat", "dog")  # 0.0 to 1.0
```

### Level 6 (WHOLE) - Intent
```python
# Extract meaning
intent_token = kernel.substrate.understand_intent(
    "I want to deploy a web server on OpenStack"
)
```

## HTTP Channel

Expose AI substrate via HTTP:

```python
from helix.ai_substrate import AIKernel, AIChannel

kernel = AIKernel("ollama:phi3:mini")
channel = AIChannel(kernel)
channel.start_http(host="localhost", port=8765)
```

Request format:
```json
{
    "protocol": "sync",
    "action": "ask",
    "payload": {
        "question": "What is ButterflyFX?",
        "context": "Optional context..."
    }
}
```

Actions: `ask`, `chat`, `embed`, `spiral_up`, `spiral_down`, `status`

## Integration with Other Substrates

### With Universal Connector
```python
from helix.ai_substrate import AIKernel
from apps.universal_connector import UniversalConnector

kernel = AIKernel("ollama")
uc = UniversalConnector()

# AI answers questions about connected resources
resources = uc.list_resources()
answer = kernel.ask(
    "What databases are available?",
    context=str(resources)
)
```

### With OpenStack Manifold
```python
from helix.ai_substrate import AIKernel
from helix.openstack_manifold import OpenStackKernel

ai = AIKernel("ollama:phi3:mini")
cloud = OpenStackKernel()

# AI-assisted cloud operations
vms = cloud.get_all_tokens("vm")
recommendation = ai.ask(
    "Which VMs should be scaled down?",
    context=str(vms)
)
```

## Best Practices

1. **Start at Level 4 (PLANE)** - Default invoke level for generation
2. **spiral_up for abstraction** - Move toward intent/meaning
3. **spiral_down for specifics** - Move toward embeddings/tokens
4. **Cache embeddings** - Use `get_token(signature)` for retrieval
5. **Stream for UX** - Use STREAM protocol for user-facing responses
6. **Mock for tests** - Use MockBackend to test without real AI

## Installation

```bash
# Ollama (recommended)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini

# Python dependencies
pip install requests  # For Ollama
pip install openai    # For OpenAI (optional)
```

## Example: Full Dimensional AI Session

```python
from helix.ai_substrate import AIKernel

# Initialize with local model
kernel = AIKernel("ollama:phi3:mini")

# Start at PLANE (default)
print(f"Level: {kernel.level}")  # PLANE

# Basic question
answer = kernel.ask("What is dimensional computing?")

# Elevate to meaning
kernel.spiral_up()  # VOLUME
kernel.spiral_up()  # WHOLE
abstract = kernel.ask("What does this philosophy imply?")

# Dive to specifics
kernel.spiral_down()  # VOLUME
kernel.spiral_down()  # PLANE
kernel.spiral_down()  # WIDTH
kernel.spiral_down()  # LINE
kernel.spiral_down()  # POINT

# At POINT, work with embeddings
emb = kernel.embed("ButterflyFX")

# Check status
print(kernel.substrate.status())
```

## Related Documentation

| Document | Purpose |
|----------|---------|
| AI_INSTRUCTIONS.md | Master AI instructions |
| AI_INSTRUCTIONS_OPENSTACK.md | Cloud integration |
| AI_INSTRUCTIONS_UNIVERSAL_CONNECTOR.md | Resource connectivity |
| BUTTERFLYFX_FORMAL_KERNEL.md | Mathematical foundation |
