"""
ButterflyFx Core - The Bridge Layer

The Core is the ONLY interface to the Kernel.
- Humans access the Core
- Machines access the Core  
- AI accesses the Core
- Code accesses the Core

The Core translates all external intent into Kernel math.
The Kernel CANNOT be directly accessed from outside this layer.

RULES:
1. Core may import from Kernel
2. Core may NOT expose Kernel internals directly
3. All operations compile down to substrate math
4. Core provides logic for validation, translation, invocation
5. No shadow models - Core transforms, Kernel is truth
"""

from .invocation import Invocator
from .translator import Translator
from .validator import Validator
from .gateway import KernelGateway
from .srl import (
    # Connection device
    SRL,
    SRLConnection,
    SRLResult,

    # Protocols
    Protocol,
    FileProtocol,
    HTTPProtocol,
    SocketProtocol,

    # Credentials
    Credentials,
    APIKey,
    BasicAuth,
    TokenAuth,

    # Errors
    SRLError,
    ConnectionError,
    AuthenticationError,

    # Factory functions
    file_srl,
    http_srl,
    socket_srl,
)

__all__ = [
    # Core components
    'Invocator',
    'Translator',
    'Validator',
    'KernelGateway',

    # SRL - Connection device
    'SRL',
    'SRLConnection',
    'SRLResult',

    # Protocols
    'Protocol',
    'FileProtocol',
    'HTTPProtocol',
    'SocketProtocol',

    # Credentials
    'Credentials',
    'APIKey',
    'BasicAuth',
    'TokenAuth',

    # Errors
    'SRLError',
    'ConnectionError',
    'AuthenticationError',

    # Factory functions
    'file_srl',
    'http_srl',
    'socket_srl',
]
