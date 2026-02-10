"""
Database configuration and models for ButterflyFx Server

Implements:
- User authentication
- TOS acceptance tracking
- Session management
- Substrate persistence
- Relationship persistence
"""

from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
from typing import Optional
import os

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://butterflyfx:butterflyfx@localhost:5432/butterflyfx"
)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# ============================================================================
# USER MODELS
# ============================================================================

class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    tos_agreements = relationship("TOSAgreement", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    substrates = relationship("SubstrateModel", back_populates="owner", cascade="all, delete-orphan")
    lenses = relationship("LensModel", back_populates="owner", cascade="all, delete-orphan")
    srl_connections = relationship("SRLConnectionModel", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"


class TOSAgreement(Base):
    """Terms of Service agreement tracking."""
    __tablename__ = "tos_agreements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tos_version = Column(String(50), nullable=False)
    agreed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tos_agreements")
    
    def __repr__(self):
        return f"<TOSAgreement(user_id={self.user_id}, version={self.tos_version})>"


class Session(Base):
    """User session tracking."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f"<Session(user_id={self.user_id}, expires_at={self.expires_at})>"


# ============================================================================
# SUBSTRATE MODELS
# ============================================================================

class SubstrateModel(Base):
    """
    Substrate Model - The DNA of Dimensional Reality

    PHILOSOPHY:
    A substrate is a mathematical expression that represents data - it's the DNA of an object,
    dimension, or concept. When created, it contains ALL possible attributes, behaviors, physics,
    and material properties in superposition. Invocation collapses potential into manifestation.

    Like looking at a car - you KNOW it has an engine, wheels, seats, etc. You don't need to
    open the hood to know the engine exists. You only invoke what you need to see.

    IDENTITY:
    - 64-bit bitwise hash (18.4 quintillion possible identities)
    - Deterministic (same expression = same hash)
    - The substrate's "fingerprint" and dimensional address

    EXPRESSION:
    - The mathematical DNA that defines everything
    - All properties derive from this expression
    - Stored server-side only, NEVER exposed to clients
    - Can be foundational (z=x*y), complex (E=mc²), dimensional (objects), or complete entities

    SUPERPOSITION:
    - All properties exist simultaneously when created
    - Invocation reveals what already exists
    - Lazy evaluation (don't compute until needed)
    - Infinite potential, finite manifestation

    TYPES:
    - Foundational: z=x*y, z=x+y, z=x^2 (building blocks)
    - Complex: E=mc², F=ma, Fibonacci (natural laws)
    - Dimensional: Point, Line, Plane, Volume (structural)
    - Object: Car, Ball, Person (complete entities)
    """
    __tablename__ = "substrates"

    id = Column(Integer, primary_key=True, index=True)

    # ========================================================================
    # IDENTITY (64-bit hash - The substrate's fingerprint)
    # ========================================================================
    identity = Column(String(18), unique=True, index=True, nullable=False)  # Hex: "0x..."
    identity_value = Column(BigInteger, unique=True, index=True, nullable=False)  # Integer

    # ========================================================================
    # EXPRESSION (The DNA - NEVER exposed to clients)
    # ========================================================================
    expression_type = Column(String(50), nullable=False)  # "lambda", "constant", "function", etc.
    expression_code = Column(Text, nullable=False)  # The sacred DNA (server-side only)

    # ========================================================================
    # CLASSIFICATION (What kind of substrate is this?)
    # ========================================================================
    substrate_category = Column(String(50), nullable=True, index=True)
    # Values: "foundational", "complex", "dimensional", "object", "custom"

    # ========================================================================
    # METADATA (Optional hints about what the substrate represents)
    # ========================================================================
    metadata = Column(JSON, nullable=True)
    # Example: {
    #     "name": "Tesla Model 3",
    #     "description": "Electric vehicle substrate with all properties in superposition",
    #     "properties": ["battery", "motor", "wheels", "computer", "sensors"],
    #     "tags": ["vehicle", "electric", "transport"],
    #     "natural_law": "E=mc²",
    #     "dimension_type": "volume"
    # }

    # ========================================================================
    # DIMENSIONAL PROPERTIES (Derived from expression)
    # ========================================================================
    dimension_level = Column(Integer, nullable=True)
    # 0=point, 1=line, 2=plane, 3=volume, 4=hypervolume, etc.

    fibonacci_index = Column(Integer, nullable=True)
    # Position in Fibonacci sequence (0-8 for standard division)
    # 0→0, 1→1, 2→1, 3→2, 4→3, 5→5, 6→8, 7→13, 8→21

    # ========================================================================
    # OWNERSHIP & TRACKING
    # ========================================================================
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ========================================================================
    # OBSERVATION STATISTICS (How many times has potential collapsed?)
    # ========================================================================
    invocation_count = Column(Integer, default=0)  # Total observations
    last_invoked_at = Column(DateTime, nullable=True)  # Last observation time

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    owner = relationship("User", back_populates="substrates")
    
    def __repr__(self):
        return f"<SubstrateModel(identity={self.identity}, owner_id={self.owner_id})>"


class RelationshipModel(Base):
    """Persistent relationship storage."""
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    rel_type = Column(String(50), nullable=False, index=True)
    source_identity = Column(String(18), nullable=False, index=True)
    target_identity = Column(String(18), nullable=False, index=True)
    bidirectional = Column(Boolean, default=False)

    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<RelationshipModel(type={self.rel_type}, {self.source_identity}->{self.target_identity})>"


# ============================================================================
# LENS MODELS - Apply Context to Substrates
# ============================================================================

class LensModel(Base):
    """
    Lens Model - Applies Context to Reveal Substrate Truths

    PHILOSOPHY:
    A lens is a transformation that extracts specific truths from a substrate.
    The substrate contains ALL information - the lens reveals what you seek.

    Like looking at a prism through different angles:
    - White light contains all colors
    - The angle (lens) reveals specific colors
    - All colors exist simultaneously

    LENS TYPES:
    - Spectrum Lenses: color, sound, light, electromagnetic
    - Logic Lenses: truth_table, circuit, decision_tree
    - Physics Lenses: gravity, quantum, fluid, thermodynamics
    - Geometric Lenses: shape, symmetry, topology, curvature
    - Domain Lenses: economic, biological, temporal, linguistic
    - Design Lenses: golden_ratio, pi, fractal, aesthetic
    - Graphics Lenses: 3d_model, texture, lighting, rendering

    EXAMPLES:
    - Color Lens: distance_from_origin → hue (0-360°)
    - Sound Lens: height → frequency (20Hz - 20kHz)
    - Physics Lens: gradient → force vector
    - Economic Lens: supply_demand → price

    DATA EFFICIENCY:
    Instead of storing color data, sound data, 3D models separately,
    store ONE expression and apply lenses on demand.
    Compression ratio: 900,000:1 or higher
    """
    __tablename__ = "lenses"

    id = Column(Integer, primary_key=True, index=True)

    # Identity
    name = Column(String(100), unique=True, index=True, nullable=False)
    lens_type = Column(String(50), nullable=False, index=True)
    # Types: "spectrum", "logic", "physics", "geometric", "domain", "design", "graphics"

    # Transformation (How to extract truth from substrate)
    transformation_code = Column(Text, nullable=False)
    # Example: "lambda z, x, y: {'hue': (sqrt(x**2 + y**2) / max_dist) * 360}"

    # Configuration
    parameters = Column(JSON, nullable=True)
    # Example: {"max_distance": 100, "color_space": "HSV", "range": [0, 360]}

    # Metadata
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)
    # Categories: "color", "sound", "light", "gravity", "fluid", "economic", etc.

    input_type = Column(String(50), nullable=True)  # "substrate", "point", "field"
    output_type = Column(String(50), nullable=True)  # "scalar", "vector", "color", "frequency"

    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = system lens
    is_system = Column(Boolean, default=False)  # System lenses are built-in
    is_public = Column(Boolean, default=True)  # Public lenses can be used by anyone

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Statistics
    usage_count = Column(Integer, default=0)

    # Relationships
    owner = relationship("User", back_populates="lenses")

    def __repr__(self):
        return f"<Lens(name={self.name}, type={self.lens_type}, category={self.category})>"


class LensApplicationModel(Base):
    """
    Lens Application - Record of applying a lens to a substrate

    PHILOSOPHY:
    This tracks when a lens was applied to a substrate to extract specific truth.
    Like a query log - what questions were asked of which substrates.

    CACHING:
    Results can be cached for performance, but the truth always exists in the substrate.
    Cache is optional - the lens can always be reapplied.
    """
    __tablename__ = "lens_applications"

    id = Column(Integer, primary_key=True, index=True)

    # What was applied
    lens_id = Column(Integer, ForeignKey("lenses.id"), nullable=False)
    substrate_identity = Column(String(18), nullable=False, index=True)

    # Parameters used
    application_parameters = Column(JSON, nullable=True)
    # Example: {"x_range": [-10, 10], "y_range": [-10, 10], "resolution": 100}

    # Result (optional cache)
    result_cached = Column(Boolean, default=False)
    result_data = Column(JSON, nullable=True)  # Cached result (optional)
    result_hash = Column(String(64), nullable=True)  # Hash of result for validation

    # Performance
    computation_time_ms = Column(Float, nullable=True)

    # Tracking
    applied_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    lens = relationship("LensModel")
    user = relationship("User")

    def __repr__(self):
        return f"<LensApplication(lens_id={self.lens_id}, substrate={self.substrate_identity})>"


# ============================================================================
# SRL MODELS - Secure Resource Locator (Universal Connector)
# ============================================================================

class SRLConnectionModel(Base):
    """
    SRL Connection - Universal connector to external resources

    PHILOSOPHY:
    An SRL is like a library card - it knows how to fetch the book but doesn't copy it.
    It's a PASSIVE connection that only fetches data when invoked.

    SECURITY:
    - Credentials stored encrypted (AES-256)
    - Never exposed to clients
    - Per-user credentials
    - Audit trail for all fetches

    RESOURCE TYPES:
    - file: Local files, S3, FTP, SFTP
    - database: PostgreSQL, MySQL, MongoDB, Redis
    - api: REST, GraphQL, SOAP
    - stream: Kafka, RabbitMQ, WebSocket
    - web: HTTP requests, web scraping
    - game: Game servers, player data
    - app: Inter-app communication
    """
    __tablename__ = "srl_connections"

    id = Column(Integer, primary_key=True, index=True)

    # Link to substrate (SRL is a special substrate)
    substrate_identity = Column(String(18), ForeignKey("substrates.identity"), unique=True, nullable=False)

    # Connection details
    name = Column(String(200), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    # Types: "file", "database", "api", "stream", "web", "game", "app"

    protocol = Column(String(50), nullable=False)
    # Examples: "postgresql", "mysql", "mongodb", "redis", "http", "https", "s3", "kafka", "websocket"

    connection_string = Column(Text, nullable=False)
    # Examples: "postgresql://host:port/db", "https://api.example.com", "s3://bucket/path"

    auth_method = Column(String(50), nullable=False)
    # Methods: "none", "basic", "bearer", "api_key", "oauth", "certificate", "password"

    # Encrypted credentials (AES-256)
    encrypted_credentials = Column(Text, nullable=True)
    # Stored as JSON: {"username": "...", "password": "...", "api_key": "...", etc.}

    # Configuration
    config = Column(JSON, nullable=True)
    # Example: {"timeout": 30, "max_retries": 3, "pool_size": 10}

    # Behavior
    passive = Column(Boolean, default=True)  # True = fetch on demand, False = active connection
    allow_cache = Column(Boolean, default=False)  # Allow caching fetched data
    default_cache_ttl = Column(Integer, nullable=True)  # Default cache TTL in seconds

    # Ownership & tracking
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)

    # Statistics
    fetch_count = Column(Integer, default=0)
    total_bytes_fetched = Column(BigInteger, default=0)

    # Status
    status = Column(String(20), default="disconnected", nullable=False, index=True)
    # Values: "connected", "disconnected", "disabled", "connecting", "blacklisted"
    is_active = Column(Boolean, default=True)
    last_error = Column(Text, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="srl_connections")
    substrate = relationship("SubstrateModel", foreign_keys=[substrate_identity])
    fetch_logs = relationship("SRLFetchLogModel", back_populates="connection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SRLConnection(name={self.name}, type={self.resource_type}, protocol={self.protocol})>"


class SRLFetchLogModel(Base):
    """
    SRL Fetch Log - Audit trail of all data fetches

    PHILOSOPHY:
    Every time an SRL fetches data, it's logged for:
    - Security audit
    - Compliance (GDPR, etc.)
    - Performance monitoring
    - Usage analytics
    """
    __tablename__ = "srl_fetch_logs"

    id = Column(Integer, primary_key=True, index=True)

    # What was fetched
    connection_id = Column(Integer, ForeignKey("srl_connections.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Fetch details
    query = Column(Text, nullable=True)  # SQL query, API endpoint, file path, etc.
    parameters = Column(JSON, nullable=True)  # Query parameters, headers, etc.

    # Result
    success = Column(Boolean, nullable=False)
    result_size_bytes = Column(BigInteger, nullable=True)
    result_rows = Column(Integer, nullable=True)  # For database queries
    cached = Column(Boolean, default=False)

    # Performance
    duration_ms = Column(Float, nullable=False)

    # Error handling
    error_message = Column(Text, nullable=True)

    # Timestamp
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    connection = relationship("SRLConnectionModel", back_populates="fetch_logs")
    user = relationship("User")

    def __repr__(self):
        return f"<SRLFetchLog(connection_id={self.connection_id}, success={self.success}, duration={self.duration_ms}ms)>"


# ============================================================================
# METRICS MODELS
# ============================================================================

class MetricsSnapshot(Base):
    """Periodic metrics snapshots for historical tracking."""
    __tablename__ = "metrics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_substrates = Column(Integer, default=0)
    total_relationships = Column(Integer, default=0)
    total_invocations = Column(Integer, default=0)

    avg_response_time_ms = Column(Float, default=0.0)
    p95_response_time_ms = Column(Float, default=0.0)
    p99_response_time_ms = Column(Float, default=0.0)

    requests_per_second = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)

    memory_usage_mb = Column(Float, default=0.0)
    cpu_usage_percent = Column(Float, default=0.0)

    def __repr__(self):
        return f"<MetricsSnapshot(timestamp={self.timestamp}, substrates={self.total_substrates})>"


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_db():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")


# Current TOS version
CURRENT_TOS_VERSION = "1.0.0"


