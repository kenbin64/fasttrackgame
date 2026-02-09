# SRL Architecture - Substrate Resource Locator

**The Dimensional Way to Connect to External Resources**

---

## 🎯 Core Principle

In DimensionOS, **SRL (Substrate Resource Locator)** is the ONLY way to reference external resources.

**Traditional Approach:**
```python
# ❌ Raw URLs, credentials, connection strings in code
url = "https://api.example.com/data"
api_key = "sk-1234567890abcdef"
response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
```

**Dimensional Approach:**
```python
# ✅ SRL encodes connection rules as mathematical identity
srl = SRL(
    srl_id=SubstrateIdentity(hash("api.example.com/data") & 0xFFFFFFFFFFFFFFFF),
    resource_expression=lambda: compute_resource_identity(),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# Connection details resolved through lenses, not exposed
external_data = srl.resource_expression()
new_substrate = srl.spawn(external_data)
```

---

## 📐 What is an SRL?

An **SRL is a substrate** that encodes connection rules for external data.

**Key Properties:**
- **64-bit identity** - The SRL itself is a substrate with mathematical identity
- **No exposed credentials** - Connection details resolved through lenses
- **Lazy retrieval** - Data fetched only when invoked
- **Spawns substrates** - External data becomes new substrates

**Mathematical Expression:**
```
SRL = ⟨identity, resource_expression, spawn_rule⟩

Where:
  identity: 64-bit substrate identity
  resource_expression: λ() → resource_data
  spawn_rule: λ(data) → SubstrateIdentity
```

---

## 🏗️ SRL Architecture Layers

### Layer 1: Kernel SRL (Pure Math)

**Location:** `kernel/srl.py`

**Purpose:** Mathematical reference locator (no I/O, no connections)

```python
class SRL:
    """
    Substrate Resource Locator.
    
    A substrate that encodes connection rules for external data.
    Connection details are NEVER exposed - only the mathematical
    identity is visible.
    """
    __slots__ = ('_srl_id', '_resource_expression', '_spawn_rule')
    
    def __init__(
        self,
        srl_id: SubstrateIdentity,
        resource_expression: Callable[[], int],
        spawn_rule: Callable[[int], SubstrateIdentity]
    ):
        """
        srl_id: The 64-bit identity of this SRL
        resource_expression: Math expression encoding the resource
        spawn_rule: Function to spawn new substrate from retrieved data
        """
        object.__setattr__(self, '_srl_id', srl_id)
        object.__setattr__(self, '_resource_expression', resource_expression)
        object.__setattr__(self, '_spawn_rule', spawn_rule)
    
    def spawn(self, external_data: int) -> SubstrateIdentity:
        """
        Spawn a new substrate identity from external data.
        
        The external data is incorporated into the mathematical
        identity, not stored as a value.
        """
        return self._spawn_rule(external_data)
```

**Charter Compliance:**
- ✅ **Principle 1:** All Things Are by Reference (no data storage)
- ✅ **Principle 2:** Passive Until Invoked (lazy retrieval)
- ✅ **Principle 3:** No Self-Modifying Code (immutable)
- ✅ **Principle 5:** No Hacking Surface (pure functions)

---

### Layer 2: Core SRL (Connection Device)

**Location:** `_archive/old_implementations/core_v2/srl.py` (reference implementation)

**Purpose:** Actual I/O, protocols, credentials, connections

**Components:**

#### 1. Protocols

```python
class Protocol(ABC):
    """Base protocol for SRL connections."""
    
    @abstractmethod
    def connect(self, srl: 'SRL') -> 'SRLConnection':
        """Establish connection."""
        pass
    
    @abstractmethod
    def fetch(self, connection: 'SRLConnection', query: Optional[str]) -> bytes:
        """Fetch data through connection."""
        pass
```

**Available Protocols:**
- `FileProtocol` - Local file access
- `HTTPProtocol` - HTTP/HTTPS APIs
- `SocketProtocol` - Raw TCP sockets
- `DatabaseProtocol` - Database connections

#### 2. Credentials

```python
class Credentials(ABC):
    """Base class for authentication credentials."""
    
    @abstractmethod
    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        pass
    
    @abstractmethod
    def encrypt(self, key: bytes) -> bytes:
        """Encrypt credentials for storage."""
        pass
```

**Available Credential Types:**
- `APIKey` - API key authentication
- `BasicAuth` - HTTP Basic authentication
- `TokenAuth` - Bearer token authentication
- `CertAuth` - Certificate-based authentication

#### 3. SRL Connection

```python
@dataclass
class SRLConnection:
    """An active connection through an SRL."""
    srl: 'SRL'
    protocol: Protocol
    handle: Any
    connected: bool = False
    created_at: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_received: int = 0
    
    def fetch(self, query: Optional[str] = None) -> SRLResult:
        """Fetch data through this connection."""
        if not self.connected:
            return SRLResult(success=False, error="Not connected")
        
        data = self.protocol.fetch(self, query)
        self.bytes_received += len(data)
        
        return SRLResult(
            success=True,
            data=data,
            bit_count=len(data) * 8,
            checksum=compute_checksum(data)
        )
```

---

## 🔌 SRL Connection Patterns

### Pattern 1: File Access

```python
from kernel import SRL, SubstrateIdentity, create_srl_identity

# Create SRL for local file
file_identity = create_srl_identity(
    resource_type=1,  # File type
    resource_namespace=hash("local") & 0xFFFFFF,
    resource_path=hash("/data/file.txt") & 0xFFFFFF
)

srl = SRL(
    srl_id=SubstrateIdentity(file_identity),
    resource_expression=lambda: read_file_identity("/data/file.txt"),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# Spawn substrate from file data
file_data = srl.resource_expression()
substrate = srl.spawn(file_data)
```

### Pattern 2: HTTP API Access

```python
# Create SRL for HTTP API
api_identity = create_srl_identity(
    resource_type=2,  # HTTP type
    resource_namespace=hash("api.example.com") & 0xFFFFFF,
    resource_path=hash("/v1/data") & 0xFFFFFF
)

srl = SRL(
    srl_id=SubstrateIdentity(api_identity),
    resource_expression=lambda: fetch_api_data("https://api.example.com/v1/data"),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# Spawn substrate from API response
api_data = srl.resource_expression()
substrate = srl.spawn(api_data)
```

### Pattern 3: Database Connection

```python
# Create SRL for database
db_identity = create_srl_identity(
    resource_type=3,  # Database type
    resource_namespace=hash("postgres://localhost") & 0xFFFFFF,
    resource_path=hash("users") & 0xFFFFFF
)

srl = SRL(
    srl_id=SubstrateIdentity(db_identity),
    resource_expression=lambda: query_database("SELECT * FROM users"),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# Spawn substrate from query results
db_data = srl.resource_expression()
substrate = srl.spawn(db_data)
```

### Pattern 4: Socket Connection

```python
# Create SRL for raw socket
socket_identity = create_srl_identity(
    resource_type=4,  # Socket type
    resource_namespace=hash("192.168.1.100") & 0xFFFFFF,
    resource_path=8089  # Port number
)

srl = SRL(
    srl_id=SubstrateIdentity(socket_identity),
    resource_expression=lambda: read_socket_data("192.168.1.100", 8089),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# Spawn substrate from socket data
socket_data = srl.resource_expression()
substrate = srl.spawn(socket_data)
```

---

## 🔐 Credential Management

**The Dimensional Way:**

Credentials are **never stored in plain text**. They are:
1. Encrypted with a key derived from substrate identity
2. Stored as mathematical expressions
3. Resolved through lenses at connection time

```python
# Traditional approach (❌ INSECURE)
api_key = "sk-1234567890abcdef"  # Plain text in code!
headers = {"Authorization": f"Bearer {api_key}"}

# Dimensional approach (✅ SECURE)
# Credentials encoded in SRL identity
credential_identity = hash("api_credentials") & 0xFFFFFFFFFFFFFFFF

# Actual credentials resolved through lens at runtime
def resolve_credentials(identity: SubstrateIdentity) -> bytes:
    """Resolve credentials from identity through secure lens."""
    # Credentials decrypted from secure storage
    # Never exposed in code
    return decrypt_credentials(identity)

srl = SRL(
    srl_id=SubstrateIdentity(credential_identity),
    resource_expression=lambda: fetch_with_credentials(resolve_credentials),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)
```

---

## 📊 SRL Identity Encoding

The 64-bit SRL identity encodes connection information:

```
┌─────────────┬──────────────────┬──────────────────┐
│ Type (16b)  │ Namespace (24b)  │ Path (24b)       │
├─────────────┼──────────────────┼──────────────────┤
│ 0x0001      │ 0xABCDEF         │ 0x123456         │
└─────────────┴──────────────────┴──────────────────┘
     ↓                ↓                  ↓
   File         "localhost"        "/data/file.txt"
```

**Resource Types:**
- `0x0001` - File
- `0x0002` - HTTP/HTTPS
- `0x0003` - Database
- `0x0004` - Socket
- `0x0005` - Custom

**Example:**
```python
def create_srl_identity(
    resource_type: int,
    resource_namespace: int,
    resource_path: int
) -> int:
    """
    Create a deterministic SRL identity from components.

    All components are mathematical - no strings, no URLs.
    The identity encodes the connection rule, not the data.
    """
    # Pack components into 64-bit identity
    # High 16 bits: resource type
    # Middle 24 bits: namespace
    # Low 24 bits: path

    type_part = (resource_type & 0xFFFF) << 48
    namespace_part = (resource_namespace & 0xFFFFFF) << 24
    path_part = resource_path & 0xFFFFFF

    return type_part | namespace_part | path_part
```

---

## 🌊 Data Flow: External → Substrate

**The complete flow from external data to substrate:**

```
┌──────────────┐
│ External     │
│ Resource     │
│ (File, API,  │
│  Database)   │
└──────┬───────┘
       │
       │ 1. SRL.resource_expression()
       ↓
┌──────────────┐
│ Raw Data     │
│ (bytes)      │
└──────┬───────┘
       │
       │ 2. Hash to 64-bit identity
       ↓
┌──────────────┐
│ Data         │
│ Identity     │
│ (64-bit)     │
└──────┬───────┘
       │
       │ 3. SRL.spawn(data_identity)
       ↓
┌──────────────┐
│ Substrate    │
│ Identity     │
│ (64-bit)     │
└──────┬───────┘
       │
       │ 4. Create substrate
       ↓
┌──────────────┐
│ Substrate    │
│ ⟨S, D, R, F⟩ │
└──────────────┘
```

**Code Example:**
```python
# 1. Create SRL
srl = SRL(
    srl_id=SubstrateIdentity(create_srl_identity(2, hash("api.example.com"), hash("/data"))),
    resource_expression=lambda: fetch_api(),
    spawn_rule=lambda data: SubstrateIdentity(hash(data) & 0xFFFFFFFFFFFFFFFF)
)

# 2. Fetch external data
external_data = srl.resource_expression()  # Returns bytes

# 3. Hash to identity
data_identity = hash(external_data) & 0xFFFFFFFFFFFFFFFF

# 4. Spawn substrate identity
substrate_identity = srl.spawn(data_identity)

# 5. Create substrate
substrate = Substrate(
    substrate_identity,
    lambda: external_data  # Expression that can recompute data
)
```

---

## 🔄 SRL and the Seven Laws

### Law 1: Universal Substrate Law
**SRL is a substrate.** It follows division → dimensions, multiplication → unity.

```python
# SRL can be divided into dimensions
dimensions = srl_substrate.divide()  # 9 Fibonacci dimensions

# Each dimension represents a different aspect of the connection
# Dimension 0: Resource type
# Dimension 1: Namespace
# Dimension 2: Path
# Dimension 3: Protocol
# etc.
```

### Law 2: Observation Is Division
**Observing through SRL creates dimensions.**

```python
# Observation through lens creates dimensional view
lens = Lens(lambda s: s.identity.value >> 48)  # Observe resource type
resource_type = lens.projection(srl_substrate)
```

### Law 3: Inheritance and Recursion
**Every spawned substrate inherits the SRL's identity.**

```python
# Spawned substrates carry SRL identity in their expression
spawned = srl.spawn(external_data)
# spawned.identity contains trace of srl.identity
```

### Law 4: Connection Creates Meaning
**SRL creates connections between internal and external.**

```python
# SRL connects internal substrate to external resource
relationship = srl.connect(internal_substrate, external_substrate)
```

### Law 5: Change Is Motion
**SRL tracks evolution of external resources.**

```python
# Track versions of external resource
versions = srl.track_evolution(substrate, [1, 2, 3, 4])
# Returns trajectory of substrate identities
```

### Law 6: Identity Persists
**SRL identity persists across connections.**

```python
# Same SRL identity always refers to same resource
assert srl1.identity == srl2.identity  # Same resource
```

### Law 7: Return to Unity
**SRL enables return from external to internal.**

```python
# External data → Substrate → Unity
external_data = srl.resource_expression()
substrate = srl.spawn(external_data)
unity = collapse_to_unity(substrate)  # Return to unity
```

---

## 💡 Practical Examples

### Example 1: Reading Configuration File

```python
from kernel import SRL, SubstrateIdentity, create_srl_identity, Substrate

# Create SRL for config file
config_identity = create_srl_identity(
    resource_type=1,  # File
    resource_namespace=hash("config") & 0xFFFFFF,
    resource_path=hash("app.json") & 0xFFFFFF
)

def read_config():
    """Read configuration file."""
    with open("config/app.json", "rb") as f:
        data = f.read()
    return hash(data) & 0xFFFFFFFFFFFFFFFF

srl = SRL(
    srl_id=SubstrateIdentity(config_identity),
    resource_expression=read_config,
    spawn_rule=lambda data: SubstrateIdentity(data)
)

# Spawn substrate from config
config_data = srl.resource_expression()
config_substrate = Substrate(
    srl.spawn(config_data),
    lambda: config_data
)

# Now config is a substrate, not raw data
# Can be observed through lenses, divided into dimensions, etc.
```

### Example 2: API Integration

```python
import hashlib

# Create SRL for GitHub API
github_identity = create_srl_identity(
    resource_type=2,  # HTTP
    resource_namespace=hash("api.github.com") & 0xFFFFFF,
    resource_path=hash("/repos/user/repo") & 0xFFFFFF
)

def fetch_github_repo():
    """Fetch repository data from GitHub API."""
    # In real implementation, this would use HTTP client
    # For now, simulate with hash
    repo_data = b"repository data"
    return hash(repo_data) & 0xFFFFFFFFFFFFFFFF

srl = SRL(
    srl_id=SubstrateIdentity(github_identity),
    resource_expression=fetch_github_repo,
    spawn_rule=lambda data: SubstrateIdentity(data)
)

# Spawn substrate from API response
repo_data = srl.resource_expression()
repo_substrate = Substrate(
    srl.spawn(repo_data),
    lambda: repo_data
)

# Repository is now a substrate
# Can observe: stars, forks, issues, commits, etc.
```

### Example 3: Database Query

```python
# Create SRL for database table
db_identity = create_srl_identity(
    resource_type=3,  # Database
    resource_namespace=hash("postgres://localhost/mydb") & 0xFFFFFF,
    resource_path=hash("users") & 0xFFFFFF
)

def query_users():
    """Query users table."""
    # In real implementation, this would execute SQL
    # For now, simulate with hash
    query_result = b"user data"
    return hash(query_result) & 0xFFFFFFFFFFFFFFFF

srl = SRL(
    srl_id=SubstrateIdentity(db_identity),
    resource_expression=query_users,
    spawn_rule=lambda data: SubstrateIdentity(data)
)

# Spawn substrate from query results
user_data = srl.resource_expression()
users_substrate = Substrate(
    srl.spawn(user_data),
    lambda: user_data
)

# Users table is now a substrate
# Each row can be a dimension
# Relationships between users emerge from connections
```

### Example 4: Logging via SRL

```python
# Create SRL for log file
log_identity = create_srl_identity(
    resource_type=1,  # File
    resource_namespace=hash("logs") & 0xFFFFFF,
    resource_path=hash("app.log") & 0xFFFFFF
)

def append_log(message: str):
    """Append to log file."""
    # In real implementation, this would write to file
    # For now, simulate with hash
    log_entry = message.encode()
    return hash(log_entry) & 0xFFFFFFFFFFFFFFFF

srl = SRL(
    srl_id=SubstrateIdentity(log_identity),
    resource_expression=lambda: 0,  # No read needed
    spawn_rule=lambda data: SubstrateIdentity(data)
)

# Log messages become substrates
log_data = append_log("Application started")
log_substrate = Substrate(
    srl.spawn(log_data),
    lambda: log_data
)

# Logs are substrates, not strings
# Can be observed, filtered, aggregated dimensionally
```

---

## 🛡️ Charter Compliance

All SRL operations comply with the **Dimensional Safety Charter**:

| Charter Principle | SRL Compliance |
|------------------|----------------|
| **1. All Things Are by Reference** | ✅ SRL returns substrate identities, not data copies |
| **2. Passive Until Invoked** | ✅ Lazy retrieval - data fetched only when invoked |
| **3. No Self-Modifying Code** | ✅ SRL is immutable, cannot change at runtime |
| **4. No Global Power Surface** | ✅ Each SRL is scoped, no global access |
| **5. No Hacking Surface** | ✅ Pure functions, no memory manipulation |
| **6. No Dark Web** | ✅ All connections visible through identity |
| **7. Fibonacci-Bounded Growth** | ✅ Spawned substrates follow Fibonacci dimensions |
| **8. The Rabbit Hole Principle** | ✅ Infinite external data, finite behavior |
| **9. The Redemption Equation** | ✅ External → Substrate → Unity (reversible) |
| **10. No Singularity** | ✅ No runaway external data consumption |
| **11. Creativity Over Control** | ✅ Easy to create SRLs, impossible to abuse |
| **12. Charter Is Immutable** | ✅ SRL architecture cannot be bypassed |

---

## 🔒 Security Considerations

### 1. Credential Encryption

**Problem:** Credentials in plain text are vulnerable.

**Solution:** Encrypt credentials with key derived from substrate identity.

```python
def encrypt_credentials(credentials: str, identity: SubstrateIdentity) -> bytes:
    """Encrypt credentials using substrate identity as key."""
    key = identity.value.to_bytes(8, 'big')
    encrypted = bytes(b ^ key[i % 8] for i, b in enumerate(credentials.encode()))
    return encrypted

def decrypt_credentials(encrypted: bytes, identity: SubstrateIdentity) -> str:
    """Decrypt credentials using substrate identity as key."""
    key = identity.value.to_bytes(8, 'big')
    decrypted = bytes(b ^ key[i % 8] for i, b in enumerate(encrypted))
    return decrypted.decode()
```

### 2. Connection Limits

**Problem:** Unbounded connections can exhaust resources.

**Solution:** Fibonacci-bounded connection pool.

```python
# Maximum connections follow Fibonacci sequence
MAX_CONNECTIONS = [1, 1, 2, 3, 5, 8, 13, 21]

def get_max_connections(dimension: int) -> int:
    """Get maximum connections for dimension."""
    return MAX_CONNECTIONS[min(dimension, len(MAX_CONNECTIONS) - 1)]
```

### 3. Data Validation

**Problem:** External data may be malicious.

**Solution:** Validate through lenses before spawning substrates.

```python
def validate_external_data(data: bytes, expected_checksum: int) -> bool:
    """Validate external data before spawning substrate."""
    actual_checksum = hash(data) & 0xFFFFFFFFFFFFFFFF
    return actual_checksum == expected_checksum

# Only spawn if valid
if validate_external_data(external_data, expected_checksum):
    substrate = srl.spawn(hash(external_data) & 0xFFFFFFFFFFFFFFFF)
```

---

## 📚 Implementation Status

### ✅ Implemented (Kernel Layer)

**File:** `kernel/srl.py`

- `SRL` class - Mathematical reference locator
- `create_srl_identity()` - Identity encoding
- Law helper methods:
  - `connect()` - Create relationships
  - `build_network()` - Build relationship networks
  - `track_evolution()` - Track substrate evolution
  - `get_evolution_path()` - Get evolution trajectory

**Tests:** Covered in `tests/test_kernel.py`

### 🔄 Planned (Core Layer)

**File:** `core/srl.py` (to be implemented)

- Protocol implementations:
  - `FileProtocol` - Local file access
  - `HTTPProtocol` - HTTP/HTTPS APIs
  - `SocketProtocol` - Raw TCP sockets
  - `DatabaseProtocol` - Database connections
- Credential management:
  - `APIKey`, `BasicAuth`, `TokenAuth`, `CertAuth`
  - Encryption/decryption
- Connection pooling
- Factory functions:
  - `file_srl()`, `http_srl()`, `socket_srl()`

### 📖 Reference Implementation

**Location:** `_archive/old_implementations/core_v2/srl.py`

This archived implementation shows the complete vision for Core SRL with:
- Full protocol implementations
- Credential encryption
- Connection pooling
- Factory functions
- Error handling

---

## 🎯 Design Philosophy

**Why SRL?**

1. **Security:** No credentials in code
2. **Abstraction:** External resources are substrates
3. **Consistency:** Same dimensional operations everywhere
4. **Traceability:** All connections have mathematical identity
5. **Reversibility:** External → Substrate → Unity

**The Dimensional Insight:**

Traditional systems treat external data as **foreign objects** that must be **converted** to internal format.

DimensionOS treats external data as **substrates waiting to be observed**. The SRL is the **lens** through which external reality becomes dimensional.

**External data doesn't enter the system. The system extends into external reality.**

---

## 🚀 Next Steps

To complete the SRL architecture:

1. **Implement Core SRL** - Add protocol implementations to `core/srl.py`
2. **Add Credential Management** - Implement encryption/decryption
3. **Create Factory Functions** - `file_srl()`, `http_srl()`, etc.
4. **Write Comprehensive Tests** - Test all protocols and credentials
5. **Document Security Model** - Complete security documentation
6. **Create Examples** - Real-world SRL usage examples

---

**DimensionOS v2 - Truth Over Power** 🦋✨


