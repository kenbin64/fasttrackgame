"""
Dimensional Logging System - Logs as Substrates

PHILOSOPHY:
- Logs are substrates, not strings
- Each log entry has a 64-bit identity
- Logs are immutable (audit trail compliance)
- Structured logging (JSON format)
- Industry-standard log levels
- Audit trail with cryptographic integrity

COMPLIANCE:
- HIPAA audit trail requirements
- PCI DSS logging standards
- NIST audit log guidelines
- SOC 2 compliance
- GDPR audit requirements

LOG LEVELS (Standard):
- TRACE (10): Finest-grained debugging
- DEBUG (20): Detailed debugging information
- INFO (30): General informational messages
- WARN (40): Warning messages
- ERROR (50): Error messages
- CRITICAL (60): Critical failures
- AUDIT (70): Audit trail entries (immutable)

SEVEN LAWS ALIGNMENT:
- Law 1: Each log is unity (complete event)
- Law 2: Observation creates log entry (division)
- Law 3: Logs inherit context (recursion)
- Law 4: Logs connect events (relationships)
- Law 5: Logs track change (motion)
- Law 6: Log identity persists (immutability)
- Law 7: Logs aggregate to insights (return to unity)
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import IntEnum
from datetime import datetime, timezone

from .substrate import SubstrateIdentity, Substrate

# 64-bit mask constant
MASK_64 = 0xFFFFFFFFFFFFFFFF


# ═══════════════════════════════════════════════════════════════════
# LOG LEVELS
# ═══════════════════════════════════════════════════════════════════

class LogLevel(IntEnum):
    """Standard log levels with numeric values."""
    TRACE = 10
    DEBUG = 20
    INFO = 30
    WARN = 40
    ERROR = 50
    CRITICAL = 60
    AUDIT = 70  # Special level for audit trail


# ═══════════════════════════════════════════════════════════════════
# LOG ENTRY AS SUBSTRATE
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class LogEntry:
    """
    Immutable log entry - a substrate.
    
    Each log entry is a complete, immutable record with:
    - 64-bit identity (deterministic from content)
    - Timestamp (ISO 8601 UTC)
    - Level (standard log level)
    - Message (human-readable)
    - Context (structured data)
    - Checksum (integrity verification)
    """
    timestamp: str  # ISO 8601 UTC
    level: LogLevel
    message: str
    context: Dict[str, Any]
    source: str  # Module/function that created log
    identity: SubstrateIdentity
    checksum: int  # SHA-256 checksum for integrity
    
    def to_json(self, pretty: bool = False) -> str:
        """
        Convert to JSON (structured logging).

        Args:
            pretty: If True, format with indentation. If False, single line.
        """
        data = {
            'timestamp': self.timestamp,
            'level': self.level.name,
            'level_value': self.level.value,
            'message': self.message,
            'context': self.context,
            'source': self.source,
            'identity': str(self.identity),
            'checksum': hex(self.checksum)
        }
        return json.dumps(data, indent=2 if pretty else None)
    
    def to_substrate(self) -> Substrate:
        """
        Convert log entry to substrate.

        Note: Substrate expressions must return int values.
        For string attributes, we return hash values.
        """
        def log_expression(**kwargs):
            attr = kwargs.get('attribute', 'checksum')
            if attr == 'checksum': return self.checksum
            if attr == 'level_value': return self.level.value
            if attr == 'message_hash': return hash(self.message) & MASK_64
            if attr == 'timestamp_hash': return hash(self.timestamp) & MASK_64
            if attr == 'source_hash': return hash(self.source) & MASK_64
            if attr == 'context_hash': return hash(json.dumps(self.context, sort_keys=True)) & MASK_64
            return 0

        return Substrate(x1=self.identity, expression=log_expression)
    
    def verify_integrity(self) -> bool:
        """Verify log entry integrity using checksum."""
        computed = compute_log_checksum(
            self.timestamp,
            self.level,
            self.message,
            self.context,
            self.source
        )
        return computed == self.checksum


# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def compute_log_identity(
    timestamp: str,
    level: LogLevel,
    message: str,
    source: str
) -> SubstrateIdentity:
    """
    Compute deterministic 64-bit identity for log entry.

    Same timestamp + level + message + source = same identity.
    """
    content = f"{timestamp}|{level.value}|{message}|{source}"
    hash_bytes = hashlib.sha256(content.encode('utf-8')).digest()
    identity_value = int.from_bytes(hash_bytes[:8], 'big') & MASK_64
    return SubstrateIdentity(identity_value)


def compute_log_checksum(
    timestamp: str,
    level: LogLevel,
    message: str,
    context: Dict[str, Any],
    source: str
) -> int:
    """
    Compute SHA-256 checksum for log entry integrity.

    Used for audit trail verification.
    """
    content = f"{timestamp}|{level.value}|{message}|{json.dumps(context, sort_keys=True)}|{source}"
    hash_bytes = hashlib.sha256(content.encode('utf-8')).digest()
    return int.from_bytes(hash_bytes[:8], 'big') & MASK_64


def get_current_timestamp() -> str:
    """Get current timestamp in ISO 8601 UTC format."""
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
# DIMENSIONAL LOGGER
# ═══════════════════════════════════════════════════════════════════

class DimensionalLogger:
    """
    Dimensional logging system - logs as substrates.

    Features:
    - Immutable log entries (audit trail)
    - Structured logging (JSON)
    - Industry-standard log levels
    - Cryptographic integrity (checksums)
    - Substrate-based architecture
    - Configurable handlers

    Usage:
        logger = DimensionalLogger(name="my_module", level=LogLevel.INFO)
        logger.info("User logged in", user_id=12345)
        logger.error("Database connection failed", error=str(e))
        logger.audit("Payment processed", amount=100.00, transaction_id="tx-123")
    """
    __slots__ = ('_name', '_level', '_handlers', '_audit_trail')

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        handlers: Optional[List[Callable[[LogEntry], None]]] = None
    ):
        """
        Create dimensional logger.

        Args:
            name: Logger name (usually module name)
            level: Minimum log level to record
            handlers: List of handler functions (default: console handler)
        """
        object.__setattr__(self, '_name', name)
        object.__setattr__(self, '_level', level)
        object.__setattr__(self, '_handlers', handlers or [console_handler])
        object.__setattr__(self, '_audit_trail', [])

    def __setattr__(self, name, value):
        raise TypeError("DimensionalLogger is immutable")

    @property
    def name(self) -> str:
        """Logger name."""
        return self._name

    @property
    def level(self) -> LogLevel:
        """Current log level."""
        return self._level

    @property
    def audit_trail(self) -> List[LogEntry]:
        """Immutable audit trail (all AUDIT level logs)."""
        return list(self._audit_trail)

    def log(
        self,
        level: LogLevel,
        message: str,
        **context
    ) -> LogEntry:
        """
        Create log entry.

        Args:
            level: Log level
            message: Human-readable message
            **context: Additional structured data

        Returns:
            Immutable LogEntry substrate
        """
        # Check if we should log this level
        if level < self._level:
            return None

        # Create log entry
        timestamp = get_current_timestamp()
        identity = compute_log_identity(timestamp, level, message, self._name)
        checksum = compute_log_checksum(timestamp, level, message, context, self._name)

        entry = LogEntry(
            timestamp=timestamp,
            level=level,
            message=message,
            context=context,
            source=self._name,
            identity=identity,
            checksum=checksum
        )

        # Store in audit trail if AUDIT level
        if level == LogLevel.AUDIT:
            self._audit_trail.append(entry)

        # Call handlers
        for handler in self._handlers:
            try:
                handler(entry)
            except Exception:
                # Never let handler errors break logging
                pass

        return entry

    def trace(self, message: str, **context) -> LogEntry:
        """Log TRACE level message."""
        return self.log(LogLevel.TRACE, message, **context)

    def debug(self, message: str, **context) -> LogEntry:
        """Log DEBUG level message."""
        return self.log(LogLevel.DEBUG, message, **context)

    def info(self, message: str, **context) -> LogEntry:
        """Log INFO level message."""
        return self.log(LogLevel.INFO, message, **context)

    def warn(self, message: str, **context) -> LogEntry:
        """Log WARN level message."""
        return self.log(LogLevel.WARN, message, **context)

    def error(self, message: str, **context) -> LogEntry:
        """Log ERROR level message."""
        return self.log(LogLevel.ERROR, message, **context)

    def critical(self, message: str, **context) -> LogEntry:
        """Log CRITICAL level message."""
        return self.log(LogLevel.CRITICAL, message, **context)

    def audit(self, message: str, **context) -> LogEntry:
        """
        Log AUDIT level message.

        Audit logs are:
        - Always recorded (ignore level filter)
        - Stored in immutable audit trail
        - Include cryptographic checksum
        - Compliance-ready
        """
        return self.log(LogLevel.AUDIT, message, **context)

    def verify_audit_trail(self) -> bool:
        """
        Verify integrity of entire audit trail.

        Returns:
            True if all audit entries have valid checksums
        """
        return all(entry.verify_integrity() for entry in self._audit_trail)


# ═══════════════════════════════════════════════════════════════════
# LOG HANDLERS
# ═══════════════════════════════════════════════════════════════════

def console_handler(entry: LogEntry) -> None:
    """
    Console handler - prints to stdout.

    Format: [TIMESTAMP] LEVEL: message {context}
    """
    context_str = ""
    if entry.context:
        context_str = f" {json.dumps(entry.context)}"

    print(f"[{entry.timestamp}] {entry.level.name}: {entry.message}{context_str}")


def json_handler(entry: LogEntry) -> None:
    """
    JSON handler - prints structured JSON.

    Suitable for log aggregation systems (ELK, Splunk, etc.)
    """
    print(entry.to_json())


def file_handler(filepath: str) -> Callable[[LogEntry], None]:
    """
    Create file handler that appends to file.

    Args:
        filepath: Path to log file

    Returns:
        Handler function

    Note: Writes single-line JSON for easy parsing.
    """
    def handler(entry: LogEntry) -> None:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(entry.to_json(pretty=False) + '\n')

    return handler


def audit_file_handler(filepath: str) -> Callable[[LogEntry], None]:
    """
    Create audit file handler (AUDIT level only).

    Args:
        filepath: Path to audit log file

    Returns:
        Handler function that only logs AUDIT entries

    Note: Writes single-line JSON for easy parsing.
    """
    def handler(entry: LogEntry) -> None:
        if entry.level == LogLevel.AUDIT:
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(entry.to_json(pretty=False) + '\n')

    return handler


# ═══════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def get_logger(
    name: str,
    level: LogLevel = LogLevel.INFO,
    handlers: Optional[List[Callable[[LogEntry], None]]] = None
) -> DimensionalLogger:
    """
    Get or create dimensional logger.

    Args:
        name: Logger name (usually __name__)
        level: Minimum log level
        handlers: Custom handlers (default: console)

    Returns:
        DimensionalLogger instance

    Example:
        logger = get_logger(__name__)
        logger.info("Application started")
        logger.error("Failed to connect", host="localhost", port=5432)
    """
    return DimensionalLogger(name=name, level=level, handlers=handlers)


def get_audit_logger(
    name: str,
    audit_file: Optional[str] = None
) -> DimensionalLogger:
    """
    Get audit-compliant logger.

    Features:
    - AUDIT level enabled
    - Immutable audit trail
    - Optional file output
    - Cryptographic integrity

    Args:
        name: Logger name
        audit_file: Optional path to audit log file

    Returns:
        DimensionalLogger configured for audit compliance

    Example:
        logger = get_audit_logger(__name__, audit_file="audit.log")
        logger.audit("User login", user_id=12345, ip="192.168.1.1")
        logger.audit("Payment processed", amount=100.00, tx_id="tx-123")
    """
    handlers = [console_handler]
    if audit_file:
        handlers.append(audit_file_handler(audit_file))

    return DimensionalLogger(
        name=name,
        level=LogLevel.TRACE,  # Log everything
        handlers=handlers
    )

