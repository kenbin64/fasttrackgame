"""
ButterflyFX Example Apps

Copyright (c) 2024-2026 Kenneth Bingham. All Rights Reserved.

This is a DERIVED IMPLEMENTATION built on the open source mathematical kernel.
This file is proprietary software. See /helix/LICENSE for details.

---

Layer 4: Applications
    Practical applications built on the foundational library.
    These demonstrate real-world usage of the dimensional model.
    
Apps:
    - HelixExplorer: Interactive dimensional data browser
    - HelixDataPipeline: ETL pipeline using dimensional levels
    - HelixAPIAggregator: Aggregate multiple APIs dimensionally
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time

from .primitives import (
    HelixContext, DimensionalType, HelixKernel,
    ManifoldSubstrate, Token, LEVEL_NAMES, LEVEL_ICONS
)
from .utilities import (
    HelixPath, HelixQuery, HelixCache, HelixLogger
)
from .foundation import (
    HelixDB, HelixFS, HelixStore, HelixGraph, HelixNode
)


# =============================================================================
# HELIX EXPLORER - Interactive dimensional data browser
# =============================================================================

class HelixExplorer:
    """
    Interactive browser for dimensional data structures.
    
    Navigate data by level, not by tree traversal.
    
    Usage:
        explorer = HelixExplorer()
        explorer.load_data({'cars': {'tesla': {'model_s': ...}}})
        explorer.invoke(6)  # See all wholes
        explorer.invoke(5)  # See all volumes
        explorer.navigate('6.cars/5.tesla')
    """
    
    def __init__(self):
        self.fs = HelixFS()
        self.db = HelixDB()
        self.history: List[str] = []
        self.current_path: Optional[HelixPath] = None
        self.logger = HelixLogger(min_level=2)
    
    # -------------------------------------------------------------------------
    # Data Loading
    # -------------------------------------------------------------------------
    
    def load_data(self, data: Dict[str, Any], base_path: str = "6.root") -> int:
        """
        Load hierarchical data into dimensional structure.
        Returns count of items loaded.
        """
        count = 0
        
        def process(obj: Any, path: str, level: int) -> None:
            nonlocal count
            
            if isinstance(obj, dict):
                self.fs.write(path, {'_type': 'container'})
                count += 1
                
                for key, value in obj.items():
                    child_level = max(0, level - 1)
                    child_path = f"{path}/{child_level}.{key}"
                    process(value, child_path, child_level)
            elif isinstance(obj, list):
                self.fs.write(path, {'_type': 'list', '_len': len(obj)})
                count += 1
                
                for i, item in enumerate(obj):
                    child_level = max(0, level - 1)
                    child_path = f"{path}/{child_level}.item_{i}"
                    process(item, child_path, child_level)
            else:
                self.fs.write(path, obj)
                count += 1
        
        process(data, base_path, 6)
        self.logger.volume(f"Loaded {count} items")
        return count
    
    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------
    
    def invoke(self, level: int) -> List[Dict[str, Any]]:
        """
        Invoke a level, returning all items.
        This is the key operation - O(1) to get all items at a level.
        """
        files = self.fs.invoke(level)
        result = []
        
        for f in files:
            result.append({
                'path': str(f.path),
                'level': f.level,
                'level_name': LEVEL_NAMES[f.level],
                'content': f.content
            })
        
        self.logger.width(f"Invoked level {level}: {len(files)} items")
        return result
    
    def navigate(self, path: str) -> Optional[Any]:
        """Navigate to a path"""
        self.history.append(path)
        self.current_path = HelixPath.parse(path)
        content = self.fs.read(path)
        self.logger.width(f"Navigated to {path}")
        return content
    
    def back(self) -> Optional[str]:
        """Go back in history"""
        if len(self.history) > 1:
            self.history.pop()  # Remove current
            return self.history[-1]
        return None
    
    def children(self) -> List[Dict[str, Any]]:
        """Get children of current path"""
        if not self.current_path:
            return []
        
        files = self.fs.list_children(str(self.current_path))
        return [
            {
                'path': str(f.path),
                'level': f.level,
                'content': f.content
            }
            for f in files
        ]
    
    # -------------------------------------------------------------------------
    # Dimensional View
    # -------------------------------------------------------------------------
    
    def dimensional_view(self) -> Dict[int, List[str]]:
        """Get a view of all data organized by level"""
        view = {i: [] for i in range(7)}
        
        for path, file in self.fs.files.items():
            view[file.level].append(path)
        
        return view
    
    def level_stats(self) -> Dict[str, Any]:
        """Get statistics about dimensional distribution"""
        stats = {}
        
        for level in range(7):
            files = self.fs.invoke(level)
            stats[LEVEL_NAMES[level]] = {
                'icon': LEVEL_ICONS[level],
                'count': len(files),
                'level': level
            }
        
        return stats
    
    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    
    def render_tree(self, max_depth: int = 3) -> str:
        """Render dimensional structure as text tree"""
        lines = []
        lines.append("Dimensional Structure:")
        lines.append("=" * 40)
        
        for level in range(6, -1, -1):
            files = self.fs.invoke(level)
            icon = LEVEL_ICONS[level]
            name = LEVEL_NAMES[level]
            
            if files:
                lines.append(f"\n{icon} Level {level} ({name}): {len(files)} items")
                for f in files[:5]:  # Show first 5
                    lines.append(f"    {f.path.target_name}: {type(f.content).__name__}")
                if len(files) > 5:
                    lines.append(f"    ... and {len(files) - 5} more")
        
        return '\n'.join(lines)


# =============================================================================
# HELIX DATA PIPELINE - ETL using dimensional levels
# =============================================================================

@dataclass
class PipelineStep:
    """A step in the data pipeline"""
    name: str
    level: int
    transform: Callable[[Any], Any]
    description: str = ""


class HelixDataPipeline:
    """
    ETL pipeline that operates by dimensional levels.
    
    Instead of linear: Extract → Transform → Load
    Use dimensional: 
        Level 6: Source definition
        Level 5: Extraction
        Level 4: Validation
        Level 3: Transformation
        Level 2: Enrichment
        Level 1: Loading
        Level 0: Completion
    
    Each level completes before the next begins.
    Failures at any level don't pollute lower levels.
    
    Usage:
        pipeline = HelixDataPipeline('user_sync')
        pipeline.add_step('extract', level=5, transform=fetch_users)
        pipeline.add_step('validate', level=4, transform=validate_data)
        pipeline.add_step('transform', level=3, transform=normalize)
        pipeline.add_step('load', level=1, transform=save_to_db)
        result = pipeline.run(source_data)
    """
    
    def __init__(self, name: str):
        self.name = name
        self.steps: Dict[int, PipelineStep] = {}
        self.results: Dict[int, Any] = {}
        self.errors: Dict[int, Exception] = {}
        self.logger = HelixLogger(min_level=3)
        self.metrics: Dict[str, Any] = {
            'total_time': 0,
            'steps_completed': 0,
            'steps_failed': 0
        }
    
    def add_step(
        self,
        name: str,
        level: int,
        transform: Callable[[Any], Any],
        description: str = ""
    ) -> 'HelixDataPipeline':
        """Add a processing step at a level"""
        self.steps[level] = PipelineStep(
            name=name,
            level=level,
            transform=transform,
            description=description
        )
        self.logger.plane(f"Added step '{name}' at level {level}")
        return self
    
    def run(self, input_data: Any) -> Dict[str, Any]:
        """
        Run the pipeline, processing level by level.
        
        Returns:
            {
                'success': bool,
                'output': final result,
                'results': {level: result},
                'errors': {level: error},
                'metrics': {...}
            }
        """
        start_time = time.time()
        current_data = input_data
        
        self.logger.whole(f"Starting pipeline '{self.name}'")
        
        # Process from highest to lowest level
        for level in sorted(self.steps.keys(), reverse=True):
            step = self.steps[level]
            step_start = time.time()
            
            self.logger.volume(f"Running step '{step.name}' at level {level}")
            
            try:
                current_data = step.transform(current_data)
                self.results[level] = current_data
                self.metrics['steps_completed'] += 1
                
                step_time = time.time() - step_start
                self.logger.plane(f"Step '{step.name}' completed in {step_time:.3f}s")
                
            except Exception as e:
                self.errors[level] = e
                self.metrics['steps_failed'] += 1
                
                self.logger.volume(f"Step '{step.name}' failed: {e}")
                
                # Stop pipeline on error
                break
        
        self.metrics['total_time'] = time.time() - start_time
        
        success = len(self.errors) == 0
        
        self.logger.whole(
            f"Pipeline {'completed' if success else 'failed'} "
            f"in {self.metrics['total_time']:.3f}s"
        )
        
        return {
            'success': success,
            'output': current_data if success else None,
            'results': self.results,
            'errors': self.errors,
            'metrics': self.metrics
        }
    
    def status(self) -> str:
        """Get pipeline status as text"""
        lines = [f"Pipeline: {self.name}", "=" * 40]
        
        for level in sorted(self.steps.keys(), reverse=True):
            step = self.steps[level]
            icon = LEVEL_ICONS[level]
            
            if level in self.errors:
                status = "❌ FAILED"
            elif level in self.results:
                status = "✅ DONE"
            else:
                status = "⏳ PENDING"
            
            lines.append(f"{icon} L{level} {step.name}: {status}")
        
        return '\n'.join(lines)


# =============================================================================
# HELIX API AGGREGATOR - Aggregate APIs dimensionally
# =============================================================================

@dataclass
class APIEndpoint:
    """An API endpoint definition"""
    name: str
    level: int
    url: str
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    transform: Optional[Callable[[Any], Any]] = None


class HelixAPIAggregator:
    """
    Aggregate multiple APIs using dimensional levels.
    
    Organize APIs by level:
        Level 6: Meta/discovery APIs
        Level 5: Authentication/session
        Level 4: Primary resource APIs
        Level 3: Detail/child APIs
        Level 2: Search/filter APIs
        Level 1: Analytics/stats APIs
        Level 0: Health/status APIs
    
    Invoke by level to batch similar requests.
    
    Usage:
        api = HelixAPIAggregator()
        api.register('users', level=4, url='/api/users')
        api.register('user_detail', level=3, url='/api/users/{id}')
        
        # Get all level-4 resources in one logical operation
        resources = api.invoke(4)
    """
    
    def __init__(self):
        self.endpoints: Dict[str, APIEndpoint] = {}
        self._by_level: Dict[int, List[str]] = {i: [] for i in range(7)}
        self.cache = HelixCache()
        self.logger = HelixLogger(min_level=3)
        
        # Mock fetcher for demo (would be real HTTP in production)
        self._fetcher: Optional[Callable[[str, str, Dict], Any]] = None
    
    def set_fetcher(self, fetcher: Callable[[str, str, Dict], Any]) -> None:
        """Set the HTTP fetcher function"""
        self._fetcher = fetcher
    
    def register(
        self,
        name: str,
        level: int,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        transform: Callable[[Any], Any] = None
    ) -> 'HelixAPIAggregator':
        """Register an API endpoint at a level"""
        endpoint = APIEndpoint(
            name=name,
            level=level,
            url=url,
            method=method,
            headers=headers or {},
            transform=transform
        )
        
        self.endpoints[name] = endpoint
        self._by_level[level].append(name)
        
        self.logger.plane(f"Registered '{name}' at level {level}")
        return self
    
    def invoke(self, level: int) -> Dict[str, Any]:
        """
        Invoke all endpoints at a level.
        Returns {endpoint_name: response_data}
        """
        results = {}
        endpoint_names = self._by_level.get(level, [])
        
        self.logger.volume(f"Invoking level {level}: {len(endpoint_names)} endpoints")
        
        for name in endpoint_names:
            # Check cache first
            cached = self.cache.get(name)
            if cached is not None:
                results[name] = cached
                continue
            
            endpoint = self.endpoints[name]
            
            # Fetch (mock or real)
            if self._fetcher:
                data = self._fetcher(endpoint.url, endpoint.method, endpoint.headers)
            else:
                data = {'mock': True, 'endpoint': name, 'url': endpoint.url}
            
            # Transform if needed
            if endpoint.transform:
                data = endpoint.transform(data)
            
            # Cache and store
            self.cache.set(name, data, level)
            results[name] = data
        
        return results
    
    def fetch(self, name: str, **kwargs) -> Any:
        """Fetch a specific endpoint with optional URL parameters"""
        if name not in self.endpoints:
            raise ValueError(f"Unknown endpoint: {name}")
        
        endpoint = self.endpoints[name]
        url = endpoint.url.format(**kwargs)
        
        # Check cache
        cache_key = f"{name}:{url}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Fetch
        if self._fetcher:
            data = self._fetcher(url, endpoint.method, endpoint.headers)
        else:
            data = {'mock': True, 'endpoint': name, 'url': url}
        
        # Transform
        if endpoint.transform:
            data = endpoint.transform(data)
        
        # Cache
        self.cache.set(cache_key, data, endpoint.level)
        
        return data
    
    def endpoints_at_level(self, level: int) -> List[APIEndpoint]:
        """Get all endpoints at a level"""
        return [self.endpoints[name] for name in self._by_level.get(level, [])]
    
    def invalidate_level(self, level: int) -> int:
        """Invalidate cache for a level and below"""
        return self.cache.invalidate_level(level)


# =============================================================================
# HELIX EVENT SYSTEM - Event handling by dimensional levels
# =============================================================================

@dataclass
class HelixEvent:
    """An event in the dimensional system"""
    name: str
    level: int
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)
    propagate: bool = True  # Should propagate to lower levels?


class HelixEventSystem:
    """
    Event system organized by dimensional levels.
    
    Events propagate DOWN (cascade) or UP (bubble).
    Handlers are organized by level.
    
    Level 6 events: System-wide
    Level 5 events: Module/component
    Level 4 events: Feature/page
    Level 3 events: Widget/section
    Level 2 events: Field/input
    Level 1 events: Character/keystroke
    Level 0 events: Raw/potential
    
    Usage:
        events = HelixEventSystem()
        events.on(4, 'page_load', handler)
        events.emit(HelixEvent('page_load', level=4, data={'page': 'home'}))
    """
    
    def __init__(self):
        self.handlers: Dict[int, Dict[str, List[Callable]]] = {
            i: {} for i in range(7)
        }
        self.logger = HelixLogger(min_level=2)
    
    def on(
        self,
        level: int,
        event_name: str,
        handler: Callable[[HelixEvent], None]
    ) -> 'HelixEventSystem':
        """Register a handler at a level"""
        if event_name not in self.handlers[level]:
            self.handlers[level][event_name] = []
        
        self.handlers[level][event_name].append(handler)
        self.logger.length(f"Registered handler for '{event_name}' at level {level}")
        return self
    
    def off(
        self,
        level: int,
        event_name: str,
        handler: Callable[[HelixEvent], None] = None
    ) -> None:
        """Remove a handler"""
        if event_name in self.handlers[level]:
            if handler:
                self.handlers[level][event_name].remove(handler)
            else:
                self.handlers[level][event_name] = []
    
    def emit(self, event: HelixEvent) -> int:
        """
        Emit an event, triggering handlers.
        Returns count of handlers called.
        """
        count = 0
        
        self.logger.width(f"Emitting '{event.name}' at level {event.level}")
        
        # Call handlers at the event's level
        if event.name in self.handlers[event.level]:
            for handler in self.handlers[event.level][event.name]:
                try:
                    handler(event)
                    count += 1
                except Exception as e:
                    self.logger.plane(f"Handler error: {e}")
        
        # Propagate to lower levels if enabled
        if event.propagate:
            for level in range(event.level - 1, -1, -1):
                if event.name in self.handlers[level]:
                    for handler in self.handlers[level][event.name]:
                        try:
                            handler(event)
                            count += 1
                        except Exception as e:
                            self.logger.plane(f"Handler error: {e}")
        
        self.logger.width(f"Event '{event.name}' triggered {count} handlers")
        return count
    
    def emit_cascade(self, event_name: str, data: Any, start_level: int = 6) -> int:
        """Emit an event that cascades through all levels"""
        total = 0
        
        for level in range(start_level, -1, -1):
            event = HelixEvent(name=event_name, level=level, data=data, propagate=False)
            total += self.emit(event)
        
        return total


# =============================================================================
# DEMO RUNNER
# =============================================================================

def run_demos():
    """Run demonstration of all apps"""
    print("=" * 60)
    print("ButterflyFX Apps Demonstration")
    print("=" * 60)
    
    # 1. Explorer Demo
    print("\n📂 HELIX EXPLORER DEMO")
    print("-" * 40)
    
    explorer = HelixExplorer()
    
    # Load sample data
    sample_data = {
        'cars': {
            'tesla': {
                'model_s': {'price': 80000, 'range': 400},
                'model_3': {'price': 40000, 'range': 350}
            },
            'ford': {
                'mustang': {'price': 55000, 'hp': 480}
            }
        },
        'users': {
            'alice': {'age': 30, 'role': 'admin'},
            'bob': {'age': 25, 'role': 'user'}
        }
    }
    
    count = explorer.load_data(sample_data)
    print(f"Loaded {count} items")
    
    # Show dimensional view
    stats = explorer.level_stats()
    for name, info in stats.items():
        if info['count'] > 0:
            print(f"  {info['icon']} Level {info['level']} ({name}): {info['count']} items")
    
    # 2. Pipeline Demo
    print("\n🔄 DATA PIPELINE DEMO")
    print("-" * 40)
    
    def extract(data):
        return [x * 2 for x in data]
    
    def validate(data):
        return [x for x in data if x > 5]
    
    def transform(data):
        return [x ** 0.5 for x in data]
    
    pipeline = HelixDataPipeline('number_process')
    pipeline.add_step('extract', level=5, transform=extract)
    pipeline.add_step('validate', level=4, transform=validate)
    pipeline.add_step('transform', level=3, transform=transform)
    
    result = pipeline.run([1, 2, 3, 4, 5])
    print(f"Input: [1, 2, 3, 4, 5]")
    print(f"Output: {result['output']}")
    print(f"Success: {result['success']}")
    print(pipeline.status())
    
    # 3. API Aggregator Demo
    print("\n🌐 API AGGREGATOR DEMO")
    print("-" * 40)
    
    api = HelixAPIAggregator()
    api.register('status', level=0, url='/health')
    api.register('users', level=4, url='/api/users')
    api.register('orders', level=4, url='/api/orders')
    api.register('user_detail', level=3, url='/api/users/{id}')
    
    # Invoke level 4 (primary resources)
    resources = api.invoke(4)
    print(f"Level 4 endpoints: {list(resources.keys())}")
    
    # Invoke level 0 (health)
    health = api.invoke(0)
    print(f"Level 0 endpoints: {list(health.keys())}")
    
    # 4. Event System Demo
    print("\n📡 EVENT SYSTEM DEMO")
    print("-" * 40)
    
    events = HelixEventSystem()
    
    received = []
    
    def system_handler(evt):
        received.append(f"System: {evt.name}")
    
    def module_handler(evt):
        received.append(f"Module: {evt.name}")
    
    def widget_handler(evt):
        received.append(f"Widget: {evt.name}")
    
    events.on(6, 'startup', system_handler)
    events.on(5, 'startup', module_handler)
    events.on(3, 'startup', widget_handler)
    
    event = HelixEvent('startup', level=6, data={'app': 'demo'})
    count = events.emit(event)
    
    print(f"Event triggered {count} handlers")
    print(f"Received: {received}")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == '__main__':
    run_demos()
