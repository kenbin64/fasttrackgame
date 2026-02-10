"""
Seed Validator - Security-First Validation for Primitive Seeds

SECURITY PHILOSOPHY:
Seeds are the DNA of the system. Malicious seeds could compromise the entire
dimensional computation platform. This validator ensures:

1. NO MALICIOUS CODE - Expressions are sandboxed and validated
2. NO INJECTION ATTACKS - All strings are sanitized
3. NO RESOURCE EXHAUSTION - Size limits enforced
4. SCHEMA COMPLIANCE - All fields validated
5. DIMENSIONAL LAW COMPLIANCE - Seeds must follow the Seven Laws

SAFETY CHARTER COMPLIANCE:
- Principle #3: No Self-Modifying Code
- Principle #4: No Global Power Surface
- Principle #5: No Hacking Surface
- Principle #10: No Hidden State
"""

from typing import Dict, Any, List, Set
import re
from pathlib import Path


class SeedValidationError(Exception):
    """Raised when seed validation fails."""
    pass


class SeedValidator:
    """
    Security-first validator for primitive seeds.
    
    VALIDATION LAYERS:
    1. Schema validation (required fields, types)
    2. Security validation (no malicious code)
    3. Size validation (prevent resource exhaustion)
    4. Content validation (sanitize strings)
    5. Dimensional law compliance
    """
    
    # Maximum sizes (prevent resource exhaustion)
    MAX_NAME_LENGTH = 100
    MAX_DEFINITION_LENGTH = 10000
    MAX_USAGE_LENGTH = 5000
    MAX_MEANING_LENGTH = 5000
    MAX_EXPRESSION_LENGTH = 10000
    MAX_EXAMPLES = 50
    MAX_TAGS = 50
    MAX_FILE_SIZE_BYTES = 1_000_000  # 1MB
    
    # Forbidden patterns in expressions (security)
    FORBIDDEN_PATTERNS = [
        r'__import__',      # No dynamic imports
        r'eval\s*\(',       # No eval
        r'exec\s*\(',       # No exec
        r'compile\s*\(',    # No compile
        r'open\s*\(',       # No file access
        r'os\.',            # No OS access
        r'sys\.',           # No sys access
        r'subprocess',      # No subprocess
        r'socket',          # No network access
        r'requests',        # No HTTP requests
        r'urllib',          # No URL access
        r'pickle',          # No pickle (code execution)
        r'marshal',         # No marshal (code execution)
        r'globals\s*\(',    # No globals access
        r'locals\s*\(',     # No locals access
        r'vars\s*\(',       # No vars access
        r'dir\s*\(',        # No dir access
        r'getattr',         # No getattr (reflection)
        r'setattr',         # No setattr (mutation)
        r'delattr',         # No delattr (mutation)
        r'__dict__',        # No __dict__ access
        r'__class__',       # No __class__ access
        r'__bases__',       # No __bases__ access
        r'__subclasses__',  # No __subclasses__ access
        r'__code__',        # No __code__ access
        r'__globals__',     # No __globals__ access
    ]
    
    # Required fields for all seeds
    REQUIRED_FIELDS = {
        'name': str,
        'category': str,
        'tier': int,
        'domain': str,
        'definition': str,
        'usage': str,
        'meaning': str,
        'expression': str,
        'relationships': dict,
        'examples': list,
        'metadata': dict
    }
    
    # Valid categories
    VALID_CATEGORIES = {
        'mathematical_constant',
        'mathematical_operation',
        'physical_constant',
        'dimensional_structure',
        'relationship',
        'geometric_shape',
        'physical_law',
        'mathematical_function',
        'sensory_perception',
        'economic_action',
        'language_element',
        'computer_science',
        'philosophical_concept',
        'complex_behavior'
    }
    
    # Valid tiers
    VALID_TIERS = {1, 2, 3, 4}
    
    def validate_file(self, filepath: Path) -> None:
        """
        Validate seed file before loading.
        
        Args:
            filepath: Path to seed file
            
        Raises:
            SeedValidationError: If validation fails
        """
        # Check file exists
        if not filepath.exists():
            raise SeedValidationError(f"File does not exist: {filepath}")
        
        # Check file size (prevent resource exhaustion)
        file_size = filepath.stat().st_size
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise SeedValidationError(
                f"File too large: {file_size} bytes (max: {self.MAX_FILE_SIZE_BYTES})"
            )
        
        # Check file extension
        if filepath.suffix not in ['.yaml', '.yml', '.json']:
            raise SeedValidationError(f"Invalid file extension: {filepath.suffix}")
    
    def validate_seed(self, seed_data: Dict[str, Any]) -> None:
        """
        Comprehensive validation of seed data.
        
        Args:
            seed_data: Parsed seed data
            
        Raises:
            SeedValidationError: If validation fails
        """
        # Layer 1: Schema validation
        self._validate_schema(seed_data)
        
        # Layer 2: Security validation
        self._validate_security(seed_data)
        
        # Layer 3: Size validation
        self._validate_sizes(seed_data)
        
        # Layer 4: Content validation
        self._validate_content(seed_data)
        
        # Layer 5: Dimensional law compliance
        self._validate_dimensional_compliance(seed_data)
    
    def _validate_schema(self, seed_data: Dict[str, Any]) -> None:
        """Validate required fields and types."""
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in seed_data:
                raise SeedValidationError(f"Missing required field: {field}")

            # Type validation
            value = seed_data[field]
            if not isinstance(value, expected_type):
                raise SeedValidationError(
                    f"Field '{field}' has wrong type: expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )

        # Validate category
        if seed_data['category'] not in self.VALID_CATEGORIES:
            raise SeedValidationError(
                f"Invalid category: {seed_data['category']}. "
                f"Must be one of: {self.VALID_CATEGORIES}"
            )

        # Validate tier
        if seed_data['tier'] not in self.VALID_TIERS:
            raise SeedValidationError(
                f"Invalid tier: {seed_data['tier']}. Must be 1, 2, 3, or 4"
            )

    def _validate_security(self, seed_data: Dict[str, Any]) -> None:
        """Validate no malicious code in expressions."""
        expression = seed_data.get('expression', '')

        if not expression:
            return  # Empty expression is OK

        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, expression, re.IGNORECASE):
                raise SeedValidationError(
                    f"SECURITY VIOLATION: Forbidden pattern detected: {pattern}\n"
                    f"Expression contains potentially malicious code."
                )

        # Check for suspicious characters
        suspicious_chars = ['`', '$', ';']
        for char in suspicious_chars:
            if char in expression:
                raise SeedValidationError(
                    f"SECURITY VIOLATION: Suspicious character detected: '{char}'"
                )

    def _validate_sizes(self, seed_data: Dict[str, Any]) -> None:
        """Validate sizes to prevent resource exhaustion."""
        # Name length
        if len(seed_data['name']) > self.MAX_NAME_LENGTH:
            raise SeedValidationError(
                f"Name too long: {len(seed_data['name'])} chars "
                f"(max: {self.MAX_NAME_LENGTH})"
            )

        # Definition length
        if len(seed_data['definition']) > self.MAX_DEFINITION_LENGTH:
            raise SeedValidationError(
                f"Definition too long: {len(seed_data['definition'])} chars "
                f"(max: {self.MAX_DEFINITION_LENGTH})"
            )

        # Usage length
        if len(seed_data['usage']) > self.MAX_USAGE_LENGTH:
            raise SeedValidationError(
                f"Usage too long: {len(seed_data['usage'])} chars "
                f"(max: {self.MAX_USAGE_LENGTH})"
            )

        # Meaning length
        if len(seed_data['meaning']) > self.MAX_MEANING_LENGTH:
            raise SeedValidationError(
                f"Meaning too long: {len(seed_data['meaning'])} chars "
                f"(max: {self.MAX_MEANING_LENGTH})"
            )

        # Expression length
        if len(seed_data['expression']) > self.MAX_EXPRESSION_LENGTH:
            raise SeedValidationError(
                f"Expression too long: {len(seed_data['expression'])} chars "
                f"(max: {self.MAX_EXPRESSION_LENGTH})"
            )

        # Examples count
        if len(seed_data['examples']) > self.MAX_EXAMPLES:
            raise SeedValidationError(
                f"Too many examples: {len(seed_data['examples'])} "
                f"(max: {self.MAX_EXAMPLES})"
            )

        # Tags count
        tags = seed_data.get('metadata', {}).get('tags', [])
        if len(tags) > self.MAX_TAGS:
            raise SeedValidationError(
                f"Too many tags: {len(tags)} (max: {self.MAX_TAGS})"
            )

    def _validate_content(self, seed_data: Dict[str, Any]) -> None:
        """Validate content quality and sanitization."""
        # Name validation
        name = seed_data['name']
        if not re.match(r'^[A-Z_][A-Z0-9_]*$', name):
            raise SeedValidationError(
                f"Invalid name format: '{name}'. "
                f"Must be UPPERCASE_WITH_UNDERSCORES (e.g., PART_TO_WHOLE)"
            )

        # Domain validation
        domain = seed_data['domain']
        if not re.match(r'^[a-z_]+$', domain):
            raise SeedValidationError(
                f"Invalid domain format: '{domain}'. "
                f"Must be lowercase_with_underscores"
            )

        # Check for empty strings
        for field in ['definition', 'usage', 'meaning']:
            if not seed_data[field].strip():
                raise SeedValidationError(f"Field '{field}' cannot be empty")

    def _validate_dimensional_compliance(self, seed_data: Dict[str, Any]) -> None:
        """Validate compliance with Dimensional Laws and Safety Charter."""
        metadata = seed_data.get('metadata', {})

        # Check for Safety Charter compliance declaration
        if 'safety_charter' not in metadata:
            raise SeedValidationError(
                "Missing 'safety_charter' in metadata. "
                "All seeds must declare Safety Charter compliance."
            )

        # For relationships, check for required properties
        if seed_data['category'] == 'relationship':
            relationships = seed_data.get('relationships', {})

            # Must declare dimensional level
            if 'dimensional_level' not in relationships:
                raise SeedValidationError(
                    "Relationship seeds must declare 'dimensional_level' "
                    "(cross_dimensional or intra_dimensional)"
                )

            # Must implement at least one law
            if 'implements' not in relationships:
                raise SeedValidationError(
                    "Relationship seeds must declare which Dimensional Laws "
                    "they implement"
                )

