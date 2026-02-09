"""
Canonical Document Example

This demonstrates how to define a Document as a canonical dimensional object:

    𝒪_doc = ⟨S, D, R, F, T⟩

Where:
    - S = document substrate (unity, immutable identity)
    - D = {title, content, word_count, author, version, ...}
    - R = {word_counting, versioning, ...}
    - F = manifestation function
    - T = time (version number)

No state is stored. All states are computed from the expression.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from kernel import (
    Substrate, SubstrateIdentity,
    create_canonical_object,
    create_dimension,
    create_relationship,
)


# ═══════════════════════════════════════════════════════════════════
# STEP 1: CREATE SUBSTRATE (S)
# ═══════════════════════════════════════════════════════════════════

def create_document_substrate(doc_id: str, title: str, author: str, initial_content: str) -> Substrate:
    """
    Create a document substrate.
    
    The substrate is unity - it contains NO data, only identity.
    All attributes are derived through the expression.
    """
    # Create 64-bit identity from document ID
    identity_value = hash(f"document:{doc_id}") & 0xFFFFFFFFFFFFFFFF
    identity = SubstrateIdentity(identity_value)
    
    # Expression that computes document attributes
    def document_expression(**kwargs):
        """
        The document's mathematical expression.
        
        This is where ALL attributes exist as potential.
        Nothing is stored - everything is computed.
        """
        attr = kwargs.get('attribute', 'identity')
        
        if attr == 'identity':
            return identity_value
        elif attr == 'doc_id':
            return doc_id
        elif attr == 'title':
            return title
        elif attr == 'author':
            return author
        elif attr == 'initial_content':
            return initial_content
        elif attr == 'created_at':
            return 0  # Version 0
        else:
            # Unknown attribute - derive from identity
            return hash(f"{identity_value}:{attr}") & 0xFFFFFFFFFFFFFFFF
    
    return Substrate(identity, document_expression)


# ═══════════════════════════════════════════════════════════════════
# STEP 2: DEFINE DIMENSIONS (D)
# ═══════════════════════════════════════════════════════════════════

def create_document_dimensions():
    """
    Define document dimensions: D = {title, content, word_count, ...}
    
    Each dimension has:
        - name: Label
        - domain: Type or validation
        - inherit: How to derive from substrate
    """
    return [
        # Title dimension
        create_dimension(
            name="title",
            domain=str,
            inherit=lambda s: s.expression(attribute="title")
        ),
        
        # Content dimension
        create_dimension(
            name="content",
            domain=str,
            inherit=lambda s: s.expression(attribute="initial_content")
        ),
        
        # Author dimension
        create_dimension(
            name="author",
            domain=str,
            inherit=lambda s: s.expression(attribute="author")
        ),
        
        # Word count dimension (computed)
        create_dimension(
            name="word_count",
            domain=int,
            inherit=lambda s: len(s.expression(attribute="initial_content").split())
        ),
        
        # Character count dimension (computed)
        create_dimension(
            name="char_count",
            domain=int,
            inherit=lambda s: len(s.expression(attribute="initial_content"))
        ),
        
        # Version dimension
        create_dimension(
            name="version",
            domain=int,
            inherit=lambda s: s.expression(attribute="created_at")
        ),
        
        # Document ID dimension
        create_dimension(
            name="doc_id",
            domain=str,
            inherit=lambda s: s.expression(attribute="doc_id")
        ),
    ]


# ═══════════════════════════════════════════════════════════════════
# STEP 3: DEFINE RELATIONSHIPS (R)
# ═══════════════════════════════════════════════════════════════════

def create_document_relationships():
    """
    Define document relationships: R = {versioning, statistics, ...}
    
    Each relationship has:
        - name: Label
        - inputs: Input dimension names
        - outputs: Output dimension names
        - f: Function mapping inputs to outputs
    """
    return [
        # Version tracking: version(t) = created_at + time
        create_relationship(
            name="versioning",
            inputs=["version", "time"],
            outputs=["version"],
            f=lambda version, time: int(version + time)
        ),
    ]


# ═══════════════════════════════════════════════════════════════════
# STEP 4: CREATE CANONICAL DOCUMENT OBJECT
# ═══════════════════════════════════════════════════════════════════

def create_document(doc_id: str, title: str, author: str, content: str):
    """
    Create a canonical document object: 𝒪_doc = ⟨S, D, R, F, T⟩

    Args:
        doc_id: Document identifier
        title: Document title
        author: Author name
        content: Initial content

    Returns:
        CanonicalObject representing the document
    """
    # S - Substrate (unity)
    substrate = create_document_substrate(doc_id, title, author, content)

    # D - Dimensions
    dimensions = create_document_dimensions()

    # R - Relationships
    relationships = create_document_relationships()

    # F - Manifestation function (uses default)
    # T - Time (version number, starts at 0)

    return create_canonical_object(
        substrate=substrate,
        dimensions=dimensions,
        relationships=relationships,
        time=0
    )


# ═══════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("CANONICAL DOCUMENT EXAMPLE")
    print("=" * 70)
    print()

    # Create a document
    doc = create_document(
        doc_id="DOC-2024-001",
        title="The Seven Dimensional Laws",
        author="Kenneth Bingham",
        content="All substrates begin as unity. Division generates dimensions."
    )

    print("Document created as canonical object:")
    print(doc)
    print()

    # Manifest at version 0
    print("State at version 0 (initial):")
    state_v0 = doc.manifest(t=0)
    for key, value in sorted(state_v0.items()):
        if key == "content":
            print(f"  {key}: \"{value[:50]}...\"")
        else:
            print(f"  {key}: {value}")
    print()

    # Get document at version 5
    doc_v5 = doc.at_time(5)

    print("State at version 5:")
    state_v5 = doc_v5.manifest(t=5)
    for key, value in sorted(state_v5.items()):
        if key == "content":
            print(f"  {key}: \"{value[:50]}...\"")
        else:
            print(f"  {key}: {value}")
    print()

    # Show that original document is unchanged
    print("Original document state (still at version 0):")
    state_original = doc.manifest(t=0)
    for key, value in sorted(state_original.items()):
        if key == "content":
            print(f"  {key}: \"{value[:50]}...\"")
        else:
            print(f"  {key}: {value}")
    print()

    # Get specific dimension values
    print("Accessing specific dimensions:")
    print(f"  Title: {doc.get_dimension_value('title')}")
    print(f"  Author: {doc.get_dimension_value('author')}")
    print(f"  Word count: {doc.get_dimension_value('word_count')}")
    print(f"  Character count: {doc.get_dimension_value('char_count')}")
    print(f"  Version: {doc.get_dimension_value('version')}")
    print()

    print("=" * 70)
    print("KEY INSIGHTS:")
    print("=" * 70)
    print("1. NO STATE IS STORED - Everything is computed from S, D, R, T")
    print("2. The document substrate (S) is immutable unity")
    print("3. Dimensions (D) define what can be observed")
    print("4. Relationships (R) define how dimensions interact")
    print("5. Time (T) represents version number, not wall-clock time")
    print("6. Manifestation (F) computes the observable state")
    print("7. Word count and char count are COMPUTED, not stored")
    print("8. Creating doc.at_time(5) doesn't mutate - it creates new object")
    print("=" * 70)

