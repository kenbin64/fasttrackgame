/**
 * ButterflyFX Core Interfaces
 * 
 * This module defines interfaces (via JSDoc) for common patterns used throughout
 * the ButterflyFX codebase. JavaScript doesn't have native interfaces, but these
 * documented contracts ensure consistency across implementations.
 * 
 * @module core/interfaces
 */

/**
 * @typedef {Object} IVector
 * @description Interface for vector types (2D, 3D, 4D)
 * @property {number} x - X component
 * @property {number} y - Y component
 * @property {function(IVector): IVector} add - Add another vector
 * @property {function(IVector): IVector} sub - Subtract another vector
 * @property {function(number): IVector} mul - Multiply by scalar
 * @property {function(): number} magnitude - Get vector length
 * @property {function(): IVector} normalize - Get unit vector
 * @property {function(): IVector} clone - Create a copy
 */

/**
 * @typedef {Object} IProjectable
 * @description Interface for objects that can be projected to lower dimensions
 * @property {function(number): Object} project3D - Project 4D to 3D
 * @property {function(Object): Object} project2D - Project 3D to 2D screen coords
 */

/**
 * @typedef {Object} IGeometry
 * @description Interface for geometric shapes
 * @property {Array} vertices - Array of vertex positions
 * @property {Array} edges - Array of edge indices [startIdx, endIdx]
 * @property {function(): void} generateGeometry - Build vertices and edges
 * @property {function(...number): Array} getTransformed - Get transformed vertices
 */

/**
 * @typedef {Object} IRenderable
 * @description Interface for objects that can be rendered
 * @property {boolean} visible - Whether the object is visible
 * @property {number} opacity - Opacity from 0 to 1
 * @property {function(CanvasRenderingContext2D): void} render - Render to canvas
 */

/**
 * @typedef {Object} IInteractive
 * @description Interface for objects that respond to user input
 * @property {boolean} enabled - Whether the object accepts input
 * @property {boolean} isHovered - Whether mouse is over object
 * @property {boolean} isFocused - Whether object has focus
 * @property {boolean} isPressed - Whether object is being pressed
 * @property {function(number, number): boolean} containsPoint - Hit test
 * @property {function(number, number): boolean} onMouseMove - Handle mouse move
 * @property {function(number, number): boolean} onMouseDown - Handle mouse down
 * @property {function(number, number): boolean} onMouseUp - Handle mouse up
 * @property {function(number, number): boolean} onClick - Handle click
 * @property {function(string, Event): boolean} onKeyDown - Handle key press
 * @property {function(): void} focus - Give focus
 * @property {function(): void} blur - Remove focus
 */

/**
 * @typedef {Object} IAnimatable
 * @description Interface for objects with animation capabilities
 * @property {number} animationTime - Current animation time
 * @property {function(number): void} update - Update animation state
 */

/**
 * @typedef {Object} IParticleEmitter
 * @description Interface for particle effect emitters
 * @property {Array} particles - Array of active particles
 * @property {number} maxParticles - Maximum particle count
 * @property {function(number, number, number): void} emitParticles - Emit particles at position
 * @property {function(number): void} updateParticles - Update particle physics
 * @property {function(CanvasRenderingContext2D): void} renderParticles - Render particles
 */

/**
 * @typedef {Object} IColorful
 * @description Interface for objects with color properties
 * @property {Object} primaryColor - Primary HSL color {h, s, l}
 * @property {Object} secondaryColor - Secondary HSL color {h, s, l}
 * @property {Object} textColor - Text HSL color {h, s, l}
 * @property {Object} backgroundColor - Background HSL color {h, s, l}
 * @property {function(Object, number): string} hsl - Convert HSL to CSS string
 * @property {function(Object, number): Object} adjustLightness - Adjust color lightness
 */

/**
 * @typedef {Object} IDimensionalLevel
 * @description Interface for objects with 7 Laws dimensional levels
 * @property {number} level - Current dimensional level (0-6)
 * @property {function(): number} getLevelAlpha - Get alpha based on level
 * @property {function(): number} getLevelBlur - Get blur based on level
 */

/**
 * @typedef {Object} ITransformable
 * @description Interface for objects that can be transformed
 * @property {number} x - X position
 * @property {number} y - Y position
 * @property {number} width - Width
 * @property {number} height - Height
 * @property {number} scale - Scale factor
 * @property {number} rotation - Rotation angle in radians
 */

/**
 * @typedef {Object} ISerializable
 * @description Interface for objects that can be serialized
 * @property {function(): Object} toJSON - Serialize to JSON-compatible object
 * @property {function(Object): void} fromJSON - Deserialize from JSON object
 */

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {};
}

// Make available globally
window.ButterflyFX = window.ButterflyFX || {};
window.ButterflyFX.Interfaces = {
    // This object exists for documentation purposes
    // Actual interface conformance is via duck typing
    VERSION: '1.0.0'
};
