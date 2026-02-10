"""
Resource monitoring system for DimensionOS.

Tracks resource usage per user (metrics only - NO content).

Privacy-first:
- NO file names
- NO database queries
- NO user content
- ONLY metrics (CPU, RAM, storage, network)
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ResourceMetrics:
    """
    Resource usage metrics for a user.
    
    Contains ONLY numbers - NO content, NO filenames, NO queries.
    """
    user_id: str
    timestamp: datetime
    
    # CPU metrics
    cpu_cores_allocated: int
    cpu_cores_used: float
    cpu_percentage: float
    
    # RAM metrics
    ram_mb_allocated: int
    ram_mb_used: int
    ram_percentage: float
    
    # Storage metrics
    storage_gb_allocated: int
    storage_gb_used: float
    storage_percentage: float
    file_count: int  # Count only - NO filenames
    substrate_count: int
    
    # Network metrics
    bandwidth_allocated: str
    bytes_sent: int
    bytes_received: int
    connections_active: int
    
    # Database metrics
    database_tables: int  # Count only
    database_records: int  # Count only - NO data
    queries_per_second: float
    
    # Activity metrics
    api_calls_per_hour: int
    file_operations_per_hour: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'cpu': {
                'allocated_cores': self.cpu_cores_allocated,
                'used_cores': self.cpu_cores_used,
                'percentage': self.cpu_percentage
            },
            'ram': {
                'allocated_mb': self.ram_mb_allocated,
                'used_mb': self.ram_mb_used,
                'percentage': self.ram_percentage
            },
            'storage': {
                'allocated_gb': self.storage_gb_allocated,
                'used_gb': self.storage_gb_used,
                'percentage': self.storage_percentage,
                'file_count': self.file_count,
                'substrate_count': self.substrate_count
            },
            'network': {
                'bandwidth_allocated': self.bandwidth_allocated,
                'bytes_sent': self.bytes_sent,
                'bytes_received': self.bytes_received,
                'connections_active': self.connections_active
            },
            'database': {
                'tables': self.database_tables,
                'records': self.database_records,
                'queries_per_second': self.queries_per_second
            },
            'activity': {
                'api_calls_per_hour': self.api_calls_per_hour,
                'file_operations_per_hour': self.file_operations_per_hour
            }
        }


class ResourceMonitor:
    """
    Monitor resource usage for all users.
    
    Tracks metrics only - NO content inspection.
    """
    
    def __init__(self):
        self.user_metrics: Dict[str, ResourceMetrics] = {}
        self.user_activity: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'api_calls': 0,
            'file_operations': 0,
            'db_queries': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        })
        self.start_time = time.time()
    
    def track_api_call(self, user_id: str):
        """Track API call (count only)."""
        self.user_activity[user_id]['api_calls'] += 1
    
    def track_file_operation(self, user_id: str):
        """Track file operation (count only - NO filename)."""
        self.user_activity[user_id]['file_operations'] += 1
    
    def track_db_query(self, user_id: str):
        """Track database query (count only - NO query content)."""
        self.user_activity[user_id]['db_queries'] += 1
    
    def track_network_traffic(self, user_id: str, bytes_sent: int, bytes_received: int):
        """Track network traffic (bytes only - NO content)."""
        self.user_activity[user_id]['bytes_sent'] += bytes_sent
        self.user_activity[user_id]['bytes_received'] += bytes_received
    
    def get_user_metrics(self, user_id: str, user_allocation: Dict[str, Any]) -> ResourceMetrics:
        """
        Get current resource metrics for user.
        
        Args:
            user_id: Anonymous user ID (hash)
            user_allocation: User's allocated resources
        
        Returns:
            ResourceMetrics with current usage
        """
        activity = self.user_activity[user_id]
        uptime_hours = (time.time() - self.start_time) / 3600
        
        # Calculate rates
        api_calls_per_hour = int(activity['api_calls'] / max(uptime_hours, 1))
        file_ops_per_hour = int(activity['file_operations'] / max(uptime_hours, 1))
        queries_per_second = activity['db_queries'] / max(time.time() - self.start_time, 1)
        
        # Get system metrics (simulated for now - will be real in production)
        cpu_used = self._get_cpu_usage(user_id)
        ram_used = self._get_ram_usage(user_id)
        storage_used = self._get_storage_usage(user_id)
        
        metrics = ResourceMetrics(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            
            # CPU
            cpu_cores_allocated=user_allocation.get('cpu_cores', 1),
            cpu_cores_used=cpu_used,
            cpu_percentage=(cpu_used / user_allocation.get('cpu_cores', 1)) * 100,
            
            # RAM
            ram_mb_allocated=user_allocation.get('ram_gb', 4) * 1024,
            ram_mb_used=ram_used,
            ram_percentage=(ram_used / (user_allocation.get('ram_gb', 4) * 1024)) * 100,
            
            # Storage
            storage_gb_allocated=user_allocation.get('storage_gb', 10),
            storage_gb_used=storage_used,
            storage_percentage=(storage_used / user_allocation.get('storage_gb', 10)) * 100,
            file_count=self._get_file_count(user_id),
            substrate_count=self._get_substrate_count(user_id),
            
            # Network
            bandwidth_allocated=user_allocation.get('bandwidth', '1Gbps'),
            bytes_sent=activity['bytes_sent'],
            bytes_received=activity['bytes_received'],
            connections_active=self._get_active_connections(user_id),
            
            # Database
            database_tables=self._get_table_count(user_id),
            database_records=self._get_record_count(user_id),
            queries_per_second=queries_per_second,
            
            # Activity
            api_calls_per_hour=api_calls_per_hour,
            file_operations_per_hour=file_ops_per_hour
        )
        
        self.user_metrics[user_id] = metrics
        return metrics
    
    # Placeholder methods - will be implemented with real substrate tracking
    def _get_cpu_usage(self, user_id: str) -> float:
        """Get CPU usage for user (simulated)."""
        return 0.5  # Will track actual substrate execution time
    
    def _get_ram_usage(self, user_id: str) -> int:
        """Get RAM usage for user in MB (simulated)."""
        return 100  # Will track actual substrate memory usage
    
    def _get_storage_usage(self, user_id: str) -> float:
        """Get storage usage for user in GB (simulated)."""
        return 0.1  # Will track actual substrate storage
    
    def _get_file_count(self, user_id: str) -> int:
        """Get file count for user (NO filenames)."""
        return 0  # Will track substrate count
    
    def _get_substrate_count(self, user_id: str) -> int:
        """Get substrate count for user."""
        return 0  # Will track from kernel
    
    def _get_active_connections(self, user_id: str) -> int:
        """Get active network connections for user."""
        return 0  # Will track from network layer
    
    def _get_table_count(self, user_id: str) -> int:
        """Get database table count (NO table names)."""
        return 0  # Will track from database layer
    
    def _get_record_count(self, user_id: str) -> int:
        """Get database record count (NO data)."""
        return 0  # Will track from database layer


# Global resource monitor instance
resource_monitor = ResourceMonitor()

