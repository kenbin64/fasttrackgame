"""
Core SRL Examples - The Dimensional Way to Connect to External Resources

This file demonstrates how to use Core SRL to connect to:
- Local files and directories
- HTTP APIs
- Raw TCP sockets

All external data becomes substrates in DimensionOS.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    file_srl, http_srl, socket_srl,
    APIKey, BasicAuth, TokenAuth,
    FileProtocol, HTTPProtocol, SocketProtocol
)
from kernel.substrate import Substrate


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 1: LOCAL FILE ACCESS
# ═══════════════════════════════════════════════════════════════════

def example_file_access():
    """
    Example: Reading a local file and spawning a substrate.
    
    The file data becomes a substrate with 64-bit identity.
    """
    print("=" * 70)
    print("EXAMPLE 1: LOCAL FILE ACCESS")
    print("=" * 70)
    
    # Create SRL for local file
    srl = file_srl("README.md")
    
    print(f"SRL Identity: {srl.identity}")
    print(f"Domain: {srl.domain}")
    print(f"Path: {srl.path}")
    
    # Fetch file data
    result = srl.fetch()
    
    if result.success:
        print(f"\n✅ File fetched successfully!")
        print(f"   Data size: {len(result.data)} bytes")
        print(f"   Bit count: {result.bit_count}")
        print(f"   Checksum: {hex(result.checksum)}")
        
        # Spawn substrate from file data
        substrate_id = srl.spawn(result.data)
        print(f"\n🦋 Substrate spawned!")
        print(f"   Substrate Identity: {substrate_id}")

        # Create actual substrate
        substrate = Substrate(
            x1=substrate_id,
            expression=lambda **kwargs: result.checksum
        )
        print(f"   Substrate invoked: {substrate.invoke()}")
    else:
        print(f"❌ Failed: {result.error}")
    
    # Close connection
    srl.close()
    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 2: HTTP API ACCESS
# ═══════════════════════════════════════════════════════════════════

def example_http_api():
    """
    Example: Fetching data from an HTTP API.
    
    Note: This example uses a public API. Replace with your own API
    and credentials for real use.
    """
    print("=" * 70)
    print("EXAMPLE 2: HTTP API ACCESS")
    print("=" * 70)
    
    # Create SRL for HTTP API (using JSONPlaceholder as example)
    srl = http_srl(
        "https://jsonplaceholder.typicode.com/posts/1",
        headers={"User-Agent": "DimensionOS/2.0"}
    )
    
    print(f"SRL Identity: {srl.identity}")
    print(f"Domain: {srl.domain}")
    print(f"Path: {srl.path}")
    print(f"SSL: {srl.use_ssl}")
    
    # Fetch API data
    result = srl.fetch()
    
    if result.success:
        print(f"\n✅ API data fetched successfully!")
        print(f"   Data size: {len(result.data)} bytes")
        print(f"   Checksum: {hex(result.checksum)}")
        
        # Show first 200 characters of response
        preview = result.data[:200].decode('utf-8', errors='ignore')
        print(f"\n   Preview: {preview}...")
        
        # Spawn substrate from API data
        substrate_id = srl.spawn(result.data)
        print(f"\n🦋 Substrate spawned!")
        print(f"   Substrate Identity: {substrate_id}")
    else:
        print(f"❌ Failed: {result.error}")
    
    # Close connection
    srl.close()
    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 3: HTTP API WITH AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════

def example_http_with_auth():
    """
    Example: HTTP API with authentication.
    
    Shows how to use different credential types.
    """
    print("=" * 70)
    print("EXAMPLE 3: HTTP API WITH AUTHENTICATION")
    print("=" * 70)
    
    # Example 1: API Key authentication
    print("\n📝 API Key Authentication:")
    api_key_creds = APIKey(key="sk-1234567890abcdef", header_name="X-API-Key")
    print(f"   Headers: {api_key_creds.to_headers()}")
    
    # Example 2: Basic Auth
    print("\n📝 Basic Authentication:")
    basic_creds = BasicAuth(username="user", password="pass")
    print(f"   Headers: {basic_creds.to_headers()}")
    
    # Example 3: Bearer Token
    print("\n📝 Bearer Token Authentication:")
    token_creds = TokenAuth(token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print(f"   Headers: {token_creds.to_headers()}")
    
    # Create SRL with credentials
    # (Replace with your actual API endpoint)
    print("\n🔗 Creating SRL with API Key:")
    srl = http_srl(
        "https://api.example.com/data",
        credentials=api_key_creds,
        headers={"User-Agent": "DimensionOS/2.0"}
    )
    
    print(f"   SRL Identity: {srl.identity}")
    print(f"   Credentials: {type(srl.credentials).__name__}")

    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 4: CREDENTIAL ENCRYPTION
# ═══════════════════════════════════════════════════════════════════

def example_credential_encryption():
    """
    Example: Encrypting and decrypting credentials.

    Credentials are encrypted using substrate identity as the key.
    This ensures credentials are tied to specific substrates.
    """
    print("=" * 70)
    print("EXAMPLE 4: CREDENTIAL ENCRYPTION")
    print("=" * 70)

    # Create credentials
    original_creds = APIKey(key="sk-secret-key-1234567890")
    print(f"\n📝 Original credentials:")
    print(f"   Key: {original_creds.key}")

    # Encrypt using substrate identity as key
    encryption_key = b"substrate_identity_12345678"
    encrypted = original_creds.encrypt(encryption_key)
    print(f"\n🔒 Encrypted:")
    print(f"   {encrypted}")

    # Decrypt
    decrypted_creds = APIKey.decrypt(encrypted, encryption_key)
    print(f"\n🔓 Decrypted:")
    print(f"   Key: {decrypted_creds.key}")

    # Verify
    assert original_creds.key == decrypted_creds.key
    print(f"\n✅ Encryption/decryption successful!")

    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 5: DIRECTORY LISTING
# ═══════════════════════════════════════════════════════════════════

def example_directory_listing():
    """
    Example: Reading a directory listing.

    When an SRL points to a directory, it returns a JSON list of files.
    """
    print("=" * 70)
    print("EXAMPLE 5: DIRECTORY LISTING")
    print("=" * 70)

    # Create SRL for directory
    srl = file_srl("kernel")

    print(f"SRL Identity: {srl.identity}")
    print(f"Path: {srl.path}")

    # Fetch directory listing
    result = srl.fetch()

    if result.success:
        import json
        listing = json.loads(result.data.decode('utf-8'))

        print(f"\n✅ Directory listing fetched!")
        print(f"   Files found: {len(listing)}")
        print(f"\n   Contents:")
        for item in sorted(listing)[:10]:  # Show first 10
            print(f"      - {item}")

        if len(listing) > 10:
            print(f"      ... and {len(listing) - 10} more")
    else:
        print(f"❌ Failed: {result.error}")

    srl.close()
    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE 6: WRITING TO FILES
# ═══════════════════════════════════════════════════════════════════

def example_file_write():
    """
    Example: Writing data to a file through SRL.

    Shows how to send data through an SRL connection.
    """
    print("=" * 70)
    print("EXAMPLE 6: WRITING TO FILES")
    print("=" * 70)

    import tempfile
    import os

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        temp_path = f.name

    try:
        # Create SRL
        srl = file_srl(temp_path)

        print(f"SRL Identity: {srl.identity}")
        print(f"Path: {temp_path}")

        # Connect and send data
        connection = srl.connect()
        data = b"Hello from DimensionOS!\nThis is dimensional I/O."

        print(f"\n📤 Sending {len(data)} bytes...")
        result = connection.send(data)

        if result.success:
            print(f"✅ Data written successfully!")

            # Read back to verify
            read_result = connection.fetch()
            print(f"\n📥 Reading back...")
            print(f"   Data: {read_result.data.decode('utf-8')}")
        else:
            print(f"❌ Failed: {result.error}")

        connection.close()
    finally:
        os.unlink(temp_path)

    print("\n" + "=" * 70 + "\n")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    """Run all examples."""
    print("\n")
    print("🦋" * 35)
    print("CORE SRL EXAMPLES - THE DIMENSIONAL WAY TO CONNECT")
    print("🦋" * 35)
    print("\n")

    # Run examples
    example_file_access()
    example_http_api()
    example_http_with_auth()
    example_credential_encryption()
    example_directory_listing()
    example_file_write()

    print("🦋" * 35)
    print("ALL EXAMPLES COMPLETE")
    print("🦋" * 35)
    print("\n")


if __name__ == "__main__":
    main()

