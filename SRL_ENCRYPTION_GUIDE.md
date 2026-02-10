# 🔐 SRL Encryption - Quick Start Guide

## 📋 **Setup**

### **1. Generate Encryption Key**

```bash
# Generate a new encryption key
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Output example:
# 8vHJZ9X2qW5nR4kP7mL3bN6cV9xA1sD4fG7hJ0kM2nQ5rT8wY=
```

### **2. Set Environment Variable**

```bash
# Linux/Mac
export SRL_ENCRYPTION_KEY="8vHJZ9X2qW5nR4kP7mL3bN6cV9xA1sD4fG7hJ0kM2nQ5rT8wY="

# Windows
set SRL_ENCRYPTION_KEY=8vHJZ9X2qW5nR4kP7mL3bN6cV9xA1sD4fG7hJ0kM2nQ5rT8wY=

# Docker
docker run -e SRL_ENCRYPTION_KEY="8vHJZ9X2qW5nR4kP7mL3bN6cV9xA1sD4fG7hJ0kM2nQ5rT8wY=" ...

# .env file
echo "SRL_ENCRYPTION_KEY=8vHJZ9X2qW5nR4kP7mL3bN6cV9xA1sD4fG7hJ0kM2nQ5rT8wY=" >> .env
```

### **3. Optional: Set Custom Salt**

```bash
export SRL_ENCRYPTION_SALT="my-custom-salt-v1"
```

---

## 💻 **Usage Examples**

### **Example 1: Encrypt Database Credentials**

```python
from server.srl_crypto import encrypt_credentials, decrypt_credentials

# Credentials to encrypt
credentials = {
    "username": "postgres_user",
    "password": "super_secret_password"
}

# Encrypt
encrypted = encrypt_credentials(credentials)
print(f"Encrypted: {encrypted}")
# Output: gAAAAABf3x2y...

# Store in database
srl_connection.encrypted_credentials = encrypted
db.commit()

# Later, decrypt when needed
decrypted = decrypt_credentials(encrypted)
print(f"Username: {decrypted['username']}")
# Output: Username: postgres_user
```

### **Example 2: Encrypt API Key**

```python
from server.srl_crypto import encrypt_credentials

# API credentials
credentials = {
    "api_key": "sk_live_abc123xyz789",
    "auth_method": "bearer"
}

# Encrypt
encrypted = encrypt_credentials(credentials)

# Store
srl_connection.encrypted_credentials = encrypted
db.commit()
```

### **Example 3: Encrypt OAuth Token**

```python
from server.srl_crypto import encrypt_credentials

# OAuth credentials
credentials = {
    "access_token": "ya29.a0AfH6SMB...",
    "refresh_token": "1//0gHJK...",
    "token_type": "Bearer",
    "expires_in": 3600
}

# Encrypt
encrypted = encrypt_credentials(credentials)

# Store
srl_connection.encrypted_credentials = encrypted
db.commit()
```

### **Example 4: Sanitize for API Response**

```python
from server.srl_crypto import sanitize_srl_for_response

# Get SRL from database
srl = db.query(SRLConnectionModel).filter_by(id=123).first()

# ❌ NEVER do this (exposes everything)
return {"srl": srl}

# ✅ ALWAYS do this (only exposes name and status)
return {"srl": sanitize_srl_for_response(srl)}

# Output:
# {
#     "srl": {
#         "id": 123,
#         "substrate_identity": "0x1a2b3c4d5e6f7890",
#         "name": "Production Database",
#         "resource_type": "database",
#         "status": "connected",
#         "created_at": "2024-01-15T10:30:00",
#         "last_used_at": "2024-01-15T14:25:00",
#         "fetch_count": 42,
#         "is_active": true
#     }
# }
```

### **Example 5: Mask Connection String for Logging**

```python
from server.srl_crypto import mask_connection_string

# Database connection string
conn_str = "postgresql://admin:secret123@db.example.com:5432/mydb"
masked = mask_connection_string(conn_str)
print(f"Connecting to: {masked}")
# Output: Connecting to: postgresql://***:***@db.example.com:5432/mydb

# API connection string
api_str = "https://api.example.com/v1/users"
masked = mask_connection_string(api_str)
print(f"API endpoint: {masked}")
# Output: API endpoint: https://api.example.com/***
```

---

## 🔄 **Key Rotation**

### **When to Rotate Keys**

- Periodically (e.g., every 90 days)
- After security incident
- When employee with key access leaves
- Compliance requirements

### **How to Rotate Keys**

```python
from server.srl_crypto import get_crypto
from server.database import SRLConnectionModel

# 1. Generate new key
new_key = "NEW_GENERATED_KEY_HERE"

# 2. Get all SRL connections
srls = db.query(SRLConnectionModel).all()

# 3. Rotate each connection
crypto = get_crypto()
for srl in srls:
    if srl.encrypted_credentials:
        # Decrypt with old key, encrypt with new key
        new_encrypted = crypto.rotate_encryption(
            srl.encrypted_credentials,
            new_key
        )
        srl.encrypted_credentials = new_encrypted

# 4. Commit changes
db.commit()

# 5. Update environment variable
import os
os.environ["SRL_ENCRYPTION_KEY"] = new_key

# 6. Restart application
```

---

## 🚨 **Security Best Practices**

### **DO ✅**

1. **Generate strong keys**
   ```python
   from cryptography.fernet import Fernet
   key = Fernet.generate_key()  # Always use this
   ```

2. **Store keys in environment variables**
   ```bash
   export SRL_ENCRYPTION_KEY="..."
   ```

3. **Decrypt only when needed**
   ```python
   credentials = decrypt_credentials(encrypted)
   result = use_credentials(credentials)
   del credentials  # Discard immediately
   ```

4. **Always sanitize responses**
   ```python
   return sanitize_srl_for_response(srl)
   ```

5. **Mask connection strings in logs**
   ```python
   logger.info(f"Connecting to {mask_connection_string(conn_str)}")
   ```

### **DON'T ❌**

1. **Never hardcode keys**
   ```python
   # ❌ NEVER DO THIS
   SRL_ENCRYPTION_KEY = "hardcoded-key-123"
   ```

2. **Never log decrypted credentials**
   ```python
   # ❌ NEVER DO THIS
   logger.info(f"Password: {credentials['password']}")
   ```

3. **Never send credentials to client**
   ```python
   # ❌ NEVER DO THIS
   return {"credentials": credentials}
   ```

4. **Never store decrypted credentials**
   ```python
   # ❌ NEVER DO THIS
   self.credentials = decrypt_credentials(encrypted)
   ```

5. **Never commit keys to git**
   ```bash
   # ❌ NEVER DO THIS
   git add .env
   git commit -m "Added encryption key"
   ```

---

## 🧪 **Testing**

### **Test Encryption/Decryption**

```python
from server.srl_crypto import encrypt_credentials, decrypt_credentials

# Test data
original = {"username": "test", "password": "secret"}

# Encrypt
encrypted = encrypt_credentials(original)
assert encrypted != str(original)
assert "test" not in encrypted
assert "secret" not in encrypted

# Decrypt
decrypted = decrypt_credentials(encrypted)
assert decrypted == original
print("✅ Encryption test passed!")
```

### **Test Sanitization**

```python
from server.srl_crypto import sanitize_srl_for_response

# Mock SRL connection
class MockSRL:
    id = 1
    substrate_identity = "0x123"
    name = "Test DB"
    resource_type = "database"
    status = "connected"
    created_at = datetime.now()
    last_used_at = None
    fetch_count = 0
    is_active = True
    encrypted_credentials = "gAAAAABf..."  # Should NOT be in output
    connection_string = "postgresql://..."  # Should NOT be in output

srl = MockSRL()
safe = sanitize_srl_for_response(srl)

assert "encrypted_credentials" not in safe
assert "connection_string" not in safe
assert safe["name"] == "Test DB"
assert safe["status"] == "connected"
print("✅ Sanitization test passed!")
```

---

## 📊 **Status Values**

| Status | Description | Set By |
|--------|-------------|--------|
| `connected` | Connection is active and working | System after successful test |
| `disconnected` | Connection is not active | Default or after failure |
| `disabled` | Manually disabled by user | User action |
| `connecting` | Connection attempt in progress | System during test |
| `blacklisted` | Blocked due to security | System after repeated failures |

---

## 🔍 **Troubleshooting**

### **Error: "SRL_ENCRYPTION_KEY environment variable not set"**

**Solution**: Set the environment variable
```bash
export SRL_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

### **Error: "Failed to decrypt credentials"**

**Possible causes**:
1. Wrong encryption key
2. Corrupted encrypted data
3. Key was rotated but data wasn't updated

**Solution**: Check encryption key matches the one used to encrypt

### **Warning: "Generating temporary encryption key for development"**

**Cause**: Running in development mode without SRL_ENCRYPTION_KEY set

**Solution**: Set the environment variable or set `ENVIRONMENT=production`

---

🔐 **Remember: Only name and status are visible. Everything else is encrypted!** 🔐

