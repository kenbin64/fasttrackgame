"""
Dimensional Computing Kernel
============================

ButterflyFX - The Mathematical Kernel for All Computation

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
https://creativecommons.org/licenses/by/4.0/

This mathematical kernel belongs to all humanity.
Attribution required: Kenneth Bingham - https://butterflyfx.us

---

This module implements the complete Dimensional Computing paradigm:
    - DimensionalObject: Base unit embedding data in manifolds
    - Kernel Operations: lift, map, bind, navigate, transform, merge, resolve
    - Substate System: Local rules and context switching
    - Lineage Tracking: Full history and explainability
    - 7-Layer Genesis Alignment: Spark → Completion

Computing becomes geometric meaning-processing:
    z = x · y (multiplicative, not additive)
    Scale-invariant, intention-aligned, lineage-tracked.

Usage:
    from helix.dimensional_kernel import DimensionalObject, DimensionalKernel
    
    kernel = DimensionalKernel()
    obj = kernel.lift("raw data")
    obj = kernel.map_to_manifold(obj)
    result = kernel.resolve(obj)
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional, Callable, Tuple, Union
from enum import Enum, auto
import hashlib
import time
import json
import math

# =============================================================================
# GENESIS CONSTANTS - The 7 Layers of Creation
# =============================================================================

class Layer(Enum):
    """The 7 Layers of Dimensional Computing (Genesis Model)"""
    SPARK = 1        # Existence - First point
    MIRROR = 2       # Direction - Second point (duality)
    RELATION = 3     # Structure - Interaction (z = x·y)
    FORM = 4         # Purpose - Shape emerges
    LIFE = 5         # Motion - Meaning flows
    MIND = 6         # Coherence - Understanding
    COMPLETION = 7   # Consciousness - Integration

# Fibonacci alignment
LAYER_FIBONACCI = {
    Layer.SPARK: 1,
    Layer.MIRROR: 1,
    Layer.RELATION: 2,
    Layer.FORM: 3,
    Layer.LIFE: 5,
    Layer.MIND: 8,
    Layer.COMPLETION: 13
}

# Creation declarations
LAYER_DECLARATIONS = {
    Layer.SPARK: "Let there be the First Point",
    Layer.MIRROR: "Let there be a second point",
    Layer.RELATION: "Let the two interact",
    Layer.FORM: "Let structure become shape",
    Layer.LIFE: "Let form become meaning",
    Layer.MIND: "Let meaning become coherence",
    Layer.COMPLETION: "Let the whole become one again"
}

# Golden ratio
PHI = (1 + math.sqrt(5)) / 2

# =============================================================================
# LINEAGE NODE - History tracking
# =============================================================================

@dataclass
class LineageNode:
    """A node in the lineage graph representing a state or transformation."""
    id: str
    operation: str
    timestamp: float = field(default_factory=time.time)
    data_hash: str = ""
    parent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"node_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"


class LineageGraph:
    """
    Directed acyclic graph tracking all transformations.
    Provides explainability: trace any output back to origins.
    """
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.root_id: Optional[str] = None
        self.current_id: Optional[str] = None
    
    def add_node(self, operation: str, parent_ids: List[str] = None, 
                 data_hash: str = "", metadata: Dict[str, Any] = None) -> str:
        """Add a new lineage node."""
        node_id = f"node_{len(self.nodes)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}"
        node = LineageNode(
            id=node_id,
            operation=operation,
            data_hash=data_hash,
            parent_ids=parent_ids or [],
            metadata=metadata or {}
        )
        self.nodes[node_id] = node
        
        if self.root_id is None:
            self.root_id = node_id
        
        self.current_id = node_id
        return node_id
    
    def trace_back(self, node_id: str = None) -> List[LineageNode]:
        """Trace lineage from a node back to root."""
        if node_id is None:
            node_id = self.current_id
        
        if node_id is None or node_id not in self.nodes:
            return []
        
        path = []
        visited = set()
        queue = [node_id]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            node = self.nodes.get(current)
            if node:
                path.append(node)
                queue.extend(node.parent_ids)
        
        return path
    
    def explain(self, node_id: str = None) -> str:
        """Generate human-readable explanation of transformations."""
        trace = self.trace_back(node_id)
        if not trace:
            return "No lineage recorded."
        
        lines = ["=== Lineage Trace ==="]
        for i, node in enumerate(trace):
            indent = "  " * i
            lines.append(f"{indent}[{node.operation}] (t={node.timestamp:.3f})")
            if node.metadata:
                for k, v in node.metadata.items():
                    lines.append(f"{indent}  {k}: {v}")
        
        return "\n".join(lines)
    
    def merge_with(self, other: 'LineageGraph') -> 'LineageGraph':
        """Merge another lineage graph into this one."""
        merged = LineageGraph()
        merged.nodes.update(self.nodes)
        merged.nodes.update(other.nodes)
        merged.root_id = self.root_id
        
        # Link the graphs
        if self.current_id and other.root_id:
            if other.root_id in merged.nodes:
                merged.nodes[other.root_id].parent_ids.append(self.current_id)
        
        merged.current_id = other.current_id or self.current_id
        return merged
    
    def to_dict(self) -> Dict:
        """Export as dictionary."""
        return {
            "nodes": {k: {
                "id": v.id,
                "operation": v.operation,
                "timestamp": v.timestamp,
                "parent_ids": v.parent_ids,
                "metadata": v.metadata
            } for k, v in self.nodes.items()},
            "root_id": self.root_id,
            "current_id": self.current_id
        }


# =============================================================================
# SUBSTATE - Local rules and context switching
# =============================================================================

@dataclass
class SubstateRule:
    """A single rule within a substate."""
    name: str
    condition: Callable[[Any], bool]  # When to apply
    transform: Callable[[Any], Any]   # What to do
    priority: int = 0                 # Higher = applied first


class Substate:
    """
    A substate defines local rules for processing.
    Examples: debug mode, render mode (wireframe vs textured), 
              precision mode (float32 vs float64), etc.
    """
    
    def __init__(self, name: str, rules: Dict[str, SubstateRule] = None):
        self.name = name
        self.rules: Dict[str, SubstateRule] = rules or {}
        self.active = False
        self.activation_count = 0
    
    def add_rule(self, name: str, condition: Callable, transform: Callable, priority: int = 0):
        """Add a rule to this substate."""
        self.rules[name] = SubstateRule(name, condition, transform, priority)
    
    def apply(self, data: Any) -> Tuple[Any, List[str]]:
        """Apply all matching rules to data. Returns (transformed_data, applied_rules)."""
        applied = []
        result = data
        
        # Sort by priority (descending)
        sorted_rules = sorted(self.rules.values(), key=lambda r: -r.priority)
        
        for rule in sorted_rules:
            try:
                if rule.condition(result):
                    result = rule.transform(result)
                    applied.append(rule.name)
            except Exception as e:
                # Rule failed to apply - skip gracefully
                pass
        
        return result, applied
    
    def activate(self):
        self.active = True
        self.activation_count += 1
    
    def deactivate(self):
        self.active = False


class SubstateManager:
    """Manages multiple substates with stack-based activation."""
    
    def __init__(self):
        self.substates: Dict[str, Substate] = {}
        self.stack: List[str] = []  # Active substate stack
        self._create_defaults()
    
    def _create_defaults(self):
        """Create default substates."""
        # Standard mode
        standard = Substate("standard")
        standard.add_rule("identity", lambda x: True, lambda x: x, priority=0)
        self.register(standard)
        
        # Debug mode - adds verbose output
        debug = Substate("debug")
        debug.add_rule("trace", lambda x: True, 
                       lambda x: {"__debug__": True, "value": x}, priority=10)
        self.register(debug)
        
        # Precision mode - higher precision for numerics
        precision = Substate("precision")
        precision.add_rule("to_float64", 
                          lambda x: isinstance(x, (float, np.floating)),
                          lambda x: np.float64(x), priority=5)
        self.register(precision)
    
    def register(self, substate: Substate):
        """Register a substate."""
        self.substates[substate.name] = substate
    
    def push(self, name: str):
        """Push a substate onto the activation stack."""
        if name in self.substates:
            self.substates[name].activate()
            self.stack.append(name)
    
    def pop(self) -> Optional[str]:
        """Pop the top substate from the stack."""
        if self.stack:
            name = self.stack.pop()
            self.substates[name].deactivate()
            return name
        return None
    
    def apply_all(self, data: Any) -> Tuple[Any, List[str]]:
        """Apply all active substates in stack order."""
        result = data
        all_applied = []
        
        for name in self.stack:
            substate = self.substates.get(name)
            if substate and substate.active:
                result, applied = substate.apply(result)
                all_applied.extend([f"{name}.{r}" for r in applied])
        
        return result, all_applied
    
    @property
    def current(self) -> Optional[Substate]:
        """Get the current (top of stack) substate."""
        if self.stack:
            return self.substates.get(self.stack[-1])
        return None


# =============================================================================
# DIMENSIONAL OBJECT - The fundamental unit
# =============================================================================

@dataclass
class DimensionalCoordinate:
    """Position on the manifold."""
    spiral: int = 0
    layer: Layer = Layer.RELATION
    position: float = 0.0
    
    @property
    def fibonacci(self) -> int:
        return LAYER_FIBONACCI.get(self.layer, 1)
    
    @property
    def declaration(self) -> str:
        return LAYER_DECLARATIONS.get(self.layer, "")
    
    def __str__(self):
        return f"(S{self.spiral}, L{self.layer.value}:{self.layer.name}, P{self.position:.2f})"


class DimensionalObject:
    """
    The fundamental unit of Dimensional Computing.
    
    Every piece of data becomes a DimensionalObject embedded in a manifold.
    Contains:
        - semantic_payload: The actual data
        - identity_vector: Position for z = x·y operations
        - context_map: Key-value metadata
        - intention_vector: What this object wants/does
        - lineage_graph: Full history of transformations
        - delta_set: Changes since last checkpoint
        - coordinate: Position on 7-layer manifold
    """
    
    def __init__(
        self,
        semantic_payload: Any,
        identity_vector: List[float] = None,
        context_map: Dict[str, Any] = None,
        intention_vector: List[float] = None,
        lineage_graph: LineageGraph = None,
        coordinate: DimensionalCoordinate = None
    ):
        self.semantic_payload = semantic_payload
        self.identity_vector = np.array(identity_vector or [1.0, 1.0])
        self.context_map = context_map or {}
        self.intention_vector = np.array(intention_vector or [0.0])
        self.lineage_graph = lineage_graph or LineageGraph()
        self.delta_set: Set[str] = set()
        self.coordinate = coordinate or DimensionalCoordinate()
        
        self._id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
        self._created_at = time.time()
        self._sealed = False
    
    # =========================================================================
    # Core Mathematical Operations
    # =========================================================================
    
    def compute_z(self) -> float:
        """
        Compute z = x · y (the canonical multiplication).
        This is the fundamental Layer 3 operation.
        """
        return float(np.prod(self.identity_vector))
    
    def compute_magnitude(self) -> float:
        """Compute |v| = √(Σ vᵢ²)"""
        return float(np.linalg.norm(self.identity_vector))
    
    def compute_intention_alignment(self, other: 'DimensionalObject') -> float:
        """
        Compute alignment between intention vectors.
        Returns cosine similarity: -1 (opposite) to 1 (aligned).
        """
        if len(self.intention_vector) != len(other.intention_vector):
            return 0.0
        
        dot = np.dot(self.intention_vector, other.intention_vector)
        norm1 = np.linalg.norm(self.intention_vector)
        norm2 = np.linalg.norm(other.intention_vector)
        
        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0
        
        return float(dot / (norm1 * norm2))
    
    def bind_with(self, other: 'DimensionalObject') -> 'DimensionalObject':
        """
        Multiplicative binding: z = x · y.
        Creates a new object from the product of two.
        """
        new_identity = self.identity_vector * other.identity_vector
        
        # Merge context maps
        new_context = {**self.context_map, **other.context_map}
        new_context["__bound_from__"] = [self._id, other._id]
        
        # Combine intention vectors
        new_intention = np.concatenate([self.intention_vector, other.intention_vector])
        
        # Merge lineage
        new_lineage = self.lineage_graph.merge_with(other.lineage_graph)
        new_lineage.add_node(
            "bind",
            parent_ids=[self.lineage_graph.current_id, other.lineage_graph.current_id],
            metadata={"left": self._id, "right": other._id}
        )
        
        # Create bound object
        bound = DimensionalObject(
            semantic_payload=(self.semantic_payload, other.semantic_payload),
            identity_vector=new_identity.tolist(),
            context_map=new_context,
            intention_vector=new_intention.tolist(),
            lineage_graph=new_lineage
        )
        
        bound.delta_set.add("bound")
        return bound
    
    # =========================================================================
    # Layer Navigation
    # =========================================================================
    
    def invoke(self, layer: Union[int, Layer]) -> 'DimensionalObject':
        """Move to a specific layer."""
        if isinstance(layer, int):
            layer = Layer(layer)
        
        old_layer = self.coordinate.layer
        self.coordinate.layer = layer
        
        self.lineage_graph.add_node(
            "invoke",
            parent_ids=[self.lineage_graph.current_id] if self.lineage_graph.current_id else [],
            metadata={"from": old_layer.name, "to": layer.name}
        )
        
        self.delta_set.add(f"layer:{layer.name}")
        return self
    
    def spiral_up(self) -> 'DimensionalObject':
        """Complete current spiral, begin new one (Layer 7 → Layer 1)."""
        if self.coordinate.layer == Layer.COMPLETION:
            self.coordinate.spiral += 1
            self.coordinate.layer = Layer.SPARK
            
            self.lineage_graph.add_node(
                "spiral_up",
                parent_ids=[self.lineage_graph.current_id] if self.lineage_graph.current_id else [],
                metadata={"new_spiral": self.coordinate.spiral}
            )
            
            self.delta_set.add(f"spiral:{self.coordinate.spiral}")
        
        return self
    
    def spiral_down(self) -> 'DimensionalObject':
        """Return to previous spiral (Layer 1 → Layer 7)."""
        if self.coordinate.layer == Layer.SPARK and self.coordinate.spiral > 0:
            self.coordinate.spiral -= 1
            self.coordinate.layer = Layer.COMPLETION
            
            self.lineage_graph.add_node(
                "spiral_down",
                parent_ids=[self.lineage_graph.current_id] if self.lineage_graph.current_id else [],
                metadata={"new_spiral": self.coordinate.spiral}
            )
            
            self.delta_set.add(f"spiral:{self.coordinate.spiral}")
        
        return self
    
    # =========================================================================
    # Delta Tracking
    # =========================================================================
    
    def checkpoint(self) -> Set[str]:
        """Create checkpoint, return accumulated deltas, and reset."""
        deltas = self.delta_set.copy()
        self.delta_set.clear()
        return deltas
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        return len(self.delta_set) > 0
    
    # =========================================================================
    # Sealing (Immutability)
    # =========================================================================
    
    def seal(self) -> 'DimensionalObject':
        """Seal this object - no more modifications."""
        self._sealed = True
        self.lineage_graph.add_node(
            "seal",
            parent_ids=[self.lineage_graph.current_id] if self.lineage_graph.current_id else [],
            metadata={"timestamp": time.time()}
        )
        return self
    
    @property
    def is_sealed(self) -> bool:
        return self._sealed
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as dictionary."""
        return {
            "id": self._id,
            "semantic_payload": str(self.semantic_payload) if not isinstance(self.semantic_payload, (dict, list, str, int, float)) else self.semantic_payload,
            "identity_vector": self.identity_vector.tolist(),
            "context_map": self.context_map,
            "intention_vector": self.intention_vector.tolist(),
            "z_value": self.compute_z(),
            "magnitude": self.compute_magnitude(),
            "coordinate": str(self.coordinate),
            "layer": self.coordinate.layer.name,
            "fibonacci": self.coordinate.fibonacci,
            "delta_set": list(self.delta_set),
            "sealed": self._sealed
        }
    
    def data_hash(self) -> str:
        """Compute hash of semantic payload."""
        return hashlib.md5(str(self.semantic_payload).encode()).hexdigest()
    
    def __repr__(self):
        return f"<DimensionalObject id={self._id} z={self.compute_z():.3f} layer={self.coordinate.layer.name}>"


# =============================================================================
# DIMENSIONAL KERNEL - The 7 Core Operations
# =============================================================================

class DimensionalKernel:
    """
    The Dimensional Computing Kernel.
    
    Implements the 7 core operations aligned with the 7 layers:
        1. lift      - Raw input → DimensionalObject (Spark)
        2. map       - Position on manifold (Mirror)
        3. bind      - Multiplicative relation z = x·y (Relation)
        4. navigate  - Move through layers/spirals (Form)
        5. transform - Apply functions (Life)
        6. merge     - Combine objects coherently (Mind)
        7. resolve   - Produce final output (Completion)
    
    Usage:
        kernel = DimensionalKernel()
        
        # Process raw data
        obj = kernel.lift("hello world")
        obj = kernel.map_to_manifold(obj)
        
        # Navigate layers
        obj = kernel.navigate(obj, Layer.FORM)
        
        # Transform
        obj = kernel.transform(obj, lambda x: x.upper())
        
        # Resolve
        result, lineage = kernel.resolve(obj)
    """
    
    def __init__(self):
        self.substate_manager = SubstateManager()
        self.operation_count = 0
        self.processed_objects: Dict[str, DimensionalObject] = {}
    
    # =========================================================================
    # Operation 1: LIFT (Layer 1 - Spark)
    # =========================================================================
    
    def lift(self, raw_input: Any, intention: List[float] = None) -> DimensionalObject:
        """
        LIFT: Raw input → DimensionalObject
        
        This is the Spark - existence begins.
        Wraps any raw data into a structured DimensionalObject.
        
        Args:
            raw_input: Any data (string, number, dict, object, etc.)
            intention: Optional intention vector
        
        Returns:
            A new DimensionalObject at Layer 1 (Spark)
        """
        obj = DimensionalObject(
            semantic_payload=raw_input,
            intention_vector=intention or [1.0]  # Default: exists
        )
        
        obj.coordinate.layer = Layer.SPARK
        
        obj.lineage_graph.add_node(
            "lift",
            metadata={"input_type": type(raw_input).__name__, "input_size": len(str(raw_input))}
        )
        
        self.operation_count += 1
        self.processed_objects[obj._id] = obj
        
        return obj
    
    # =========================================================================
    # Operation 2: MAP (Layer 2 - Mirror)
    # =========================================================================
    
    def map_to_manifold(
        self, 
        obj: DimensionalObject,
        manifold_func: Callable[[Any], List[float]] = None
    ) -> DimensionalObject:
        """
        MAP: Position object on manifold.
        
        This is the Mirror - duality established.
        Converts semantic payload to identity vector for z = x·y operations.
        
        Args:
            obj: The DimensionalObject to map
            manifold_func: Custom function to compute identity vector
                           Default uses size-based scaling
        
        Returns:
            The same object with updated identity_vector at Layer 2
        """
        if manifold_func is None:
            # Default manifold mapping: size-based with reciprocal
            size = len(str(obj.semantic_payload)) + 1
            obj.identity_vector = np.array([
                float(size),
                1.0 / float(size)  # Reciprocal for z = x·y = 1 (neutral binding)
            ])
        else:
            obj.identity_vector = np.array(manifold_func(obj.semantic_payload))
        
        obj.coordinate.layer = Layer.MIRROR
        
        obj.lineage_graph.add_node(
            "map",
            parent_ids=[obj.lineage_graph.current_id] if obj.lineage_graph.current_id else [],
            data_hash=obj.data_hash(),
            metadata={
                "identity_vector": obj.identity_vector.tolist(),
                "z_value": obj.compute_z()
            }
        )
        
        obj.delta_set.add("mapped")
        self.operation_count += 1
        
        return obj
    
    # =========================================================================
    # Operation 3: BIND (Layer 3 - Relation)
    # =========================================================================
    
    def bind(
        self, 
        obj1: DimensionalObject, 
        obj2: DimensionalObject,
        binding_type: str = "multiplicative"
    ) -> DimensionalObject:
        """
        BIND: Create relation z = x · y
        
        This is the Relation - interaction creates structure.
        Multiplicative binding preserves scale-invariant relationships.
        
        Args:
            obj1: First object (x)
            obj2: Second object (y)
            binding_type: Type of binding (multiplicative, additive, etc.)
        
        Returns:
            New DimensionalObject representing z = x·y at Layer 3
        """
        if binding_type == "multiplicative":
            bound = obj1.bind_with(obj2)
        elif binding_type == "additive":
            # Additive binding (less common, breaks scale invariance)
            new_identity = obj1.identity_vector + obj2.identity_vector
            bound = DimensionalObject(
                semantic_payload=(obj1.semantic_payload, "+", obj2.semantic_payload),
                identity_vector=new_identity.tolist()
            )
            bound.lineage_graph = obj1.lineage_graph.merge_with(obj2.lineage_graph)
        else:
            # Default to multiplicative
            bound = obj1.bind_with(obj2)
        
        bound.coordinate.layer = Layer.RELATION
        
        bound.context_map["binding_type"] = binding_type
        bound.context_map["z_value"] = bound.compute_z()
        
        self.operation_count += 1
        self.processed_objects[bound._id] = bound
        
        return bound
    
    # =========================================================================
    # Operation 4: NAVIGATE (Layer 4 - Form)
    # =========================================================================
    
    def navigate(
        self, 
        obj: DimensionalObject, 
        target_layer: Union[int, Layer] = None,
        target_spiral: int = None
    ) -> DimensionalObject:
        """
        NAVIGATE: Move through layers and spirals.
        
        This is Form - structure becomes shape.
        Navigates the object to a specific position in the manifold.
        
        Args:
            obj: The DimensionalObject to navigate
            target_layer: Target layer (1-7 or Layer enum)
            target_spiral: Target spiral index (optional)
        
        Returns:
            The same object at new position (Layer 4)
        """
        if target_layer is not None:
            obj.invoke(target_layer)
        
        if target_spiral is not None:
            delta = target_spiral - obj.coordinate.spiral
            if delta > 0:
                for _ in range(delta):
                    obj.coordinate.layer = Layer.COMPLETION
                    obj.spiral_up()
            elif delta < 0:
                for _ in range(-delta):
                    obj.coordinate.layer = Layer.SPARK
                    obj.spiral_down()
        
        # Set to Form layer if not explicitly navigating
        if target_layer is None:
            obj.coordinate.layer = Layer.FORM
        
        obj.lineage_graph.add_node(
            "navigate",
            parent_ids=[obj.lineage_graph.current_id] if obj.lineage_graph.current_id else [],
            metadata={
                "target_layer": str(obj.coordinate.layer.name if hasattr(obj.coordinate.layer, 'name') else obj.coordinate.layer),
                "target_spiral": obj.coordinate.spiral
            }
        )
        
        obj.delta_set.add("navigated")
        self.operation_count += 1
        
        return obj
    
    # =========================================================================
    # Operation 5: TRANSFORM (Layer 5 - Life)
    # =========================================================================
    
    def transform(
        self, 
        obj: DimensionalObject, 
        func: Callable[[Any], Any],
        track_delta: bool = True
    ) -> DimensionalObject:
        """
        TRANSFORM: Apply function to semantic payload.
        
        This is Life - form becomes meaning.
        Applies any transformation while preserving lineage.
        
        Args:
            obj: The DimensionalObject to transform
            func: Function to apply to semantic_payload
            track_delta: Whether to track this change
        
        Returns:
            The same object with transformed payload at Layer 5
        """
        old_hash = obj.data_hash()
        old_payload = obj.semantic_payload
        
        try:
            obj.semantic_payload = func(obj.semantic_payload)
        except Exception as e:
            obj.context_map["transform_error"] = str(e)
            return obj
        
        new_hash = obj.data_hash()
        
        obj.coordinate.layer = Layer.LIFE
        
        obj.lineage_graph.add_node(
            "transform",
            parent_ids=[obj.lineage_graph.current_id] if obj.lineage_graph.current_id else [],
            data_hash=new_hash,
            metadata={
                "function": func.__name__ if hasattr(func, '__name__') else "lambda",
                "old_hash": old_hash,
                "changed": old_hash != new_hash
            }
        )
        
        if track_delta and old_hash != new_hash:
            obj.delta_set.add("transformed")
        
        self.operation_count += 1
        
        return obj
    
    # =========================================================================
    # Operation 6: MERGE (Layer 6 - Mind)
    # =========================================================================
    
    def merge(self, objects: List[DimensionalObject], strategy: str = "union") -> DimensionalObject:
        """
        MERGE: Combine multiple objects coherently.
        
        This is Mind - meaning becomes coherence.
        Merges objects into a unified whole.
        
        Args:
            objects: List of DimensionalObjects to merge
            strategy: Merge strategy ("union", "intersection", "first", "last")
        
        Returns:
            New DimensionalObject representing the merged whole at Layer 6
        """
        if not objects:
            raise ValueError("Cannot merge empty list")
        
        if len(objects) == 1:
            return objects[0]
        
        # Merge semantic payloads based on strategy
        if strategy == "union":
            merged_payload = [obj.semantic_payload for obj in objects]
        elif strategy == "intersection":
            # Find common elements (works for dicts/sets)
            merged_payload = objects[0].semantic_payload
        elif strategy == "first":
            merged_payload = objects[0].semantic_payload
        elif strategy == "last":
            merged_payload = objects[-1].semantic_payload
        else:
            merged_payload = [obj.semantic_payload for obj in objects]
        
        # Merge identity vectors (element-wise product for multiplicative coherence)
        merged_identity = objects[0].identity_vector.copy()
        for obj in objects[1:]:
            # Pad or truncate to match
            if len(obj.identity_vector) > len(merged_identity):
                merged_identity = np.pad(merged_identity, 
                    (0, len(obj.identity_vector) - len(merged_identity)), 
                    constant_values=1.0)
            elif len(obj.identity_vector) < len(merged_identity):
                obj.identity_vector = np.pad(obj.identity_vector,
                    (0, len(merged_identity) - len(obj.identity_vector)),
                    constant_values=1.0)
            merged_identity = merged_identity * obj.identity_vector
        
        # Merge context maps
        merged_context = {}
        for obj in objects:
            merged_context.update(obj.context_map)
        merged_context["__merged_count__"] = len(objects)
        merged_context["__merge_strategy__"] = strategy
        
        # Merge intention vectors (concatenate)
        merged_intention = np.concatenate([obj.intention_vector for obj in objects])
        
        # Merge lineage graphs
        merged_lineage = objects[0].lineage_graph
        for obj in objects[1:]:
            merged_lineage = merged_lineage.merge_with(obj.lineage_graph)
        
        merged_lineage.add_node(
            "merge",
            parent_ids=[obj.lineage_graph.current_id for obj in objects if obj.lineage_graph.current_id],
            metadata={
                "strategy": strategy,
                "object_count": len(objects),
                "object_ids": [obj._id for obj in objects]
            }
        )
        
        # Create merged object
        merged = DimensionalObject(
            semantic_payload=merged_payload,
            identity_vector=merged_identity.tolist(),
            context_map=merged_context,
            intention_vector=merged_intention.tolist(),
            lineage_graph=merged_lineage
        )
        
        merged.coordinate.layer = Layer.MIND
        merged.delta_set.add("merged")
        
        self.operation_count += 1
        self.processed_objects[merged._id] = merged
        
        return merged
    
    # =========================================================================
    # Operation 7: RESOLVE (Layer 7 - Completion)
    # =========================================================================
    
    def resolve(
        self, 
        obj: DimensionalObject, 
        output_format: str = "raw"
    ) -> Tuple[Any, str]:
        """
        RESOLVE: Produce final output with explanation.
        
        This is Completion - the whole becomes one again.
        Extracts the result and provides full lineage explanation.
        
        Args:
            obj: The DimensionalObject to resolve
            output_format: "raw" (payload only), "dict" (full state), "json" (serialized)
        
        Returns:
            Tuple of (output, lineage_explanation)
        """
        obj.coordinate.layer = Layer.COMPLETION
        
        # Apply any active substates
        result, applied_rules = self.substate_manager.apply_all(obj.semantic_payload)
        
        obj.lineage_graph.add_node(
            "resolve",
            parent_ids=[obj.lineage_graph.current_id] if obj.lineage_graph.current_id else [],
            data_hash=obj.data_hash(),
            metadata={
                "output_format": output_format,
                "applied_substates": applied_rules,
                "final_z": obj.compute_z()
            }
        )
        
        # Generate explanation
        explanation = obj.lineage_graph.explain()
        
        # Format output
        if output_format == "raw":
            output = result
        elif output_format == "dict":
            output = obj.to_dict()
            output["resolved_payload"] = result
        elif output_format == "json":
            output = json.dumps(obj.to_dict(), indent=2, default=str)
        else:
            output = result
        
        self.operation_count += 1
        
        return output, explanation
    
    # =========================================================================
    # Convenience Methods
    # =========================================================================
    
    def process(
        self, 
        raw_input: Any,
        transforms: List[Callable] = None,
        intention: List[float] = None
    ) -> Tuple[Any, str]:
        """
        Full processing pipeline: lift → map → transform... → resolve
        """
        obj = self.lift(raw_input, intention=intention)
        obj = self.map_to_manifold(obj)
        
        if transforms:
            for func in transforms:
                obj = self.transform(obj, func)
        
        return self.resolve(obj)
    
    def process_many(
        self, 
        inputs: List[Any],
        merge_strategy: str = "union"
    ) -> Tuple[Any, str]:
        """
        Process multiple inputs and merge them.
        """
        objects = [self.lift(inp) for inp in inputs]
        objects = [self.map_to_manifold(obj) for obj in objects]
        merged = self.merge(objects, strategy=merge_strategy)
        return self.resolve(merged)
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get kernel statistics."""
        return {
            "operation_count": self.operation_count,
            "processed_objects": len(self.processed_objects),
            "active_substates": len(self.substate_manager.stack)
        }


# =============================================================================
# FACTORY FUNCTIONS - Quick creation
# =============================================================================

def create_dimensional_object(
    data: Any,
    layer: Union[int, Layer] = Layer.RELATION,
    intention: str = "exist"
) -> DimensionalObject:
    """
    Quick factory function to create a DimensionalObject.
    
    Args:
        data: The semantic payload
        layer: Starting layer (default: Relation)
        intention: Text description of intention
    
    Returns:
        A configured DimensionalObject
    """
    kernel = DimensionalKernel()
    obj = kernel.lift(data, intention=[hash(intention) % 100 / 100.0])
    obj = kernel.map_to_manifold(obj)
    obj = kernel.navigate(obj, layer)
    return obj


def bind_objects(*objects: DimensionalObject) -> DimensionalObject:
    """
    Bind multiple objects: z = x · y · w · ...
    """
    if len(objects) < 2:
        raise ValueError("Need at least 2 objects to bind")
    
    kernel = DimensionalKernel()
    result = kernel.bind(objects[0], objects[1])
    
    for obj in objects[2:]:
        result = kernel.bind(result, obj)
    
    return result


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    'Layer',
    'LAYER_FIBONACCI',
    'LAYER_DECLARATIONS',
    'PHI',
    
    # Classes
    'LineageNode',
    'LineageGraph',
    'SubstateRule',
    'Substate',
    'SubstateManager',
    'DimensionalCoordinate',
    'DimensionalObject',
    'DimensionalKernel',
    
    # Factory functions
    'create_dimensional_object',
    'bind_objects',
]
