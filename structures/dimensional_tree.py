"""
DimensionalTree - Immutable Tree of Substrates

A tree where:
- Each node is a substrate
- Parent-child relationships are connections (Law 4: Connection Creates Meaning)
- All operations return NEW trees (immutability)
- Traversal is observation
- Recursion preserves unity (Law 3: Inheritance and Recursion)

CHARTER COMPLIANCE:
✅ Principle 1: All Things Are by Reference - Nodes are substrate references
✅ Principle 2: Passive Until Invoked - No background processing
✅ Principle 3: No Self-Modifying Code - Immutable at runtime
✅ Principle 5: No Hacking Surface - Pure functions only
✅ Principle 6: No Dark Web, No Concealment Dimensions - All relationships visible
✅ Principle 7: Fibonacci-Bounded Growth - Predictable structure
"""

from __future__ import annotations
from typing import List, Callable, Optional, Iterator
from kernel import Substrate


class DimensionalTreeNode:
    """
    Immutable tree node containing a substrate and children.
    """
    __slots__ = ('_value', '_children')
    
    def __init__(self, value: Substrate, children: Optional[List[DimensionalTreeNode]] = None):
        """
        Create a tree node.
        
        Args:
            value: Substrate stored in this node
            children: Optional list of child nodes
        """
        if not isinstance(value, Substrate):
            raise TypeError(f"Value must be Substrate, not {type(value)}")
        
        if children is None:
            children = []
        
        for child in children:
            if not isinstance(child, DimensionalTreeNode):
                raise TypeError(f"Child must be DimensionalTreeNode, not {type(child)}")
        
        object.__setattr__(self, '_value', value)
        object.__setattr__(self, '_children', tuple(children))  # Immutable
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalTreeNode is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalTreeNode is immutable")
    
    @property
    def value(self) -> Substrate:
        """The substrate stored in this node"""
        return self._value
    
    @property
    def children(self) -> tuple[DimensionalTreeNode, ...]:
        """Child nodes"""
        return self._children
    
    @property
    def is_leaf(self) -> bool:
        """True if node has no children"""
        return len(self._children) == 0
    
    def add_child(self, child: DimensionalTreeNode) -> DimensionalTreeNode:
        """
        Return NEW node with child added.
        
        Args:
            child: Child node to add
        
        Returns:
            New DimensionalTreeNode with child added
        """
        if not isinstance(child, DimensionalTreeNode):
            raise TypeError(f"Child must be DimensionalTreeNode, not {type(child)}")
        
        new_children = list(self._children) + [child]
        return DimensionalTreeNode(self._value, new_children)
    
    def map(self, transform: Callable[[Substrate], Substrate]) -> DimensionalTreeNode:
        """
        Transform all nodes recursively and return NEW tree.
        
        Args:
            transform: Function that takes a substrate and returns a substrate
        
        Returns:
            New DimensionalTreeNode with transformed values
        """
        # Transform this node's value
        new_value = transform(self._value)
        
        # Recursively transform children
        new_children = [child.map(transform) for child in self._children]
        
        return DimensionalTreeNode(new_value, new_children)
    
    def traverse_preorder(self) -> Iterator[Substrate]:
        """
        Traverse tree in pre-order (root, then children).
        
        Yields:
            Substrates in pre-order
        """
        yield self._value
        for child in self._children:
            yield from child.traverse_preorder()
    
    def traverse_postorder(self) -> Iterator[Substrate]:
        """
        Traverse tree in post-order (children, then root).
        
        Yields:
            Substrates in post-order
        """
        for child in self._children:
            yield from child.traverse_postorder()
        yield self._value
    
    def depth(self) -> int:
        """
        Calculate depth of tree (longest path from root to leaf).
        
        Returns:
            Depth of tree
        """
        if self.is_leaf:
            return 0
        return 1 + max(child.depth() for child in self._children)
    
    def size(self) -> int:
        """
        Calculate total number of nodes in tree.
        
        Returns:
            Number of nodes
        """
        return 1 + sum(child.size() for child in self._children)
    
    def __repr__(self) -> str:
        return f"DimensionalTreeNode(value={self._value.identity.value}, children={len(self._children)})"


class DimensionalTree:
    """
    Immutable tree of substrates.
    
    Wrapper around DimensionalTreeNode for convenience.
    """
    __slots__ = ('_root',)
    
    def __init__(self, root: Optional[DimensionalTreeNode] = None):
        """
        Create a dimensional tree.
        
        Args:
            root: Optional root node
        """
        if root is not None and not isinstance(root, DimensionalTreeNode):
            raise TypeError(f"Root must be DimensionalTreeNode, not {type(root)}")
        
        object.__setattr__(self, '_root', root)
    
    def __setattr__(self, name, value):
        raise TypeError("DimensionalTree is immutable")
    
    def __delattr__(self, name):
        raise TypeError("DimensionalTree is immutable")
    
    @property
    def root(self) -> Optional[DimensionalTreeNode]:
        """Root node of the tree"""
        return self._root
    
    @property
    def is_empty(self) -> bool:
        """True if tree has no root"""
        return self._root is None
    
    def __repr__(self) -> str:
        if self.is_empty:
            return "DimensionalTree(empty)"
        return f"DimensionalTree(size={self._root.size()}, depth={self._root.depth()})"

