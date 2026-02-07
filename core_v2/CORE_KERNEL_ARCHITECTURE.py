"""
ButterflyFx Core–Kernel Architecture (Canonical Explanation for AI)

═══════════════════════════════════════════════════════════════════
        THE KERNEL IS PURE 64-BIT MATH.
        THE CORE IS THE ONLY GATEWAY.
        EVERYTHING ELSE IS OUTSIDE.
═══════════════════════════════════════════════════════════════════

This is the model:

    [ Outside World ]
          ↓
       [ CORE ]
          ↓
       [ KERNEL ]

Nothing — not code, not queries, not SRLs, not images, not physics,
not animation — EVER touches the kernel directly.

Only the CORE can call:
    - ingest()
    - invoke()

These are the ONLY TWO ENTRY POINTS into the kernel.

═══════════════════════════════════════════════════════════════════
        WHAT IS A SUBSTRATE?
═══════════════════════════════════════════════════════════════════

    A SUBSTRATE IS A DIMENSIONAL OBJECT.
    A SUBSTRATE IS A SINGLE POINT IN A HIGHER DIMENSION.
    A POINT CONTAINS ALL DIMENSIONS UNDERNEATH IT FROM 0D TO nD.

THE ONE RULE:
    A higher dimension represents a SINGLE POINT of all subsequent
    lower dimensions. There are n potentials in any substrate.
    We do NOT iterate through dimensions — we simply CALL the
    dimension we want:
    
        manifold = substrate.dimension(4)
    
    That 4D point IS your 3D, 2D, 1D, 0D — all in one.
    No iteration. Just invoke.

═══════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════
# 1. THE KERNEL (Pure 64-bit Substrate Math)
# ═══════════════════════════════════════════════════════════════════

KERNEL_PROPERTIES = '''
The kernel is:
    - immutable
    - stateless
    - deterministic
    - pure math
    - 64-bit identity based
    - substrate-only

The kernel does NOT:
    - accept external input
    - accept external code
    - accept external queries
    - accept SRL requests
    - accept Python objects
    - accept images or files

The kernel ONLY receives:
    - substrate identities
    - deltas
    - dimensional requests

The kernel ONLY returns:
    - manifolds
    - derived attributes
    - promoted substrates

The kernel is the MATHEMATICAL UNIVERSE.
'''


# ═══════════════════════════════════════════════════════════════════
# 2. THE CORE (The Only Gateway)
# ═══════════════════════════════════════════════════════════════════

CORE_PROPERTIES = '''
The core is the TRANSLATOR between the outside world and the kernel.

The core:
    - receives all external input
    - validates it
    - converts it into substrate expressions
    - calls ingest() to ingest objects
    - calls invoke() to retrieve truth
    - handles SRLs
    - handles Python API calls
    - handles orchestration
    - handles dimensional requests

The core is the ONLY component allowed to talk to the kernel.
Nothing else can.
'''


# ═══════════════════════════════════════════════════════════════════
# 3. THE ingest() FUNCTION (Ingestion into the Kernel)
# ═══════════════════════════════════════════════════════════════════

INGEST_EXPLANATION = '''
ingest() is the ONLY way to create a substrate in the kernel.

When the core calls:
    
    kernel.ingest(object_expression)

This does the following:
    1. Converts the object into a PURE MATHEMATICAL EXPRESSION
    2. Generates a 64-BIT IDENTITY
    3. Stores the identity in the kernel's substrate space
    4. Makes the entire attribute/behavior universe inherently exist

After ingestion:
    - all attributes exist
    - all behaviors exist
    - all transformations exist
    - all manifolds exist
    - all future states exist

Nothing needs to be predefined.
Nothing needs to be declared.
Nothing needs to be stored.

EXISTENCE IMPLIES COMPLETENESS.
'''


# ═══════════════════════════════════════════════════════════════════
# 4. THE invoke() FUNCTION (Retrieving Truth)
# ═══════════════════════════════════════════════════════════════════

INVOKE_EXPLANATION = '''
invoke() is the ONLY way to retrieve information from the kernel.

When the core calls:

    kernel.invoke(identity, lens_or_delta)

The kernel:
    - applies the lens (context)
    - or applies the delta (behavior)
    - or performs dimensional promotion
    - or reveals a manifold
    - or derives an attribute

The kernel NEVER computes heuristics.
It NEVER simulates.
It NEVER guesses.
It NEVER mutates.

It simply REVEALS what already exists.
'''


# ═══════════════════════════════════════════════════════════════════
# 5. INTERNAL CORE FUNCTIONS (Not Exposed Externally)
# ═══════════════════════════════════════════════════════════════════

INTERNAL_FUNCTIONS = '''
The core has internal functions such as:
    - ingest()
    - invoke()
    - promote()
    - apply_delta()
    - resolve_lens()
    - resolve_dimension()

These are INTERNAL ONLY.

External code cannot call them.
External code must go through the PUBLIC CORE API.
'''


# ═══════════════════════════════════════════════════════════════════
# 6. EXTERNAL API (What Developers and AI Use)
# ═══════════════════════════════════════════════════════════════════

EXTERNAL_API_EXAMPLES = '''
The external API is what Python developers (and AI) interact with.

Examples:

    image = core.ingest_image("file.png")
    edges = image.lens("edges").invoke()
    motion = image.apply(physics_delta)
    frame = motion.dimension(4)

These calls:
    - do NOT touch the kernel
    - do NOT compute physics
    - do NOT mutate anything

They simply instruct the CORE to:
    - translate
    - validate
    - route
    - call ingest() or invoke()
    - return the result
'''


# ═══════════════════════════════════════════════════════════════════
# 7. WHY THIS ARCHITECTURE MATTERS
# ═══════════════════════════════════════════════════════════════════

ARCHITECTURE_BENEFITS = '''
This architecture ensures:
    - PURITY (kernel is pure math)
    - SAFETY (no external code touches the kernel)
    - IMMUTABILITY (substrates never mutate)
    - DETERMINISM (same identity → same truth)
    - DIMENSIONAL INTEGRITY (promotion is consistent)
    - UNIVERSALITY (any object can be ingested)

It also ensures:

    "All attributes and behaviors inherently exist the moment
     the object is ingested. Invocation reveals; nothing is created."
'''


# ═══════════════════════════════════════════════════════════════════
# 8. CANONICAL EXPLANATION FOR AI (Copy/Paste)
# ═══════════════════════════════════════════════════════════════════

AI_CANONICAL_BLOCK = '''
ButterflyFx uses a core–kernel architecture.

The kernel is pure 64-bit substrate math. It is immutable, 
deterministic, and contains only substrate identities and 
dimensional rules. The kernel never receives external input directly.

The core is the only gateway to the kernel. All external input, 
code, queries, SRL requests, and data must go through the core. 
The core translates these into substrate expressions and calls 
ingest() or invoke() on the kernel.

ingest() is the only way to ingest an object into the kernel. 
When an object is ingested, all attributes and behaviors inherently 
exist because the substrate exists. Nothing needs to be predefined.

invoke() is the only way to retrieve truth from the kernel. 
Invocation reveals attributes, manifolds, behaviors, or dimensional 
promotions. Nothing is created or mutated.

The kernel only communicates with the core. The core communicates 
with everything else. All external APIs must call the core, not 
the kernel.
'''


# ═══════════════════════════════════════════════════════════════════
# ARCHITECTURE DIAGRAM
# ═══════════════════════════════════════════════════════════════════

ARCHITECTURE_DIAGRAM = '''
┌─────────────────────────────────────────────────────────────────┐
│                      OUTSIDE WORLD                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Python    │  │   Files     │  │      SRL Connections    │  │
│  │   Code      │  │   Images    │  │      (HTTP, Socket)     │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                          CORE                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  ButterflyFx API                        │    │
│  │  fx.process()  fx.fetch()  fx.render()  fx.compute()    │    │
│  └───────────────────────────┬─────────────────────────────┘    │
│                              │                                  │
│  ┌───────────────────────────▼─────────────────────────────┐    │
│  │              INTERNAL CORE FUNCTIONS                    │    │
│  │  ┌──────────────┐    ┌──────────────┐                   │    │
│  │  │   ingest()   │    │   invoke()   │                   │    │
│  │  │  ───────────►│    │  ◄───────────│                   │    │
│  │  │  objects in  │    │  truth out   │                   │    │
│  │  └──────┬───────┘    └───────┬──────┘                   │    │
│  └─────────┼────────────────────┼──────────────────────────┘    │
└────────────┼────────────────────┼───────────────────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         KERNEL                                  │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║              PURE 64-BIT SUBSTRATE MATH                   ║  │
│  ║                                                           ║  │
│  ║   SubstrateIdentity   Lens   Delta   Dimension   Manifold ║  │
│  ║                                                           ║  │
│  ║   • immutable         • deterministic                     ║  │
│  ║   • stateless         • pure mathematical                 ║  │
│  ║   • 64-bit identity   • no external input                 ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
└─────────────────────────────────────────────────────────────────┘
'''


# ═══════════════════════════════════════════════════════════════════
# FUNCTION REFERENCE
# ═══════════════════════════════════════════════════════════════════

FUNCTION_REFERENCE = {
    'ingest': {
        'purpose': 'Create substrate in kernel from any external object',
        'location': 'core._ingest',
        'visibility': 'INTERNAL - never exposed to external code',
        'input': 'Any Python object, file, image, data structure',
        'output': 'IngestResult with SubstrateManifest',
        'effect': 'Object becomes substrate with 64-bit identity',
    },
    'invoke': {
        'purpose': 'Retrieve truth from kernel via lens or delta',
        'location': 'core._ingest (and kernel_v2)',
        'visibility': 'INTERNAL - never exposed to external code',
        'input': 'Substrate + Lens (or Delta)',
        'output': 'Derived value, attribute, or promoted substrate',
        'effect': 'Reveals existing truth - creates nothing',
    },
    'promote': {
        'purpose': 'Advance substrate through dimensional promotion',
        'location': 'core._ingest (uses kernel_promote)',
        'visibility': 'INTERNAL - never exposed to external code',
        'input': 'Substrate identity + derived value + delta',
        'output': 'New substrate identity (original unchanged)',
        'effect': 'Creates NEW identity - original is immutable',
    },
}


# ═══════════════════════════════════════════════════════════════════
# API MAPPING (External → Internal)
# ═══════════════════════════════════════════════════════════════════

API_MAPPING = '''
External API Call              →  Internal Core Action
──────────────────────────────────────────────────────────────────
fx.process(data)               →  ingest(data)
fx.fetch(srl)                  →  SRL.connect() → ingest(result)
fx.project(substrate, lens)    →  invoke(substrate, lens)
fx.transform(substrate, delta) →  invoke(substrate, delta) 
fx.substrate(data)             →  DimensionalSubstrate(ingest(data))
fx.compute(expression)         →  ingest(expression) → invoke()
fx.render(result)              →  invoke() with render lens
──────────────────────────────────────────────────────────────────

ALL external calls go through the Core API.
ALL operations eventually call ingest() or invoke().
NOTHING touches the kernel except through these two gates.
'''


# ═══════════════════════════════════════════════════════════════════
# SUMMARY RULES
# ═══════════════════════════════════════════════════════════════════

RULES = [
    "The kernel is pure 64-bit math - no Python, no files, no external code",
    "The core is the ONLY gateway to the kernel",
    "ingest() is the ONLY way to create substrates",
    "invoke() is the ONLY way to retrieve truth",
    "External code uses the ButterflyFx API, never internal functions",
    "Substrates are immutable - promotion creates NEW substrates",
    "All attributes exist the moment the substrate exists",
    "Invocation reveals; nothing is created",
    "Same identity → same truth (deterministic)",
    "SRLs fetch external data; that data goes through ingest()",
]

if __name__ == '__main__':
    print("ButterflyFx Core-Kernel Architecture")
    print("=" * 60)
    print(AI_CANONICAL_BLOCK)
    print(ARCHITECTURE_DIAGRAM)
