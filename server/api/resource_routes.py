"""
Resource monitoring API routes for DimensionOS Platform.

Privacy-first resource monitoring:
- Track ONLY metrics (CPU, RAM, storage, network)
- NO content inspection
- NO file names
- NO query logging

Endpoints:
- GET /resources/metrics - Get current resource metrics
- GET /resources/usage - Get resource usage summary
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any

from server.models.user import User
from server.auth import get_current_user
from server.monitoring.resource_monitor import resource_monitor


router = APIRouter(prefix="/resources", tags=["Resources"])


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class ResourceMetricsResponse(BaseModel):
    """Resource metrics response."""
    user_id: str
    timestamp: str
    cpu: Dict[str, Any]
    ram: Dict[str, Any]
    storage: Dict[str, Any]
    network: Dict[str, Any]
    database: Dict[str, Any]
    activity: Dict[str, Any]


class ResourceUsageResponse(BaseModel):
    """Resource usage summary response."""
    allocated: Dict[str, Any]
    used: Dict[str, Any]
    percentage: Dict[str, Any]


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/metrics", response_model=ResourceMetricsResponse)
async def get_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get current resource metrics for user.
    
    Privacy-first:
    - Returns ONLY metrics (numbers)
    - NO content
    - NO file names
    - NO query logs
    
    Returns:
    - CPU metrics (cores allocated, used, percentage)
    - RAM metrics (MB allocated, used, percentage)
    - Storage metrics (GB allocated, used, percentage, file count)
    - Network metrics (bytes sent/received, connections)
    - Database metrics (table count, record count, queries/sec)
    - Activity metrics (API calls/hour, file operations/hour)
    """
    # Get user's allocated resources
    user_allocation = {
        'cpu_cores': current_user.cpu_cores_allocated,
        'ram_gb': current_user.ram_gb_allocated,
        'storage_gb': current_user.storage_gb_allocated,
        'bandwidth': current_user.bandwidth_allocated
    }
    
    # Get current metrics
    metrics = resource_monitor.get_user_metrics(
        user_id=current_user.user_id,
        user_allocation=user_allocation
    )
    
    return metrics.to_dict()


@router.get("/usage", response_model=ResourceUsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user)
):
    """
    Get resource usage summary for user.
    
    Returns:
    - Allocated resources
    - Used resources
    - Usage percentages
    """
    # Get user's allocated resources
    user_allocation = {
        'cpu_cores': current_user.cpu_cores_allocated,
        'ram_gb': current_user.ram_gb_allocated,
        'storage_gb': current_user.storage_gb_allocated,
        'bandwidth': current_user.bandwidth_allocated
    }
    
    # Get current metrics
    metrics = resource_monitor.get_user_metrics(
        user_id=current_user.user_id,
        user_allocation=user_allocation
    )
    
    return {
        "allocated": {
            "cpu_cores": metrics.cpu_cores_allocated,
            "ram_gb": metrics.ram_mb_allocated / 1024,
            "storage_gb": metrics.storage_gb_allocated,
            "bandwidth": metrics.bandwidth_allocated
        },
        "used": {
            "cpu_cores": metrics.cpu_cores_used,
            "ram_gb": metrics.ram_mb_used / 1024,
            "storage_gb": metrics.storage_gb_used,
            "bytes_sent": metrics.bytes_sent,
            "bytes_received": metrics.bytes_received
        },
        "percentage": {
            "cpu": metrics.cpu_percentage,
            "ram": metrics.ram_percentage,
            "storage": metrics.storage_percentage
        }
    }

