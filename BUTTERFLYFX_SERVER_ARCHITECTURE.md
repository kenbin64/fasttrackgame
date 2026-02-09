# BUTTERFLYFX SERVER ARCHITECTURE

**Date:** 2026-02-09  
**Purpose:** Expose ButterflyFx substrate operations as a production HTTP server  
**Philosophy:** "Substrates are mathematical expressions, not data containers" - now accessible via API

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATIONS                      │
│  (Web Apps, Mobile Apps, CLI Tools, Other Services)         │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                   BUTTERFLYFX SERVER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  REST API Layer (FastAPI)                             │  │
│  │  - Substrate CRUD                                     │  │
│  │  - Dimensional Operations (divide, multiply, invoke)  │  │
│  │  - Relationship Management                            │  │
│  │  - Query Engine                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Server Core                                          │  │
│  │  - Substrate Registry (in-memory)                     │  │
│  │  - Relationship Graph                                 │  │
│  │  - Authentication & Authorization                     │  │
│  │  - Rate Limiting                                      │  │
│  └───────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  DimensionOS Core (Existing)                          │  │
│  │  - kernel/ (pure math)                                │  │
│  │  - core/ (bridge layer)                               │  │
│  │  - interface/ (Human, Machine, AI)                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Web Framework** | FastAPI | Async, high-performance, auto-docs, type hints |
| **Server** | Uvicorn | ASGI server, production-ready, WebSocket support |
| **Serialization** | JSON + Pydantic | Type-safe, validation, OpenAPI schema |
| **Authentication** | JWT + API Keys | Stateless, scalable, industry standard |
| **Rate Limiting** | slowapi | Prevent abuse, protect substrate operations |
| **Logging** | Dimensional Logging | Existing system (kernel/logging.py) |
| **Testing** | pytest + httpx | Async test client, existing test infrastructure |

---

## API DESIGN

### REST Endpoints

#### **Substrate Operations**

```
POST   /api/v1/substrates              Create substrate
GET    /api/v1/substrates/{id}         Get substrate by identity
DELETE /api/v1/substrates/{id}         Delete substrate
POST   /api/v1/substrates/{id}/divide  Divide substrate (returns 9 dimensions)
POST   /api/v1/substrates/{id}/invoke  Invoke substrate expression
POST   /api/v1/substrates/multiply     Multiply dimensions to unity
```

#### **Relationship Operations**

```
POST   /api/v1/relationships            Create relationship
GET    /api/v1/relationships/{id}       Get relationship
GET    /api/v1/relationships/outgoing/{substrate_id}  Get outgoing relationships
GET    /api/v1/relationships/incoming/{substrate_id}  Get incoming relationships
GET    /api/v1/relationships/graph      Query relationship graph
```

#### **Query Operations**

```
POST   /api/v1/query/traverse           Traverse relationship graph
POST   /api/v1/query/search             Search substrates by criteria
GET    /api/v1/query/stats              Get system statistics
```

#### **System Operations**

```
GET    /api/v1/health                   Health check
GET    /api/v1/metrics                  Prometheus metrics
GET    /api/v1/docs                     OpenAPI documentation (auto-generated)
```

---

## REQUEST/RESPONSE FORMATS

### Create Substrate

**Request:**
```json
POST /api/v1/substrates
{
  "expression_type": "lambda",
  "expression_code": "lambda **kw: kw.get('x', 0) * kw.get('y', 0)",
  "metadata": {
    "name": "multiply_substrate",
    "description": "Multiplies x and y"
  }
}
```

**Response:**
```json
{
  "substrate_id": "0x1A2B3C4D5E6F7890",
  "identity": 1883899461035270288,
  "created_at": "2026-02-09T12:34:56Z",
  "expression_type": "lambda",
  "metadata": {
    "name": "multiply_substrate",
    "description": "Multiplies x and y"
  }
}
```

### Divide Substrate

**Request:**
```json
POST /api/v1/substrates/0x1A2B3C4D5E6F7890/divide
{}
```

**Response:**
```json
{
  "substrate_id": "0x1A2B3C4D5E6F7890",
  "dimensions": [
    {"level": 0, "name": "Void", "description": "Potential"},
    {"level": 1, "name": "Identity", "description": "Who"},
    {"level": 1, "name": "Domain", "description": "What type"},
    {"level": 2, "name": "Length", "description": "Attributes"},
    {"level": 3, "name": "Area", "description": "Relationships"},
    {"level": 5, "name": "Volume", "description": "State + change"},
    {"level": 8, "name": "Frequency", "description": "Temporal patterns"},
    {"level": 13, "name": "System", "description": "Behaviors"},
    {"level": 21, "name": "Complete", "description": "Whole object"}
  ],
  "fibonacci_sequence": [0, 1, 1, 2, 3, 5, 8, 13, 21]
}
```

### Invoke Substrate

**Request:**
```json
POST /api/v1/substrates/0x1A2B3C4D5E6F7890/invoke
{
  "parameters": {
    "x": 5,
    "y": 7
  }
}
```

**Response:**
```json
{
  "substrate_id": "0x1A2B3C4D5E6F7890",
  "result": 35,
  "invocation_time_ms": 0.023
}
```

---

## AUTHENTICATION & AUTHORIZATION

### API Key Authentication

```
GET /api/v1/substrates/0x1A2B3C4D5E6F7890
Authorization: Bearer sk-butterflyfx-1234567890abcdef
```

### JWT Authentication (for user sessions)

```
POST /api/v1/auth/login
{
  "username": "ken",
  "password": "********"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## RATE LIMITING

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1675958400
```

**Limits:**
- **Free Tier:** 100 requests/minute
- **Pro Tier:** 1,000 requests/minute
- **Enterprise:** Unlimited

---

## SCALING STRATEGY

### Phase 1: Single Server (Current)
- In-memory substrate registry
- Single Uvicorn process
- Good for: 1,000-10,000 substrates

### Phase 2: Horizontal Scaling
- Multiple server instances behind load balancer
- Shared Redis for substrate registry
- Good for: 10,000-1,000,000 substrates

### Phase 3: Distributed
- Substrate sharding by identity hash
- Distributed relationship graph (Neo4j/TigerGraph)
- Good for: 1,000,000+ substrates

---

## NEXT STEPS

1. ✅ Design complete
2. ⏳ Implement FastAPI server (`server/main.py`)
3. ⏳ Implement substrate endpoints
4. ⏳ Implement relationship endpoints
5. ⏳ Add authentication
6. ⏳ Add rate limiting
7. ⏳ Write API tests
8. ⏳ Deploy to production


