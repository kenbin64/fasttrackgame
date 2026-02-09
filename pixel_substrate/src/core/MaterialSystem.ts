/**
 * MaterialSystem - Material Properties for Pixels
 * 
 * Defines what a pixel is MADE OF and how it behaves as a material.
 * 
 * Material types:
 * - SOLID: Rigid, maintains shape
 * - LIQUID: Flows, takes container shape
 * - GAS: Expands to fill space
 * - PLASMA: Ionized, emits light
 * - PARTICLE: Individual particle (dust, smoke, etc.)
 * - EMITTER: Light/sound source
 * - VOID: Empty space (air, vacuum)
 * - GLASS: Transparent solid with refraction
 * - METAL: Reflective, conductive
 * - FABRIC: Flexible, porous
 */

/**
 * Material type enumeration
 */
export enum MaterialType {
  SOLID = 'solid',
  LIQUID = 'liquid',
  GAS = 'gas',
  PLASMA = 'plasma',
  PARTICLE = 'particle',
  EMITTER = 'emitter',
  VOID = 'void',
  GLASS = 'glass',
  METAL = 'metal',
  FABRIC = 'fabric',
}

/**
 * Spectrum: wavelength → intensity mapping
 * Used for absorption, reflection, emission spectra
 * 
 * Key wavelengths (nanometers):
 * - 380-450: Violet/Blue
 * - 450-495: Blue
 * - 495-570: Green
 * - 570-590: Yellow
 * - 590-620: Orange
 * - 620-750: Red
 */
export type Spectrum = Map<number, number>;

/**
 * Material properties
 * 
 * These properties define how a pixel behaves as a material.
 */
export interface MaterialProperties {
  // ========================================
  // BASIC PROPERTIES
  // ========================================
  
  /**
   * Type of material
   */
  materialType: MaterialType;
  
  /**
   * Density (kg/m³)
   * - Air: ~1.2
   * - Water: 1000
   * - Steel: 7850
   * - Gold: 19320
   */
  density: number;
  
  /**
   * Opacity [0-1]
   * - 0: Fully transparent
   * - 1: Fully opaque
   */
  opacity: number;
  
  // ========================================
  // OPTICAL PROPERTIES
  // ========================================
  
  /**
   * Refractive index
   * - Vacuum: 1.0
   * - Air: 1.0003
   * - Water: 1.33
   * - Glass: 1.5-1.9
   * - Diamond: 2.42
   */
  refractiveIndex: number;
  
  /**
   * Absorption spectrum
   * Maps wavelength (nm) → absorption coefficient [0-1]
   * 
   * Defines what wavelengths this material absorbs.
   * High absorption = light is absorbed (converted to heat)
   * Low absorption = light passes through or reflects
   */
  absorptionSpectrum: Spectrum;
  
  /**
   * Reflection spectrum
   * Maps wavelength (nm) → reflection coefficient [0-1]
   * 
   * Defines what wavelengths this material reflects.
   * This determines the material's COLOR.
   * 
   * Example: Red apple
   * - High reflection at 620-750nm (red)
   * - Low reflection at other wavelengths
   */
  reflectionSpectrum: Spectrum;
  
  /**
   * Scattering coefficient [0-1]
   * How much light scatters when passing through
   * - 0: No scattering (clear)
   * - 1: Maximum scattering (frosted, cloudy)
   */
  scatteringCoefficient: number;
  
  // ========================================
  // MECHANICAL PROPERTIES
  // ========================================
  
  /**
   * Hardness [0-1]
   * Resistance to deformation
   * - 0: Very soft (gas, liquid)
   * - 1: Very hard (diamond)
   */
  hardness: number;
  
  /**
   * Elasticity [0-1]
   * Ability to return to original shape after deformation
   * - 0: Plastic (permanent deformation)
   * - 1: Elastic (returns to shape)
   */
  elasticity: number;
  
  /**
   * Friction coefficient [0-1]
   * Resistance to sliding
   * - 0: Frictionless (ice)
   * - 1: High friction (rubber)
   */
  friction: number;
  
  // ========================================
  // ACOUSTIC PROPERTIES
  // ========================================
  
  /**
   * Sound absorption coefficient [0-1]
   * How much sound energy is absorbed
   * - 0: Reflects all sound (hard surfaces)
   * - 1: Absorbs all sound (acoustic foam)
   */
  soundAbsorption: number;
  
  /**
   * Sound speed (m/s)
   * Speed of sound through this material
   * - Air: 343
   * - Water: 1482
   * - Steel: 5960
   */
  soundSpeed: number;
  
  // ========================================
  // METADATA
  // ========================================
  
  /**
   * Material name (for debugging/display)
   */
  name: string;
  
  /**
   * Custom properties (extensible)
   */
  custom: Map<string, any>;
}

/**
 * Create default material properties
 */
export function createDefaultMaterial(type: MaterialType = MaterialType.SOLID): MaterialProperties {
  return {
    materialType: type,
    density: 1000,
    opacity: 1.0,
    refractiveIndex: 1.0,
    absorptionSpectrum: new Map(),
    reflectionSpectrum: new Map(),
    scatteringCoefficient: 0.0,
    hardness: 0.5,
    elasticity: 0.5,
    friction: 0.5,
    soundAbsorption: 0.5,
    soundSpeed: 343,
    name: type,
    custom: new Map(),
  };
}

