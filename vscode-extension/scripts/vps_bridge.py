#!/usr/bin/env python3
"""
Dimensional VPS Bridge - Python CLI for VS Code Extension

This script provides a CLI interface to the helix dimensional_kernel,
enabling the VS Code extension to execute kernel operations via subprocess.

Usage:
    python vps_bridge.py lift '{"cpu": 50, "memory": 8000}'
    python vps_bridge.py bind obj1_json obj2_json
    python vps_bridge.py optimize
    python vps_bridge.py metrics
    python vps_bridge.py resolve obj_json
"""

import sys
import os
import json
import argparse
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add helix to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helix import (
    DimensionalKernel,
    DimensionalObject,
    Layer,
    LAYER_FIBONACCI,
    LAYER_DECLARATIONS,
    PHI,
    LineageGraph,
    Substate,
    SubstateManager,
    create_dimensional_object,
    bind_objects
)


class VPSBridge:
    """Bridge between VS Code extension and helix dimensional_kernel."""
    
    def __init__(self):
        self.kernel = DimensionalKernel()
    
    def get_vps_metrics(self) -> Dict[str, Any]:
        """Collect VPS system metrics."""
        metrics = {
            'cpu': self._get_cpu_metrics(),
            'memory': self._get_memory_metrics(),
            'disk': self._get_disk_metrics(),
            'network': self._get_network_metrics(),
            'processes': self._get_top_processes(),
            'uptime': self._get_uptime(),
            'timestamp': datetime.now().isoformat()
        }
        return metrics
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU usage metrics."""
        try:
            # Read load average
            with open('/proc/loadavg', 'r') as f:
                load = list(map(float, f.read().split()[:3]))
            
            # Get CPU count
            cores = os.cpu_count() or 1
            
            # Read CPU stats
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
                parts = list(map(int, cpu_line.split()[1:]))
                idle = parts[3]
                total = sum(parts)
                usage = 100 * (1 - idle / total) if total > 0 else 0
            
            return {'usage': usage, 'cores': cores, 'load': load}
        except Exception as e:
            return {'usage': 0, 'cores': 1, 'load': [0, 0, 0], 'error': str(e)}
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory usage metrics."""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split()
                    key = parts[0].rstrip(':')
                    value = int(parts[1]) * 1024  # Convert KB to bytes
                    meminfo[key] = value
            
            total = meminfo.get('MemTotal', 0)
            free = meminfo.get('MemAvailable', meminfo.get('MemFree', 0))
            used = total - free
            percentage = (used / total * 100) if total > 0 else 0
            
            return {'total': total, 'used': used, 'free': free, 'percentage': percentage}
        except Exception as e:
            return {'total': 0, 'used': 0, 'free': 0, 'percentage': 0, 'error': str(e)}
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk usage metrics."""
        try:
            stat = os.statvfs('/')
            total = stat.f_blocks * stat.f_frsize
            free = stat.f_bavail * stat.f_frsize
            used = total - free
            percentage = (used / total * 100) if total > 0 else 0
            
            return {'total': total, 'used': used, 'free': free, 'percentage': percentage}
        except Exception as e:
            return {'total': 0, 'used': 0, 'free': 0, 'percentage': 0, 'error': str(e)}
    
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network I/O metrics."""
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip headers
                
            bytes_in = bytes_out = 0
            for line in lines:
                if ':' in line:
                    parts = line.split(':')[1].split()
                    bytes_in += int(parts[0])
                    bytes_out += int(parts[8])
            
            return {'bytesIn': bytes_in, 'bytesOut': bytes_out}
        except Exception as e:
            return {'bytesIn': 0, 'bytesOut': 0, 'error': str(e)}
    
    def _get_top_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top processes by CPU usage."""
        try:
            result = subprocess.run(
                ['ps', 'aux', '--sort=-%cpu'],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')[1:limit+1]
            
            processes = []
            for line in lines:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': int(parts[1]),
                        'cpu': float(parts[2]),
                        'memory': float(parts[3]),
                        'name': parts[10][:50]
                    })
            return processes
        except Exception as e:
            return [{'error': str(e)}]
    
    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        try:
            with open('/proc/uptime', 'r') as f:
                return float(f.read().split()[0])
        except:
            return 0
    
    def lift(self, data: Any) -> Dict[str, Any]:
        """Lift data into a Dimensional Object."""
        obj = self.kernel.lift(data)
        return self._serialize_object(obj)
    
    def bind(self, obj1_data: Dict, obj2_data: Dict) -> Dict[str, Any]:
        """Bind two objects."""
        obj1 = self._deserialize_object(obj1_data)
        obj2 = self._deserialize_object(obj2_data)
        bound = self.kernel.bind(obj1, obj2)
        return self._serialize_object(bound)
    
    def transform(self, obj_data: Dict, transform_type: str = 'analyze') -> Dict[str, Any]:
        """Transform an object."""
        obj = self._deserialize_object(obj_data)
        
        if transform_type == 'analyze':
            transformed = self.kernel.transform(obj, lambda x: {
                'original': x,
                'analyzed': True,
                'phi_scaled': PHI
            })
        elif transform_type == 'optimize':
            transformed = self.kernel.transform(obj, self._optimize_payload)
        else:
            transformed = self.kernel.transform(obj, lambda x: x)
        
        return self._serialize_object(transformed)
    
    def _optimize_payload(self, payload: Any) -> Dict[str, Any]:
        """Apply optimization logic to payload."""
        if not isinstance(payload, dict):
            return {'optimized': payload}
        
        analysis = {
            'original': payload,
            'recommendation': '',
            'priority': 0
        }
        
        cpu = payload.get('cpu', {}).get('usage', 0)
        mem = payload.get('memory', {}).get('percentage', 0)
        
        if cpu > 80 and mem < 50:
            analysis['recommendation'] = 'CPU-bound: Consider scaling CPU'
            analysis['priority'] = 1
        elif mem > 80 and cpu < 50:
            analysis['recommendation'] = 'Memory-bound: Free memory or add swap'
            analysis['priority'] = 2
        elif cpu > 80 and mem > 80:
            analysis['recommendation'] = 'Resource saturation: Scale up'
            analysis['priority'] = 3
        else:
            analysis['recommendation'] = 'System healthy'
            analysis['priority'] = 0
        
        return analysis
    
    def resolve(self, obj_data: Dict) -> Dict[str, Any]:
        """Resolve an object to final result."""
        obj = self._deserialize_object(obj_data)
        result = self.kernel.resolve(obj)
        
        return {
            'result': result.result,
            'explanation': result.explanation,
            'z': result.z,
            'layer': result.layer.name if hasattr(result, 'layer') else 'COMPLETION',
            'fibonacci': LAYER_FIBONACCI.get(Layer.COMPLETION, 13),
            'lineage': [
                {
                    'operation': n.operation,
                    'layer': n.layer.name if hasattr(n.layer, 'name') else str(n.layer),
                    'timestamp': n.timestamp
                }
                for n in (result.lineage if hasattr(result, 'lineage') else [])
            ]
        }
    
    def optimize(self) -> Dict[str, Any]:
        """Full optimization pipeline: metrics → lift → bind → transform → resolve."""
        # Get metrics
        metrics = self.get_vps_metrics()
        
        # Lift each resource type
        cpu_obj = self.kernel.lift(metrics['cpu'])
        mem_obj = self.kernel.lift(metrics['memory'])
        disk_obj = self.kernel.lift(metrics['disk'])
        net_obj = self.kernel.lift(metrics['network'])
        
        # Bind CPU + Memory
        bound = self.kernel.bind(cpu_obj, mem_obj)
        
        # Merge all
        merged = self.kernel.merge([bound, disk_obj, net_obj])
        
        # Transform with optimization
        optimized = self.kernel.transform(merged, self._optimize_payload)
        
        # Navigate to completion layer
        navigated = self.kernel.navigate(optimized, Layer.COMPLETION)
        
        # Resolve
        result = self.kernel.resolve(navigated)
        
        return {
            'metrics': metrics,
            'z': result.z,
            'explanation': result.explanation,
            'result': result.result,
            'lineage_count': len(self.kernel.lineage.nodes) if hasattr(self.kernel, 'lineage') else 0
        }
    
    def _serialize_object(self, obj: DimensionalObject) -> Dict[str, Any]:
        """Serialize DimensionalObject to JSON-compatible dict."""
        return {
            'id': obj.id,
            'identity_vector': list(obj.identity_vector),
            'intention_vector': list(obj.intention_vector),
            'z': float(obj.compute_z()),
            'layer': obj.coordinate.layer.name,
            'spiral': obj.coordinate.spiral,
            'position': obj.coordinate.position,
            'payload_type': type(obj.payload).__name__,
            'payload': obj.payload if isinstance(obj.payload, (dict, list, str, int, float, bool, type(None))) else str(obj.payload)
        }
    
    def _deserialize_object(self, data: Dict) -> DimensionalObject:
        """Deserialize dict back to DimensionalObject."""
        return create_dimensional_object(
            payload=data.get('payload', data),
            identity_vector=tuple(data.get('identity_vector', [1.0, 1.0])),
            intention_vector=data.get('intention_vector', [1.0, 0.0, 0.0])
        )


def main():
    parser = argparse.ArgumentParser(description='Dimensional VPS Bridge')
    parser.add_argument('command', choices=['metrics', 'lift', 'bind', 'transform', 'resolve', 'optimize', 'info'])
    parser.add_argument('args', nargs='*', help='Command arguments (JSON)')
    parser.add_argument('--format', choices=['json', 'pretty'], default='json')
    
    args = parser.parse_args()
    bridge = VPSBridge()
    
    try:
        if args.command == 'metrics':
            result = bridge.get_vps_metrics()
        
        elif args.command == 'lift':
            data = json.loads(args.args[0]) if args.args else {}
            result = bridge.lift(data)
        
        elif args.command == 'bind':
            obj1 = json.loads(args.args[0])
            obj2 = json.loads(args.args[1])
            result = bridge.bind(obj1, obj2)
        
        elif args.command == 'transform':
            obj = json.loads(args.args[0])
            transform_type = args.args[1] if len(args.args) > 1 else 'analyze'
            result = bridge.transform(obj, transform_type)
        
        elif args.command == 'resolve':
            obj = json.loads(args.args[0])
            result = bridge.resolve(obj)
        
        elif args.command == 'optimize':
            result = bridge.optimize()
        
        elif args.command == 'info':
            result = {
                'phi': PHI,
                'layers': [layer.name for layer in Layer],
                'fibonacci': {layer.name: fib for layer, fib in LAYER_FIBONACCI.items()},
                'declarations': LAYER_DECLARATIONS
            }
        
        else:
            result = {'error': f'Unknown command: {args.command}'}
        
        # Output
        if args.format == 'pretty':
            print(json.dumps(result, indent=2, default=str))
        else:
            print(json.dumps(result, default=str))
        
        sys.exit(0)
    
    except Exception as e:
        error_result = {'error': str(e), 'type': type(e).__name__}
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()
