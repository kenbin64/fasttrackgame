"""
ButterflyFX Helix Integration Tests

Runs through all layers to verify the complete system works.
"""

import sys
import time

def test_primitives():
    """Test Layer 1: Primitives"""
    print("\n🔹 Testing Primitives Layer")
    print("-" * 40)
    
    from helix.primitives import (
        DimensionalType, LazyValue, HelixContext,
        DimensionalIterator, HelixCollection
    )
    
    # Test DimensionalType
    d = DimensionalType(42, level=4)
    assert d.value == 42
    assert d.level == 4
    assert d.level_name == "Plane"
    print(f"  ✓ DimensionalType: {d}")
    
    # Test LazyValue
    computed = False
    def expensive():
        nonlocal computed
        computed = True
        return "computed!"
    
    lazy = LazyValue(expensive)
    assert not lazy.is_materialized
    assert not computed
    
    value = lazy.value  # Now it computes
    assert lazy.is_materialized
    assert computed
    assert value == "computed!"
    print(f"  ✓ LazyValue: {lazy}")
    
    # Test HelixContext
    with HelixContext() as ctx:
        token = ctx.register("test", level=5, data={"name": "test"})
        assert ctx.level == 0
        assert ctx.spiral == 0
        tokens = ctx.invoke(5)
        assert len(tokens) > 0
    print(f"  ✓ HelixContext: registered and invoked")
    
    # Test DimensionalIterator
    levels_visited = []
    for level in DimensionalIterator(6, 0):
        levels_visited.append(level)
    assert levels_visited == [6, 5, 4, 3, 2, 1, 0]
    print(f"  ✓ DimensionalIterator: {levels_visited}")
    
    # Test HelixCollection
    coll = HelixCollection[str]()
    coll.add("alpha", level=5)
    coll.add("beta", level=5)
    coll.add("gamma", level=3)
    
    assert len(coll) == 3
    assert coll.level_counts[5] == 2
    assert coll.level_counts[3] == 1
    assert coll.invoke(5) == ["alpha", "beta"]
    print(f"  ✓ HelixCollection: {coll.level_counts}")
    
    print("  ✅ Primitives Layer OK")
    return True


def test_utilities():
    """Test Layer 2: Utilities"""
    print("\n🔸 Testing Utilities Layer")
    print("-" * 40)
    
    from helix.utilities import (
        HelixPath, HelixQuery, HelixCache,
        HelixSerializer, HelixDiff, HelixLogger
    )
    from helix.substrate import ManifoldSubstrate, Token
    
    # Test HelixPath
    path = HelixPath.parse("6.root/5.data/4.users")
    assert path.depth == 3
    assert path.target_level == 4
    assert path.target_name == "users"
    assert path.levels_traversed() == {6, 5, 4}
    print(f"  ✓ HelixPath: {path}")
    
    # Test from traditional path
    trad_path = HelixPath.from_traditional("/home/user/docs/file.txt")
    assert trad_path.depth == 4
    print(f"  ✓ Traditional path conversion: {trad_path}")
    
    # Test HelixCache
    cache = HelixCache()
    cache.set("config", {"debug": True}, level=6)
    cache.set("user_data", {"name": "test"}, level=3)
    
    assert cache.get("config") == {"debug": True}
    
    count = cache.invalidate_level(4)  # Should invalidate level 3 and 4
    assert cache.get("user_data") is None
    assert cache.get("config") == {"debug": True}  # Level 6 still valid
    print(f"  ✓ HelixCache: invalidated {count} entries")
    
    # Test HelixQuery
    substrate = ManifoldSubstrate()
    substrate.create_token(
        location=(0, 5, 0),
        signature={5},
        payload=lambda: {"name": "Alice", "age": 30}
    )
    substrate.create_token(
        location=(1, 5, 0),
        signature={5},
        payload=lambda: {"name": "Bob", "age": 25}
    )
    substrate.create_token(
        location=(0, 3, 0),
        signature={3},
        payload=lambda: {"name": "Charlie", "age": 35}
    )
    
    query = HelixQuery().at_level(5)
    results = query.execute(substrate)
    assert len(results) == 2
    print(f"  ✓ HelixQuery: found {len(results)} at level 5")
    
    # Test HelixSerializer
    json_data = HelixSerializer.to_json(substrate)
    assert '"tokens"' in json_data
    
    restored = HelixSerializer.from_json(json_data)
    assert len(restored._tokens) == len(substrate._tokens)
    print(f"  ✓ HelixSerializer: serialized {len(substrate._tokens)} tokens")
    
    # Test HelixLogger
    logger = HelixLogger(min_level=3)
    logger.whole("System started")
    logger.plane("Feature loaded")
    logger.width("User action")
    
    assert len(logger.entries) == 3
    level_6_logs = logger.get_by_level(6)
    assert len(level_6_logs) == 1
    print(f"  ✓ HelixLogger: {len(logger.entries)} entries")
    
    print("  ✅ Utilities Layer OK")
    return True


def test_foundation():
    """Test Layer 3: Foundation"""
    print("\n🔶 Testing Foundation Layer")
    print("-" * 40)
    
    from helix.foundation import (
        HelixDB, HelixFS, HelixStore, HelixGraph
    )
    
    # Test HelixDB
    db = HelixDB("test_db")
    db.create_table("users", level=5)
    
    id1 = db.insert("users", {"name": "Alice", "age": 30})
    id2 = db.insert("users", {"name": "Bob", "age": 25})
    
    assert db.count("users") == 2
    
    results = db.query("users").where(lambda d: d["age"] > 27).execute()
    assert len(results) == 1
    assert results[0].data["name"] == "Alice"
    
    # Test invoke_level
    records = db.invoke_level(4)  # Records are at level-1 from table
    assert len(records) == 2
    print(f"  ✓ HelixDB: {db.count('users')} users, query found {len(results)}")
    
    # Test HelixFS
    fs = HelixFS()
    fs.write("6.data/5.config/4.app.json", {"debug": True})
    fs.write("6.data/5.users/4.alice.json", {"name": "Alice"})
    
    content = fs.read("6.data/5.config/4.app.json")
    assert content == {"debug": True}
    
    level_4_files = fs.invoke(4)
    assert len(level_4_files) == 2
    print(f"  ✓ HelixFS: {len(fs.files)} files, {len(level_4_files)} at level 4")
    
    # Test HelixStore
    store = HelixStore[dict]()
    store.set("config:app", {"name": "MyApp"}, level=6)
    store.set("user:alice", {"role": "admin"}, level=4)
    store.set("session:abc", {"token": "xyz"}, level=2)
    
    assert store.get("config:app")["name"] == "MyApp"
    assert len(store) == 3
    
    level_4 = store.get_level(4)
    assert "user:alice" in level_4
    print(f"  ✓ HelixStore: {len(store)} items")
    
    # Test HelixGraph
    graph = HelixGraph()
    graph.add_node("system", level=6, data={"name": "System"})
    graph.add_node("auth", level=5, data={"name": "Auth Module"})
    graph.add_node("db", level=5, data={"name": "DB Module"})
    graph.add_node("users", level=4, data={"name": "Users"})
    
    graph.add_edge("system", "auth")
    graph.add_edge("system", "db")
    graph.add_edge("auth", "users")
    
    children = graph.children("system")
    assert len(children) == 2
    
    parents = graph.parents("users")
    assert len(parents) == 1
    assert parents[0].id == "auth"
    
    print(f"  ✓ HelixGraph: {len(graph.nodes)} nodes, {graph.edge_count()} edges")
    
    print("  ✅ Foundation Layer OK")
    return True


def test_apps():
    """Test Layer 4: Apps"""
    print("\n🔷 Testing Apps Layer")
    print("-" * 40)
    
    from helix.apps import (
        HelixExplorer, HelixDataPipeline,
        HelixAPIAggregator, HelixEventSystem, HelixEvent
    )
    
    # Test HelixExplorer
    explorer = HelixExplorer()
    count = explorer.load_data({
        "cars": {
            "tesla": {"price": 80000},
            "ford": {"price": 50000}
        }
    })
    
    assert count > 0
    stats = explorer.level_stats()
    assert sum(s["count"] for s in stats.values()) > 0
    print(f"  ✓ HelixExplorer: loaded {count} items")
    
    # Test HelixDataPipeline
    pipeline = HelixDataPipeline("test_pipe")
    pipeline.add_step("double", level=5, transform=lambda x: [i*2 for i in x])
    pipeline.add_step("filter", level=4, transform=lambda x: [i for i in x if i > 4])
    pipeline.add_step("sum", level=3, transform=lambda x: sum(x))
    
    result = pipeline.run([1, 2, 3, 4, 5])
    
    assert result["success"] == True
    assert result["output"] == 6 + 8 + 10  # 24
    print(f"  ✓ HelixDataPipeline: [1,2,3,4,5] → {result['output']}")
    
    # Test HelixAPIAggregator
    api = HelixAPIAggregator()
    api.register("health", level=0, url="/health")
    api.register("users", level=4, url="/api/users")
    api.register("posts", level=4, url="/api/posts")
    
    level_4 = api.invoke(4)
    assert len(level_4) == 2
    assert "users" in level_4
    assert "posts" in level_4
    print(f"  ✓ HelixAPIAggregator: {len(level_4)} endpoints at level 4")
    
    # Test HelixEventSystem
    events = HelixEventSystem()
    
    received = []
    events.on(6, "startup", lambda e: received.append("system"))
    events.on(5, "startup", lambda e: received.append("module"))
    events.on(3, "startup", lambda e: received.append("widget"))
    
    event = HelixEvent("startup", level=6, data={})
    count = events.emit(event)
    
    assert count == 3
    assert received == ["system", "module", "widget"]
    print(f"  ✓ HelixEventSystem: {count} handlers triggered")
    
    print("  ✅ Apps Layer OK")
    return True


def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("ButterflyFX Helix - Integration Tests")
    print("=" * 60)
    
    start = time.time()
    
    results = {
        "Primitives": test_primitives(),
        "Utilities": test_utilities(),
        "Foundation": test_foundation(),
        "Apps": test_apps(),
    }
    
    elapsed = time.time() - start
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for layer, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {layer}")
    
    print(f"\nCompleted in {elapsed:.3f}s")
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        sys.exit(1)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
