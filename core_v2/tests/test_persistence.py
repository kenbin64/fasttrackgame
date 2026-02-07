"""
Test: Persistence Layer via SRL

Demonstrates internal (local) and external (central) data persistence.
All substrates are SRL-addressed.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '.')

from kernel_v2 import Substrate, SubstrateIdentity
from core_v2 import (
    Persistence,
    LocalStore,
    CentralStore,
    StoreType,
    SyncMode,
    create_local_store,
    create_memory_store,
)


def test_local_store():
    """Test local file-based storage."""
    print("=" * 60)
    print("TEST: LocalStore (single-user, file-based)")
    print("=" * 60)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        store = LocalStore(tmpdir)
        
        # Create a substrate
        identity = 12345
        data = b'{"name": "test_car", "mass_kg": 1600}'
        
        # Save
        ref = store.save(identity, data, namespace="vehicles")
        print(f"  Saved:     identity={identity}, namespace=vehicles")
        print(f"  SRL ref:   {ref.srl_id:016x}")
        print(f"  Version:   {ref.version}")
        
        # Load
        loaded = store.load(ref)
        print(f"  Loaded:    {loaded.decode()}")
        
        # Exists
        print(f"  Exists:    {store.exists(ref)}")
        
        # List namespace
        refs = list(store.list_namespace("vehicles"))
        print(f"  In namespace: {len(refs)} substrate(s)")
        
        # Delete
        store.delete(ref)
        print(f"  Deleted:   {not store.exists(ref)}")
        
        store.close()
    
    print("  ✓ LocalStore PASSED\n")


def test_central_store_memory():
    """Test in-memory central store."""
    print("=" * 60)
    print("TEST: CentralStore (memory://)")
    print("=" * 60)
    
    store = create_memory_store()
    
    # Save multiple substrates
    refs = []
    for i in range(5):
        identity = 1000 + i
        data = f'{{"id": {i}, "value": {i * 100}}}'.encode()
        ref = store.save(identity, data, namespace="test")
        refs.append(ref)
        print(f"  Saved: identity={identity}, version={ref.version}")
    
    # Load one
    loaded = store.load(refs[2])
    print(f"  Loaded ref[2]: {loaded.decode()}")
    
    # Update (save again)
    new_ref = store.save(1002, b'{"id": 2, "value": 999}', namespace="test")
    print(f"  Updated ref[2]: version {refs[2].version} -> {new_ref.version}")
    
    # List
    all_refs = list(store.list_namespace("test"))
    print(f"  Total in namespace: {len(all_refs)}")
    
    store.close()
    print("  ✓ CentralStore (memory) PASSED\n")


def test_persistence_manager():
    """Test unified persistence manager."""
    print("=" * 60)
    print("TEST: Persistence Manager (internal + external)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create both stores
        local = LocalStore(tmpdir)
        central = create_memory_store()
        
        # Create persistence manager
        persist = Persistence(internal=local, external=central)
        
        # Save to local (default)
        substrate = Substrate(
            SubstrateIdentity(42),
            lambda: {"type": "car", "wheels": 4}
        )
        ref = persist.save(substrate, namespace="objects")
        print(f"  Saved to LOCAL: identity=42, srl={ref.srl_id:016x}")
        
        # Save to central explicitly
        substrate2 = Substrate(
            SubstrateIdentity(99),
            lambda: {"type": "truck", "wheels": 18}
        )
        ref2 = persist.save(substrate2, namespace="objects", store_type=StoreType.CENTRAL)
        print(f"  Saved to CENTRAL: identity=99, srl={ref2.srl_id:016x}")
        
        # Load from each
        data1 = persist.load(ref)
        data2 = persist.load(ref2)
        print(f"  Loaded from LOCAL: {data1[8:]}")  # Skip identity bytes
        print(f"  Loaded from CENTRAL: {data2[8:]}")
        
        # Sync local to central
        print("\n  Syncing LOCAL → CENTRAL...")
        stats = persist.sync(SyncMode.LOCAL_TO_CENTRAL, namespace="objects")
        print(f"  Uploaded: {stats['uploaded']}")
        
        # Verify central now has local's data
        central_refs = list(central.list_namespace("objects"))
        print(f"  Central now has: {len(central_refs)} substrate(s)")
        
        persist.close()
    
    print("  ✓ Persistence Manager PASSED\n")


def test_srl_addressing():
    """Test SRL-based addressing."""
    print("=" * 60)
    print("TEST: SRL Addressing")
    print("=" * 60)
    
    from core_v2.persistence import SRLReference, StoreSRL
    
    # Create SRL reference
    ref = SRLReference(
        identity=0x123456789ABCDEF0,
        store_type=StoreType.LOCAL,
        namespace="production"
    )
    
    print(f"  Identity:    {ref.identity:016x}")
    print(f"  Store type:  {ref.store_type.name}")
    print(f"  Namespace:   {ref.namespace}")
    print(f"  SRL ID:      {ref.srl_id:016x}")
    
    # Serialize and deserialize
    serialized = ref.to_bytes()
    restored = SRLReference.from_bytes(serialized)
    
    print(f"  Serialized:  {len(serialized)} bytes")
    print(f"  Restored:    identity={restored.identity:016x}")
    print(f"  Match:       {ref.identity == restored.identity}")
    
    # Store SRL
    store_srl = StoreSRL(
        store_type=StoreType.CENTRAL,
        connection_hash=hash("redis://localhost:6379"),
        namespace="cache"
    )
    print(f"\n  Store SRL:   {store_srl.identity:016x}")
    
    print("  ✓ SRL Addressing PASSED\n")


def test_substrate_serialization():
    """Test substrate serialization round-trip."""
    print("=" * 60)
    print("TEST: Substrate Serialization")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        persist = Persistence(internal=LocalStore(tmpdir))
        
        # Create complex substrate
        car = Substrate(
            SubstrateIdentity(777),
            lambda: {
                "type": "sports_car",
                "engine": {"cylinders": 8, "displacement_cc": 5000},
                "transmission": {"gears": 7, "type": "dual-clutch"},
                "mass_kg": 1450,
                "top_speed_kmh": 340
            }
        )
        
        print(f"  Original identity: {int(car.identity)}")
        print(f"  Original value:    {car()}")
        
        # Save
        ref = persist.save(car, namespace="sports")
        print(f"  Saved to:          {ref.namespace}")
        
        # Load back as substrate
        loaded = persist.load_substrate(ref)
        print(f"  Loaded identity:   {int(loaded.identity)}")
        print(f"  Loaded value:      {loaded()}")
        
        # Verify
        assert int(car.identity) == int(loaded.identity)
        assert car() == loaded()
        
        persist.close()
    
    print("  ✓ Substrate Serialization PASSED\n")


def test_central_sqlite():
    """Test SQLite central store."""
    print("=" * 60)
    print("TEST: CentralStore (sqlite://)")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "central.db"
        store = CentralStore(f"sqlite://{db_path}")
        
        # Save
        ref = store.save(555, b'{"shared": true}', namespace="shared")
        print(f"  Saved to SQLite: identity=555")
        
        # Load
        data = store.load(ref)
        print(f"  Loaded: {data.decode()}")
        
        # Verify file exists
        print(f"  DB exists: {db_path.exists()}")
        print(f"  DB size: {db_path.stat().st_size} bytes")
        
        store.close()
    
    print("  ✓ CentralStore (sqlite) PASSED\n")


def demonstrate_architecture():
    """Show how persistence fits the architecture."""
    print("=" * 60)
    print("ARCHITECTURE: Persistence via SRL")
    print("=" * 60)
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │                    APPLICATION                          │
    │                                                         │
    │   persist.save(substrate)  →  SRLReference              │
    │   persist.load(ref)        →  Substrate                 │
    └─────────────────────────────┬───────────────────────────┘
                                  │
    ┌─────────────────────────────▼───────────────────────────┐
    │                      CORE                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │               PERSISTENCE                         │  │
    │  │                                                   │  │
    │  │   ┌─────────────┐      ┌────────────────────┐    │  │
    │  │   │ LocalStore  │      │   CentralStore     │    │  │
    │  │   │ (SQLite)    │      │ (Redis/Postgres/   │    │  │
    │  │   │             │      │  HTTP/SQLite)      │    │  │
    │  │   └──────┬──────┘      └──────────┬─────────┘    │  │
    │  │          │                        │              │  │
    │  │          └─────────┬──────────────┘              │  │
    │  │                    │                             │  │
    │  │              ┌─────▼─────┐                       │  │
    │  │              │    SRL    │ ← 64-bit reference    │  │
    │  │              └─────┬─────┘                       │  │
    │  └────────────────────┼─────────────────────────────┘  │
    │                       │                                │
    │             ┌─────────▼─────────┐                      │
    │             │ ingest() / invoke()│                      │
    │             └─────────┬─────────┘                      │
    └───────────────────────┼────────────────────────────────┘
                            │
    ┌───────────────────────▼────────────────────────────────┐
    │                     KERNEL                             │
    │              (pure 64-bit math)                        │
    │                                                        │
    │   Substrate ← 64-bit identity + expression             │
    │   Lens ← projects values                               │
    │   Delta ← transforms values                            │
    │                                                        │
    │   NO storage details. NO connections. NO I/O.          │
    │   Just mathematical operations on identity.            │
    └────────────────────────────────────────────────────────┘
    
    KEY INSIGHT:
    ═══════════════════════════════════════════════════════════
    The Kernel NEVER sees storage.
    
    - LocalStore saves to disk → Core handles I/O
    - CentralStore syncs to server → Core handles network
    - Kernel only sees: SubstrateIdentity(42) ← pure math
    
    SRL is the 64-bit reference. The substrate EXISTS.
    Persistence is just revealing WHERE it exists.
    ═══════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    test_local_store()
    test_central_store_memory()
    test_persistence_manager()
    test_srl_addressing()
    test_substrate_serialization()
    test_central_sqlite()
    demonstrate_architecture()
    
    print("=" * 60)
    print("ALL PERSISTENCE TESTS PASSED")
    print("=" * 60)
