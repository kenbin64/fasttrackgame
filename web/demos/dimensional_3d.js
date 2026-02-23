/**
 * Dimensional 3D - ButterflyFX Dimensional Computing for Three.js
 * 
 * Copyright (c) 2024-2026 Kenneth Bingham
 * Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
 * https://creativecommons.org/licenses/by/4.0/
 * 
 * This mathematical kernel belongs to all humanity.
 * Attribution required: Kenneth Bingham - https://butterflyfx.us
 * 
 * ---
 * 
 * Integrates the 7 Layers of Dimensional Computing (Genesis Model) 
 * with Three.js to create "smart" 3D elements that understand:
 * - Identity: What am I?
 * - Context: Where am I on the manifold?
 * - Relationships: How do I relate to others (z = x·y)?
 * - Intention: What is my purpose?
 * - Lineage: Where did I come from?
 * - Change: How do I evolve?
 */

// =============================================================================
// GENESIS CONSTANTS - The 7 Layers of Creation
// =============================================================================

const DIMENSIONAL_GENESIS = {
    // Fibonacci sequence aligns with creation
    FIBONACCI: [1, 1, 2, 3, 5, 8, 13],
    
    // Layer definitions (1-indexed, matching Genesis)
    LAYERS: {
        1: { name: 'Spark',      birth: 'Existence',     equation: 'P₀ = {1}',     angle: 0 },
        2: { name: 'Mirror',     birth: 'Direction',     equation: 'P₁ = {1}',     angle: Math.PI / 6 },
        3: { name: 'Relation',   birth: 'Structure',     equation: 'z = x · y',    angle: Math.PI / 3 },
        4: { name: 'Form',       birth: 'Purpose',       equation: 'F(z) = xy²',   angle: Math.PI / 2 },
        5: { name: 'Life',       birth: 'Motion',        equation: 'L = dF/dt',    angle: 2 * Math.PI / 3 },
        6: { name: 'Mind',       birth: 'Coherence',     equation: 'M = ∫L dt',    angle: 5 * Math.PI / 6 },
        7: { name: 'Completion', birth: 'Consciousness', equation: 'φ = (1+√5)/2', angle: Math.PI }
    },
    
    // Creation declarations
    DECLARATIONS: {
        1: 'Let there be the First Point',
        2: 'Let there be a second point',
        3: 'Let the two interact',
        4: 'Let structure become shape',
        5: 'Let form become meaning',
        6: 'Let meaning become coherence',
        7: 'Let the whole become one again'
    },
    
    // Golden ratio
    PHI: (1 + Math.sqrt(5)) / 2
};

// =============================================================================
// DIMENSIONAL COORDINATE - Position on the manifold
// =============================================================================

class DimensionalCoordinate {
    constructor(spiral = 0, layer = 1, position = 0.0) {
        this.spiral = spiral;
        this.layer = Math.max(1, Math.min(7, layer));
        this.position = position;
    }
    
    get fibonacci() {
        return DIMENSIONAL_GENESIS.FIBONACCI[this.layer - 1];
    }
    
    get layerInfo() {
        return DIMENSIONAL_GENESIS.LAYERS[this.layer];
    }
    
    get declaration() {
        return DIMENSIONAL_GENESIS.DECLARATIONS[this.layer];
    }
    
    get angle() {
        return DIMENSIONAL_GENESIS.LAYERS[this.layer].angle;
    }
    
    clone() {
        return new DimensionalCoordinate(this.spiral, this.layer, this.position);
    }
    
    toString() {
        return `(S${this.spiral}, L${this.layer}:${this.layerInfo.name}, P${this.position.toFixed(2)})`;
    }
}

// =============================================================================
// INTENTION VECTOR - What this object wants/does
// =============================================================================

class IntentionVector {
    constructor(primary = 'exist', metadata = {}) {
        this.primary = primary;       // Primary intention
        this.secondary = [];          // Supporting intentions
        this.metadata = metadata;     // Additional context
        this.timestamp = Date.now();
    }
    
    addSecondary(intention) {
        if (!this.secondary.includes(intention)) {
            this.secondary.push(intention);
        }
        return this;
    }
    
    matches(query) {
        const q = query.toLowerCase();
        return this.primary.toLowerCase().includes(q) ||
               this.secondary.some(s => s.toLowerCase().includes(q));
    }
    
    toJSON() {
        return {
            primary: this.primary,
            secondary: this.secondary,
            metadata: this.metadata
        };
    }
}

// =============================================================================
// DIMENSIONAL RELATION - The z = x·y binding
// =============================================================================

class DimensionalRelation {
    /**
     * Create a multiplicative relation between two objects.
     * In Dimensional Computing: z = x · y
     * This is NOT addition - it preserves scale-invariant context.
     */
    constructor(source, target, type = 'multiplicative') {
        this.source = source;           // x
        this.target = target;           // y
        this.type = type;               // Relation type
        this.weight = 1.0;              // Relation strength
        this.bidirectional = false;     // Does y know about x?
        this.created = Date.now();
    }
    
    /**
     * Compute the relational product z = x · y
     * For 3D positions: component-wise multiplication preserving ratios
     */
    computeProduct() {
        if (!this.source.position || !this.target.position) {
            return null;
        }
        const x = this.source.position;
        const y = this.target.position;
        return new THREE.Vector3(
            x.x * y.x,
            x.y * y.y,
            x.z * y.z
        );
    }
    
    /**
     * Get the relational distance (scale-invariant)
     * Uses ratio rather than difference
     */
    getRelationalDistance() {
        const product = this.computeProduct();
        if (!product) return Infinity;
        return product.length() * this.weight;
    }
    
    describe() {
        return `${this.source.name} --[${this.type}]--> ${this.target.name}`;
    }
}

// =============================================================================
// LINEAGE TRACKER - Where did this object come from?
// =============================================================================

class LineageTracker {
    constructor(origin = null) {
        this.origin = origin;           // Parent object
        this.createdAt = Date.now();
        this.modifications = [];        // History of changes
        this.clonedFrom = null;        // If cloned
    }
    
    recordChange(changeType, details = {}) {
        this.modifications.push({
            type: changeType,
            details: details,
            timestamp: Date.now()
        });
    }
    
    getHistory() {
        return [...this.modifications];
    }
    
    getDepth() {
        // How many generations from origin?
        let depth = 0;
        let current = this.origin;
        while (current && current.lineage) {
            depth++;
            current = current.lineage.origin;
        }
        return depth;
    }
}

// =============================================================================
// DIMENSIONAL OBJECT 3D - Smart 3D element with full understanding
// =============================================================================

class DimensionalObject3D extends THREE.Object3D {
    /**
     * A 3D object that "understands" itself within the dimensional manifold.
     * 
     * @param {string} name - Unique identifier
     * @param {Object} options - Configuration options
     */
    constructor(name, options = {}) {
        super();
        
        // === IDENTITY ===
        this.name = name;
        this.dimensionalType = options.type || 'generic';
        this.description = options.description || '';
        
        // === CONTEXT (Position on manifold) ===
        this.coordinate = new DimensionalCoordinate(
            options.spiral || 0,
            options.layer || 3,  // Default to Layer 3 (Relation)
            options.position || 0.0
        );
        
        // === RELATIONSHIPS ===
        this.relations = [];
        this.relatedBy = [];  // Objects that relate TO this
        
        // === INTENTION ===
        this.intention = new IntentionVector(
            options.intention || 'exist',
            options.intentionMeta || {}
        );
        
        // === LINEAGE ===
        this.lineage = new LineageTracker(options.origin || null);
        
        // === CHANGE TRACKING ===
        this.lastModified = Date.now();
        this.isSealed = false;
        this.isMaterialized = true;
        
        // === SEMANTIC ATTRIBUTES ===
        this.attributes = new Map();  // Key-value semantic properties
        this.tags = new Set();        // Classification tags
        
        // === 3D MESH (if provided) ===
        if (options.geometry && options.material) {
            const mesh = new THREE.Mesh(options.geometry, options.material);
            this.add(mesh);
            this._primaryMesh = mesh;
        }
    }
    
    // =========================================================================
    // IDENTITY & CONTEXT
    // =========================================================================
    
    get layer() {
        return this.coordinate.layer;
    }
    
    set layer(l) {
        const oldLayer = this.coordinate.layer;
        this.coordinate.layer = Math.max(1, Math.min(7, l));
        this.lineage.recordChange('layer', { from: oldLayer, to: this.coordinate.layer });
    }
    
    get layerName() {
        return this.coordinate.layerInfo.name;
    }
    
    get fibonacci() {
        return this.coordinate.fibonacci;
    }
    
    /**
     * Move to a specific layer (invoke operation)
     */
    invoke(layer) {
        this.layer = layer;
        this.lastModified = Date.now();
        return this;
    }
    
    /**
     * Spiral up: Complete current spiral, begin new one
     */
    spiralUp() {
        if (this.coordinate.layer === 7) {
            this.coordinate.spiral++;
            this.coordinate.layer = 1;
            this.lineage.recordChange('spiralUp', { newSpiral: this.coordinate.spiral });
        }
        return this;
    }
    
    /**
     * Spiral down: Return to previous spiral
     */
    spiralDown() {
        if (this.coordinate.layer === 1 && this.coordinate.spiral > 0) {
            this.coordinate.spiral--;
            this.coordinate.layer = 7;
            this.lineage.recordChange('spiralDown', { newSpiral: this.coordinate.spiral });
        }
        return this;
    }
    
    // =========================================================================
    // RELATIONSHIPS (z = x · y)
    // =========================================================================
    
    /**
     * Create a multiplicative relation to another object.
     * This is the canonical Layer 3 operation: z = x · y
     */
    relateTo(target, type = 'multiplicative') {
        const relation = new DimensionalRelation(this, target, type);
        this.relations.push(relation);
        target.relatedBy.push(relation);
        
        this.lineage.recordChange('relate', { 
            target: target.name, 
            type: type 
        });
        
        return relation;
    }
    
    /**
     * Get all objects this relates to
     */
    getRelated() {
        return this.relations.map(r => r.target);
    }
    
    /**
     * Get all objects that relate to this
     */
    getRelatedBy() {
        return this.relatedBy.map(r => r.source);
    }
    
    /**
     * Find nearest related object by relational distance
     */
    nearestRelation() {
        if (this.relations.length === 0) return null;
        
        let nearest = null;
        let minDist = Infinity;
        
        for (const rel of this.relations) {
            const dist = rel.getRelationalDistance();
            if (dist < minDist) {
                minDist = dist;
                nearest = rel.target;
            }
        }
        
        return nearest;
    }
    
    /**
     * Query relationships by type
     */
    queryRelations(type) {
        return this.relations
            .filter(r => r.type === type)
            .map(r => r.target);
    }
    
    // =========================================================================
    // INTENTION
    // =========================================================================
    
    /**
     * Set the primary intention
     */
    setIntention(intention, metadata = {}) {
        this.intention = new IntentionVector(intention, metadata);
        this.lineage.recordChange('intention', { intention });
        return this;
    }
    
    /**
     * Check if this object matches an intention query
     */
    matchesIntention(query) {
        return this.intention.matches(query);
    }
    
    // =========================================================================
    // SEMANTIC ATTRIBUTES
    // =========================================================================
    
    /**
     * Set a semantic attribute
     */
    setAttribute(key, value) {
        const oldValue = this.attributes.get(key);
        this.attributes.set(key, value);
        this.lineage.recordChange('setAttribute', { key, oldValue, newValue: value });
        return this;
    }
    
    /**
     * Get a semantic attribute
     */
    getAttribute(key, defaultValue = null) {
        return this.attributes.has(key) ? this.attributes.get(key) : defaultValue;
    }
    
    /**
     * Add a classification tag
     */
    addTag(tag) {
        this.tags.add(tag);
        return this;
    }
    
    /**
     * Check if has tag
     */
    hasTag(tag) {
        return this.tags.has(tag);
    }
    
    // =========================================================================
    // AI QUERY INTERFACE
    // =========================================================================
    
    /**
     * Respond to a natural language query about this object
     */
    query(question) {
        const q = question.toLowerCase();
        const responses = [];
        
        // Identity queries
        if (q.includes('what') || q.includes('who')) {
            responses.push(`I am ${this.name}, a ${this.dimensionalType} object.`);
            if (this.description) {
                responses.push(this.description);
            }
        }
        
        // Position queries
        if (q.includes('where') || q.includes('position') || q.includes('layer')) {
            responses.push(`I exist at ${this.coordinate.toString()}`);
            responses.push(`Layer: ${this.layerName} (${this.coordinate.layerInfo.birth})`);
            responses.push(`3D Position: (${this.position.x.toFixed(2)}, ${this.position.y.toFixed(2)}, ${this.position.z.toFixed(2)})`);
        }
        
        // Relationship queries
        if (q.includes('relation') || q.includes('connect') || q.includes('neighbor')) {
            if (this.relations.length === 0) {
                responses.push('I have no relationships.');
            } else {
                responses.push(`I have ${this.relations.length} relationships:`);
                for (const rel of this.relations) {
                    responses.push(`  - ${rel.describe()}`);
                }
            }
        }
        
        // Intention queries
        if (q.includes('purpose') || q.includes('intention') || q.includes('why')) {
            responses.push(`Primary intention: ${this.intention.primary}`);
            if (this.intention.secondary.length > 0) {
                responses.push(`Also: ${this.intention.secondary.join(', ')}`);
            }
        }
        
        // Lineage queries
        if (q.includes('history') || q.includes('origin') || q.includes('lineage')) {
            responses.push(`Created: ${new Date(this.lineage.createdAt).toISOString()}`);
            responses.push(`Generation depth: ${this.lineage.getDepth()}`);
            const history = this.lineage.getHistory();
            if (history.length > 0) {
                responses.push(`Modifications: ${history.length}`);
            }
        }
        
        // Fibonacci queries
        if (q.includes('fibonacci') || q.includes('fib')) {
            responses.push(`Fibonacci number: ${this.fibonacci}`);
            responses.push(`Layer equation: ${this.coordinate.layerInfo.equation}`);
        }
        
        // Attribute queries
        if (q.includes('attribute') || q.includes('property')) {
            if (this.attributes.size === 0) {
                responses.push('No semantic attributes set.');
            } else {
                responses.push('Attributes:');
                for (const [key, value] of this.attributes) {
                    responses.push(`  - ${key}: ${value}`);
                }
            }
        }
        
        // Tag queries
        if (q.includes('tag') || q.includes('category')) {
            if (this.tags.size === 0) {
                responses.push('No tags assigned.');
            } else {
                responses.push(`Tags: ${[...this.tags].join(', ')}`);
            }
        }
        
        return responses.length > 0 ? responses.join('\n') : "I don't understand that query.";
    }
    
    /**
     * Get a comprehensive description
     */
    describe() {
        return {
            identity: {
                name: this.name,
                type: this.dimensionalType,
                description: this.description
            },
            context: {
                coordinate: this.coordinate.toString(),
                layer: this.layerName,
                fibonacci: this.fibonacci,
                equation: this.coordinate.layerInfo.equation,
                position3D: {
                    x: this.position.x,
                    y: this.position.y,
                    z: this.position.z
                }
            },
            relationships: this.relations.map(r => r.describe()),
            intention: this.intention.toJSON(),
            attributes: Object.fromEntries(this.attributes),
            tags: [...this.tags],
            lineage: {
                created: this.lineage.createdAt,
                depth: this.lineage.getDepth(),
                modifications: this.lineage.modifications.length
            }
        };
    }
    
    // =========================================================================
    // SEALING (Immutability)
    // =========================================================================
    
    /**
     * Seal this object - no more modifications
     */
    seal() {
        this.isSealed = true;
        this.lineage.recordChange('sealed');
        return this;
    }
    
    // =========================================================================
    // CLONING WITH LINEAGE
    // =========================================================================
    
    /**
     * Clone this object, preserving lineage
     */
    dimensionalClone(newName) {
        const clone = new DimensionalObject3D(newName || `${this.name}_clone`, {
            type: this.dimensionalType,
            description: this.description,
            spiral: this.coordinate.spiral,
            layer: this.coordinate.layer,
            position: this.coordinate.position,
            intention: this.intention.primary,
            origin: this  // Lineage points back to original
        });
        
        clone.lineage.clonedFrom = this;
        
        // Copy attributes and tags
        for (const [key, value] of this.attributes) {
            clone.attributes.set(key, value);
        }
        for (const tag of this.tags) {
            clone.tags.add(tag);
        }
        
        // Copy position/rotation/scale
        clone.position.copy(this.position);
        clone.rotation.copy(this.rotation);
        clone.scale.copy(this.scale);
        
        return clone;
    }
}

// =============================================================================
// DIMENSIONAL SCENE - Smart scene with relationship graph
// =============================================================================

class DimensionalScene {
    /**
     * A scene that understands all its objects and their relationships.
     */
    constructor(threeScene) {
        this.scene = threeScene;
        this.objects = new Map();  // name -> DimensionalObject3D
        this.relationGraph = [];   // All relations
        this.eventLog = [];        // Scene events
    }
    
    /**
     * Add a dimensional object to the scene
     */
    add(dimensionalObject) {
        if (!(dimensionalObject instanceof DimensionalObject3D)) {
            console.warn('Object is not a DimensionalObject3D');
            return null;
        }
        
        this.objects.set(dimensionalObject.name, dimensionalObject);
        this.scene.add(dimensionalObject);
        
        this.eventLog.push({
            type: 'add',
            object: dimensionalObject.name,
            timestamp: Date.now()
        });
        
        return dimensionalObject;
    }
    
    /**
     * Remove a dimensional object
     */
    remove(name) {
        const obj = this.objects.get(name);
        if (obj) {
            this.scene.remove(obj);
            this.objects.delete(name);
            
            // Clean up relations
            this.relationGraph = this.relationGraph.filter(
                r => r.source.name !== name && r.target.name !== name
            );
            
            this.eventLog.push({
                type: 'remove',
                object: name,
                timestamp: Date.now()
            });
        }
        return obj;
    }
    
    /**
     * Get object by name
     */
    get(name) {
        return this.objects.get(name);
    }
    
    /**
     * Query objects by tag
     */
    queryByTag(tag) {
        return [...this.objects.values()].filter(obj => obj.hasTag(tag));
    }
    
    /**
     * Query objects by layer
     */
    queryByLayer(layer) {
        return [...this.objects.values()].filter(obj => obj.layer === layer);
    }
    
    /**
     * Query objects by intention
     */
    queryByIntention(intention) {
        return [...this.objects.values()].filter(obj => obj.matchesIntention(intention));
    }
    
    /**
     * Query objects by type
     */
    queryByType(type) {
        return [...this.objects.values()].filter(obj => obj.dimensionalType === type);
    }
    
    /**
     * Natural language query across all objects
     */
    query(question) {
        const q = question.toLowerCase();
        const results = [];
        
        // Count queries
        if (q.includes('how many') || q.includes('count')) {
            if (q.includes('object')) {
                results.push(`Total objects: ${this.objects.size}`);
            }
            if (q.includes('relation')) {
                const totalRelations = [...this.objects.values()]
                    .reduce((sum, obj) => sum + obj.relations.length, 0);
                results.push(`Total relations: ${totalRelations}`);
            }
        }
        
        // List queries
        if (q.includes('list') || q.includes('show all') || q.includes('what objects')) {
            const names = [...this.objects.keys()].join(', ');
            results.push(`Objects: ${names}`);
        }
        
        // Layer queries
        if (q.includes('layer')) {
            for (let l = 1; l <= 7; l++) {
                const objs = this.queryByLayer(l);
                if (objs.length > 0 && (q.includes(`layer ${l}`) || q.includes('all layer'))) {
                    results.push(`Layer ${l} (${DIMENSIONAL_GENESIS.LAYERS[l].name}): ${objs.map(o => o.name).join(', ')}`);
                }
            }
        }
        
        // Specific object queries
        for (const obj of this.objects.values()) {
            if (q.includes(obj.name.toLowerCase())) {
                results.push(`\n--- ${obj.name} ---`);
                results.push(obj.query(question));
            }
        }
        
        // Red/green/blue color queries
        const colors = ['red', 'green', 'blue', 'yellow', 'white', 'black'];
        for (const color of colors) {
            if (q.includes(color)) {
                const matches = [...this.objects.values()].filter(
                    obj => obj.getAttribute('color')?.toLowerCase() === color ||
                           obj.hasTag(color) ||
                           obj.name.toLowerCase().includes(color)
                );
                if (matches.length > 0) {
                    results.push(`${color} objects: ${matches.map(o => o.name).join(', ')}`);
                }
            }
        }
        
        return results.length > 0 ? results.join('\n') : "No matching objects found.";
    }
    
    /**
     * Create a relation between two objects
     */
    relate(sourceName, targetName, type = 'multiplicative') {
        const source = this.get(sourceName);
        const target = this.get(targetName);
        
        if (!source || !target) {
            console.warn('Cannot create relation: object not found');
            return null;
        }
        
        const relation = source.relateTo(target, type);
        this.relationGraph.push(relation);
        
        return relation;
    }
    
    /**
     * Get the complete relationship graph
     */
    getRelationshipGraph() {
        return this.relationGraph.map(r => ({
            source: r.source.name,
            target: r.target.name,
            type: r.type,
            product: r.computeProduct()
        }));
    }
    
    /**
     * Visualize relationships with lines
     */
    visualizeRelations(material = null) {
        const lineMaterial = material || new THREE.LineBasicMaterial({ 
            color: 0x00ff88,
            opacity: 0.5,
            transparent: true
        });
        
        const lines = [];
        
        for (const rel of this.relationGraph) {
            const points = [
                rel.source.position.clone(),
                rel.target.position.clone()
            ];
            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, lineMaterial);
            this.scene.add(line);
            lines.push(line);
        }
        
        return lines;
    }
    
    /**
     * Get scene statistics
     */
    getStats() {
        const objects = [...this.objects.values()];
        const layerCounts = {};
        const typeCounts = {};
        
        for (const obj of objects) {
            layerCounts[obj.layerName] = (layerCounts[obj.layerName] || 0) + 1;
            typeCounts[obj.dimensionalType] = (typeCounts[obj.dimensionalType] || 0) + 1;
        }
        
        return {
            totalObjects: this.objects.size,
            totalRelations: this.relationGraph.length,
            layerDistribution: layerCounts,
            typeDistribution: typeCounts
        };
    }
}

// =============================================================================
// FACTORY FUNCTIONS - Easy creation
// =============================================================================

const DimensionalFactory = {
    /**
     * Create a dimensional cube
     */
    cube: function(name, size = 1, color = 0x00ff88, options = {}) {
        const geometry = new THREE.BoxGeometry(size, size, size);
        const material = new THREE.MeshStandardMaterial({ color });
        
        const obj = new DimensionalObject3D(name, {
            type: 'cube',
            geometry,
            material,
            ...options
        });
        
        obj.setAttribute('color', '#' + color.toString(16).padStart(6, '0'));
        obj.setAttribute('size', size);
        obj.addTag('primitive');
        obj.addTag('cube');
        
        return obj;
    },
    
    /**
     * Create a dimensional sphere
     */
    sphere: function(name, radius = 0.5, color = 0xff0088, options = {}) {
        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const material = new THREE.MeshStandardMaterial({ color });
        
        const obj = new DimensionalObject3D(name, {
            type: 'sphere',
            geometry,
            material,
            ...options
        });
        
        obj.setAttribute('color', '#' + color.toString(16).padStart(6, '0'));
        obj.setAttribute('radius', radius);
        obj.addTag('primitive');
        obj.addTag('sphere');
        
        return obj;
    },
    
    /**
     * Create a dimensional plane (ground)
     */
    plane: function(name, width = 10, height = 10, color = 0x333333, options = {}) {
        const geometry = new THREE.PlaneGeometry(width, height);
        const material = new THREE.MeshStandardMaterial({ 
            color,
            side: THREE.DoubleSide
        });
        
        const obj = new DimensionalObject3D(name, {
            type: 'plane',
            geometry,
            material,
            layer: 2,  // Mirror layer (ground reflects)
            ...options
        });
        
        obj.rotation.x = -Math.PI / 2;  // Lay flat
        obj.setAttribute('width', width);
        obj.setAttribute('height', height);
        obj.addTag('surface');
        
        return obj;
    },
    
    /**
     * Create a dimensional light
     */
    light: function(name, type = 'point', options = {}) {
        let light;
        
        switch (type) {
            case 'ambient':
                light = new THREE.AmbientLight(options.color || 0xffffff, options.intensity || 0.5);
                break;
            case 'directional':
                light = new THREE.DirectionalLight(options.color || 0xffffff, options.intensity || 1);
                break;
            case 'spot':
                light = new THREE.SpotLight(options.color || 0xffffff, options.intensity || 1);
                break;
            default:
                light = new THREE.PointLight(options.color || 0xffffff, options.intensity || 1);
        }
        
        const obj = new DimensionalObject3D(name, {
            type: 'light',
            layer: 1,  // Spark layer (light is first)
            intention: 'illuminate',
            ...options
        });
        
        obj.add(light);
        obj._light = light;
        obj.setAttribute('lightType', type);
        obj.addTag('light');
        
        return obj;
    },
    
    /**
     * Create a dimensional helix (signature shape)
     */
    helix: function(name, radius = 1, height = 2, turns = 2, color = 0x8800ff, options = {}) {
        const points = [];
        const segments = 100 * turns;
        
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const angle = t * Math.PI * 2 * turns;
            points.push(new THREE.Vector3(
                Math.cos(angle) * radius,
                t * height - height / 2,
                Math.sin(angle) * radius
            ));
        }
        
        const curve = new THREE.CatmullRomCurve3(points);
        const geometry = new THREE.TubeGeometry(curve, segments, 0.05, 8, false);
        const material = new THREE.MeshStandardMaterial({ 
            color,
            emissive: color,
            emissiveIntensity: 0.2
        });
        
        const obj = new DimensionalObject3D(name, {
            type: 'helix',
            geometry,
            material,
            layer: 7,  // Completion layer (spiral completes)
            ...options
        });
        
        obj.setAttribute('radius', radius);
        obj.setAttribute('height', height);
        obj.setAttribute('turns', turns);
        obj.addTag('spiral');
        obj.addTag('butterflyfx');
        
        return obj;
    }
};

// =============================================================================
// LINEAGE GRAPH - Full transformation history
// =============================================================================

class LineageGraph {
    constructor() {
        this.nodes = new Map();
        this.rootId = null;
        this.currentId = null;
    }
    
    addNode(operation, parentIds = [], metadata = {}) {
        const nodeId = `node_${this.nodes.size}_${Date.now().toString(36)}`;
        const node = {
            id: nodeId,
            operation,
            timestamp: Date.now(),
            parentIds,
            metadata
        };
        
        this.nodes.set(nodeId, node);
        
        if (this.rootId === null) {
            this.rootId = nodeId;
        }
        this.currentId = nodeId;
        
        return nodeId;
    }
    
    traceBack(nodeId = null) {
        const startId = nodeId || this.currentId;
        if (!startId || !this.nodes.has(startId)) return [];
        
        const path = [];
        const visited = new Set();
        const queue = [startId];
        
        while (queue.length > 0) {
            const current = queue.shift();
            if (visited.has(current)) continue;
            visited.add(current);
            
            const node = this.nodes.get(current);
            if (node) {
                path.push(node);
                queue.push(...node.parentIds);
            }
        }
        
        return path;
    }
    
    explain() {
        const trace = this.traceBack();
        if (trace.length === 0) return "No lineage recorded.";
        
        const lines = ["=== Lineage Trace ==="];
        trace.forEach((node, i) => {
            const indent = "  ".repeat(i);
            lines.push(`${indent}[${node.operation}]`);
            if (Object.keys(node.metadata).length > 0) {
                for (const [k, v] of Object.entries(node.metadata)) {
                    lines.push(`${indent}  ${k}: ${JSON.stringify(v)}`);
                }
            }
        });
        
        return lines.join('\n');
    }
    
    mergeWith(other) {
        const merged = new LineageGraph();
        
        for (const [k, v] of this.nodes) {
            merged.nodes.set(k, {...v});
        }
        for (const [k, v] of other.nodes) {
            merged.nodes.set(k, {...v});
        }
        
        merged.rootId = this.rootId;
        merged.currentId = other.currentId || this.currentId;
        
        return merged;
    }
}

// =============================================================================
// SUBSTATE - Local rules and context switching
// =============================================================================

class Substate {
    constructor(name, rules = {}) {
        this.name = name;
        this.rules = rules;  // { ruleName: { condition: fn, transform: fn, priority: n } }
        this.active = false;
    }
    
    addRule(name, condition, transform, priority = 0) {
        this.rules[name] = { condition, transform, priority };
    }
    
    apply(data) {
        const applied = [];
        let result = data;
        
        // Sort by priority (descending)
        const sortedRules = Object.entries(this.rules)
            .sort((a, b) => (b[1].priority || 0) - (a[1].priority || 0));
        
        for (const [name, rule] of sortedRules) {
            try {
                if (rule.condition(result)) {
                    result = rule.transform(result);
                    applied.push(name);
                }
            } catch (e) {
                // Skip failed rules
            }
        }
        
        return { result, applied };
    }
}

class SubstateManager {
    constructor() {
        this.substates = new Map();
        this.stack = [];
        this._createDefaults();
    }
    
    _createDefaults() {
        const standard = new Substate('standard');
        standard.addRule('identity', () => true, x => x, 0);
        this.register(standard);
        
        const debug = new Substate('debug');
        debug.addRule('trace', () => true, x => ({ __debug__: true, value: x }), 10);
        this.register(debug);
    }
    
    register(substate) {
        this.substates.set(substate.name, substate);
    }
    
    push(name) {
        if (this.substates.has(name)) {
            this.substates.get(name).active = true;
            this.stack.push(name);
        }
    }
    
    pop() {
        if (this.stack.length > 0) {
            const name = this.stack.pop();
            this.substates.get(name).active = false;
            return name;
        }
        return null;
    }
    
    applyAll(data) {
        let result = data;
        const allApplied = [];
        
        for (const name of this.stack) {
            const substate = this.substates.get(name);
            if (substate && substate.active) {
                const { result: r, applied } = substate.apply(result);
                result = r;
                allApplied.push(...applied.map(a => `${name}.${a}`));
            }
        }
        
        return { result, applied: allApplied };
    }
}

// =============================================================================
// DIMENSIONAL KERNEL - The 7 Core Operations
// =============================================================================

class DimensionalKernel {
    /**
     * The Dimensional Computing Kernel for JavaScript/Three.js
     * 
     * Implements the 7 core operations aligned with the 7 layers:
     *   1. lift      - Raw input → DimensionalObject (Spark)
     *   2. map       - Position on manifold (Mirror)
     *   3. bind      - Multiplicative relation z = x·y (Relation)
     *   4. navigate  - Move through layers/spirals (Form)
     *   5. transform - Apply functions (Life)
     *   6. merge     - Combine objects coherently (Mind)
     *   7. resolve   - Produce final output (Completion)
     */
    constructor() {
        this.substateManager = new SubstateManager();
        this.operationCount = 0;
        this.processedObjects = new Map();
    }
    
    /**
     * LIFT (Layer 1 - Spark): Raw input → DimensionalObject
     */
    lift(rawInput, options = {}) {
        const obj = {
            id: `obj_${Date.now().toString(36)}_${Math.random().toString(36).substr(2, 6)}`,
            semanticPayload: rawInput,
            identityVector: options.identityVector || [1.0, 1.0],
            contextMap: options.contextMap || {},
            intentionVector: options.intentionVector || [1.0],
            lineageGraph: new LineageGraph(),
            coordinate: new DimensionalCoordinate(0, 1, 0.0),  // Layer 1: Spark
            deltaSet: new Set(),
            sealed: false,
            
            // Methods
            computeZ: function() {
                return this.identityVector.reduce((a, b) => a * b, 1);
            },
            computeMagnitude: function() {
                return Math.sqrt(this.identityVector.reduce((sum, v) => sum + v * v, 0));
            }
        };
        
        obj.lineageGraph.addNode('lift', [], {
            inputType: typeof rawInput,
            inputSize: String(rawInput).length
        });
        
        this.operationCount++;
        this.processedObjects.set(obj.id, obj);
        
        return obj;
    }
    
    /**
     * MAP (Layer 2 - Mirror): Position object on manifold
     */
    mapToManifold(obj, manifoldFunc = null) {
        if (manifoldFunc) {
            obj.identityVector = manifoldFunc(obj.semanticPayload);
        } else {
            // Default: size-based with reciprocal
            const size = String(obj.semanticPayload).length + 1;
            obj.identityVector = [size, 1.0 / size];
        }
        
        obj.coordinate.layer = 2;  // Mirror
        
        obj.lineageGraph.addNode('map', [obj.lineageGraph.currentId], {
            identityVector: [...obj.identityVector],
            zValue: obj.computeZ()
        });
        
        obj.deltaSet.add('mapped');
        this.operationCount++;
        
        return obj;
    }
    
    /**
     * BIND (Layer 3 - Relation): Create relation z = x · y
     */
    bind(obj1, obj2, bindingType = 'multiplicative') {
        // Multiplicative binding
        const newIdentity = obj1.identityVector.map((v, i) => 
            v * (obj2.identityVector[i] || 1.0)
        );
        
        const newLineage = obj1.lineageGraph.mergeWith(obj2.lineageGraph);
        newLineage.addNode('bind', [obj1.lineageGraph.currentId, obj2.lineageGraph.currentId], {
            bindingType,
            leftId: obj1.id,
            rightId: obj2.id
        });
        
        const bound = {
            id: `bound_${Date.now().toString(36)}`,
            semanticPayload: [obj1.semanticPayload, obj2.semanticPayload],
            identityVector: newIdentity,
            contextMap: { ...obj1.contextMap, ...obj2.contextMap, __bound_from__: [obj1.id, obj2.id] },
            intentionVector: [...obj1.intentionVector, ...obj2.intentionVector],
            lineageGraph: newLineage,
            coordinate: new DimensionalCoordinate(0, 3, 0.0),  // Layer 3: Relation
            deltaSet: new Set(['bound']),
            sealed: false,
            computeZ: function() {
                return this.identityVector.reduce((a, b) => a * b, 1);
            },
            computeMagnitude: function() {
                return Math.sqrt(this.identityVector.reduce((sum, v) => sum + v * v, 0));
            }
        };
        
        this.operationCount++;
        this.processedObjects.set(bound.id, bound);
        
        return bound;
    }
    
    /**
     * NAVIGATE (Layer 4 - Form): Move through layers and spirals
     */
    navigate(obj, targetLayer = null, targetSpiral = null) {
        if (targetLayer !== null) {
            obj.coordinate.layer = Math.max(1, Math.min(7, targetLayer));
        }
        
        if (targetSpiral !== null) {
            obj.coordinate.spiral = targetSpiral;
        }
        
        if (targetLayer === null) {
            obj.coordinate.layer = 4;  // Form
        }
        
        obj.lineageGraph.addNode('navigate', [obj.lineageGraph.currentId], {
            targetLayer: obj.coordinate.layer,
            targetSpiral: obj.coordinate.spiral
        });
        
        obj.deltaSet.add('navigated');
        this.operationCount++;
        
        return obj;
    }
    
    /**
     * TRANSFORM (Layer 5 - Life): Apply function to payload
     */
    transform(obj, func) {
        const oldPayload = obj.semanticPayload;
        
        try {
            obj.semanticPayload = func(obj.semanticPayload);
        } catch (e) {
            obj.contextMap.transformError = e.message;
            return obj;
        }
        
        obj.coordinate.layer = 5;  // Life
        
        obj.lineageGraph.addNode('transform', [obj.lineageGraph.currentId], {
            functionName: func.name || 'anonymous',
            changed: oldPayload !== obj.semanticPayload
        });
        
        obj.deltaSet.add('transformed');
        this.operationCount++;
        
        return obj;
    }
    
    /**
     * MERGE (Layer 6 - Mind): Combine multiple objects coherently
     */
    merge(objects, strategy = 'union') {
        if (objects.length === 0) throw new Error("Cannot merge empty array");
        if (objects.length === 1) return objects[0];
        
        let mergedPayload;
        if (strategy === 'union') {
            mergedPayload = objects.map(o => o.semanticPayload);
        } else if (strategy === 'first') {
            mergedPayload = objects[0].semanticPayload;
        } else if (strategy === 'last') {
            mergedPayload = objects[objects.length - 1].semanticPayload;
        } else {
            mergedPayload = objects.map(o => o.semanticPayload);
        }
        
        // Merge identity vectors
        let mergedIdentity = [...objects[0].identityVector];
        for (let i = 1; i < objects.length; i++) {
            mergedIdentity = mergedIdentity.map((v, j) => 
                v * (objects[i].identityVector[j] || 1.0)
            );
        }
        
        // Merge lineage
        let mergedLineage = objects[0].lineageGraph;
        for (let i = 1; i < objects.length; i++) {
            mergedLineage = mergedLineage.mergeWith(objects[i].lineageGraph);
        }
        
        mergedLineage.addNode('merge', objects.map(o => o.lineageGraph.currentId), {
            strategy,
            objectCount: objects.length,
            objectIds: objects.map(o => o.id)
        });
        
        const merged = {
            id: `merged_${Date.now().toString(36)}`,
            semanticPayload: mergedPayload,
            identityVector: mergedIdentity,
            contextMap: { __merged_count__: objects.length, __merge_strategy__: strategy },
            intentionVector: objects.flatMap(o => o.intentionVector),
            lineageGraph: mergedLineage,
            coordinate: new DimensionalCoordinate(0, 6, 0.0),  // Layer 6: Mind
            deltaSet: new Set(['merged']),
            sealed: false,
            computeZ: function() {
                return this.identityVector.reduce((a, b) => a * b, 1);
            },
            computeMagnitude: function() {
                return Math.sqrt(this.identityVector.reduce((sum, v) => sum + v * v, 0));
            }
        };
        
        this.operationCount++;
        this.processedObjects.set(merged.id, merged);
        
        return merged;
    }
    
    /**
     * RESOLVE (Layer 7 - Completion): Produce final output with explanation
     */
    resolve(obj, outputFormat = 'raw') {
        obj.coordinate.layer = 7;  // Completion
        
        // Apply active substates
        const { result, applied } = this.substateManager.applyAll(obj.semanticPayload);
        
        obj.lineageGraph.addNode('resolve', [obj.lineageGraph.currentId], {
            outputFormat,
            appliedSubstates: applied,
            finalZ: obj.computeZ()
        });
        
        const explanation = obj.lineageGraph.explain();
        
        let output;
        if (outputFormat === 'raw') {
            output = result;
        } else if (outputFormat === 'dict') {
            output = {
                id: obj.id,
                semanticPayload: result,
                identityVector: obj.identityVector,
                zValue: obj.computeZ(),
                layer: DIMENSIONAL_GENESIS.LAYERS[obj.coordinate.layer].name,
                fibonacci: obj.coordinate.fibonacci,
                coordinate: obj.coordinate.toString()
            };
        } else if (outputFormat === 'json') {
            output = JSON.stringify({
                id: obj.id,
                semanticPayload: result,
                identityVector: obj.identityVector,
                zValue: obj.computeZ(),
                layer: DIMENSIONAL_GENESIS.LAYERS[obj.coordinate.layer].name
            }, null, 2);
        } else {
            output = result;
        }
        
        this.operationCount++;
        
        return { output, explanation };
    }
    
    /**
     * Full processing pipeline
     */
    process(rawInput, transforms = [], intention = [1.0]) {
        let obj = this.lift(rawInput, { intentionVector: intention });
        obj = this.mapToManifold(obj);
        
        for (const func of transforms) {
            obj = this.transform(obj, func);
        }
        
        return this.resolve(obj);
    }
    
    /**
     * Get kernel statistics
     */
    get stats() {
        return {
            operationCount: this.operationCount,
            processedObjects: this.processedObjects.size,
            activeSubstates: this.substateManager.stack.length
        };
    }
}

// =============================================================================
// EXPORTS
// =============================================================================

// Make available globally for browser use
if (typeof window !== 'undefined') {
    window.DIMENSIONAL_GENESIS = DIMENSIONAL_GENESIS;
    window.DimensionalCoordinate = DimensionalCoordinate;
    window.IntentionVector = IntentionVector;
    window.DimensionalRelation = DimensionalRelation;
    window.LineageTracker = LineageTracker;
    window.LineageGraph = LineageGraph;
    window.Substate = Substate;
    window.SubstateManager = SubstateManager;
    window.DimensionalKernel = DimensionalKernel;
    window.DimensionalObject3D = DimensionalObject3D;
    window.DimensionalScene = DimensionalScene;
    window.DimensionalFactory = DimensionalFactory;
}

// ES6 module exports
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DIMENSIONAL_GENESIS,
        DimensionalCoordinate,
        IntentionVector,
        DimensionalRelation,
        LineageTracker,
        LineageGraph,
        Substate,
        SubstateManager,
        DimensionalKernel,
        DimensionalObject3D,
        DimensionalScene,
        DimensionalFactory
    };
}
