/**
 * PixelState - The Foundation of Universal Pixel Substrate
 * 
 * Every pixel is a full physical, acoustic, and material agent.
 * This class represents the complete state of a single pixel.
 * 
 * Philosophy:
 * - Pixels are NOT just color values
 * - Pixels are AGENTS with material properties, physics, and behavior
 * - Pixels interact with light, sound, and other pixels
 * - Pixels know their structural role in objects
 * - Pixels carry their own animation and motion plan
 * 
 * Integration with DimensionOS:
 * - Each pixel has a 64-bit dimensional identity
 * - Material properties are dimensional attributes
 * - Interactions are dimensional operators
 * - Structure is dimensional relationships
 */

import { MaterialProperties } from './MaterialSystem';
import { LightInteraction } from './LightSystem';
import { SoundInteraction } from './SoundSystem';
import { PhysicsState } from './PhysicsSystem';
import { AnimationState } from './AnimationSystem';
import { StructuralRole } from './ObjectSystem';

/**
 * Core pixel data (color, position, etc.)
 */
export interface PixelData {
  // Visual
  color: [number, number, number, number];  // RGBA [0-1]
  
  // Spatial
  position: [number, number, number];       // XYZ in world space
  screenPosition: [number, number];         // XY in screen space
  
  // Depth
  depth: number;                            // Z-depth for rendering
  
  // Metadata
  timestamp: number;                        // When this state was computed
}

/**
 * Complete pixel state
 * 
 * This is the FULL representation of a pixel as a material agent.
 */
export class PixelState {
  // ========================================
  // IDENTITY (from DimensionOS)
  // ========================================
  
  /**
   * 64-bit dimensional identity
   * Connects this pixel to DimensionOS substrate system
   */
  public readonly identity: bigint;
  
  // ========================================
  // MATERIAL PROPERTIES
  // ========================================
  
  /**
   * Material properties define how this pixel behaves
   * - What it's made of (solid, liquid, gas, etc.)
   * - How dense it is
   * - How transparent it is
   * - How it refracts light
   * - What wavelengths it absorbs/reflects
   */
  public material: MaterialProperties;
  
  // ========================================
  // LIGHT INTERACTION
  // ========================================
  
  /**
   * How this pixel interacts with light
   * - Incoming light from all directions
   * - Absorption, reflection, refraction, scattering
   * - Emission (if pixel is a light source)
   */
  public light: LightInteraction;
  
  // ========================================
  // SOUND INTERACTION
  // ========================================
  
  /**
   * How this pixel interacts with sound waves
   * - Incoming sound from all directions
   * - Absorption, reflection, transmission
   * - Resonance frequencies
   */
  public sound: SoundInteraction;
  
  // ========================================
  // PHYSICS STATE
  // ========================================
  
  /**
   * Physical properties and motion
   * - Position, velocity, acceleration
   * - Mass and forces
   * - Motion integration
   */
  public physics: PhysicsState;
  
  // ========================================
  // STRUCTURAL ROLE
  // ========================================
  
  /**
   * This pixel's role in object structure
   * - Is it a vertex, edge, face, or interior point?
   * - What object does it belong to?
   * - What are its local coordinates?
   * - What is its surface normal?
   */
  public structure: StructuralRole;
  
  // ========================================
  // ANIMATION STATE
  // ========================================
  
  /**
   * Animation and keyframe data
   * - Current keyframe phase
   * - Easing curve
   * - Target state
   */
  public animation: AnimationState;
  
  // ========================================
  // DOUBLE-BUFFERED STATE
  // ========================================
  
  /**
   * Current rendered state
   */
  public current: PixelData;
  
  /**
   * Next state (computed but not yet rendered)
   * 
   * Frame update cycle:
   * 1. Compute all nextState for all pixels
   * 2. Commit: current = next for all pixels
   * 3. Render current state
   */
  public next: PixelData;
  
  // ========================================
  // CONSTRUCTOR
  // ========================================
  
  constructor(
    identity: bigint,
    material: MaterialProperties,
    light: LightInteraction,
    sound: SoundInteraction,
    physics: PhysicsState,
    structure: StructuralRole,
    animation: AnimationState,
    initialData: PixelData
  ) {
    this.identity = identity;
    this.material = material;
    this.light = light;
    this.sound = sound;
    this.physics = physics;
    this.structure = structure;
    this.animation = animation;
    this.current = initialData;
    this.next = { ...initialData };
  }
  
  // ========================================
  // METHODS
  // ========================================
  
  /**
   * Commit next state to current state
   * Called after all pixels have computed their next state
   */
  public commit(): void {
    this.current = { ...this.next };
  }
  
  /**
   * Clone this pixel state
   */
  public clone(): PixelState {
    return new PixelState(
      this.identity,
      { ...this.material },
      { ...this.light },
      { ...this.sound },
      { ...this.physics },
      { ...this.structure },
      { ...this.animation },
      { ...this.current }
    );
  }
}

