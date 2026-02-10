# 🔗 SRL (Secure Resource Locator) - Universal Connector System

## 🎯 **Core Philosophy**

**SRL is a special type of substrate that acts as a "library card" - it knows how to fetch the book but doesn't copy it.**

### **The Library Card Analogy**

Just like a library card:
- ✅ **Grants access** to resources you have legitimate rights to
- ✅ **Fetches on demand** - only when you ask
- ✅ **Never copies** - unless explicitly requested
- ✅ **Never caches** - unless explicitly requested
- ✅ **Passive connection** - the connection exists but doesn't pull data until invoked
- ✅ **Secure** - credentials stored encrypted, never exposed

---

## 🌐 **What SRL Can Connect To**

### **Data Sources**
- **Files**: Local files, network files, cloud storage (S3, Google Drive, Dropbox)
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch
- **Data Stores**: Key-value stores, document stores, graph databases

### **APIs & Services**
- **REST APIs**: Any HTTP/HTTPS API with authentication
- **GraphQL**: GraphQL endpoints
- **Web Services**: SOAP, XML-RPC, gRPC
- **Websites**: Web scraping with authentication

### **Streaming & Real-time**
- **Streams**: Kafka, RabbitMQ, MQTT, WebSockets
- **Real-time**: Server-Sent Events (SSE), WebRTC
- **Feeds**: RSS, Atom, JSON feeds

### **Applications & Games**
- **Other Apps**: Inter-app communication via APIs
- **Game Servers**: Game state, player data, leaderboards
- **Microservices**: Service mesh connections

### **Anything with Credentials**
If you have legitimate access and credentials, SRL can connect to it.

---

## 🏗️ **SRL Architecture**

### **1. SRL Substrate**

An SRL is a **special substrate** with:
- **Category**: `"srl"` (Secure Resource Locator)
- **Expression**: Connection logic (how to fetch)
- **Identity**: 64-bit hash of connection parameters
- **Metadata**: Resource type, description, tags

### **2. Connection Registry**

Stores connection configurations:
- **Resource Type**: file, database, api, stream, etc.
- **Connection String**: URL, host, port, path
- **Protocol**: http, https, postgresql, mongodb, kafka, etc.
- **Authentication Method**: basic, bearer, oauth, api_key, certificate

### **3. Credential Vault**

Securely stores credentials:
- **Encrypted Storage**: AES-256 encryption
- **Per-User Credentials**: Each user has their own credentials
- **Never Exposed**: Credentials NEVER sent to client
- **Rotation Support**: Credentials can be updated

### **4. Connection Adapters**

Protocol-specific adapters:
- **FileAdapter**: Local files, S3, FTP, SFTP
- **DatabaseAdapter**: PostgreSQL, MySQL, MongoDB, Redis
- **APIAdapter**: REST, GraphQL, SOAP
- **StreamAdapter**: Kafka, RabbitMQ, WebSocket
- **WebAdapter**: HTTP requests, web scraping

---

## 🔐 **Security Model**

### **Principle: Zero Trust, Maximum Security**

1. **Credentials Never Leave Server**
   - Stored encrypted in database
   - Decrypted only in memory during fetch
   - Never sent to client

2. **User Ownership**
   - Each SRL belongs to a user
   - Only owner can invoke SRL
   - Credentials are per-user

3. **Audit Trail**
   - Every fetch is logged
   - Timestamp, user, resource, result
   - Compliance-ready

4. **Rate Limiting**
   - Prevent abuse
   - Respect API rate limits
   - Configurable per-resource

---

## 📊 **SRL Lifecycle**

### **1. Registration** (Create SRL)

```json
POST /api/v1/srl/register
{
    "name": "my_postgres_db",
    "resource_type": "database",
    "protocol": "postgresql",
    "connection_string": "postgresql://localhost:5432/mydb",
    "auth_method": "password",
    "credentials": {
        "username": "user",
        "password": "secret"
    },
    "metadata": {
        "description": "Production database",
        "tags": ["production", "postgres"]
    }
}
```

**Result**: SRL substrate created with 64-bit identity

### **2. Invocation** (Fetch Data)

```json
POST /api/v1/srl/{srl_id}/fetch
{
    "query": "SELECT * FROM users WHERE id = 123",
    "cache": false  // Don't cache unless explicitly requested
}
```

**Result**: Data fetched from resource, returned to user

### **3. Optional Caching**

```json
POST /api/v1/srl/{srl_id}/fetch
{
    "query": "SELECT * FROM products",
    "cache": true,
    "cache_ttl": 3600  // Cache for 1 hour
}
```

**Result**: Data fetched and cached for specified duration

### **4. Credential Update**

```json
PUT /api/v1/srl/{srl_id}/credentials
{
    "username": "new_user",
    "password": "new_secret"
}
```

**Result**: Credentials updated (encrypted)

---

## 🎭 **SRL as a Substrate**

### **Why SRL is a Substrate**

1. **64-bit Identity**: Unique hash of connection parameters
2. **Expression**: The connection logic (how to fetch)
3. **Invocation**: Fetching data is invoking the substrate
4. **Lazy Evaluation**: No data fetched until invoked
5. **Dimensional**: Can be divided, multiplied, related to other substrates

### **Example SRL Substrate**

```python
{
    "substrate_category": "srl",
    "expression_type": "connection",
    "expression_code": "postgresql://localhost:5432/mydb",
    "dimension_level": 0,  // 0D = point (single connection)
    "metadata": {
        "name": "Production DB",
        "resource_type": "database",
        "protocol": "postgresql",
        "auth_method": "password"
    }
}
```

---

## 🔄 **Passive vs Active Connections**

### **Passive (Default)**
- Connection exists but doesn't pull data
- Like a library card in your wallet
- Zero resource usage until invoked
- **This is the SRL way**

### **Active (Optional)**
- Connection actively pulls data
- Like subscribing to a magazine
- Continuous resource usage
- Only when explicitly requested (e.g., streaming)

---

## 📡 **Connection Types**

### **1. Pull (Request-Response)**
- **Files**: Read file content
- **Databases**: Execute query
- **APIs**: HTTP request
- **Default behavior**: Fetch when invoked

### **2. Push (Streaming)**
- **Streams**: Subscribe to topic
- **WebSockets**: Receive messages
- **SSE**: Server-sent events
- **Special handling**: Active connection with buffering

### **3. Hybrid**
- **Polling**: Periodic pull
- **Long-polling**: Extended request
- **Webhooks**: Push notifications

---

## 🎨 **Use Cases**

### **1. Database Integration**
```python
# Register database connection
srl = register_srl("my_db", "postgresql://...")

# Fetch data when needed
users = invoke_srl(srl, query="SELECT * FROM users")
```

### **2. API Integration**
```python
# Register API connection
srl = register_srl("weather_api", "https://api.weather.com")

# Fetch weather when needed
weather = invoke_srl(srl, endpoint="/current", params={"city": "NYC"})
```

### **3. File Access**
```python
# Register S3 bucket
srl = register_srl("s3_bucket", "s3://my-bucket/data/")

# Fetch file when needed
data = invoke_srl(srl, path="reports/2024.csv")
```

### **4. Stream Subscription**
```python
# Register Kafka topic
srl = register_srl("kafka_events", "kafka://localhost:9092/events")

# Subscribe to stream (active connection)
stream = invoke_srl(srl, mode="subscribe", buffer_size=100)
```

---

## 🛡️ **Privacy & Compliance**

### **GDPR Compliance**
- No data stored unless explicitly cached
- User controls all data access
- Right to be forgotten (delete SRL = delete access)

### **Data Minimization**
- Only fetch what's requested
- No background data collection
- Explicit user consent for caching

### **Audit Trail**
- Every fetch logged
- Compliance reports available
- Transparent data access

---

## 🚀 **Performance**

### **Zero Overhead (Passive)**
- No background connections
- No polling
- No resource usage until invoked

### **Optimized Fetching**
- Connection pooling for databases
- HTTP keep-alive for APIs
- Batch requests when possible

### **Optional Caching**
- Redis-backed cache
- User-controlled TTL
- Cache invalidation on demand

---

## 🔑 **Key Principles**

1. **Passive by Default**: No data fetched until invoked
2. **No Copying**: Data not stored unless explicitly cached
3. **Secure**: Credentials encrypted, never exposed
4. **User-Owned**: Each user has their own SRLs and credentials
5. **Auditable**: Every access logged
6. **Universal**: Connect to anything with credentials
7. **Substrate-Based**: SRL is a special substrate type

---

## 📁 **Database Schema**

### **SRL Substrate**
- Inherits from `SubstrateModel`
- `substrate_category = "srl"`
- `expression_code` = connection logic

### **Connection Table**
- `id`, `srl_substrate_id`, `resource_type`, `protocol`
- `connection_string`, `auth_method`
- `owner_id`, `created_at`, `updated_at`

### **Credential Vault**
- `id`, `connection_id`, `user_id`
- `encrypted_credentials` (AES-256)
- `created_at`, `updated_at`, `last_rotated`

### **Fetch Log**
- `id`, `srl_id`, `user_id`, `timestamp`
- `query`, `result_size`, `cached`, `duration_ms`

---

🔗 **SRL: The library card that fetches the book but never copies it.** 🔗

