/**
 * ButterflyFX Dimensional Entity - JavaScript Implementation
 * 
 * Formal Helix Kernel implementation following BUTTERFLYFX_SPECIFICATION.md
 * 
 * State Space: H = {(s, ℓ) | s ∈ Z, ℓ ∈ {0,1,2,3,4,5,6}}
 * 
 * Operations:
 *   - INVOKE(k): (s, ℓ) → (s, k)
 *   - SPIRAL_UP: (s, 6) → (s+1, 0)
 *   - SPIRAL_DOWN: (s, 0) → (s-1, 6)
 *   - COLLAPSE: (s, ℓ) → (s, 0)
 */

// =============================================================================
// LEVEL DEFINITIONS
// =============================================================================

const LEVELS = {
    POTENTIAL: 0,  // Pure possibility, nothing instantiated
    POINT: 1,      // Single instantiation
    LENGTH: 2,     // Linear extension
    WIDTH: 3,      // 2D extension
    PLANE: 4,      // Surface completeness
    VOLUME: 5,     // 3D existence
    WHOLE: 6       // Complete entity
};

const LEVEL_NAMES = ['Potential', 'Point', 'Length', 'Width', 'Plane', 'Volume', 'Whole'];
const LEVEL_ICONS = ['○', '•', '━', '▭', '▦', '▣', '◉'];

// =============================================================================
// HELIX STATE (Immutable)
// =============================================================================

class HelixState {
    constructor(spiral = 0, level = 0) {
        if (level < 0 || level > 6) {
            throw new Error(`Invalid level: ${level}. Must be 0-6.`);
        }
        this.spiral = spiral;
        this.level = level;
        Object.freeze(this);  // Immutable
    }
    
    get levelName() {
        return LEVEL_NAMES[this.level];
    }
    
    get levelIcon() {
        return LEVEL_ICONS[this.level];
    }
    
    toString() {
        return `(${this.spiral}, ${this.level}:${this.levelName})`;
    }
    
    equals(other) {
        return this.spiral === other.spiral && this.level === other.level;
    }
}

// =============================================================================
// DIMENSIONAL TOKEN
// =============================================================================

class DimensionalToken {
    /**
     * τ = (x, σ, π)
     * @param {string} path - Location in manifold (dimensional path)
     * @param {number[]} signature - Which levels can see this token
     * @param {*} payload - The actual value (lazy)
     * @param {Object} metadata - Additional token metadata
     */
    constructor(path, signature, payload, metadata = {}) {
        this.path = path;
        this.signature = signature;
        this.payload = payload;
        this.metadata = {
            created: Date.now(),
            lastMaterialized: null,
            materializationCount: 0,
            ...metadata
        };
    }
    
    canMaterializeAt(level) {
        return this.signature.includes(level);
    }
    
    materialize() {
        this.metadata.lastMaterialized = Date.now();
        this.metadata.materializationCount++;
        return this.payload;
    }
}

// =============================================================================
// DIMENSIONAL ENTITY BASE CLASS
// =============================================================================

class DimensionalEntity {
    constructor(id = null) {
        this._id = id || crypto.randomUUID?.() || `entity_${Date.now()}`;
        this._helixState = new HelixState(0, 0);
        this._substrate = new Map();  // Map<path, DimensionalToken>
        this._materializedView = null;
        this._events = [];  // Event sourcing
        this._accessLog = [];
    }
    
    // =========================================================================
    // KERNEL OPERATIONS
    // =========================================================================
    
    /**
     * INVOKE(k): (s, ℓ) → (s, k)
     * Jump directly to level k within current spiral
     */
    invoke(level) {
        if (typeof level === 'string') {
            level = LEVELS[level.toUpperCase()];
        }
        if (level < 0 || level > 6) {
            throw new Error(`Invalid level: ${level}`);
        }
        
        const previousState = this._helixState;
        this._helixState = new HelixState(this._helixState.spiral, level);
        
        this._events.push({
            type: 'INVOKE',
            from: previousState.toString(),
            to: this._helixState.toString(),
            level: level,
            timestamp: Date.now()
        });
        
        this._materializedView = this._materialize();
        return this._materializedView;
    }
    
    /**
     * SPIRAL_UP: (s, 6) → (s+1, 0)
     * Move from Whole to Potential of next spiral
     */
    spiralUp() {
        if (this._helixState.level !== 6) {
            throw new Error(`SPIRAL_UP requires level 6 (Whole), current: ${this._helixState.level}`);
        }
        
        const previousState = this._helixState;
        this._helixState = new HelixState(this._helixState.spiral + 1, 0);
        
        this._events.push({
            type: 'SPIRAL_UP',
            from: previousState.toString(),
            to: this._helixState.toString(),
            timestamp: Date.now()
        });
        
        this._materializedView = null;
        return this;
    }
    
    /**
     * SPIRAL_DOWN: (s, 0) → (s-1, 6)
     * Move from Potential to Whole of previous spiral
     */
    spiralDown() {
        if (this._helixState.level !== 0) {
            throw new Error(`SPIRAL_DOWN requires level 0 (Potential), current: ${this._helixState.level}`);
        }
        
        const previousState = this._helixState;
        this._helixState = new HelixState(this._helixState.spiral - 1, 6);
        
        this._events.push({
            type: 'SPIRAL_DOWN',
            from: previousState.toString(),
            to: this._helixState.toString(),
            timestamp: Date.now()
        });
        
        this._materializedView = this._materialize();
        return this;
    }
    
    /**
     * COLLAPSE: (s, ℓ) → (s, 0)
     * Return all levels to Potential
     */
    collapse() {
        const previousState = this._helixState;
        this._helixState = new HelixState(this._helixState.spiral, 0);
        
        this._events.push({
            type: 'COLLAPSE',
            from: previousState.toString(),
            to: this._helixState.toString(),
            timestamp: Date.now()
        });
        
        this._materializedView = null;
        return this;
    }
    
    // =========================================================================
    // SUBSTRATE OPERATIONS
    // =========================================================================
    
    /**
     * Register a token in the substrate
     */
    registerToken(path, signature, payload, metadata = {}) {
        const token = new DimensionalToken(path, signature, payload, metadata);
        this._substrate.set(path, token);
        return token;
    }
    
    /**
     * Materialization function μ: H → P(T)
     * Returns tokens compatible with current helix state
     */
    _materialize() {
        const level = this._helixState.level;
        const result = {};
        
        for (const [path, token] of this._substrate) {
            if (token.canMaterializeAt(level)) {
                const value = token.materialize();
                this._setNestedValue(result, path, value);
                
                this._accessLog.push({
                    timestamp: Date.now(),
                    state: this._helixState.toString(),
                    path: path,
                    level: level
                });
            }
        }
        
        return result;
    }
    
    /**
     * Measure a specific path (with level checking)
     */
    measure(path) {
        const token = this._substrate.get(path);
        
        if (!token) {
            return { path, value: undefined, error: 'Token not found' };
        }
        
        if (!token.canMaterializeAt(this._helixState.level)) {
            return { 
                path, 
                value: undefined, 
                error: `Token requires levels ${token.signature}, current level: ${this._helixState.level}` 
            };
        }
        
        const value = token.materialize();
        this._accessLog.push({
            timestamp: Date.now(),
            state: this._helixState.toString(),
            path: path,
            level: this._helixState.level,
            value: value
        });
        
        return { path, value, level: this._helixState.level };
    }
    
    // =========================================================================
    // PURE TRANSFORMATIONS
    // =========================================================================
    
    /**
     * Transform the entity's state via pure function
     * Returns transformation event (does not mutate directly)
     */
    createTransformEvent(type, data) {
        return {
            type: type,
            entity: this._id,
            spiralState: this._helixState.toString(),
            timestamp: Date.now(),
            data: data
        };
    }
    
    /**
     * Apply a transformation event
     */
    applyEvent(event) {
        this._events.push(event);
        // Subclasses implement specific event handling
        return this;
    }
    
    // =========================================================================
    // UTILITIES
    // =========================================================================
    
    _setNestedValue(obj, path, value) {
        const parts = path.split('.');
        let current = obj;
        
        for (let i = 0; i < parts.length - 1; i++) {
            const part = parts[i];
            const arrayMatch = part.match(/^(\w+)\[(\d+)\]$/);
            
            if (arrayMatch) {
                const name = arrayMatch[1];
                const index = parseInt(arrayMatch[2]);
                if (!current[name]) current[name] = [];
                if (!current[name][index]) current[name][index] = {};
                current = current[name][index];
            } else {
                if (!current[part]) current[part] = {};
                current = current[part];
            }
        }
        
        current[parts[parts.length - 1]] = value;
    }
    
    get id() { return this._id; }
    get state() { return this._helixState; }
    get events() { return [...this._events]; }
    get accessLog() { return [...this._accessLog]; }
    
    getMetrics() {
        const tokenCount = this._substrate.size;
        const materializedCount = this._accessLog.length;
        const uniquePaths = new Set(this._accessLog.map(e => e.path)).size;
        
        return {
            totalTokens: tokenCount,
            materialized: materializedCount,
            uniquePaths: uniquePaths,
            dimensionalEfficiency: tokenCount > 0 ? uniquePaths / tokenCount : 0,
            currentState: this._helixState.toString(),
            spiralRange: this._events.filter(e => e.type.startsWith('SPIRAL')).length,
            invokeCount: this._events.filter(e => e.type === 'INVOKE').length
        };
    }
}

// =============================================================================
// DIMENSIONAL CAR (Concrete Implementation)
// =============================================================================

class DimensionalCarV2 extends DimensionalEntity {
    constructor(apiData) {
        super(`car_${apiData.make}_${apiData.model}`);
        this._apiData = apiData;
        this._buildSubstrate(apiData);
        this._runtimeState = {
            position: { distance_ft: 0, lane_offset: 0 },
            velocity: { speed_mph: 0 },
            controls: { throttle: 0, brake: 0, steering: 0, gear: 0 }
        };
    }
    
    _buildSubstrate(api) {
        // Level 1 (Point) - Identity
        this.registerToken('make', [1,2,3,4,5,6], api.make);
        this.registerToken('model', [1,2,3,4,5,6], api.model);
        this.registerToken('year', [1,2,3,4,5,6], api.year);
        
        // Level 2 (Length) - 1D Properties
        this.registerToken('engine.displacement_L', [2,3,4,5,6], api.engine.displacement_L);
        this.registerToken('chassis.weight_lbs', [2,3,4,5,6], api.chassis.weight_lbs);
        this.registerToken('chassis.wheelbase_in', [2,3,4,5,6], api.chassis.wheelbase_in);
        this.registerToken('engine.horsepower', [2,3,4,5,6], api.engine.horsepower);
        this.registerToken('engine.torque_lb_ft', [2,3,4,5,6], api.engine.torque_lb_ft);
        
        // Level 3 (Width) - 2D Properties
        this.registerToken('chassis.dimensions', [3,4,5,6], {
            width: 72,  // inches
            length: api.chassis.wheelbase_in * 1.5
        });
        
        // Level 4 (Plane) - Surfaces
        this.registerToken('exterior.body_style', [4,5,6], 'sedan');
        this.registerToken('exterior.paint_color', [4,5,6], 'metallic');
        this.registerToken('windows.count', [4,5,6], 6);
        
        // Level 5 (Volume) - 3D Mechanical Systems
        this.registerToken('engine.cylinder_count', [5,6], api.engine.cylinders);
        this.registerToken('engine.compression_ratio', [5,6], api.engine.compression_ratio);
        this.registerToken('transmission.type', [5,6], api.transmission.type);
        this.registerToken('transmission.speeds', [5,6], api.transmission.speeds);
        this.registerToken('drivetrain.type', [5,6], api.drivetrain.type);
        
        // Build cylinders (Level 5+)
        for (let i = 0; i < api.engine.cylinders; i++) {
            this.registerToken(`engine.cylinders[${i}].piston`, [5,6], {
                position: 0.5,
                stroke_in: api.engine.displacement_L * 61.024 / api.engine.cylinders / (Math.PI * 2.25)
            });
            this.registerToken(`engine.cylinders[${i}].spark_plug`, [5,6], {
                gap_mm: 0.8,
                firing: false
            });
        }
        
        // Level 6 (Whole) - Complete Operational
        this.registerToken('performance.top_speed_mph', [6], api.performance.top_speed_mph);
        this.registerToken('performance.zero_to_sixty_s', [6], api.performance.zero_to_sixty_s);
        this.registerToken('fuel.capacity_gal', [6], api.fuel.capacity_gal);
        this.registerToken('fuel.mpg_combined', [6], api.fuel.mpg_combined);
        
        // Operational state (only at Whole)
        this.registerToken('operational.ready', [6], true);
    }
    
    /**
     * Physics transformation - pure function
     */
    transformPhysics(dt, controls) {
        const s = this._runtimeState;
        
        // Must be at Whole level to operate
        if (this._helixState.level !== 6) {
            return { error: 'Car must be at Whole level to operate' };
        }
        
        // Get required values via measurement
        const mass = this.measure('chassis.weight_lbs').value * 0.453592;
        const hp = this.measure('engine.horsepower').value;
        const topSpeed = this.measure('performance.top_speed_mph').value;
        
        // Pure physics computation
        const speed_mps = s.velocity.speed_mph * 0.44704;
        const power_watts = hp * 745.7;
        const max_force = speed_mps > 0.1 ? Math.min(power_watts / speed_mps, 5000) : 5000;
        
        const engine_force = controls.throttle * max_force;
        const brake_force = controls.brake * mass * 10;
        const drag = 0.5 * 1.225 * 0.30 * 2.2 * speed_mps * speed_mps;
        
        const net_force = engine_force - brake_force - drag;
        const accel = net_force / mass;
        const accel_mph_s = accel * 2.23694;
        
        // Create transformation event (immutable)
        const event = this.createTransformEvent('PHYSICS_TICK', {
            dt: dt,
            controls: { ...controls },
            forces: {
                engine: engine_force,
                brake: brake_force,
                drag: drag,
                net: net_force
            },
            acceleration_mph_s: accel_mph_s,
            previousSpeed: s.velocity.speed_mph
        });
        
        // Apply event
        const newSpeed = Math.max(0, Math.min(topSpeed, s.velocity.speed_mph + accel_mph_s * dt));
        const dist = Math.abs(newSpeed * 1.46667 * dt);
        
        s.velocity.speed_mph = newSpeed;
        s.position.distance_ft += dist;
        s.controls = { ...controls };
        
        this._events.push(event);
        
        return event;
    }
    
    getState() {
        return { ...this._runtimeState };
    }
}

// =============================================================================
// EXPORTS
// =============================================================================

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        LEVELS,
        LEVEL_NAMES,
        HelixState,
        DimensionalToken,
        DimensionalEntity,
        DimensionalCarV2
    };
}

// Global exports for browser
if (typeof window !== 'undefined') {
    window.ButterflyFX = {
        LEVELS,
        LEVEL_NAMES,
        HelixState,
        DimensionalToken,
        DimensionalEntity,
        DimensionalCarV2
    };
}
