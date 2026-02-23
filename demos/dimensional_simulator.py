#!/usr/bin/env python3
"""
Dimensional Simulator
=====================

ButterflyFX - Interactive demonstration of Dimensional Computing

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

A command-line simulator that demonstrates:
- The 7 kernel operations (lift, map, bind, navigate, transform, merge, resolve)
- Lineage tracking and explainability
- Substate switching
- z = x·y multiplicative binding

Usage:
    python dimensional_simulator.py              # Interactive mode
    python dimensional_simulator.py --demo       # Run demo scenarios
    python dimensional_simulator.py --test       # Run tests
"""

import sys
import json
from typing import Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from helix.dimensional_kernel import (
    DimensionalKernel,
    DimensionalObject,
    Layer,
    LAYER_DECLARATIONS,
    LAYER_FIBONACCI,
    PHI,
    create_dimensional_object,
    bind_objects,
    Substate,
    SubstateRule
)


# =============================================================================
# COLOR OUTPUT
# =============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def c(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.ENDC}"

def header(text: str):
    print(f"\n{c('═' * 60, Colors.CYAN)}")
    print(c(f"  {text}", Colors.CYAN + Colors.BOLD))
    print(c('═' * 60, Colors.CYAN))

def info(text: str):
    print(c(f"  → {text}", Colors.GREEN))

def detail(text: str):
    print(c(f"    {text}", Colors.YELLOW))

def section(text: str):
    print(f"\n{c('─' * 40, Colors.BLUE)}")
    print(c(f"  {text}", Colors.BLUE + Colors.BOLD))
    print(c('─' * 40, Colors.BLUE))


# =============================================================================
# DEMO SCENARIOS
# =============================================================================

def demo_basic_operations():
    """Demonstrate the 7 core kernel operations."""
    header("DEMO: Basic Kernel Operations")
    
    kernel = DimensionalKernel()
    
    # 1. LIFT
    section("1. LIFT (Spark → Existence)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.SPARK]}\"")
    print()
    
    raw_data = "Hello, Dimensional World!"
    info(f"Raw input: {raw_data}")
    
    obj = kernel.lift(raw_data)
    detail(f"Created: {obj}")
    detail(f"Layer: {obj.coordinate.layer.name} (Fibonacci: {obj.coordinate.fibonacci})")
    
    # 2. MAP
    section("2. MAP (Mirror → Direction)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.MIRROR]}\"")
    print()
    
    obj = kernel.map_to_manifold(obj)
    info(f"Identity vector: {obj.identity_vector}")
    detail(f"z = x·y = {obj.compute_z():.4f}")
    detail(f"Magnitude: {obj.compute_magnitude():.4f}")
    
    # 3. BIND
    section("3. BIND (Relation → Structure)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.RELATION]}\"")
    print()
    
    obj2 = kernel.lift("Second object")
    obj2 = kernel.map_to_manifold(obj2)
    
    info(f"Object 1 z: {obj.compute_z():.4f}")
    info(f"Object 2 z: {obj2.compute_z():.4f}")
    
    bound = kernel.bind(obj, obj2)
    detail(f"Bound z: {bound.compute_z():.4f}")
    detail(f"Layer: {bound.coordinate.layer.name}")
    
    # 4. NAVIGATE
    section("4. NAVIGATE (Form → Purpose)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.FORM]}\"")
    print()
    
    info(f"Before: Layer {bound.coordinate.layer.name}, Spiral {bound.coordinate.spiral}")
    bound = kernel.navigate(bound, Layer.FORM)
    detail(f"After: Layer {bound.coordinate.layer.name}, Spiral {bound.coordinate.spiral}")
    
    # 5. TRANSFORM
    section("5. TRANSFORM (Life → Motion)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.LIFE]}\"")
    print()
    
    # Create fresh object for clear transform demo
    text_obj = kernel.lift("hello world")
    text_obj = kernel.map_to_manifold(text_obj)
    
    info(f"Before transform: {text_obj.semantic_payload}")
    text_obj = kernel.transform(text_obj, lambda x: x.upper())
    detail(f"After transform: {text_obj.semantic_payload}")
    detail(f"Layer: {text_obj.coordinate.layer.name}")
    
    # 6. MERGE
    section("6. MERGE (Mind → Coherence)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.MIND]}\"")
    print()
    
    objs = [
        kernel.lift("Alpha"),
        kernel.lift("Beta"),
        kernel.lift("Gamma")
    ]
    objs = [kernel.map_to_manifold(o) for o in objs]
    
    info(f"Merging {len(objs)} objects...")
    merged = kernel.merge(objs, strategy="union")
    detail(f"Merged payload: {merged.semantic_payload}")
    detail(f"Merged z: {merged.compute_z():.4f}")
    detail(f"Layer: {merged.coordinate.layer.name}")
    
    # 7. RESOLVE
    section("7. RESOLVE (Completion → Consciousness)")
    print(f"  Declaration: \"{LAYER_DECLARATIONS[Layer.COMPLETION]}\"")
    print()
    
    result, explanation = kernel.resolve(merged, output_format="dict")
    info(f"Resolved output type: {type(result).__name__}")
    detail(f"Final layer: {result.get('layer', 'N/A')}")
    detail(f"Final z: {result.get('z_value', 'N/A'):.4f}")
    
    print(f"\n{c('Lineage Explanation:', Colors.HEADER)}")
    for line in explanation.split('\n')[:10]:  # First 10 lines
        print(f"  {line}")
    
    # Stats
    section("Kernel Statistics")
    stats = kernel.stats
    info(f"Total operations: {stats['operation_count']}")
    info(f"Objects processed: {stats['processed_objects']}")


def demo_multiplicative_binding():
    """Demonstrate z = x·y multiplicative binding properties."""
    header("DEMO: Multiplicative Binding (z = x·y)")
    
    kernel = DimensionalKernel()
    
    section("Scale Invariance")
    print("  Multiplicative binding preserves ratios, not differences.")
    print()
    
    # Create objects with specific identity vectors
    def map_custom(data):
        val = float(data)
        return [val, 1.0 / val]
    
    obj_2 = kernel.lift(2.0)
    obj_2 = kernel.map_to_manifold(obj_2, manifold_func=map_custom)
    
    obj_3 = kernel.lift(3.0)
    obj_3 = kernel.map_to_manifold(obj_3, manifold_func=map_custom)
    
    obj_6 = kernel.lift(6.0)
    obj_6 = kernel.map_to_manifold(obj_6, manifold_func=map_custom)
    
    info(f"Object A (2.0): identity={obj_2.identity_vector}, z={obj_2.compute_z():.4f}")
    info(f"Object B (3.0): identity={obj_3.identity_vector}, z={obj_3.compute_z():.4f}")
    info(f"Object C (6.0): identity={obj_6.identity_vector}, z={obj_6.compute_z():.4f}")
    
    bound_23 = kernel.bind(obj_2, obj_3)
    info(f"\nBound(A,B): z = 2·3 · (1/2)·(1/3) = {bound_23.compute_z():.4f}")
    
    section("Commutativity")
    print("  A · B = B · A")
    print()
    
    bound_ab = kernel.bind(obj_2, obj_3)
    bound_ba = kernel.bind(obj_3, obj_2)
    
    info(f"A · B = {bound_ab.compute_z():.4f}")
    info(f"B · A = {bound_ba.compute_z():.4f}")
    detail(f"Equal: {abs(bound_ab.compute_z() - bound_ba.compute_z()) < 1e-10}")
    
    section("Associativity")
    print("  (A · B) · C = A · (B · C)")
    print()
    
    bound_ab_c = kernel.bind(kernel.bind(obj_2, obj_3), obj_6)
    bound_a_bc = kernel.bind(obj_2, kernel.bind(obj_3, obj_6))
    
    info(f"(A · B) · C = {bound_ab_c.compute_z():.4f}")
    info(f"A · (B · C) = {bound_a_bc.compute_z():.4f}")
    detail(f"Equal: {abs(bound_ab_c.compute_z() - bound_a_bc.compute_z()) < 1e-10}")


def demo_layer_navigation():
    """Demonstrate navigation through the 7 layers."""
    header("DEMO: Layer Navigation (Fibonacci Spiral)")
    
    kernel = DimensionalKernel()
    
    section("The 7 Layers of Creation")
    for layer in Layer:
        fib = LAYER_FIBONACCI[layer]
        decl = LAYER_DECLARATIONS[layer]
        print(f"  Layer {layer.value}: {layer.name:12} │ Fib: {fib:2} │ \"{decl}\"")
    
    section("Spiral Navigation")
    
    obj = kernel.lift("Dimensional Traveler")
    obj = kernel.map_to_manifold(obj)
    
    info(f"Starting: {obj.coordinate}")
    
    # Navigate through all layers
    for layer in [Layer.RELATION, Layer.FORM, Layer.LIFE, Layer.MIND, Layer.COMPLETION]:
        obj = kernel.navigate(obj, layer)
        detail(f"→ {obj.coordinate}")
    
    # Spiral up
    info("\nSpiral Up (Completion → Spark of next spiral)")
    obj.spiral_up()
    detail(f"After spiral_up: {obj.coordinate}")
    
    # Navigate back
    obj = kernel.navigate(obj, Layer.COMPLETION)
    detail(f"Navigate to Completion: {obj.coordinate}")
    
    # Spiral down
    info("\nSpiral Down (Spark → Completion of previous spiral)")
    obj.coordinate.layer = Layer.SPARK  # Must be at spark to spiral down
    obj.spiral_down()
    detail(f"After spiral_down: {obj.coordinate}")


def demo_lineage_tracking():
    """Demonstrate full lineage tracking for explainability."""
    header("DEMO: Lineage Tracking (Explainability)")
    
    kernel = DimensionalKernel()
    
    section("Creating Objects with Full History")
    
    # Create and transform an object through multiple operations
    obj = kernel.lift("Original Data")
    obj = kernel.map_to_manifold(obj)
    obj = kernel.navigate(obj, Layer.FORM)
    obj = kernel.transform(obj, lambda x: x.lower())
    obj = kernel.transform(obj, lambda x: x.replace(" ", "_"))
    obj = kernel.navigate(obj, Layer.LIFE)
    
    result, explanation = kernel.resolve(obj)
    
    info(f"Final result: {result}")
    print()
    
    section("Full Lineage Trace")
    print(explanation)
    
    section("Lineage Graph Statistics")
    graph = obj.lineage_graph
    info(f"Total nodes: {len(graph.nodes)}")
    info(f"Root: {graph.root_id}")
    info(f"Current: {graph.current_id}")


def demo_substates():
    """Demonstrate substate switching."""
    header("DEMO: Substate System")
    
    kernel = DimensionalKernel()
    
    section("Default Substates")
    for name in kernel.substate_manager.substates:
        sub = kernel.substate_manager.substates[name]
        print(f"  • {name}: {len(sub.rules)} rules")
    
    section("Creating Custom Substate")
    
    # Create a 'sanitize' substate
    sanitize = Substate("sanitize")
    sanitize.add_rule(
        "trim_whitespace",
        condition=lambda x: isinstance(x, str),
        transform=lambda x: x.strip(),
        priority=10
    )
    sanitize.add_rule(
        "lowercase",
        condition=lambda x: isinstance(x, str),
        transform=lambda x: x.lower(),
        priority=5
    )
    
    kernel.substate_manager.register(sanitize)
    info("Registered 'sanitize' substate with 2 rules")
    
    section("Processing with Substates")
    
    # Process without substate
    obj1 = kernel.lift("  HELLO WORLD  ")
    obj1 = kernel.map_to_manifold(obj1)
    result1, _ = kernel.resolve(obj1)
    info(f"Without substate: '{result1}'")
    
    # Process with substate
    kernel.substate_manager.push("sanitize")
    obj2 = kernel.lift("  HELLO WORLD  ")
    obj2 = kernel.map_to_manifold(obj2)
    result2, _ = kernel.resolve(obj2)
    info(f"With 'sanitize' substate: '{result2}'")
    kernel.substate_manager.pop()


def demo_3d_application():
    """Demonstrate 3D graphics application of dimensional computing."""
    header("DEMO: 3D Graphics Application")
    
    kernel = DimensionalKernel()
    
    section("3D Objects as DimensionalObjects")
    print("  In 3D: semantic_payload = mesh data")
    print("         identity_vector = [x, y, z, scale]")
    print("         intention = purpose in scene")
    print()
    
    # Simulate 3D objects
    class Mesh:
        def __init__(self, name: str, vertices: int):
            self.name = name
            self.vertices = vertices
        def __repr__(self):
            return f"Mesh({self.name}, {self.vertices} verts)"
    
    def map_3d_object(mesh):
        # Position based on name hash, scale based on vertices
        h = hash(mesh.name) % 1000
        return [h / 100.0, h / 200.0, mesh.vertices / 100.0, 1.0]
    
    cube = kernel.lift(Mesh("cube", 8))
    cube = kernel.map_to_manifold(cube, manifold_func=map_3d_object)
    cube.intention_vector[0] = 0.8  # "be solid"
    
    sphere = kernel.lift(Mesh("sphere", 482))
    sphere = kernel.map_to_manifold(sphere, manifold_func=map_3d_object)
    sphere.intention_vector[0] = 0.5  # "be decorative"
    
    info(f"Cube: {cube.semantic_payload}")
    detail(f"  Position/scale: {cube.identity_vector}")
    detail(f"  z-product: {cube.compute_z():.4f}")
    
    info(f"\nSphere: {sphere.semantic_payload}")
    detail(f"  Position/scale: {sphere.identity_vector}")
    detail(f"  z-product: {sphere.compute_z():.4f}")
    
    section("Relational Binding (z = x·y)")
    
    # Bind objects relationally
    bound_scene = kernel.bind(cube, sphere)
    info(f"Bound scene objects")
    detail(f"Combined z: {bound_scene.compute_z():.4f}")
    detail(f"Intention alignment: {cube.compute_intention_alignment(sphere):.4f}")
    
    section("Scene Resolution")
    
    result, explanation = kernel.resolve(bound_scene, output_format="dict")
    info(f"Resolved scene with {len(explanation.split(chr(10)))} lineage steps")
    detail(f"Final layer: {result['layer']}")


def demo_fibonacci_alignment():
    """Demonstrate Fibonacci sequence alignment in the kernel."""
    header("DEMO: Fibonacci Alignment")
    
    section("Fibonacci Sequence in Layers")
    sequence = []
    for layer in Layer:
        fib = LAYER_FIBONACCI[layer]
        sequence.append(fib)
        bar = "█" * fib
        print(f"  Layer {layer.value} ({layer.name:12}): {fib:2} │ {bar}")
    
    info(f"\nSequence: {sequence}")
    detail(f"Sum: {sum(sequence)} (= 21 = Fib(8))")
    
    section("Golden Ratio (φ)")
    info(f"φ = (1 + √5) / 2 = {PHI:.10f}")
    detail(f"1/φ = {1/PHI:.10f}")
    detail(f"φ² = {PHI**2:.10f}")
    detail(f"φ - 1 = 1/φ = {PHI - 1:.10f}")
    
    section("Fibonacci Ratios → φ")
    for i, layer in enumerate(list(Layer)[1:], 1):
        prev = LAYER_FIBONACCI[list(Layer)[i-1]]
        curr = LAYER_FIBONACCI[layer]
        if prev > 0:
            ratio = curr / prev
            print(f"  {curr}/{prev} = {ratio:.6f}  (φ ≈ {PHI:.6f})")


def run_all_demos():
    """Run all demonstration scenarios."""
    print(c("\n" + "█" * 60, Colors.HEADER))
    print(c("  DIMENSIONAL COMPUTING SIMULATOR", Colors.HEADER + Colors.BOLD))
    print(c("  ButterflyFX - The Mathematical Kernel", Colors.HEADER))
    print(c("█" * 60, Colors.HEADER))
    
    demo_basic_operations()
    demo_multiplicative_binding()
    demo_layer_navigation()
    demo_lineage_tracking()
    demo_substates()
    demo_3d_application()
    demo_fibonacci_alignment()
    
    header("SIMULATION COMPLETE")
    print(f"\n  {c('All demos completed successfully!', Colors.GREEN)}")
    print(f"  The Dimensional Computing kernel is ready for use.\n")


# =============================================================================
# INTERACTIVE MODE
# =============================================================================

def interactive_mode():
    """Run interactive REPL for the dimensional kernel."""
    print(c("\n════════════════════════════════════════════════════════════", Colors.CYAN))
    print(c("  DIMENSIONAL COMPUTING - Interactive Mode", Colors.CYAN + Colors.BOLD))
    print(c("════════════════════════════════════════════════════════════", Colors.CYAN))
    
    kernel = DimensionalKernel()
    objects: dict[str, DimensionalObject] = {}
    
    help_text = """
Commands:
  lift <name> <data>       - Create a DimensionalObject from data
  map <name>               - Map object to manifold
  bind <name1> <name2>     - Bind two objects (z = x·y)
  navigate <name> <layer>  - Navigate to layer (1-7)
  transform <name> <func>  - Transform (upper, lower, reverse)
  resolve <name>           - Resolve and show result
  show <name>              - Show object details
  list                     - List all objects
  layers                   - Show 7-layer structure
  stats                    - Show kernel statistics
  demo                     - Run demo scenarios
  help                     - Show this help
  quit                     - Exit
"""
    
    print(help_text)
    
    while True:
        try:
            line = input(c("\ndimensional> ", Colors.GREEN)).strip()
            if not line:
                continue
            
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "quit" or cmd == "exit":
                print(c("Goodbye!", Colors.CYAN))
                break
            
            elif cmd == "help":
                print(help_text)
            
            elif cmd == "demo":
                run_all_demos()
            
            elif cmd == "layers":
                for layer in Layer:
                    fib = LAYER_FIBONACCI[layer]
                    print(f"  {layer.value}: {layer.name:12} Fib={fib:2}  \"{LAYER_DECLARATIONS[layer]}\"")
            
            elif cmd == "stats":
                stats = kernel.stats
                print(f"  Operations: {stats['operation_count']}")
                print(f"  Objects in kernel: {stats['processed_objects']}")
                print(f"  Objects in session: {len(objects)}")
            
            elif cmd == "list":
                if not objects:
                    print("  (no objects)")
                for name, obj in objects.items():
                    print(f"  {name}: {obj}")
            
            elif cmd == "lift":
                if len(args) < 2:
                    print("  Usage: lift <name> <data>")
                    continue
                name = args[0]
                data = " ".join(args[1:])
                obj = kernel.lift(data)
                objects[name] = obj
                print(f"  Created {name}: {obj}")
            
            elif cmd == "map":
                if len(args) < 1:
                    print("  Usage: map <name>")
                    continue
                name = args[0]
                if name not in objects:
                    print(f"  Object '{name}' not found")
                    continue
                objects[name] = kernel.map_to_manifold(objects[name])
                print(f"  Mapped {name}: z={objects[name].compute_z():.4f}")
            
            elif cmd == "bind":
                if len(args) < 2:
                    print("  Usage: bind <name1> <name2>")
                    continue
                if args[0] not in objects or args[1] not in objects:
                    print("  One or both objects not found")
                    continue
                result_name = f"bound_{len(objects)}"
                objects[result_name] = kernel.bind(objects[args[0]], objects[args[1]])
                print(f"  Bound → {result_name}: z={objects[result_name].compute_z():.4f}")
            
            elif cmd == "navigate":
                if len(args) < 2:
                    print("  Usage: navigate <name> <layer 1-7>")
                    continue
                name = args[0]
                if name not in objects:
                    print(f"  Object '{name}' not found")
                    continue
                try:
                    layer = Layer(int(args[1]))
                    objects[name] = kernel.navigate(objects[name], layer)
                    print(f"  Navigated {name} to {layer.name}")
                except ValueError:
                    print("  Layer must be 1-7")
            
            elif cmd == "transform":
                if len(args) < 2:
                    print("  Usage: transform <name> <upper|lower|reverse>")
                    continue
                name = args[0]
                if name not in objects:
                    print(f"  Object '{name}' not found")
                    continue
                func_name = args[1]
                funcs = {
                    "upper": lambda x: x.upper() if isinstance(x, str) else x,
                    "lower": lambda x: x.lower() if isinstance(x, str) else x,
                    "reverse": lambda x: x[::-1] if isinstance(x, str) else x
                }
                if func_name not in funcs:
                    print(f"  Unknown function: {func_name}")
                    continue
                objects[name] = kernel.transform(objects[name], funcs[func_name])
                print(f"  Transformed {name}: {objects[name].semantic_payload}")
            
            elif cmd == "resolve":
                if len(args) < 1:
                    print("  Usage: resolve <name>")
                    continue
                name = args[0]
                if name not in objects:
                    print(f"  Object '{name}' not found")
                    continue
                result, explanation = kernel.resolve(objects[name], output_format="dict")
                print(f"  Result: {result.get('semantic_payload', result)}")
                print(f"  Layer: {result.get('layer', 'N/A')}")
                print(f"  z: {result.get('z_value', 'N/A')}")
            
            elif cmd == "show":
                if len(args) < 1:
                    print("  Usage: show <name>")
                    continue
                name = args[0]
                if name not in objects:
                    print(f"  Object '{name}' not found")
                    continue
                obj = objects[name]
                print(f"  ID: {obj._id}")
                print(f"  Payload: {obj.semantic_payload}")
                print(f"  Identity: {obj.identity_vector}")
                print(f"  z = x·y: {obj.compute_z():.6f}")
                print(f"  Coordinate: {obj.coordinate}")
                print(f"  Fibonacci: {obj.coordinate.fibonacci}")
                print(f"  Context: {obj.context_map}")
                print(f"  Deltas: {obj.delta_set}")
            
            else:
                print(f"  Unknown command: {cmd}")
                print("  Type 'help' for commands")
        
        except KeyboardInterrupt:
            print(c("\nGoodbye!", Colors.CYAN))
            break
        except Exception as e:
            print(c(f"  Error: {e}", Colors.RED))


# =============================================================================
# TESTS
# =============================================================================

def run_tests():
    """Run basic tests."""
    header("Running Tests")
    
    kernel = DimensionalKernel()
    passed = 0
    failed = 0
    
    def test(name, condition):
        nonlocal passed, failed
        if condition:
            print(c(f"  ✓ {name}", Colors.GREEN))
            passed += 1
        else:
            print(c(f"  ✗ {name}", Colors.RED))
            failed += 1
    
    # Test lift
    obj = kernel.lift("test")
    test("lift creates object", obj is not None)
    test("lift sets spark layer", obj.coordinate.layer == Layer.SPARK)
    
    # Test map
    obj = kernel.map_to_manifold(obj)
    test("map updates identity", len(obj.identity_vector) > 0)
    test("map sets mirror layer", obj.coordinate.layer == Layer.MIRROR)
    
    # Test z = x·y
    z = obj.compute_z()
    test("compute_z returns float", isinstance(z, float))
    test("z ≈ 1 for neutral mapping", 0.8 < z < 1.2)
    
    # Test bind
    obj2 = kernel.lift("data")
    obj2 = kernel.map_to_manifold(obj2)
    bound = kernel.bind(obj, obj2)
    test("bind creates new object", bound._id != obj._id)
    test("bind sets relation layer", bound.coordinate.layer == Layer.RELATION)
    
    # Test navigate
    bound = kernel.navigate(bound, Layer.LIFE)
    test("navigate changes layer", bound.coordinate.layer == Layer.LIFE)
    
    # Test transform
    text_obj = kernel.lift("hello")
    text_obj = kernel.transform(text_obj, lambda x: x.upper())
    test("transform modifies payload", text_obj.semantic_payload == "HELLO")
    test("transform sets life layer", text_obj.coordinate.layer == Layer.LIFE)
    
    # Test merge
    objs = [kernel.lift(x) for x in ["a", "b", "c"]]
    merged = kernel.merge(objs)
    test("merge combines objects", len(merged.semantic_payload) == 3)
    test("merge sets mind layer", merged.coordinate.layer == Layer.MIND)
    
    # Test resolve
    result, explanation = kernel.resolve(merged)
    test("resolve returns result", result is not None)
    test("resolve returns explanation", "Lineage" in explanation)
    
    # Test lineage
    test("lineage has nodes", len(merged.lineage_graph.nodes) > 0)
    
    # Test spiral
    obj = kernel.lift("spiral test")
    obj.coordinate.layer = Layer.COMPLETION
    obj.spiral_up()
    test("spiral_up increments spiral", obj.coordinate.spiral == 1)
    test("spiral_up resets to spark", obj.coordinate.layer == Layer.SPARK)
    
    # Summary
    section("Test Results")
    print(f"  Passed: {c(str(passed), Colors.GREEN)}")
    print(f"  Failed: {c(str(failed), Colors.RED if failed else Colors.GREEN)}")
    
    return failed == 0


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--demo":
            run_all_demos()
        elif arg == "--test":
            success = run_tests()
            sys.exit(0 if success else 1)
        elif arg == "--help" or arg == "-h":
            print(__doc__)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --demo, --test, or no arguments for interactive mode")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
