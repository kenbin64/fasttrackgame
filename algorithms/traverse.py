"""
Dimensional Traversal Algorithms

Traversal algorithms for dimensional trees and graphs:
- All algorithms are pure functions (no mutation)
- All algorithms return NEW structures
- Traversal is observation (Law 2: Observation Is Division)
- Follows Charter principles (immutability, no side effects)

CHARTER COMPLIANCE:
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
"""

from __future__ import annotations
from typing import Callable, Optional, Set
from kernel import Substrate
from structures import DimensionalList, DimensionalTreeNode, DimensionalGraph


def dfs_tree(
    node: DimensionalTreeNode,
    order: str = "preorder"
) -> DimensionalList:
    """
    Depth-First Search traversal of dimensional tree.
    
    Time complexity: O(n)
    Space complexity: O(h) where h is height
    
    Args:
        node: Root node to traverse from
        order: Traversal order - "preorder", "postorder", or "inorder"
    
    Returns:
        DimensionalList of substrates in traversal order
    
    Example:
        substrates = dfs_tree(root, "preorder")
    """
    if order == "preorder":
        return DimensionalList(list(node.traverse_preorder()))
    elif order == "postorder":
        return DimensionalList(list(node.traverse_postorder()))
    else:
        raise ValueError(f"Unknown order: {order}")


def bfs_tree(
    node: DimensionalTreeNode
) -> DimensionalList:
    """
    Breadth-First Search traversal of dimensional tree.
    
    Time complexity: O(n)
    Space complexity: O(w) where w is max width
    
    Args:
        node: Root node to traverse from
    
    Returns:
        DimensionalList of substrates in level-order
    
    Example:
        substrates = bfs_tree(root)
    """
    result = []
    queue = [node]
    
    while queue:
        current = queue.pop(0)
        result.append(current.value)
        
        # Add children to queue
        for child in current.children:
            queue.append(child)
    
    return DimensionalList(result)


def dfs_graph(
    graph: DimensionalGraph,
    start_identity: int,
    visited: Optional[Set[int]] = None
) -> DimensionalList:
    """
    Depth-First Search traversal of dimensional graph.
    
    Time complexity: O(V + E)
    Space complexity: O(V)
    
    Args:
        graph: DimensionalGraph to traverse
        start_identity: Identity of starting vertex
        visited: Set of already visited identities (for recursion)
    
    Returns:
        DimensionalList of substrates in DFS order
    
    Example:
        substrates = dfs_graph(graph, 1)
    """
    if visited is None:
        visited = set()
    
    result = []
    
    # Mark current as visited
    if start_identity in visited:
        return DimensionalList(result)
    
    visited.add(start_identity)
    
    # Get current vertex
    current = graph.get_vertex(start_identity)
    if current is None:
        return DimensionalList(result)
    
    result.append(current)
    
    # Visit neighbors
    neighbors = graph.neighbors(start_identity)
    for neighbor in neighbors:
        neighbor_id = neighbor.identity.value
        if neighbor_id not in visited:
            sub_result = dfs_graph(graph, neighbor_id, visited)
            for substrate in sub_result:
                result.append(substrate)
    
    return DimensionalList(result)


def bfs_graph(
    graph: DimensionalGraph,
    start_identity: int
) -> DimensionalList:
    """
    Breadth-First Search traversal of dimensional graph.
    
    Time complexity: O(V + E)
    Space complexity: O(V)
    
    Args:
        graph: DimensionalGraph to traverse
        start_identity: Identity of starting vertex
    
    Returns:
        DimensionalList of substrates in BFS order
    
    Example:
        substrates = bfs_graph(graph, 1)
    """
    result = []
    visited = set()
    queue = [start_identity]
    visited.add(start_identity)
    
    while queue:
        current_id = queue.pop(0)
        
        # Get current vertex
        current = graph.get_vertex(current_id)
        if current is None:
            continue
        
        result.append(current)
        
        # Visit neighbors
        neighbors = graph.neighbors(current_id)
        for neighbor in neighbors:
            neighbor_id = neighbor.identity.value
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(neighbor_id)
    
    return DimensionalList(result)


def find_path(
    graph: DimensionalGraph,
    start_identity: int,
    end_identity: int
) -> Optional[DimensionalList]:
    """
    Find path between two vertices using BFS.
    
    Time complexity: O(V + E)
    Space complexity: O(V)
    
    Args:
        graph: DimensionalGraph to search
        start_identity: Identity of starting vertex
        end_identity: Identity of ending vertex
    
    Returns:
        DimensionalList representing path, or None if no path exists
    
    Example:
        path = find_path(graph, 1, 5)
    """
    if start_identity == end_identity:
        vertex = graph.get_vertex(start_identity)
        if vertex is None:
            return None
        return DimensionalList([vertex])
    
    visited = set()
    queue = [(start_identity, [start_identity])]
    visited.add(start_identity)
    
    while queue:
        current_id, path = queue.pop(0)
        
        # Visit neighbors
        neighbors = graph.neighbors(current_id)
        for neighbor in neighbors:
            neighbor_id = neighbor.identity.value
            
            if neighbor_id == end_identity:
                # Found path!
                path_ids = path + [neighbor_id]
                path_substrates = []
                for vertex_id in path_ids:
                    vertex = graph.get_vertex(vertex_id)
                    if vertex is not None:
                        path_substrates.append(vertex)
                return DimensionalList(path_substrates)
            
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append((neighbor_id, path + [neighbor_id]))
    
    return None

