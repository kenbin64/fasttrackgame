"""
SRL - Substrate Reference Locator.

Universal identifier for substrate locations.
Like a URL but for substrates.
"""

from ._identity import SubstrateIdentity

__all__ = ['SRL', 'create_srl_identity']


class SRL:
    """
    Substrate Reference Locator.
    
    Format: srl://<domain>/<path>#<identity>
    
    Used to reference substrates across dimensional boundaries.
    """
    __slots__ = ('_domain', '_path', '_identity')
    
    def __init__(self, domain: str, path: str, identity: SubstrateIdentity):
        """
        Create an SRL.
        
        Args:
            domain: The domain (e.g., "butterflyfx.local")
            path: The path (e.g., "/substrates/image")
            identity: The substrate identity
        """
        object.__setattr__(self, '_domain', domain)
        object.__setattr__(self, '_path', path)
        object.__setattr__(self, '_identity', identity)
    
    def __setattr__(self, name, value):
        raise TypeError("SRL is immutable")
    
    def __delattr__(self, name):
        raise TypeError("SRL is immutable")
    
    @property
    def domain(self) -> str:
        """The domain component."""
        return self._domain
    
    @property
    def path(self) -> str:
        """The path component."""
        return self._path
    
    @property
    def identity(self) -> SubstrateIdentity:
        """The substrate identity."""
        return self._identity
    
    def to_uri(self) -> str:
        """Convert to URI string."""
        return f"srl://{self._domain}{self._path}#{self._identity.value:016x}"
    
    @classmethod
    def from_uri(cls, uri: str) -> 'SRL':
        """Parse URI string to SRL."""
        # Parse: srl://domain/path#identity
        if not uri.startswith("srl://"):
            raise ValueError("Invalid SRL: must start with srl://")
        
        rest = uri[6:]  # Remove "srl://"
        
        # Split on #
        if '#' in rest:
            location, identity_hex = rest.rsplit('#', 1)
            identity = SubstrateIdentity(int(identity_hex, 16))
        else:
            location = rest
            identity = SubstrateIdentity(0)
        
        # Split domain and path
        if '/' in location:
            domain, path = location.split('/', 1)
            path = '/' + path
        else:
            domain = location
            path = '/'
        
        return cls(domain, path, identity)
    
    def __repr__(self) -> str:
        return f"SRL({self.to_uri()})"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, SRL):
            return (
                self._domain == other._domain and
                self._path == other._path and
                self._identity == other._identity
            )
        return False
    
    def __hash__(self) -> int:
        return hash((self._domain, self._path, self._identity))


def create_srl_identity(domain: str, path: str, seed: int = 0) -> SubstrateIdentity:
    """
    Create a deterministic identity from domain and path.
    
    Uses FNV-1a hash for consistent 64-bit identity.
    """
    # FNV-1a constants
    FNV_PRIME = 0x100000001b3
    FNV_OFFSET = 0xcbf29ce484222325
    
    data = f"{domain}{path}{seed}".encode('utf-8')
    
    h = FNV_OFFSET
    for byte in data:
        h ^= byte
        h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
    
    return SubstrateIdentity(h)
