"""
Terms of Service (TOS) enforcement system.

Monitors usage patterns for TOS compliance WITHOUT inspecting content.

Privacy-first:
- NO content inspection
- NO file access
- NO query logging
- ONLY pattern analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class ViolationType(str, Enum):
    """Types of TOS violations."""
    EXCESSIVE_CPU = "excessive_cpu"
    EXCESSIVE_BANDWIDTH = "excessive_bandwidth"
    EXCESSIVE_API_CALLS = "excessive_api_calls"
    SPAM_DETECTED = "spam_detected"
    MALWARE_DETECTED = "malware_detected"
    DDOS_DETECTED = "ddos_detected"
    COPYRIGHT_COMPLAINT = "copyright_complaint"
    ABUSE_REPORTED = "abuse_reported"


@dataclass
class TOSViolation:
    """Record of a TOS violation."""
    user_id: str
    violation_type: ViolationType
    timestamp: datetime
    severity: str  # 'low', 'medium', 'high', 'critical'
    details: str  # Description (NO content)
    action_taken: str  # 'warning', 'suspension', 'termination'


class TOSEnforcement:
    """
    Enforce Terms of Service through pattern analysis.
    
    NO content inspection - only metrics and patterns.
    """
    
    # Thresholds for violations
    MAX_CPU_HOURS_PER_DAY = 24 * 8  # 8 cores × 24 hours
    MAX_BANDWIDTH_GB_PER_DAY = 1000  # 1 TB/day
    MAX_API_CALLS_PER_HOUR = 10000
    MAX_DB_QUERIES_PER_HOUR = 50000
    MAX_FILE_OPERATIONS_PER_HOUR = 10000
    
    def __init__(self):
        self.violations: Dict[str, List[TOSViolation]] = {}
    
    def check_resource_abuse(self, user_id: str, metrics: Dict[str, Any]) -> Optional[TOSViolation]:
        """
        Check for resource abuse based on metrics.
        
        Args:
            user_id: Anonymous user ID
            metrics: Resource usage metrics (NO content)
        
        Returns:
            TOSViolation if abuse detected, None otherwise
        """
        # Check CPU abuse
        if metrics.get('cpu_hours_per_day', 0) > self.MAX_CPU_HOURS_PER_DAY:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.EXCESSIVE_CPU,
                severity='high',
                details=f"CPU usage: {metrics['cpu_hours_per_day']} hours/day (limit: {self.MAX_CPU_HOURS_PER_DAY})",
                action='warning'
            )
        
        # Check bandwidth abuse
        if metrics.get('bandwidth_gb_per_day', 0) > self.MAX_BANDWIDTH_GB_PER_DAY:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.EXCESSIVE_BANDWIDTH,
                severity='high',
                details=f"Bandwidth: {metrics['bandwidth_gb_per_day']} GB/day (limit: {self.MAX_BANDWIDTH_GB_PER_DAY})",
                action='warning'
            )
        
        # Check API abuse
        if metrics.get('api_calls_per_hour', 0) > self.MAX_API_CALLS_PER_HOUR:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.EXCESSIVE_API_CALLS,
                severity='medium',
                details=f"API calls: {metrics['api_calls_per_hour']}/hour (limit: {self.MAX_API_CALLS_PER_HOUR})",
                action='warning'
            )
        
        return None
    
    def check_spam_patterns(self, user_id: str, metrics: Dict[str, Any]) -> Optional[TOSViolation]:
        """
        Detect spam patterns (NO content inspection).
        
        Looks for:
        - High email send rate
        - Unusual traffic patterns
        - Repetitive API calls
        """
        spam_score = self._calculate_spam_score(metrics)
        
        if spam_score > 0.8:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.SPAM_DETECTED,
                severity='critical',
                details=f"Spam score: {spam_score:.2f} (threshold: 0.8)",
                action='suspension'
            )
        
        return None
    
    def check_malware_patterns(self, user_id: str, metrics: Dict[str, Any]) -> Optional[TOSViolation]:
        """
        Detect malware patterns (NO content inspection).
        
        Looks for:
        - Unusual network connections
        - Suspicious file operations
        - Known malware signatures (hashes only)
        """
        malware_score = self._calculate_malware_score(metrics)
        
        if malware_score > 0.8:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.MALWARE_DETECTED,
                severity='critical',
                details=f"Malware score: {malware_score:.2f} (threshold: 0.8)",
                action='suspension'
            )
        
        return None
    
    def check_ddos_patterns(self, user_id: str, metrics: Dict[str, Any]) -> Optional[TOSViolation]:
        """
        Detect DDoS patterns (NO content inspection).
        
        Looks for:
        - High connection rate
        - Unusual traffic patterns
        - Distributed attack signatures
        """
        ddos_score = self._calculate_ddos_score(metrics)
        
        if ddos_score > 0.8:
            return self._create_violation(
                user_id=user_id,
                violation_type=ViolationType.DDOS_DETECTED,
                severity='critical',
                details=f"DDoS score: {ddos_score:.2f} (threshold: 0.8)",
                action='suspension'
            )
        
        return None
    
    def report_copyright_complaint(self, user_id: str, complaint_details: str):
        """
        Handle DMCA/copyright complaint.
        
        Args:
            user_id: Anonymous user ID
            complaint_details: Complaint description (NO content)
        """
        violation = self._create_violation(
            user_id=user_id,
            violation_type=ViolationType.COPYRIGHT_COMPLAINT,
            severity='critical',
            details=complaint_details,
            action='suspension'
        )
        
        self._record_violation(violation)
        return violation
    
    def _create_violation(self, user_id: str, violation_type: ViolationType, 
                         severity: str, details: str, action: str) -> TOSViolation:
        """Create a TOS violation record."""
        violation = TOSViolation(
            user_id=user_id,
            violation_type=violation_type,
            timestamp=datetime.utcnow(),
            severity=severity,
            details=details,
            action_taken=action
        )
        
        self._record_violation(violation)
        return violation
    
    def _record_violation(self, violation: TOSViolation):
        """Record a violation."""
        if violation.user_id not in self.violations:
            self.violations[violation.user_id] = []
        self.violations[violation.user_id].append(violation)
    
    def _calculate_spam_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate spam likelihood score (0.0 - 1.0)."""
        # Placeholder - will implement real spam detection
        return 0.0
    
    def _calculate_malware_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate malware likelihood score (0.0 - 1.0)."""
        # Placeholder - will implement real malware detection
        return 0.0
    
    def _calculate_ddos_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate DDoS likelihood score (0.0 - 1.0)."""
        # Placeholder - will implement real DDoS detection
        return 0.0
    
    def get_user_violations(self, user_id: str) -> List[TOSViolation]:
        """Get all violations for a user."""
        return self.violations.get(user_id, [])
    
    def get_violation_count(self, user_id: str) -> int:
        """Get total violation count for a user."""
        return len(self.violations.get(user_id, []))


# Global TOS enforcement instance
tos_enforcement = TOSEnforcement()

