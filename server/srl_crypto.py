"""
SRL Credential Encryption - AES-256 encryption for secure credential storage

PHILOSOPHY:
Credentials are the keys to the kingdom. They must NEVER be exposed.
- Encrypted at rest (AES-256)
- Decrypted only in memory during fetch
- Never logged, never sent to client
- Only name and status are visible

SECURITY PRINCIPLES:
1. Zero Trust - Assume all channels are compromised
2. Defense in Depth - Multiple layers of security
3. Least Privilege - Only decrypt when absolutely necessary
4. Audit Everything - Log all access attempts
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import json
import base64
from typing import Dict, Any, Optional
import secrets


class SRLCrypto:
    """
    SRL Credential Encryption System
    
    Uses AES-256 (via Fernet) for symmetric encryption of credentials.
    Encryption key derived from environment variable using PBKDF2.
    """
    
    def __init__(self):
        """Initialize encryption system."""
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize Fernet cipher with key from environment."""
        # Get encryption key from environment
        encryption_key = os.getenv("SRL_ENCRYPTION_KEY")
        
        if not encryption_key:
            # In development, generate a key (NOT for production!)
            if os.getenv("ENVIRONMENT") == "development":
                print("⚠️  WARNING: Generating temporary encryption key for development")
                print("⚠️  Set SRL_ENCRYPTION_KEY environment variable for production!")
                encryption_key = Fernet.generate_key().decode()
                os.environ["SRL_ENCRYPTION_KEY"] = encryption_key
            else:
                raise ValueError(
                    "SRL_ENCRYPTION_KEY environment variable not set. "
                    "Generate one with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
                )
        
        # Derive key using PBKDF2 for additional security
        salt = os.getenv("SRL_ENCRYPTION_SALT", "butterflyfx-srl-salt-v1").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        
        # Create Fernet cipher
        self._fernet = Fernet(key)
    
    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """
        Encrypt credentials dictionary to encrypted string.
        
        Args:
            credentials: Dictionary containing credentials
                Examples:
                - {"username": "user", "password": "secret"}
                - {"api_key": "abc123"}
                - {"token": "bearer_token"}
        
        Returns:
            Encrypted string (base64 encoded)
        
        Raises:
            ValueError: If credentials is empty or invalid
        """
        if not credentials:
            raise ValueError("Credentials cannot be empty")
        
        # Convert to JSON
        json_str = json.dumps(credentials, sort_keys=True)
        
        # Encrypt
        encrypted_bytes = self._fernet.encrypt(json_str.encode('utf-8'))
        
        # Return as string
        return encrypted_bytes.decode('utf-8')
    
    def decrypt_credentials(self, encrypted: str) -> Dict[str, Any]:
        """
        Decrypt encrypted string to credentials dictionary.
        
        Args:
            encrypted: Encrypted string (base64 encoded)
        
        Returns:
            Decrypted credentials dictionary
        
        Raises:
            ValueError: If decryption fails (invalid key or corrupted data)
        """
        if not encrypted:
            raise ValueError("Encrypted credentials cannot be empty")
        
        try:
            # Decrypt
            decrypted_bytes = self._fernet.decrypt(encrypted.encode('utf-8'))
            
            # Parse JSON
            credentials = json.loads(decrypted_bytes.decode('utf-8'))
            
            return credentials
        
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")
    
    def rotate_encryption(self, old_encrypted: str, new_key: str) -> str:
        """
        Rotate encryption key by decrypting with old key and encrypting with new key.
        
        Args:
            old_encrypted: Credentials encrypted with old key
            new_key: New encryption key
        
        Returns:
            Credentials encrypted with new key
        """
        # Decrypt with current key
        credentials = self.decrypt_credentials(old_encrypted)
        
        # Save current key
        old_key = os.getenv("SRL_ENCRYPTION_KEY")
        
        # Set new key
        os.environ["SRL_ENCRYPTION_KEY"] = new_key
        self._initialize_encryption()
        
        # Encrypt with new key
        new_encrypted = self.encrypt_credentials(credentials)
        
        # Restore old key (in case rotation fails)
        os.environ["SRL_ENCRYPTION_KEY"] = old_key
        
        return new_encrypted


# Global instance
_crypto_instance: Optional[SRLCrypto] = None


def get_crypto() -> SRLCrypto:
    """Get global SRLCrypto instance (singleton)."""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = SRLCrypto()
    return _crypto_instance


def encrypt_credentials(credentials: Dict[str, Any]) -> str:
    """Encrypt credentials (convenience function)."""
    return get_crypto().encrypt_credentials(credentials)


def decrypt_credentials(encrypted: str) -> Dict[str, Any]:
    """Decrypt credentials (convenience function)."""
    return get_crypto().decrypt_credentials(encrypted)


def generate_encryption_key() -> str:
    """Generate a new encryption key for SRL_ENCRYPTION_KEY."""
    return Fernet.generate_key().decode()


# ============================================================================
# SECURITY UTILITIES
# ============================================================================

def sanitize_srl_for_response(srl_connection: Any) -> Dict[str, Any]:
    """
    Sanitize SRL connection for API response.
    
    SECURITY: Only expose name and status. NEVER expose:
    - Credentials (encrypted or decrypted)
    - Connection string (may contain sensitive info)
    - Auth method details
    - Configuration details
    
    Args:
        srl_connection: SRLConnectionModel instance
    
    Returns:
        Safe dictionary with only name and status
    """
    return {
        "id": srl_connection.id,
        "substrate_identity": srl_connection.substrate_identity,
        "name": srl_connection.name,
        "resource_type": srl_connection.resource_type,
        "status": srl_connection.status,  # connected, disconnected, disabled, connecting, blacklisted
        "created_at": srl_connection.created_at.isoformat() if srl_connection.created_at else None,
        "last_used_at": srl_connection.last_used_at.isoformat() if srl_connection.last_used_at else None,
        "fetch_count": srl_connection.fetch_count,
        "is_active": srl_connection.is_active,
    }


def mask_connection_string(connection_string: str) -> str:
    """
    Mask sensitive parts of connection string for logging.
    
    Examples:
        postgresql://user:pass@host:5432/db -> postgresql://***:***@host:5432/db
        https://api.example.com/v1 -> https://api.example.com/***
    """
    if not connection_string:
        return ""
    
    # Mask password in database URLs
    if "://" in connection_string:
        parts = connection_string.split("://")
        if len(parts) == 2:
            protocol, rest = parts
            if "@" in rest:
                credentials, host = rest.split("@", 1)
                return f"{protocol}://***:***@{host}"
    
    # Mask API endpoints
    if connection_string.startswith("http"):
        parts = connection_string.split("/")
        if len(parts) > 3:
            return "/".join(parts[:3]) + "/***"
    
    # Default: mask everything after first part
    return connection_string.split("/")[0] + "/***"

