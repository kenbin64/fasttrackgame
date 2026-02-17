"""
ButterflyFX Validators - Input Validation Utilities

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

Attribution required: Kenneth Bingham - https://butterflyfx.us

---

Validators for ensuring data integrity in ButterflyFX operations.

Validators:
    - Level validators: Ensure valid dimensional levels
    - Token validators: Validate token structure
    - State validators: Validate helix state transitions
    - Signature validators: Validate level signatures
    - Payload validators: Validate payload content
"""

from __future__ import annotations
from typing import Any, Dict, List, Union, Optional, Set, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
import re

from .kernel import HelixState, LEVEL_NAMES
from .substrate import Token, PayloadSource


# =============================================================================
# VALIDATION RESULT
# =============================================================================

class ValidationSeverity(Enum):
    """Severity level of validation issues"""
    ERROR = "error"       # Must be fixed
    WARNING = "warning"   # Should be reviewed
    INFO = "info"         # Informational only


@dataclass
class ValidationIssue:
    """A single validation issue"""
    field: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    value: Any = None
    
    def __str__(self):
        return f"[{self.severity.value.upper()}] {self.field}: {self.message}"


@dataclass
class ValidationResult:
    """Complete validation result"""
    valid: bool
    issues: List[ValidationIssue]
    
    def __bool__(self):
        return self.valid
    
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]
    
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]
    
    def raise_if_invalid(self):
        """Raise ValueError if validation failed"""
        if not self.valid:
            errors = self.errors()
            raise ValueError(f"Validation failed: {'; '.join(str(e) for e in errors)}")
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        return cls(valid=True, issues=[])
    
    @classmethod
    def failure(cls, issues: List[ValidationIssue]) -> 'ValidationResult':
        return cls(valid=False, issues=issues)
    
    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge two validation results"""
        return ValidationResult(
            valid=self.valid and other.valid,
            issues=self.issues + other.issues
        )


# =============================================================================
# LEVEL VALIDATORS
# =============================================================================

def validate_level(level: Any) -> ValidationResult:
    """Validate that a value is a valid helix level (0-6)"""
    issues = []
    
    if not isinstance(level, int):
        issues.append(ValidationIssue(
            field="level",
            message=f"Level must be an integer, got {type(level).__name__}",
            value=level
        ))
        return ValidationResult(valid=False, issues=issues)
    
    if level < 0:
        issues.append(ValidationIssue(
            field="level",
            message=f"Level cannot be negative, got {level}",
            value=level
        ))
    elif level > 6:
        issues.append(ValidationIssue(
            field="level",
            message=f"Level cannot exceed 6, got {level}",
            value=level
        ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_level_range(min_level: int, max_level: int) -> ValidationResult:
    """Validate a level range is valid"""
    issues = []
    
    min_result = validate_level(min_level)
    max_result = validate_level(max_level)
    issues.extend(min_result.issues)
    issues.extend(max_result.issues)
    
    if min_result.valid and max_result.valid:
        if min_level > max_level:
            issues.append(ValidationIssue(
                field="level_range",
                message=f"min_level ({min_level}) cannot exceed max_level ({max_level})"
            ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


# =============================================================================
# SPIRAL VALIDATORS
# =============================================================================

def validate_spiral(spiral: Any) -> ValidationResult:
    """Validate spiral number (any integer)"""
    issues = []
    
    if not isinstance(spiral, int):
        issues.append(ValidationIssue(
            field="spiral",
            message=f"Spiral must be an integer, got {type(spiral).__name__}",
            value=spiral
        ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_spiral_range(min_spiral: int, max_spiral: int) -> ValidationResult:
    """Validate a spiral range"""
    issues = []
    
    if not isinstance(min_spiral, int) or not isinstance(max_spiral, int):
        issues.append(ValidationIssue(
            field="spiral_range",
            message="Spiral values must be integers"
        ))
    elif min_spiral > max_spiral:
        issues.append(ValidationIssue(
            field="spiral_range",
            message=f"min_spiral ({min_spiral}) cannot exceed max_spiral ({max_spiral})"
        ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


# =============================================================================
# STATE VALIDATORS
# =============================================================================

def validate_state(state: Any) -> ValidationResult:
    """Validate a HelixState object or tuple"""
    issues = []
    
    if isinstance(state, HelixState):
        spiral, level = state.spiral, state.level
    elif isinstance(state, tuple) and len(state) == 2:
        spiral, level = state
    else:
        issues.append(ValidationIssue(
            field="state",
            message=f"State must be HelixState or (spiral, level) tuple, got {type(state).__name__}",
            value=state
        ))
        return ValidationResult(valid=False, issues=issues)
    
    spiral_result = validate_spiral(spiral)
    level_result = validate_level(level)
    issues.extend(spiral_result.issues)
    issues.extend(level_result.issues)
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_state_transition(from_state: HelixState, to_state: HelixState, operation: str) -> ValidationResult:
    """
    Validate that a state transition is legal.
    
    Operations:
        - INVOKE: Any level change within same spiral
        - SPIRAL_UP: Must be at level 6, moves to (spiral+1, 0)
        - SPIRAL_DOWN: Must be at level 0, moves to (spiral-1, 6)
        - COLLAPSE: Returns to level 0
    """
    issues = []
    
    if operation == "INVOKE":
        if from_state.spiral != to_state.spiral:
            issues.append(ValidationIssue(
                field="transition",
                message=f"INVOKE cannot change spiral (from {from_state.spiral} to {to_state.spiral})"
            ))
    
    elif operation == "SPIRAL_UP":
        if from_state.level != 6:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_UP requires level 6, current level is {from_state.level}"
            ))
        if to_state.spiral != from_state.spiral + 1:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_UP must increase spiral by 1"
            ))
        if to_state.level != 0:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_UP must set level to 0"
            ))
    
    elif operation == "SPIRAL_DOWN":
        if from_state.level != 0:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_DOWN requires level 0, current level is {from_state.level}"
            ))
        if to_state.spiral != from_state.spiral - 1:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_DOWN must decrease spiral by 1"
            ))
        if to_state.level != 6:
            issues.append(ValidationIssue(
                field="transition",
                message=f"SPIRAL_DOWN must set level to 6"
            ))
    
    elif operation == "COLLAPSE":
        if to_state.level != 0:
            issues.append(ValidationIssue(
                field="transition",
                message=f"COLLAPSE must set level to 0"
            ))
        if from_state.spiral != to_state.spiral:
            issues.append(ValidationIssue(
                field="transition",
                message=f"COLLAPSE cannot change spiral"
            ))
    
    else:
        issues.append(ValidationIssue(
            field="operation",
            message=f"Unknown operation: {operation}"
        ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


# =============================================================================
# TOKEN VALIDATORS
# =============================================================================

def validate_token_id(token_id: str) -> ValidationResult:
    """Validate token ID format"""
    issues = []
    
    if not isinstance(token_id, str):
        issues.append(ValidationIssue(
            field="token_id",
            message=f"Token ID must be string, got {type(token_id).__name__}",
            value=token_id
        ))
        return ValidationResult(valid=False, issues=issues)
    
    if not token_id:
        issues.append(ValidationIssue(
            field="token_id",
            message="Token ID cannot be empty"
        ))
    
    # Check for problematic characters
    if any(c in token_id for c in '\n\r\t'):
        issues.append(ValidationIssue(
            field="token_id",
            message="Token ID contains invalid whitespace characters",
            severity=ValidationSeverity.WARNING
        ))
    
    return ValidationResult(valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues=issues)


def validate_signature(signature: Any) -> ValidationResult:
    """Validate token signature (set of levels)"""
    issues = []
    
    if not isinstance(signature, (set, frozenset)):
        issues.append(ValidationIssue(
            field="signature",
            message=f"Signature must be a set, got {type(signature).__name__}",
            value=signature
        ))
        return ValidationResult(valid=False, issues=issues)
    
    if len(signature) == 0:
        issues.append(ValidationIssue(
            field="signature",
            message="Signature cannot be empty"
        ))
    
    for level in signature:
        level_result = validate_level(level)
        for issue in level_result.issues:
            issue.field = f"signature[{level}]"
            issues.append(issue)
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_location(location: Any) -> ValidationResult:
    """Validate token location (tuple of coordinates)"""
    issues = []
    
    if not isinstance(location, tuple):
        issues.append(ValidationIssue(
            field="location",
            message=f"Location must be a tuple, got {type(location).__name__}",
            value=location
        ))
        return ValidationResult(valid=False, issues=issues)
    
    if len(location) == 0:
        issues.append(ValidationIssue(
            field="location",
            message="Location cannot be empty"
        ))
    
    for i, coord in enumerate(location):
        if not isinstance(coord, (int, float)):
            issues.append(ValidationIssue(
                field=f"location[{i}]",
                message=f"Coordinate must be numeric, got {type(coord).__name__}",
                value=coord
            ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_token(token: Any) -> ValidationResult:
    """Complete token validation"""
    issues = []
    
    if not isinstance(token, Token):
        issues.append(ValidationIssue(
            field="token",
            message=f"Expected Token, got {type(token).__name__}",
            value=token
        ))
        return ValidationResult(valid=False, issues=issues)
    
    # Validate components
    id_result = validate_token_id(token.id)
    location_result = validate_location(token.location)
    signature_result = validate_signature(token.signature)
    
    issues.extend(id_result.issues)
    issues.extend(location_result.issues)
    issues.extend(signature_result.issues)
    
    # Check payload is callable
    if not callable(token.payload):
        issues.append(ValidationIssue(
            field="payload",
            message="Token payload must be callable"
        ))
    
    return ValidationResult(valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues=issues)


# =============================================================================
# PAYLOAD VALIDATORS
# =============================================================================

def validate_json_serializable(value: Any) -> ValidationResult:
    """Validate that a value can be serialized to JSON"""
    import json
    issues = []
    
    try:
        json.dumps(value)
    except (TypeError, ValueError) as e:
        issues.append(ValidationIssue(
            field="payload",
            message=f"Value is not JSON serializable: {e}",
            value=type(value).__name__
        ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


def validate_payload_schema(payload: Dict, schema: Dict[str, type]) -> ValidationResult:
    """
    Validate payload against a schema.
    
    Schema format: {'field_name': expected_type, ...}
    """
    issues = []
    
    if not isinstance(payload, dict):
        issues.append(ValidationIssue(
            field="payload",
            message=f"Payload must be dict, got {type(payload).__name__}"
        ))
        return ValidationResult(valid=False, issues=issues)
    
    for field, expected_type in schema.items():
        if field not in payload:
            issues.append(ValidationIssue(
                field=f"payload.{field}",
                message=f"Missing required field: {field}"
            ))
        elif not isinstance(payload[field], expected_type):
            issues.append(ValidationIssue(
                field=f"payload.{field}",
                message=f"Expected {expected_type.__name__}, got {type(payload[field]).__name__}",
                value=payload[field]
            ))
    
    return ValidationResult(valid=len(issues) == 0, issues=issues)


# =============================================================================
# PATH VALIDATORS
# =============================================================================

def validate_helix_path(path: str) -> ValidationResult:
    """
    Validate helix path format.
    
    Valid formats:
        - "6.root/5.child/4.leaf"
        - "root/child/leaf" (levels inferred)
    """
    issues = []
    
    if not isinstance(path, str):
        issues.append(ValidationIssue(
            field="path",
            message=f"Path must be string, got {type(path).__name__}"
        ))
        return ValidationResult(valid=False, issues=issues)
    
    if not path:
        issues.append(ValidationIssue(
            field="path",
            message="Path cannot be empty"
        ))
        return ValidationResult(valid=False, issues=issues)
    
    segments = path.split('/')
    prev_level = 7
    
    for i, segment in enumerate(segments):
        if '.' in segment:
            parts = segment.split('.', 1)
            try:
                level = int(parts[0])
                if level < 0 or level > 6:
                    issues.append(ValidationIssue(
                        field=f"path[{i}]",
                        message=f"Invalid level {level} in segment '{segment}'"
                    ))
                if level > prev_level:
                    issues.append(ValidationIssue(
                        field=f"path[{i}]",
                        message=f"Level {level} increases from previous {prev_level} (path should descend)",
                        severity=ValidationSeverity.WARNING
                    ))
                prev_level = level
            except ValueError:
                issues.append(ValidationIssue(
                    field=f"path[{i}]",
                    message=f"Invalid level format in segment '{segment}'"
                ))
    
    return ValidationResult(valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0, issues=issues)


# =============================================================================
# COMPOSITE VALIDATORS
# =============================================================================

class Validator:
    """
    Fluent validator builder.
    
    Usage:
        result = Validator(value).is_int().in_range(0, 6).validate()
    """
    
    def __init__(self, value: Any, field_name: str = "value"):
        self.value = value
        self.field_name = field_name
        self.checks: List[Callable[[], ValidationResult]] = []
    
    def is_type(self, expected_type: type) -> 'Validator':
        """Check value is of expected type"""
        def check():
            if not isinstance(self.value, expected_type):
                return ValidationResult.failure([ValidationIssue(
                    field=self.field_name,
                    message=f"Expected {expected_type.__name__}, got {type(self.value).__name__}",
                    value=self.value
                )])
            return ValidationResult.success()
        self.checks.append(check)
        return self
    
    def is_int(self) -> 'Validator':
        return self.is_type(int)
    
    def is_str(self) -> 'Validator':
        return self.is_type(str)
    
    def is_dict(self) -> 'Validator':
        return self.is_type(dict)
    
    def in_range(self, min_val: Any, max_val: Any) -> 'Validator':
        """Check value is in range [min_val, max_val]"""
        def check():
            if not (min_val <= self.value <= max_val):
                return ValidationResult.failure([ValidationIssue(
                    field=self.field_name,
                    message=f"Value {self.value} not in range [{min_val}, {max_val}]",
                    value=self.value
                )])
            return ValidationResult.success()
        self.checks.append(check)
        return self
    
    def not_empty(self) -> 'Validator':
        """Check value is not empty"""
        def check():
            if not self.value:
                return ValidationResult.failure([ValidationIssue(
                    field=self.field_name,
                    message="Value cannot be empty",
                    value=self.value
                )])
            return ValidationResult.success()
        self.checks.append(check)
        return self
    
    def matches(self, pattern: str) -> 'Validator':
        """Check string value matches regex pattern"""
        def check():
            if not re.match(pattern, str(self.value)):
                return ValidationResult.failure([ValidationIssue(
                    field=self.field_name,
                    message=f"Value does not match pattern '{pattern}'",
                    value=self.value
                )])
            return ValidationResult.success()
        self.checks.append(check)
        return self
    
    def custom(self, check_fn: Callable[[Any], bool], message: str) -> 'Validator':
        """Add custom validation check"""
        def check():
            if not check_fn(self.value):
                return ValidationResult.failure([ValidationIssue(
                    field=self.field_name,
                    message=message,
                    value=self.value
                )])
            return ValidationResult.success()
        self.checks.append(check)
        return self
    
    def validate(self) -> ValidationResult:
        """Run all validation checks"""
        result = ValidationResult.success()
        for check in self.checks:
            result = result.merge(check())
        return result


# =============================================================================
# QUICK VALIDATORS
# =============================================================================

def is_valid_level(level: Any) -> bool:
    """Quick check if level is valid"""
    return isinstance(level, int) and 0 <= level <= 6


def is_valid_state(state: Any) -> bool:
    """Quick check if state is valid"""
    return validate_state(state).valid


def is_valid_token(token: Any) -> bool:
    """Quick check if token is valid"""
    return validate_token(token).valid


def ensure_level(level: Any) -> int:
    """Ensure value is valid level, raise if not"""
    result = validate_level(level)
    result.raise_if_invalid()
    return level


def ensure_state(state: Any) -> HelixState:
    """Ensure value is valid state, raise if not"""
    result = validate_state(state)
    result.raise_if_invalid()
    if isinstance(state, tuple):
        return HelixState(state[0], state[1])
    return state
