/**
 * SceneNode - Pure Data Container for Scene Objects
 * 
 * Following Universal Design Philosophy:
 * - Geometric Beauty: Clean data structure with mathematical elegance
 * - Separation of Concerns: ZERO rendering logic - pure data only
 * - Single Responsibility: Only manages scene object state and hierarchy
 * - Domain Fidelity: Reflects essential scene graph relationships
 * 
 * CRITICAL PRINCIPLE: Scene nodes are DATA CONTAINERS ONLY
 * - NO rendering logic
 * - NO Three.js object creation
 * - NO material management
 * - ONLY state management and hierarchy
 */

// Browser-compatible EventEmitter implementation
class EventEmitter {
    constructor() {
        this._events = {};
    }
    
    on(event, listener) {
        if (!this._events[event]) {
            this._events[event] = [];
        }
        this._events[event].push(listener);
        return this;
    }
    
    emit(event, ...args) {
        if (this._events[event]) {
            this._events[event].forEach(listener => listener(...args));
        }
        return this;
    }
    
    off(event, listener) {
        if (this._events[event]) {
            this._events[event] = this._events[event].filter(l => l !== listener);
        }
        return this;
    }
    
    removeAllListeners(event) {
        if (event) {
            delete this._events[event];
        } else {
            this._events = {};
        }
        return this;
    }
}

/**
 * Pure Scene Node - Data container with zero rendering responsibilities
 * 
 * SOLID Principles:
 * - Single Responsibility: Only manages node data and hierarchy
 * - Open/Closed: Extensible through inheritance without modification
 * - Liskov Substitution: All scene nodes are interchangeable data containers
 * - Interface Segregation: Clean data-only interface
 * - Dependency Inversion: No dependencies on rendering systems
 */
export class SceneNode extends EventEmitter {
    constructor(name, type = 'SceneNode') {
        super();
        
        // Core identity (immutable after creation)
        this.id = this._generateNodeId();
        this.name = name;
        this.type = type;
        this.created = Date.now();
        
        // Hierarchy management (pure data)
        this.parent = null;
        this.children = new Map();
        
        // Transform data (computed by backend)
        this.transform = {
            position: { x: 0, y: 0, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 1, y: 1, z: 1 }
        };
        
        // Visibility and state (pure data)
        this.visible = true;
        this.enabled = true;
        this.dirty = false; // Needs backend recomputation
        
        // Node-specific data (varies by type)
        this.data = {};
        
        // Metadata for backend communication
        this.metadata = {
            lastUpdate: Date.now(),
            version: 1,
            needsBackendUpdate: false
        };
        
        console.log(`📦 SceneNode created: ${this.name} [${this.type}] - Pure data container`);
    }
    
    // =============================================================================
    // HIERARCHY MANAGEMENT - Pure Data Operations
    // =============================================================================
    
    /**
     * Add child node (pure hierarchy management)
     */
    addChild(childNode) {
        if (!(childNode instanceof SceneNode)) {
            throw new Error('Child must be a SceneNode instance');
        }
        
        if (childNode.parent) {
            childNode.parent.removeChild(childNode);
        }
        
        childNode.parent = this;
        this.children.set(childNode.id, childNode);
        
        this._markDirty();
        this.emit('childAdded', childNode);
        
        console.log(`🔗 Child added: ${childNode.name} -> ${this.name}`);
    }
    
    /**
     * Remove child node (pure hierarchy management)
     */
    removeChild(childNode) {
        const nodeId = typeof childNode === 'string' ? childNode : childNode.id;
        const child = this.children.get(nodeId);
        
        if (child) {
            child.parent = null;
            this.children.delete(nodeId);
            
            this._markDirty();
            this.emit('childRemoved', child);
            
            console.log(`🔗 Child removed: ${child.name} from ${this.name}`);
        }
    }
    
    /**
     * Get child by ID or name
     */
    getChild(identifier) {
        // Try by ID first
        if (this.children.has(identifier)) {
            return this.children.get(identifier);
        }
        
        // Try by name
        for (const child of this.children.values()) {
            if (child.name === identifier) {
                return child;
            }
        }
        
        return null;
    }
    
    /**
     * Get all children as array
     */
    getChildren() {
        return Array.from(this.children.values());
    }
    
    /**
     * Traverse hierarchy with visitor pattern
     */
    traverse(visitor, includeThis = true) {
        if (includeThis) {
            visitor(this);
        }
        
        for (const child of this.children.values()) {
            child.traverse(visitor, true);
        }
    }
    
    // =============================================================================
    // TRANSFORM MANAGEMENT - Pure Data (Computed by Backend)
    // =============================================================================
    
    /**
     * Set transform data (computed by backend)
     * NO local computation - only data storage
     */
    setTransform(transform) {
        this.transform = {
            position: { ...transform.position },
            rotation: { ...transform.rotation },
            scale: { ...transform.scale }
        };
        
        this._updateMetadata();
        this.emit('transformChanged', this.transform);
    }
    
    /**
     * Get current transform data
     */
    getTransform() {
        return { ...this.transform };
    }
    
        /**
     * Set position (data only)
     */
    setPosition(x, y, z) {
        this.transform.position = { x, y, z };
        this.markForBackendUpdate();
        this.emit('positionChanged', this.transform.position);
    }

    /**
     * Set rotation (data only)
     */
    setRotation(x, y, z) {
        this.transform.rotation = { x, y, z };
        this.markForBackendUpdate();
        this.emit('rotationChanged', this.transform.rotation);
    }

    /**
     * Set scale (data only)
     */
    setScale(x, y, z) {
        this.transform.scale = { x, y, z };
        this.markForBackendUpdate();
        this.emit('scaleChanged', this.transform.scale);
    }
    
    // =============================================================================
    // DATA MANAGEMENT - Node-Specific Data Storage
    // =============================================================================
    
    /**
     * Set node-specific data
     */
    setData(key, value) {
        this.data[key] = value;
        this.markForBackendUpdate();
        this.emit('dataChanged', key, value);
    }
    
    /**
     * Get node-specific data
     */
    getData(key) {
        return this.data[key];
    }
    
    /**
     * Get all node data
     */
    getAllData() {
        return { ...this.data };
    }
    
    /**
     * Update multiple data properties
     */
    updateData(dataObject) {
        Object.assign(this.data, dataObject);
        this._updateMetadata();
        this.emit('dataUpdated', dataObject);
    }
    
    // =============================================================================
    // STATE MANAGEMENT - Pure State Operations
    // =============================================================================
    
    /**
     * Set visibility state
     */
    setVisible(visible) {
        if (this.visible !== visible) {
            this.visible = visible;
            this._updateMetadata();
            this.emit('visibilityChanged', visible);
        }
    }
    
    /**
     * Set enabled state
     */
    setEnabled(enabled) {
        if (this.enabled !== enabled) {
            this.enabled = enabled;
            this._updateMetadata();
            this.emit('enabledChanged', enabled);
        }
    }
    
    /**
     * Check if node needs backend update
     */
    needsBackendUpdate() {
        return this.metadata.needsBackendUpdate || this.dirty;
    }
    
    /**
     * Mark node as needing backend update
     */
    markForBackendUpdate() {
        this.metadata.needsBackendUpdate = true;
        this.dirty = true;
        this.emit('backendUpdateNeeded');
    }
    
    /**
     * Mark node as updated by backend
     */
    markBackendUpdated() {
        this.metadata.needsBackendUpdate = false;
        this.dirty = false;
        this._updateMetadata();
        this.emit('backendUpdated');
    }
    
    // =============================================================================
    // SERIALIZATION - For Backend Communication
    // =============================================================================
    
    /**
     * Serialize node data for backend communication
     */
    serialize() {
        return {
            id: this.id,
            name: this.name,
            type: this.type,
            transform: this.transform,
            visible: this.visible,
            enabled: this.enabled,
            data: this.data,
            metadata: this.metadata,
            children: Array.from(this.children.values()).map(child => child.serialize())
        };
    }
    
    /**
     * Deserialize node data from backend
     */
    deserialize(serializedData) {
        // Update transform
        if (serializedData.transform) {
            this.setTransform(serializedData.transform);
        }
        
        // Update visibility and state
        if (typeof serializedData.visible === 'boolean') {
            this.setVisible(serializedData.visible);
        }
        
        if (typeof serializedData.enabled === 'boolean') {
            this.setEnabled(serializedData.enabled);
        }
        
        // Update data
        if (serializedData.data) {
            this.updateData(serializedData.data);
        }
        
        // Update metadata
        if (serializedData.metadata) {
            this.metadata = { ...this.metadata, ...serializedData.metadata };
        }
        
        this.emit('deserialized', serializedData);
    }
    
    // =============================================================================
    // UTILITY METHODS - Pure Functions
    // =============================================================================
    
    /**
     * Generate unique node ID
     */
    _generateNodeId() {
        return `node_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Mark node as dirty (needs update)
     */
    _markDirty() {
        this.dirty = true;
        this.metadata.needsBackendUpdate = true;
    }
    
    /**
     * Update metadata timestamps
     */
    _updateMetadata() {
        this.metadata.lastUpdate = Date.now();
        this.metadata.version += 1;
    }
    
    /**
     * Get node summary for debugging
     */
    getDebugInfo() {
        return {
            id: this.id,
            name: this.name,
            type: this.type,
            childCount: this.children.size,
            visible: this.visible,
            enabled: this.enabled,
            dirty: this.dirty,
            needsBackendUpdate: this.needsBackendUpdate(),
            transform: this.transform,
            dataKeys: Object.keys(this.data)
        };
    }
    
    /**
     * Clean up node (remove all references)
     */
    destroy() {
        // Remove from parent
        if (this.parent) {
            this.parent.removeChild(this);
        }
        
        // Destroy all children
        for (const child of this.children.values()) {
            child.destroy();
        }
        
        // Clear all data
        this.children.clear();
        this.data = {};
        
        // Remove all listeners
        this.removeAllListeners();
        
        console.log(`🗑️ SceneNode destroyed: ${this.name} [${this.type}]`);
    }
}

// =============================================================================
// SPECIALIZED SCENE NODE TYPES - Pure Data Containers
// =============================================================================

/**
 * MouseSceneNode - Pure data container for mouse anatomy
 * NO rendering logic - only mouse-specific data management
 */
export class MouseSceneNode extends SceneNode {
    constructor(name = "Mouse") {
        super(name, "Mouse");
        
        // Mouse-specific data structure
        this.data = {
            // Geometry data (from backend)
            vertices: null,
            faces: null,
            normals: null,
            
            // STL file information (pure data)
            stlPath: null,
            stlLoaded: false,
            
            // Landmark data (from backend)
            landmarks: {},
            landmarkTypes: [],
            landmarksDetected: false,
            landmarkDetectionInProgress: false,
            
            // Anatomical alignment state (pure data)
            anatomicallyAligned: false,
            alignmentTransform: null,
            
            // Physical properties
            length: 5.0, // cm
            scaleFactor: 1.0,
            
            // Material properties (for renderer)
            materialType: 'vertex_colored',
            colorScheme: 'anatomical',
            
            // Visibility flags
            showLandmarks: true,
            showDebugInfo: false,
            showReferenceLines: true,
            enableAnatomicalAlignment: true
        };
        
        console.log(`🐭 MouseSceneNode created: ${this.name} - Pure data container`);
    }
    
    /**
     * Set STL file path (pure data operation)
     */
    setSTLPath(stlPath) {
        this.setData('stlPath', stlPath);
        this.setData('stlLoaded', false); // Reset loaded state
        this.markForBackendUpdate();
    }
    
    /**
     * Mark STL as loaded (pure data operation)
     */
    markSTLLoaded(loaded = true) {
        this.setData('stlLoaded', loaded);
    }
    
    /**
     * Set mesh data from backend
     */
    setMeshData(vertices, faces, normals = null) {
        this.setData('vertices', vertices);
        this.setData('faces', faces);
        this.setData('normals', normals);
        this.markForBackendUpdate();
    }
    
    /**
     * Set landmarks from backend
     */
    setLandmarks(landmarks) {
        this.setData('landmarks', landmarks);
        this.setData('landmarkTypes', Object.keys(landmarks));
        this.setData('landmarksDetected', true);
        this.emit('landmarksUpdated', landmarks);
    }
    
    /**
     * Set landmark detection state (pure data)
     */
    setLandmarkDetectionState(inProgress, detected = false) {
        this.setData('landmarkDetectionInProgress', inProgress);
        this.setData('landmarksDetected', detected);
    }
    
    /**
     * Set anatomical alignment state (pure data)
     */
    setAnatomicalAlignment(alignmentTransform, aligned = true) {
        this.setData('alignmentTransform', alignmentTransform);
        this.setData('anatomicallyAligned', aligned);
        if (alignmentTransform) {
            this.setTransform(alignmentTransform);
        }
    }
    
    /**
     * Set mouse physical properties
     */
    setMouseProperties(length, scaleFactor) {
        this.setData('length', length);
        this.setData('scaleFactor', scaleFactor);
        this.markForBackendUpdate();
    }
    
    /**
     * Get specific landmark (pure data access)
     */
    getLandmark(landmarkName) {
        const landmarks = this.getData('landmarks');
        return landmarks ? landmarks[landmarkName] : null;
    }
    
    /**
     * Check if model is loaded (pure data query)
     */
    isModelLoaded() {
        return this.getData('stlLoaded') === true;
    }
    
    /**
     * Check if landmarks are detected (pure data query)
     */
    areLandmarksDetected() {
        return this.getData('landmarksDetected') === true;
    }
    
    /**
     * Check if anatomically aligned (pure data query)
     */
    isAnatomicallyAligned() {
        return this.getData('anatomicallyAligned') === true;
    }
}

/**
 * MonitorSceneNode - Pure data container for monitor display
 * NO rendering logic - only monitor-specific data management
 */
export class MonitorSceneNode extends SceneNode {
    constructor(name = "Monitor") {
        super(name, "Monitor");
        
        // Monitor-specific data structure
        this.data = {
            // Physical dimensions
            width: 33.53,  // cm
            height: 59.69, // cm
            distance: 10.0, // cm from mouse
            
            // Display properties
            resolution: [1920, 1080],
            refreshRate: 60,
            
            // Stimulus data (from backend)
            currentStimulus: null,
            stimulusFrames: [],
            
            // Visual properties (for renderer)
            showFrame: true,
            showStimulus: true,
            opacity: 1.0
        };
        
        console.log(`🖥️ MonitorSceneNode created: ${this.name} - Pure data container`);
    }
    
    /**
     * Set monitor dimensions
     */
    setDimensions(width, height, distance) {
        this.setData('width', width);
        this.setData('height', height);
        this.setData('distance', distance);
        this.markForBackendUpdate();
    }
    
    /**
     * Set stimulus data from backend
     */
    setStimulusData(stimulusFrames) {
        this.setData('stimulusFrames', stimulusFrames);
        this.setData('currentStimulus', stimulusFrames[0] || null);
        this.emit('stimulusUpdated', stimulusFrames);
    }
}

/**
 * FloorPlanSceneNode - Pure data container for experimental floor plan
 * NO rendering logic - only floor plan-specific data management
 */
export class FloorPlanSceneNode extends SceneNode {
    constructor(name = "FloorPlan") {
        super(name, "FloorPlan");
        
        // Floor plan-specific data structure
        this.data = {
            // Room dimensions
            roomWidth: 100,  // cm
            roomDepth: 100,  // cm
            roomHeight: 50,  // cm
            
            // Table dimensions (from view_geometry.py)
            tableWidth: 10,   // cm
            tableDepth: 10,   // cm  
            tableHeight: 3,   // cm
            
            // Floor properties
            floorColor: 0x444444,
            floorOpacity: 0.8,
            
            // Table properties
            tableColor: 0x8B4513, // Brown
            tableOpacity: 1.0,
            
            // Grid properties
            showGrid: true,
            gridSize: 100,
            gridDivisions: 20,
            gridColor: 0x333333,
            
            // Axis helper properties
            showAxes: true,
            axesSize: 10
        };
        
        console.log(`🏠 FloorPlanSceneNode created: ${this.name} - Pure data container`);
    }
    
    /**
     * Set room dimensions
     */
    setRoomDimensions(width, depth, height) {
        this.setData('roomWidth', width);
        this.setData('roomDepth', depth);
        this.setData('roomHeight', height);
        this.markForBackendUpdate();
    }
    
    /**
     * Set table dimensions
     */
    setTableDimensions(width, depth, height) {
        this.setData('tableWidth', width);
        this.setData('tableDepth', depth);
        this.setData('tableHeight', height);
        this.markForBackendUpdate();
    }
    
    /**
     * Set grid properties
     */
    setGridProperties(size, divisions, color) {
        this.setData('gridSize', size);
        this.setData('gridDivisions', divisions);
        this.setData('gridColor', color);
        this.markForBackendUpdate();
    }
} 