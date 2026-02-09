"""
DimensionalGraph - Immutable Graph of Substrates

A graph where:
- Vertices are substrates (identified by 64-bit identity)
- Edges are relationships (Law 4: Connection Creates Meaning)
- All operations return NEW graphs (immutability)
- Traversal is observation
- Can be directed or undirected

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Vertices are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All relationships visible
"""

from __future__ import annotations
from typing import Dict, Set, List, Optional, Iterator, Tuple
from kernel import Substrate


class DimensionalGraph:
    """
    Immutable graph of substrates.
    
    Vertices are substrates, edges are relationships.
    All operations return NEW graphs, preserving immutability.
    """
    __slots__ = ('_vertices', '_edges', '_directed')
    
    def __init__(
        self,
        vertices: Optional[List[Substrate]] = None,
        edges: Optional[List[Tuple[int, int]]] = None,
        directed: bool = False
    ):
        """
        Create a dimensional graph.
        
        Args:
            vertices: Optional list of substrates (vertices)
            edges: Optional list of (from_identity, to_identity) tuples
            directed: Whether graph is directed (default: False)
        """
        if vertices is None:
            vertices = []
        if edges is None:
            edges = []
        
        # Store vertices as dict mapping identity -> substrate
        vertex_dict = {}
        for vertex in vertices:
            if not isinstance(vertex, Substrate):
                raise TypeError(f"Vertex must be Substrate, not {type(vertex)}")
            vertex_dict[vertex.identity.value] = vertex
        
        # Store edges as dict mapping from_identity -> set of to_identities
        edge_dict = {}
        for from_id, to_id in edges:
            if from_id not in vertex_dict:
                raise ValueError(f"Edge references unknown vertex: {from_id}")
            if to_id not in vertex_dict:
                raise ValueError(f"Edge references unknown vertex: {to_id}")
            
            if from_id not in edge_dict:
                edge_dict[from_id] = set()
            edge_dict[from_id].add(to_id)
            
            # For undirected graphs, add reverse edge
            if not directed:
                if to_id not in edge_dict:
                    edge_dict[to_id] = set()
                edge_dict[to_id].add(from_id)
        
        object.__setattr__(self, '_vertices', vertex_dict)
        object.__setattr__(self, '_edges', edge_dict)
        object.__setattr__(self, '_directed', directed)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalGraph is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalGraph is immutable")
    
    @property
    def vertex_count(self) -> int:
        """Number of vertices"""
        return len(self._vertices)
    
    @property
    def edge_count(self) -> int:
        """Number of edges"""
        if self._directed:
            return sum(len(neighbors) for neighbors in self._edges.values())
        else:
            # For undirected, each edge is counted twice
            return sum(len(neighbors) for neighbors in self._edges.values()) // 2
    
    @property
    def is_directed(self) -> bool:
        """True if graph is directed"""
        return self._directed
    
    def vertices(self) -> Iterator[Substrate]:
        """Iterate over vertices"""
        return iter(self._vertices.values())

    def get_vertex(self, identity: int) -> Optional[Substrate]:
        """
        Get vertex by identity.

        Args:
            identity: Vertex identity

        Returns:
            Substrate with given identity, or None if not found
        """
        return self._vertices.get(identity)

    def edges(self) -> Iterator[Tuple[int, int]]:
        """
        Iterate over edges as (from_identity, to_identity) tuples.
        
        For undirected graphs, each edge is yielded once.
        """
        seen = set()
        for from_id, to_ids in self._edges.items():
            for to_id in to_ids:
                if self._directed:
                    yield (from_id, to_id)
                else:
                    # For undirected, only yield each edge once
                    edge = tuple(sorted([from_id, to_id]))
                    if edge not in seen:
                        seen.add(edge)
                        yield (from_id, to_id)
    
    def has_vertex(self, identity: int) -> bool:
        """Check if vertex exists"""
        return identity in self._vertices
    
    def has_edge(self, from_id: int, to_id: int) -> bool:
        """Check if edge exists"""
        return from_id in self._edges and to_id in self._edges[from_id]
    
    def neighbors(self, identity: int) -> List[Substrate]:
        """
        Get neighbors of a vertex.
        
        Args:
            identity: Vertex identity
        
        Returns:
            List of neighboring substrates
        """
        if identity not in self._vertices:
            raise ValueError(f"Vertex {identity} not in graph")
        
        if identity not in self._edges:
            return []
        
        return [self._vertices[neighbor_id] for neighbor_id in self._edges[identity]]
    
    def add_vertex(self, substrate: Substrate) -> DimensionalGraph:
        """
        Return NEW graph with vertex added.
        
        Args:
            substrate: Substrate to add as vertex
        
        Returns:
            New DimensionalGraph with vertex added
        """
        if not isinstance(substrate, Substrate):
            raise TypeError(f"Vertex must be Substrate, not {type(substrate)}")
        
        new_vertices = list(self._vertices.values())
        if substrate.identity.value not in self._vertices:
            new_vertices.append(substrate)
        
        new_edges = list(self.edges())
        return DimensionalGraph(new_vertices, new_edges, self._directed)
    
    def add_edge(self, from_id: int, to_id: int) -> DimensionalGraph:
        """
        Return NEW graph with edge added.
        
        Args:
            from_id: Source vertex identity
            to_id: Target vertex identity
        
        Returns:
            New DimensionalGraph with edge added
        """
        if from_id not in self._vertices:
            raise ValueError(f"Vertex {from_id} not in graph")
        if to_id not in self._vertices:
            raise ValueError(f"Vertex {to_id} not in graph")
        
        new_vertices = list(self._vertices.values())
        new_edges = list(self.edges())
        
        # Add edge if it doesn't exist
        if not self.has_edge(from_id, to_id):
            new_edges.append((from_id, to_id))
        
        return DimensionalGraph(new_vertices, new_edges, self._directed)
    
    def __repr__(self) -> str:
        graph_type = "directed" if self._directed else "undirected"
        return f"DimensionalGraph({self.vertex_count} vertices, {self.edge_count} edges, {graph_type})"

