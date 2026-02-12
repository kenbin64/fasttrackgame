"""
Demo: Generate a Dimensional Presentation

Creates a non-linear, navigable presentation with drill-down/drill-up.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helix.dimensional_presentation import (
    DimensionalBuilder,
    DimensionalHTMLGenerator
)


def create_butterflyfx_presentation():
    """Create a dimensional presentation about ButterflyFX"""
    
    pres = (DimensionalBuilder("butterflyfx", "ButterflyFX Architecture")
        .spirals(["Core", "Applications", "Future"])
        .size(1920, 1080)
        
        # =====================================================================
        # SPIRAL 0: CORE CONCEPTS
        # =====================================================================
        
        # Level 6: META - The big picture
        .at(0, 6, 0)
        .node("meta-overview", "ButterflyFX", '''
            <p>A revolutionary approach to computing based on 
            <strong>dimensional mathematics</strong>.</p>
            
            <p>Instead of storing and transmitting raw data, 
            we transmit <em>mathematical functions</em>.</p>
            
            <h2>Core Insight</h2>
            <p><code>f(t) = sin(2π × 440 × t)</code></p>
            <p>43 bytes describes infinite audio. Math is universal.</p>
            
            <p style="color: #8b5cf6; margin-top: 2em;">
                ↓ Drill down to explore the architecture
            </p>
        ''', background="#1a1a2e")
            .children("parallel-vs-traditional", "parallel-vs-quantum")
        
        # Level 5: PARALLEL - Alternatives/comparisons
        .at(0, 5, 0)
        .node("parallel-vs-traditional", "vs Traditional Computing", '''
            <table style="width: 100%; font-size: 1.2em; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #333;">
                    <th style="text-align: left; padding: 15px;">Traditional</th>
                    <th style="text-align: left; padding: 15px;">ButterflyFX</th>
                </tr>
                <tr style="border-bottom: 1px solid #333;">
                    <td style="padding: 15px;">Send 192KB/sec audio</td>
                    <td style="padding: 15px; color: #22c55e;">Send 43 bytes (function)</td>
                </tr>
                <tr style="border-bottom: 1px solid #333;">
                    <td style="padding: 15px;">Latency limited by data size</td>
                    <td style="padding: 15px; color: #22c55e;">Near-zero encoding overhead</td>
                </tr>
                <tr style="border-bottom: 1px solid #333;">
                    <td style="padding: 15px;">Lost packet = lost data</td>
                    <td style="padding: 15px; color: #22c55e;">Function continues</td>
                </tr>
                <tr>
                    <td style="padding: 15px;">Codec compatibility issues</td>
                    <td style="padding: 15px; color: #22c55e;">Math is universal</td>
                </tr>
            </table>
        ''', background="#1e293b")
            .link_next("parallel-vs-quantum")
        
        .at(0, 5, 1)
        .node("parallel-vs-quantum", "vs Quantum Computing", '''
            <p>Quantum computing uses superposition and entanglement.</p>
            <p>ButterflyFX uses <strong>dimensional projection</strong>.</p>
            
            <h2>Key Difference</h2>
            <ul>
                <li>Quantum: Probabilistic, requires special hardware</li>
                <li>ButterflyFX: Deterministic, runs on any computer</li>
            </ul>
            
            <p style="margin-top: 1.5em;">
                Both explore computation beyond classical limits,
                but ButterflyFX is <em>practical today</em>.
            </p>
        ''', background="#1e293b")
            .link_prev("parallel-vs-traditional")
        
        # Level 4: TIME - Evolution / Timeline
        .at(0, 4, 0)
        .node("time-evolution", "Evolution", '''
            <h2>Development Timeline</h2>
            
            <div style="display: flex; gap: 30px; margin-top: 1em;">
                <div style="flex: 1; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <h3 style="color: #3b82f6;">Phase 1</h3>
                    <p>Core manifold mathematics</p>
                    <p>7-level helix structure</p>
                </div>
                <div style="flex: 1; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <h3 style="color: #8b5cf6;">Phase 2</h3>
                    <p>Transport protocols</p>
                    <p>Audio/video streaming</p>
                </div>
                <div style="flex: 1; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">
                    <h3 style="color: #22c55e;">Phase 3</h3>
                    <p>Presentation engine</p>
                    <p>Dimensional navigation</p>
                </div>
            </div>
        ''', background="#0f172a")
        
        # Level 3: VOLUME - Spatial/3D
        .at(0, 3, 0)
        .node("volume-architecture", "System Architecture", '''
            <pre style="font-size: 1.1em; line-height: 1.6;">
┌──────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                      │
│   Explorer │ Connector │ FileSystem │ Presentation       │
├──────────────────────────────────────────────────────────┤
│                    TRANSPORT LAYER                        │
│   HelixPacket │ AudioTransport │ ManifoldServer          │
├──────────────────────────────────────────────────────────┤
│                    FOUNDATION LAYER                       │
│   HelixDB │ HelixFS │ HelixStore │ HelixGraph            │
├──────────────────────────────────────────────────────────┤
│                    PRIMITIVES LAYER                       │
│   DimensionalType │ LazyValue │ HelixContext             │
├──────────────────────────────────────────────────────────┤
│                      CORE LAYER                           │
│         HelixKernel │ ManifoldSubstrate                  │
└──────────────────────────────────────────────────────────┘
            </pre>
        ''', background="#0c0c1a")
            .children("plane-modules")
        
        # Level 2: PLANE - Grid/Table
        .at(0, 2, 0)
        .node("plane-modules", "Module Grid", '''
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                <div style="padding: 25px; background: #ef4444; border-radius: 10px; text-align: center;">
                    <strong>kernel.py</strong><br><small>Core state machine</small>
                </div>
                <div style="padding: 25px; background: #f97316; border-radius: 10px; text-align: center;">
                    <strong>substrate.py</strong><br><small>Data storage</small>
                </div>
                <div style="padding: 25px; background: #eab308; border-radius: 10px; text-align: center;">
                    <strong>manifold.py</strong><br><small>Math surface</small>
                </div>
                <div style="padding: 25px; background: #22c55e; border-radius: 10px; text-align: center;">
                    <strong>primitives.py</strong><br><small>Core types</small>
                </div>
                <div style="padding: 25px; background: #06b6d4; border-radius: 10px; text-align: center;">
                    <strong>transport.py</strong><br><small>Network protocol</small>
                </div>
                <div style="padding: 25px; background: #3b82f6; border-radius: 10px; text-align: center;">
                    <strong>foundation.py</strong><br><small>DB, FS, Store</small>
                </div>
                <div style="padding: 25px; background: #8b5cf6; border-radius: 10px; text-align: center;">
                    <strong>assembler.py</strong><br><small>File reconstruction</small>
                </div>
                <div style="padding: 25px; background: #ec4899; border-radius: 10px; text-align: center;">
                    <strong>presentation.py</strong><br><small>Timeline content</small>
                </div>
                <div style="padding: 25px; background: #64748b; border-radius: 10px; text-align: center;">
                    <strong>utilities.py</strong><br><small>Helpers</small>
                </div>
            </div>
        ''', background="#0a0a15")
            .children("line-kernel", "line-manifold")
        
        # Level 1: LINE - Sequence
        .at(0, 1, 0)
        .node("line-kernel", "Kernel Data Flow", '''
            <div style="display: flex; align-items: center; justify-content: center; gap: 20px; font-size: 1.3em;">
                <div style="padding: 20px; background: #ef4444; border-radius: 10px;">Input</div>
                <span>→</span>
                <div style="padding: 20px; background: #f97316; border-radius: 10px;">Encode</div>
                <span>→</span>
                <div style="padding: 20px; background: #eab308; border-radius: 10px;">Transform</div>
                <span>→</span>
                <div style="padding: 20px; background: #22c55e; border-radius: 10px;">Project</div>
                <span>→</span>
                <div style="padding: 20px; background: #3b82f6; border-radius: 10px;">Output</div>
            </div>
            
            <p style="margin-top: 2em; text-align: center; color: #888;">
                Each step maintains dimensional integrity through the helix
            </p>
        ''', background="#0a0a12")
            .link_next("line-manifold")
            .children("point-kernel")
        
        .at(0, 1, 1)
        .node("line-manifold", "Manifold Evaluation", '''
            <div style="text-align: center;">
                <p style="font-size: 1.5em; margin-bottom: 1em;">
                    Given coordinate <code>(spiral, level, position)</code>
                </p>
                
                <div style="display: flex; justify-content: center; gap: 30px;">
                    <div style="padding: 30px; background: rgba(139,92,246,0.3); border-radius: 10px;">
                        <code>θ = level × (2π/7)</code>
                    </div>
                    <div style="padding: 30px; background: rgba(59,130,246,0.3); border-radius: 10px;">
                        <code>r = spiral + 1</code>
                    </div>
                    <div style="padding: 30px; background: rgba(34,197,94,0.3); border-radius: 10px;">
                        <code>z = position × pitch</code>
                    </div>
                </div>
                
                <p style="margin-top: 1.5em; font-size: 1.3em;">
                    <code>point = (r×cos(θ), r×sin(θ), z)</code>
                </p>
            </div>
        ''', background="#0a0a12")
            .link_prev("line-kernel")
        
        # Level 0: POINT - Core concept
        .at(0, 0, 0)
        .node("point-kernel", "The Kernel", '''
            <div style="text-align: center;">
                <div style="font-size: 5em; margin-bottom: 0.3em;">⬡</div>
                <h2>HelixKernel</h2>
                <p style="font-size: 1.3em; max-width: 600px; margin: 1em auto;">
                    The atomic unit. A state machine with 7 levels,
                    each representing a dimension of computation.
                </p>
                
                <div style="display: inline-block; text-align: left; background: rgba(0,0,0,0.3); 
                            padding: 20px 40px; border-radius: 10px; margin-top: 1em;">
                    <code style="font-size: 1.1em;">
kernel = HelixKernel()<br>
kernel.set(0, "physical", data)<br>
kernel.set(1, "datalink", frame)<br>
kernel.set(2, "network", packet)
                    </code>
                </div>
            </div>
        ''', background="#0a0a0f")
            .link_next("point-manifold")
        
        .at(0, 0, 1)
        .node("point-manifold", "The Manifold", '''
            <div style="text-align: center;">
                <div style="font-size: 5em; margin-bottom: 0.3em;">∿</div>
                <h2>Mathematical Surface</h2>
                <p style="font-size: 1.3em; max-width: 600px; margin: 1em auto;">
                    A continuous surface that produces data from coordinates.
                    Evaluate at any point to get a value.
                </p>
                
                <div style="background: rgba(139,92,246,0.2); padding: 30px; 
                            border-radius: 10px; margin-top: 1em; display: inline-block;">
                    <code style="font-size: 1.5em;">
                        f(x, y) → value
                    </code>
                </div>
            </div>
        ''', background="#0a0a0f")
            .link_prev("point-kernel")
        
        # =====================================================================
        # SPIRAL 1: APPLICATIONS
        # =====================================================================
        
        .at(1, 6, 0)
        .node("apps-overview", "Applications", '''
            <p>ButterflyFX enables new kinds of applications:</p>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 1.5em;">
                <div style="padding: 30px; background: rgba(34,197,94,0.2); border-radius: 15px;">
                    <h3 style="color: #22c55e;">🎵 Music Collaboration</h3>
                    <p>Real-time jamming with near-zero latency. 
                    Send math instead of audio samples.</p>
                </div>
                <div style="padding: 30px; background: rgba(59,130,246,0.2); border-radius: 15px;">
                    <h3 style="color: #3b82f6;">🎬 Presentations</h3>
                    <p>Non-linear, dimensional navigation. 
                    Drill down into detail, up for overview.</p>
                </div>
                <div style="padding: 30px; background: rgba(139,92,246,0.2); border-radius: 15px;">
                    <h3 style="color: #8b5cf6;">💾 Universal Storage</h3>
                    <p>Store any file type as manifold coordinates.
                    O(1) access by position.</p>
                </div>
                <div style="padding: 30px; background: rgba(236,72,153,0.2); border-radius: 15px;">
                    <h3 style="color: #ec4899;">🌐 Network Protocol</h3>
                    <p>7-layer helix maps to OSI.
                    Priority channels, zero-copy routing.</p>
                </div>
            </div>
        ''', background="#1a1a2e")
            .children("apps-audio", "apps-presentation")
        
        .at(1, 3, 0)
        .node("apps-audio", "Audio Transport", '''
            <h2>JamKazam Integration</h2>
            
            <p>For real-time music collaboration, every millisecond matters.</p>
            
            <h3 style="margin-top: 1.5em;">The Problem</h3>
            <ul>
                <li>Traditional: 192KB/sec of raw audio</li>
                <li>Network latency causes sync drift</li>
                <li>Jitter requires large buffers</li>
            </ul>
            
            <h3 style="margin-top: 1.5em;">The Solution</h3>
            <ul>
                <li>Send waveform equations: <code>f(t) = sin(2πft)</code></li>
                <li>Receiver generates samples locally</li>
                <li>Can predict ahead - no jitter buffer needed</li>
            </ul>
            
            <p style="color: #22c55e; margin-top: 1em;">
                <strong>Result: 2,233x smaller data, deterministic sync</strong>
            </p>
        ''', background="#0f172a")
            .link_next("apps-presentation")
        
        .at(1, 3, 1)
        .node("apps-presentation", "Presentation Engine", '''
            <h2>This Very Presentation</h2>
            
            <p>You're experiencing a dimensional presentation right now.</p>
            
            <h3 style="margin-top: 1.5em;">Features</h3>
            <ul>
                <li><strong>Drill down</strong> (↓) - More detail</li>
                <li><strong>Drill up</strong> (↑) - Broader context</li>
                <li><strong>Navigate</strong> (←→) - Related topics</li>
                <li><strong>Switch spirals</strong> (1-9) - Different branches</li>
            </ul>
            
            <p style="margin-top: 1.5em;">
                Content is computed from coordinates, not stored as pages.
                Each "slide" exists at <code>(spiral, level, position)</code>.
            </p>
        ''', background="#0f172a")
            .link_prev("apps-audio")
        
        # =====================================================================
        # SPIRAL 2: FUTURE
        # =====================================================================
        
        .at(2, 6, 0)
        .node("future-overview", "The Future", '''
            <h2>Where We're Going</h2>
            
            <p style="font-size: 1.3em;">
                ButterflyFX is not just a library. 
                It's a new way of thinking about computation.
            </p>
            
            <div style="margin-top: 2em; padding: 30px; background: rgba(139,92,246,0.2); 
                        border-radius: 15px; border-left: 4px solid #8b5cf6;">
                <h3 style="color: #8b5cf6;">Vision</h3>
                <p>A world where data is mathematical, 
                transmission is instantaneous, 
                and every computer speaks the universal language of math.</p>
            </div>
            
            <p style="margin-top: 2em; color: #888;">
                ↓ Drill down to see the roadmap
            </p>
        ''', background="#1a1025")
            .children("future-roadmap")
        
        .at(2, 4, 0)
        .node("future-roadmap", "Roadmap", '''
            <div style="display: flex; flex-direction: column; gap: 20px;">
                <div style="display: flex; gap: 20px;">
                    <div style="width: 120px; text-align: right; color: #888;">Q1 2026</div>
                    <div style="flex: 1; padding: 20px; background: rgba(34,197,94,0.2); border-radius: 10px;">
                        <strong style="color: #22c55e;">✓ Core Framework</strong>
                        <br>Kernel, substrate, manifold, transport
                    </div>
                </div>
                <div style="display: flex; gap: 20px;">
                    <div style="width: 120px; text-align: right; color: #888;">Q2 2026</div>
                    <div style="flex: 1; padding: 20px; background: rgba(59,130,246,0.2); border-radius: 10px;">
                        <strong style="color: #3b82f6;">Audio Integration</strong>
                        <br>JamKazam plugin, real-time streaming
                    </div>
                </div>
                <div style="display: flex; gap: 20px;">
                    <div style="width: 120px; text-align: right; color: #888;">Q3 2026</div>
                    <div style="flex: 1; padding: 20px; background: rgba(139,92,246,0.2); border-radius: 10px;">
                        <strong style="color: #8b5cf6;">Cloud Platform</strong>
                        <br>Hosted manifold servers, API access
                    </div>
                </div>
                <div style="display: flex; gap: 20px;">
                    <div style="width: 120px; text-align: right; color: #888;">Q4 2026</div>
                    <div style="flex: 1; padding: 20px; background: rgba(236,72,153,0.2); border-radius: 10px;">
                        <strong style="color: #ec4899;">SDK Release</strong>
                        <br>Python, JavaScript, Rust bindings
                    </div>
                </div>
            </div>
        ''', background="#150f20")
        
        .start_at("meta-overview")
        .build()
    )
    
    return pres


def main():
    print("Creating dimensional presentation...")
    
    pres = create_butterflyfx_presentation()
    
    print(f"  Title: {pres.title}")
    print(f"  Nodes: {len(pres.nodes)}")
    print(f"  Spirals: {pres.spirals}")
    
    # Show structure
    structure = pres.get_structure()
    print("\n  Structure:")
    for spiral in sorted(structure.keys()):
        print(f"    Spiral {spiral}:")
        for level in sorted(structure[spiral].keys(), reverse=True):
            nodes = structure[spiral][level]
            print(f"      Level {level}: {', '.join(nodes)}")
    
    # Generate HTML
    print("\nGenerating HTML...")
    html = DimensionalHTMLGenerator.generate(pres)
    
    output_path = os.path.join(os.path.dirname(__file__), "..", "web", "dimensional_demo.html")
    output_path = os.path.abspath(output_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"  Saved to: {output_path}")
    print(f"  Size: {len(html):,} bytes")
    
    print("\n✓ Open the HTML file in a browser!")
    print("  Controls:")
    print("    ↑ / W    : Drill UP (overview)")
    print("    ↓ / S    : Drill DOWN (detail)")
    print("    ← / A    : Previous")
    print("    → / D    : Next")
    print("    1, 2, 3  : Switch spirals")
    print("    Home     : Go to start")
    print("    Backspace: Go back")


if __name__ == "__main__":
    main()
