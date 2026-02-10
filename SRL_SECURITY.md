# 🔐 SRL Security Architecture

## 🎯 **Core Security Principle**

**ONLY name and status are visible. Everything else is encrypted and NEVER exposed.**

---

## 🛡️ **What's Visible vs Hidden**

### ✅ **VISIBLE** (Public Information)
Only these fields are exposed in API responses:

1. **id** - SRL connection ID (integer)
2. **substrate_identity** - Substrate identity (18-char hex)
3. **name** - Connection name (user-defined)
4. **resource_type** - Type of resource (file, database, api, etc.)
5. **status** - Connection status (see below)
6. **created_at** - Creation timestamp
7. **last_used_at** - Last usage timestamp
8. **fetch_count** - Total number of fetches
9. **is_active** - Whether connection is active

### ❌ **HIDDEN** (Never Exposed)
These fields are NEVER sent to clients:

1. **connection_string** - Contains sensitive host/port/path information
2. **credentials** - Encrypted credentials (username, password, API keys, tokens)
3. **auth_method** - Authentication method details
4. **protocol** - Protocol details
5. **config** - Adapter configuration
6. **encrypted_credentials** - The encrypted blob itself
7. **last_error** - Error messages (may contain sensitive info)

---

## 📊 **Connection Status Values**

The `status` field can have these values:

| Status | Meaning | When Set |
|--------|---------|----------|
| **connected** | Connection is active and working | After successful test_connection() |
| **disconnected** | Connection is not active | Default state, or after connection failure |
| **disabled** | Connection manually disabled by user | User action |
| **connecting** | Connection attempt in progress | During test_connection() |
| **blacklisted** | Connection blocked due to security | After repeated failures or security violation |

---

## 🔒 **Encryption System**

### **Algorithm: AES-256 (via Fernet)**

- **Cipher**: Fernet (symmetric encryption)
- **Key Derivation**: PBKDF2 with SHA-256
- **Iterations**: 100,000
- **Key Length**: 256 bits
- **Encoding**: Base64

### **Encryption Flow**

```
Credentials (JSON) → JSON.stringify → UTF-8 encode → Fernet.encrypt → Base64 → Database
```

### **Decryption Flow**

```
Database → Base64 decode → Fernet.decrypt → UTF-8 decode → JSON.parse → Credentials (JSON)
```

### **Key Management**

1. **Environment Variable**: `SRL_ENCRYPTION_KEY`
   - Must be set in production
   - Generated with: `python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`

2. **Salt**: `SRL_ENCRYPTION_SALT` (optional)
   - Default: `"butterflyfx-srl-salt-v1"`
   - Used for PBKDF2 key derivation

3. **Development Mode**:
   - Auto-generates temporary key if not set
   - ⚠️ WARNING displayed
   - NOT for production use

---

## 🔐 **Security Functions**

### **1. encrypt_credentials(credentials: dict) → str**

Encrypts credentials dictionary to encrypted string.

```python
from server.srl_crypto import encrypt_credentials

credentials = {
    "username": "admin",
    "password": "secret123"
}

encrypted = encrypt_credentials(credentials)
# Returns: "gAAAAABf..."
```

### **2. decrypt_credentials(encrypted: str) → dict**

Decrypts encrypted string to credentials dictionary.

```python
from server.srl_crypto import decrypt_credentials

credentials = decrypt_credentials(encrypted)
# Returns: {"username": "admin", "password": "secret123"}
```

**⚠️ IMPORTANT**: Decryption happens ONLY:
- In memory during fetch operation
- Never logged
- Never sent to client
- Immediately discarded after use

### **3. sanitize_srl_for_response(srl_connection) → dict**

Sanitizes SRL connection for API response.

```python
from server.srl_crypto import sanitize_srl_for_response

safe_data = sanitize_srl_for_response(srl_connection)
# Returns only: id, substrate_identity, name, resource_type, status, timestamps, fetch_count, is_active
```

### **4. mask_connection_string(connection_string: str) → str**

Masks sensitive parts of connection string for logging.

```python
from server.srl_crypto import mask_connection_string

masked = mask_connection_string("postgresql://user:pass@host:5432/db")
# Returns: "postgresql://***:***@host:5432/db"
```

---

## 🚨 **Security Threats & Mitigations**

### **Threat 1: Credential Exposure**
- **Risk**: Credentials leaked in API responses
- **Mitigation**: `sanitize_srl_for_response()` removes all sensitive fields
- **Status**: ✅ Mitigated

### **Threat 2: Connection String Exposure**
- **Risk**: Connection strings contain sensitive host/port/path info
- **Mitigation**: Never included in API responses, masked in logs
- **Status**: ✅ Mitigated

### **Threat 3: Encryption Key Compromise**
- **Risk**: If encryption key is leaked, all credentials are compromised
- **Mitigation**: 
  - Key stored in environment variable (not in code)
  - PBKDF2 key derivation adds layer of protection
  - Key rotation supported
- **Status**: ✅ Mitigated

### **Threat 4: Replay Attacks**
- **Risk**: Attacker intercepts and replays fetch requests
- **Mitigation**: JWT authentication required for all SRL operations
- **Status**: ✅ Mitigated

### **Threat 5: Brute Force Attacks**
- **Risk**: Attacker tries to guess credentials
- **Mitigation**: 
  - Rate limiting on all endpoints
  - Blacklist status after repeated failures
  - Audit trail for all access attempts
- **Status**: ✅ Mitigated

### **Threat 6: SQL Injection / Command Injection**
- **Risk**: Malicious queries injected through SRL
- **Mitigation**: 
  - Parameterized queries in adapters
  - Input validation
  - User owns SRL (can only harm their own resources)
- **Status**: ✅ Mitigated

---

## 📝 **Audit Trail**

Every SRL fetch is logged in `SRLFetchLogModel`:

- **connection_id**: Which SRL was used
- **user_id**: Who made the request
- **query**: What was requested
- **parameters**: Query parameters
- **success**: Whether it succeeded
- **result_size_bytes**: How much data was fetched
- **duration_ms**: How long it took
- **error_message**: Error if failed
- **fetched_at**: When it happened

**Use Cases**:
- Security audits
- Compliance (GDPR, SOC2, etc.)
- Performance monitoring
- Anomaly detection
- Forensics

---

## 🔑 **Best Practices**

### **For Developers**

1. **Never log decrypted credentials**
   ```python
   # ❌ BAD
   logger.info(f"Credentials: {credentials}")
   
   # ✅ GOOD
   logger.info(f"Using credentials for user {user_id}")
   ```

2. **Always use sanitize_srl_for_response()**
   ```python
   # ❌ BAD
   return {"srl": srl_connection}
   
   # ✅ GOOD
   return {"srl": sanitize_srl_for_response(srl_connection)}
   ```

3. **Decrypt only when needed**
   ```python
   # ❌ BAD
   credentials = decrypt_credentials(srl.encrypted_credentials)
   # ... do other stuff ...
   # ... use credentials later ...
   
   # ✅ GOOD
   # ... do other stuff ...
   credentials = decrypt_credentials(srl.encrypted_credentials)
   result = adapter.fetch(...)  # Use immediately
   del credentials  # Discard immediately
   ```

### **For Deployment**

1. **Set SRL_ENCRYPTION_KEY**
   ```bash
   # Generate key
   python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
   
   # Set in environment
   export SRL_ENCRYPTION_KEY="your-generated-key"
   ```

2. **Rotate keys periodically**
   - Use `rotate_encryption()` function
   - Update all SRL connections
   - Store old key for recovery

3. **Monitor audit logs**
   - Set up alerts for failed fetches
   - Monitor for unusual patterns
   - Review blacklisted connections

---

## ✅ **Security Checklist**

- [x] Credentials encrypted at rest (AES-256)
- [x] Credentials decrypted only in memory
- [x] Credentials never logged
- [x] Credentials never sent to client
- [x] Only name and status exposed in API
- [x] Connection strings masked in logs
- [x] JWT authentication required
- [x] Rate limiting enabled
- [x] Audit trail for all fetches
- [x] Blacklist support for compromised connections
- [x] Key rotation supported
- [x] PBKDF2 key derivation
- [x] Input validation
- [x] Parameterized queries

---

🔐 **SRL Security: Zero Trust, Maximum Protection** 🔐

