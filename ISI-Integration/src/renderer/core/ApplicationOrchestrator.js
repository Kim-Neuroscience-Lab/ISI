/**
 * Application Orchestrator - Unified Coordination of All System Components
 * 
 * Following Universal Design Philosophy:
 * - Geometric Beauty: Elegant composition of all system components
 * - Canonical Interfaces: Single entry point for all application operations
 * - Architectural Purity: Clean separation between data, computation, and rendering
 * - Unified Ecosystem: Seamless integration of all subsystems
 * 
 * CRITICAL ARCHITECTURAL PRINCIPLE:
 * - Scene Nodes: Pure data containers
 * - Backend APIs: All computation and processing
 * - Rendering System: All visualization operations
 * - Orchestrator: Coordinates between all layers
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { SceneNode, MouseSceneNode, MonitorSceneNode, FloorPlanSceneNode } from './SceneNode.js';
import { RenderingSystem } from './RenderingSystem.js';

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
 * Application Orchestrator - Single source of truth for application coordination
 * 
 * SOLID Principles:
 * - Single Responsibility: Only coordinates between system components
 * - Open/Closed: Extensible through component registration
 * - Liskov Substitution: All components follow standard interfaces
 * - Interface Segregation: Clean contracts between layers
 * - Dependency Inversion: Depends on component abstractions
 * 
 * Separation of Concerns:
 * - Data Management: Scene graph with pure data nodes
 * - Computation: Backend APIs handle all processing
 * - Visualization: Rendering system handles all Three.js operations
 * - Coordination: This orchestrator manages the flow between layers
 */
export class ApplicationOrchestrator extends EventEmitter {
    constructor(config = {}) {
        super();
        // Core configuration
        this.config = {
            enableShadows: true,
            enableAntialiasing: true,
            backgroundColor: 0x1a1a1a,
            cameraPosition: { x: 8, y: 5, z: 8 },
            ...config
        };

        // Three.js components (will be initialized later)
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.renderingSystem = null;
        
        // No API client needed for frontend-only mode
        this.apiClient = null;

        // Scene graph (pure data)
        this.sceneGraph = new SceneNode('RootScene', 'Root');
        this.sceneNodes = new Map(); // ID -> SceneNode

        // Application state
        this.state = {
            initialized: false,
            running: false,
            backendAvailable: false,
            currentExperiment: null,
            renderLoop: null
        };

        console.log('ApplicationOrchestrator initialized - Unified system coordination');

        // Add parameter tracking
        this.parameterValues = {
            monitor: {
                orientation: 'landscape',
                width: 33.53,
                height: 59.69,
                distance: 10,
                elevation: 20,
                rotation: 0
            },
            mouse: {
                length: 7.5,
                eyeHeight: 5,
                visualFieldVertical: 110,
                visualFieldHorizontal: 140,
                bisectorHeight: 30
            },
            transform: {
                type: 'angular-grid'
            },
            landmarks: {
                show: true
            }
        };
    }

    // =============================================================================
    // CANONICAL APPLICATION INTERFACE - Single Entry Point for All Operations
    // =============================================================================

    /**
     * Initialize application (canonical method)
     * 
     * Geometric Beauty: Elegant initialization sequence
     * Unified Ecosystem: All components initialized in harmony
     */
    async initialize(container) {
        try {
            console.log('🚀 Starting ApplicationOrchestrator initialization...');
            
            // Store container reference
            this.config.canvasElement = container;
            
            // Initialize Three.js components
            await this._initializeThreeJS(container);
            
            // Initialize rendering system
            this.renderingSystem = new RenderingSystem(this.scene, this.camera, this.renderer);
            
            // Initialize scene manager
            await this._setupDefaultScene();
            
            // Start render loop
            this._startRenderLoop();
            
            // Setup event handlers
            this._setupEventHandlers();
            
            // Connect parameter controls
            this._connectParameterControls();
            
            this.state.initialized = true;
            this.state.running = true;
            console.log('✅ ApplicationOrchestrator initialization complete');
            
        } catch (error) {
            console.error('❌ Failed to initialize ApplicationOrchestrator:', error);
            throw error;
        }
    }

    /**
     * Load mouse model (canonical method)
     * 
     * Single Source of Truth: All mouse loading through this interface
     * Proper SoC: Data loading -> Backend processing -> Rendering
     */
    async loadMouseModel(stlPath, config = {}) {
        console.log(`🐭 Loading mouse model: ${stlPath}`);

        try {
            // Create mouse data node (pure data container)
            const mouseNode = new MouseSceneNode('Mouse');

            // Set STL path (pure data operation)
            mouseNode.setSTLPath(stlPath);

            // Set mouse properties from config
            const length = config.length || 5.0;
            const scaleFactor = config.scaleFactor || 1.0;
            mouseNode.setMouseProperties(length, scaleFactor);

            // Position mouse (can be overridden by config)
            if (config.position) {
                mouseNode.setPosition(config.position.x, config.position.y, config.position.z);
            } else {
                // Default position on table surface
                mouseNode.setPosition(0, 3.5, 2);
            }

            // Add to scene graph
            this.addSceneNode(mouseNode);

            // Mark as loaded (for now - in future this would be done after backend processing)
            mouseNode.markSTLLoaded(true);

            // Rendering system will automatically create visualization
            this.renderingSystem.renderNode(mouseNode);

            console.log('✅ Mouse model loaded and rendered successfully');
            this.emit('mouseModelLoaded', mouseNode);

            return mouseNode;

        } catch (error) {
            console.error('❌ Failed to load mouse model:', error);
            throw error;
        }
    }

    /**
     * Setup experiment (canonical method)
     * 
     * Backend Delegation: All experiment logic handled by backend
     * Unified Interface: Single way to setup experiments
     */
    async setupExperiment(experimentConfig) {
        console.log('🔬 Setting up experiment...');

        try {
            // Call backend for experiment setup
            const response = await this.apiClient.setupExperiment(experimentConfig);

            if (!response.success) {
                throw new Error(`Experiment setup failed: ${response.error}`);
            }

            // Store experiment state
            this.state.currentExperiment = response.data;

            // Update scene based on experiment configuration
            await this._updateSceneForExperiment(response.data);

            console.log('✅ Experiment setup completed');
            this.emit('experimentSetup', response.data);

            return response.data;

        } catch (error) {
            console.error('❌ Experiment setup failed:', error);
            throw error;
        }
    }

    /**
     * Generate stimulus (canonical method)
     * 
     * Backend Processing: All stimulus generation done by backend
     * Data Flow: Backend -> Scene Node -> Rendering System
     */
    async generateStimulus(stimulusParams) {
        console.log('🎬 Generating stimulus...');

        try {
            // Get current experiment setup
            if (!this.state.currentExperiment) {
                throw new Error('No experiment setup available for stimulus generation');
            }

            // Call backend for stimulus generation
            const response = await this.apiClient.generateStimulus(
                stimulusParams,
                this.state.currentExperiment.setup_params
            );

            if (!response.success) {
                throw new Error(`Stimulus generation failed: ${response.error}`);
            }

            // Update monitor node with stimulus data
            const monitorNode = this.getSceneNode('Monitor');
            if (monitorNode) {
                monitorNode.setStimulusData(response.data.frames);
                this.renderingSystem.renderNode(monitorNode);
            }

            console.log('✅ Stimulus generated and applied');
            this.emit('stimulusGenerated', response.data);

            return response.data;

        } catch (error) {
            console.error('❌ Stimulus generation failed:', error);
            throw error;
        }
    }

    /**
     * Start data acquisition (canonical method)
     */
    async startAcquisition(acquisitionParams) {
        console.log('📹 Starting data acquisition...');

        try {
            // Initialize acquisition via backend
            const initResponse = await this.apiClient.initializeAcquisition(acquisitionParams);

            if (!initResponse.success) {
                throw new Error(`Acquisition initialization failed: ${initResponse.error}`);
            }

            // Start acquisition with current stimulus
            const stimulusFrames = this.state.currentExperiment?.stimulus_frames || [];
            const startResponse = await this.apiClient.startAcquisition(stimulusFrames);

            if (!startResponse.success) {
                throw new Error(`Acquisition start failed: ${startResponse.error}`);
            }

            console.log('✅ Data acquisition started');
            this.emit('acquisitionStarted', startResponse.data);

            return startResponse.data;

        } catch (error) {
            console.error('❌ Data acquisition failed:', error);
            throw error;
        }
    }

    /**
     * Run data analysis (canonical method)
     */
    async runAnalysis(analysisParams) {
        console.log('📊 Running data analysis...');

        try {
            // Get acquisition data
            const acquisitionData = this.state.currentExperiment?.acquisition_data;
            if (!acquisitionData) {
                throw new Error('No acquisition data available for analysis');
            }

            // Call backend for analysis
            const response = await this.apiClient.runAnalysis(acquisitionData, analysisParams);

            if (!response.success) {
                throw new Error(`Data analysis failed: ${response.error}`);
            }

            console.log('✅ Data analysis completed');
            this.emit('analysisCompleted', response.data);

            return response.data;

        } catch (error) {
            console.error('❌ Data analysis failed:', error);
            throw error;
        }
    }

    // =============================================================================
    // SCENE GRAPH MANAGEMENT - Pure Data Operations
    // =============================================================================

    /**
     * Add scene node to graph
     */
    addSceneNode(sceneNode, parentId = null) {
        if (!(sceneNode instanceof SceneNode)) {
            throw new Error('Object must be a SceneNode instance');
        }

        // Add to registry
        this.sceneNodes.set(sceneNode.id, sceneNode);

        // Add to hierarchy
        const parent = parentId ? this.sceneNodes.get(parentId) : this.sceneGraph;
        if (parent) {
            parent.addChild(sceneNode);
        }

        // Setup event listeners
        this._setupSceneNodeEvents(sceneNode);

        console.log(`📦 Added scene node: ${sceneNode.name} [${sceneNode.type}]`);
        this.emit('sceneNodeAdded', sceneNode);
    }

    /**
     * Remove scene node from graph
     */
    removeSceneNode(nodeId) {
        const sceneNode = this.sceneNodes.get(nodeId);
        if (!sceneNode) {
            console.warn(`⚠️ Scene node not found: ${nodeId}`);
            return;
        }

        // Remove from rendering
        this.renderingSystem.removeNode(sceneNode.id);

        // Remove from hierarchy
        if (sceneNode.parent) {
            sceneNode.parent.removeChild(sceneNode);
        }

        // Remove from registry
        this.sceneNodes.delete(nodeId);

        // Clean up
        sceneNode.destroy();

        console.log(`🗑️ Removed scene node: ${sceneNode.name}`);
        this.emit('sceneNodeRemoved', sceneNode);
    }

    /**
     * Get scene node by ID or name
     */
    getSceneNode(identifier) {
        // Try by ID first
        if (this.sceneNodes.has(identifier)) {
            return this.sceneNodes.get(identifier);
        }

        // Try by name
        for (const node of this.sceneNodes.values()) {
            if (node.name === identifier) {
                return node;
            }
        }

        return null;
    }

    /**
     * Get all scene nodes of specific type
     */
    getSceneNodesByType(nodeType) {
        return Array.from(this.sceneNodes.values()).filter(
            node => node.type === nodeType
        );
    }

    /**
     * Get all scene nodes (for scene tree display)
     */
    getAllSceneNodes() {
        return Array.from(this.sceneNodes.values());
    }

    // =============================================================================
    // RENDERING COORDINATION - Bridge Between Data and Visualization
    // =============================================================================

    /**
     * Update all visualizations - Simple and Direct
     */
    async updateVisualizations() {
        console.log('🔄 Updating visualizations...');
        await this.renderingSystem.renderSceneGraph(this.sceneGraph);
        
        // Return render statistics for debugging
        const stats = this.renderingSystem.getStats();
        console.log('✅ Visualizations updated:', stats);
        return stats;
    }

    /**
     * Set camera position
     */
    setCameraPosition(x, y, z) {
        this.camera.position.set(x, y, z);
        this.camera.lookAt(0, 0, 0);
    }

    /**
     * Set camera target
     */
    setCameraTarget(x, y, z) {
        this.camera.lookAt(x, y, z);
    }

    /**
     * Resize renderer
     */
    resize(width, height) {
        console.log('🔄 Resize called:', { width, height });
        
        // Safeguard against zero dimensions
        if (width <= 0 || height <= 0) {
            console.warn('⚠️ Resize called with invalid dimensions, ignoring:', { width, height });
            return;
        }
        
        console.log('🔄 Applying resize...');
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
        
        // Force a render after resize to ensure objects remain visible
        this.renderingSystem.render();
        
        console.log('✅ Resize completed and re-rendered:', {
            cameraAspect: this.camera.aspect,
            rendererSize: this.renderer.getSize(new THREE.Vector2())
        });
    }

    // =============================================================================
    // PRIVATE METHODS - Internal System Management
    // =============================================================================

    /**
     * Initialize Three.js components
     */
    _initializeThreeJS(container) {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.config.backgroundColor);

        // Get container dimensions with fallback
        const containerRect = container.getBoundingClientRect();
        let width = containerRect.width;
        let height = containerRect.height;
        
        // Fallback to computed styles if getBoundingClientRect returns 0
        if (width === 0 || height === 0) {
            const computedStyle = window.getComputedStyle(container);
            width = parseInt(computedStyle.width) || 800;
            height = parseInt(computedStyle.height) || 600;
        }
        
        // Final fallback to reasonable defaults
        if (width === 0 || height === 0) {
            width = 800;
            height = 600;
            console.warn('🔧 Using fallback dimensions:', { width, height });
        }
        
        console.log(`🎨 Initializing Three.js with dimensions: ${width}x${height}`);

        // Camera
        this.camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
        this.camera.position.set(
            this.config.cameraPosition.x,
            this.config.cameraPosition.y,
            this.config.cameraPosition.z
        );

        // Renderer optimized for performance
        this.renderer = new THREE.WebGLRenderer({
            antialias: this.config.enableAntialiasing,
            alpha: false,
            preserveDrawingBuffer: false,
            powerPreference: "high-performance"
        });
        
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Performance optimizations
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.toneMapping = THREE.NoToneMapping;

        // Shadows disabled for better performance
        this.renderer.shadowMap.enabled = false;

        // Remove existing canvas if present, then append new canvas
        const existingCanvas = container.querySelector('canvas');
        if (existingCanvas) {
            container.removeChild(existingCanvas);
        }
        
        // Basic canvas styling
        this.renderer.domElement.style.display = 'block';
        this.renderer.domElement.style.width = '100%';
        this.renderer.domElement.style.height = '100%';
        
        container.appendChild(this.renderer.domElement);

        // Standard OrbitControls - exactly like Three.js examples
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        
        console.log('🎮 Standard OrbitControls initialized');

        console.log(`✅ Three.js initialized successfully`);
    }

    /**
     * Setup default scene
     */
    async _setupDefaultScene() {
        console.log('🎬 Setting up default scene...');
        
        // Create floor plan first (centered at origin)
        const floorPlanNode = new FloorPlanSceneNode('FloorPlan');
        floorPlanNode.setRoomDimensions(80, 80, 50); // 80x80cm room
        floorPlanNode.setTableDimensions(10, 10, 3); // 10x10x3cm table
        floorPlanNode.setGridProperties(80, 8, 0x333333); // 80cm grid with 8 divisions = 10cm cells
        floorPlanNode.setPosition(0, 0, 0); // Centered at origin
        this.addSceneNode(floorPlanNode);
        console.log('🏠 Floor plan: 80x80cm room, 10cm grid cells, 10cm axes');
        
        // Create monitor node positioned above table
        const monitorNode = new MonitorSceneNode('Monitor');
        monitorNode.setDimensions(10, 8, 1.0); // Reasonable monitor size
        monitorNode.setPosition(0, 15, -8); // Above table, tilted toward mouse position
        this.addSceneNode(monitorNode);
        console.log('🖥️ Monitor node created:', monitorNode.getDebugInfo());

        // Create mouse node positioned on floor
        const mouseNode = new MouseSceneNode('Mouse');
        mouseNode.setMouseProperties(3.0, 1.0); // 3cm mouse
        mouseNode.setPosition(0, 0, 0); // On floor surface (will be adjusted by landmark detection)
        mouseNode.setData('showLandmarks', true); // Enable landmarks for orientation
        this.addSceneNode(mouseNode);
        console.log('🐭 Mouse node created:', mouseNode.getDebugInfo());

        // Debug scene graph structure before rendering
        console.log('🔍 Scene graph structure before rendering:');
        console.log('🔍 Root scene graph children:', this.sceneGraph.children.size);
        this.sceneGraph.traverse((node) => {
            console.log(`🔍 Node: ${node.name} [${node.type}] visible=${node.visible} needsUpdate=${node.needsBackendUpdate()}`);
            console.log(`🔍   Data:`, node.getAllData());
            console.log(`🔍   Transform:`, node.getTransform());
        });
        
        // Render entire scene graph (Single Source of Truth)
        console.log('🎨 Rendering entire scene graph...');
        const sceneRenderStats = await this.updateVisualizations();
        console.log('✅ All objects rendered through unified scene graph system');
        console.log('🔍 Render stats:', sceneRenderStats);
        
        // Force an immediate render to make sure objects appear
        console.log('🎯 Forcing immediate render...');
        this.renderingSystem.render();
        console.log('✅ Immediate render completed');
        
        // Debug Three.js scene after rendering
        console.log('🔍 Three.js scene children after rendering:', this.scene.children.length);
        this.scene.children.forEach((child, index) => {
            console.log(`🔍 Scene child ${index}: ${child.name || child.type} visible=${child.visible} position=(${child.position.x.toFixed(1)}, ${child.position.y.toFixed(1)}, ${child.position.z.toFixed(1)})`);
        });

        // Position camera to see all objects in the scene
        this.camera.position.set(50, 30, 50);  // Higher and further back to see the 80x80 floor
        this.controls.target.set(0, 5, 0);     // Look at the center of the scene, slightly elevated
        this.controls.update();
        
        console.log('📷 Camera positioned at (50, 30, 50) looking at scene center');
        
        // Log what objects should be visible
        console.log('🔍 Expected objects in view (all measurements in cm):');
        console.log('  🏠 Floor: 80x80cm gray plane at ground level');
        console.log('  📦 Table: 10x10x3cm brown box at (0, 1.5, 0)');
        console.log('  🖥️ Monitor: 10x8x1cm black frame at (0, 15, -8)');
        console.log('  🐭 Mouse: 3x1x1.5cm brown box at (0, 3.5, 2)');
        console.log('  🗂️ Grid: 10cm x 10cm cells (8 divisions across 80cm)');
        console.log('  🎯 Axes: 10cm long (Red=X, Green=Y, Blue=Z)');
        
        // Debug camera setup
        console.log('🔍 Camera debug info:', {
            position: this.camera.position,
            rotation: this.camera.rotation,
            fov: this.camera.fov,
            aspect: this.camera.aspect,
            near: this.camera.near,
            far: this.camera.far,
            matrixWorldNeedsUpdate: this.camera.matrixWorldNeedsUpdate
        });
        
        // Update camera matrices to ensure they're current
        this.camera.updateMatrixWorld();
        this.camera.updateProjectionMatrix();

        console.log('📦 Default scene setup completed');
        console.log('🎯 Scene objects count:', this.scene.children.length);
        console.log('📷 Camera position:', this.camera.position);
        console.log('🎨 Renderer size:', this.renderer.getSize(new THREE.Vector2()));
        
        // Debug: Check canvas visibility and DOM state
        const canvas = this.renderer.domElement;
        console.log('🔍 Canvas DOM state:', {
            isConnected: canvas.isConnected,
            parentElement: canvas.parentElement?.tagName,
            offsetWidth: canvas.offsetWidth,
            offsetHeight: canvas.offsetHeight,
            clientWidth: canvas.clientWidth,
            clientHeight: canvas.clientHeight,
            canvasWidth: canvas.width,
            canvasHeight: canvas.height,
            style: canvas.style.cssText,
            computedStyle: window.getComputedStyle(canvas).display
        });
        
        // Debug: Check WebGL context
        const gl = this.renderer.getContext();
        console.log('🔍 WebGL context state:', {
            contextLost: gl.isContextLost(),
            drawingBufferWidth: gl.drawingBufferWidth,
            drawingBufferHeight: gl.drawingBufferHeight,
            viewport: gl.getParameter(gl.VIEWPORT),
            clearColor: gl.getParameter(gl.COLOR_CLEAR_VALUE)
        });
        
        // Debug: Check container state
        const container = this.config.canvasElement;
        console.log('🔍 Container DOM state:', {
            tagName: container.tagName,
            id: container.id,
            className: container.className,
            offsetWidth: container.offsetWidth,
            offsetHeight: container.offsetHeight,
            clientWidth: container.clientWidth,
            clientHeight: container.clientHeight,
            childElementCount: container.childElementCount,
            isVisible: window.getComputedStyle(container).display !== 'none'
        });
        
        // Debug: List all scene children
        console.log('🔍 Scene children:');
        this.scene.children.forEach((child, index) => {
            console.log(`  ${index}: ${child.name || child.type} at (${child.position.x.toFixed(1)}, ${child.position.y.toFixed(1)}, ${child.position.z.toFixed(1)})`);
        });
        
        // Debug: List all scene nodes
        console.log('🔍 Scene nodes:');
        this.sceneNodes.forEach((node, id) => {
            console.log(`  ${id}: ${node.name} [${node.type}] visible=${node.visible}`);
        });
        
        // Debug: Check rendering system stats
        const renderStats = this.renderingSystem.getStats();
        console.log('🔍 Rendering stats:', renderStats);
        
        // Render loop will handle all rendering
        
        // Add a safety check to ensure objects remain visible
        setTimeout(() => {
            console.log('🔍 Safety check: Scene has', this.scene.children.length, 'children');
            console.log('🔍 Safety check: Camera at', this.camera.position);
            console.log('🔍 Safety check: Render objects:', this.renderingSystem.renderObjects.size);
            
            // Force another render just to be sure
            this.renderingSystem.render();
            console.log('🔍 Safety render completed');
        }, 1000);
        
        console.log('✅ Default scene setup completed');
    }

    /**
     * Update scene for experiment
     */
    async _updateSceneForExperiment(experimentData) {
        // Update monitor based on experiment setup
        const monitorNode = this.getSceneNode('Monitor');
        if (monitorNode && experimentData.setup_params) {
            const setup = experimentData.setup_params;
            if (setup.monitor_size) {
                monitorNode.setDimensions(
                    setup.monitor_size[0],
                    setup.monitor_size[1],
                    setup.monitor_distance || 10.0
                );
            }
        }

        // Re-render affected nodes
        this.updateVisualizations();
    }

    /**
     * Setup scene node event handlers
     */
    _setupSceneNodeEvents(sceneNode) {
        // DISABLED: These automatic re-renders interfere with OrbitControls
        // Only re-render when explicitly requested, not on every data change
        
        console.log(`🔇 Scene node events disabled for: ${sceneNode.name} to prevent controls interference`);
        
        // If we need updates later, they should be triggered manually via updateVisualization()
        // rather than automatically on every scene node change
    }

    /**
     * Setup application event handlers
     */
    _setupEventHandlers() {
        // Simple window resize handler
        window.addEventListener('resize', () => {
            if (this.config.canvasElement) {
                const rect = this.config.canvasElement.getBoundingClientRect();
                this.resize(rect.width, rect.height);
            }
        });

        // Keyboard shortcuts
        window.addEventListener('keydown', (event) => {
            this._handleKeyboardShortcut(event);
        });
    }

    /**
     * Handle keyboard shortcuts
     */
    _handleKeyboardShortcut(event) {
        switch (event.code) {
            case 'KeyR':
                // Reset camera
                this.setCameraPosition(10, 10, 10);
                break;

            case 'KeyL':
                // Toggle landmark visibility
                const mouseNode = this.getSceneNode('Mouse');
                if (mouseNode) {
                    const config = mouseNode.getConfig();
                    mouseNode.updateConfig({ showLandmarks: !config.showLandmarks });
                }
                break;
        }
    }

    /**
     * Start render loop - Exact Three.js example pattern
     */
    _startRenderLoop() {
        function animate() {
            requestAnimationFrame(animate);
            this.controls.update();
            this.renderer.render(this.scene, this.camera);
        }
        
        // Bind context and start
        animate = animate.bind(this);
        animate();
        
        console.log('🎬 Three.js standard render loop started');
    }

    /**
     * Stop render loop
     */
    _stopRenderLoop() {
        if (this.state.renderLoop) {
            cancelAnimationFrame(this.state.renderLoop);
            this.state.renderLoop = null;
        }

        this.state.running = false;
        console.log('⏹️ Render loop stopped');
    }

    /**
     * Clean up application
     */
    dispose() {
        console.log('🗑️ Disposing ApplicationOrchestrator...');

        // Stop render loop
        this._stopRenderLoop();
        
        // Clean up scene nodes
        for (const node of this.sceneNodes.values()) {
            node.destroy();
        }
        this.sceneNodes.clear();

        // Clean up rendering system
        this.renderingSystem.dispose();
        
        // Clean up controls
        if (this.controls) {
            this.controls.dispose();
            this.controls = null;
        }

        // Clean up Three.js
        this.renderer.dispose();

        this.state.initialized = false;
        console.log('✅ ApplicationOrchestrator disposed');
    }

    /**
     * Get application statistics
     */
    getStats() {
        return {
            sceneNodeCount: this.sceneNodes.size,
            renderingStats: this.renderingSystem.getStats(),
            state: { ...this.state }
        };
    }

    // =============================================================================
    // UI INTERFACE METHODS - Methods expected by app.js
    // =============================================================================

    /**
     * Update visualization with parameters (simplified)
     */
    async updateVisualization(params) {
        console.log('🔄 Updating visualization with parameters:', params);

        try {
            // Update scene based on parameters
            if (params) {
                // Update monitor if parameters provided
                const monitorNode = this.getSceneNode('Monitor');
                if (monitorNode && params.monitor_width && params.monitor_height) {
                    monitorNode.setDimensions(
                        params.monitor_width,
                        params.monitor_height,
                        params.monitor_distance || 10.0
                    );
                }

                // Update mouse if parameters provided
                const mouseNode = this.getSceneNode('Mouse');
                if (mouseNode) {
                    if (params.mouse_length) {
                        mouseNode.setMouseProperties(params.mouse_length, 1.0);
                    }
                    if (params.show_landmarks !== undefined) {
                        mouseNode.setData('showLandmarks', params.show_landmarks);
                    }
                }
            }

            // Always re-render - simple and reliable
            this.updateVisualizations();
            console.log('✅ Visualization updated successfully');
        } catch (error) {
            console.error('❌ Failed to update visualization:', error);
            throw error;
        }
    }

    /**
     * Get scene statistics (alias for getStats for app.js compatibility)
     */
    getSceneStats() {
        const stats = this.getStats();
        return {
            nodeCount: stats.sceneNodeCount,
            triangles: stats.renderingStats?.triangles || 0,
            ...stats.renderingStats
        };
    }

    /**
     * Reset camera to default position
     */
    resetCamera() {
        this.camera.position.set(50, 30, 50);
        this.controls.target.set(0, 5, 0);
        this.controls.update();
        console.log('📷 Camera reset to overview position');
    }
    
    /**
     * Fit camera to show all scene objects
     */
    fitCameraToScene() {
        // Position to see the full 80x80 floor plus elevated objects
        this.camera.position.set(60, 40, 60);  // Even further back and higher
        this.controls.target.set(0, 5, 0);     // Look at scene center
        this.controls.update();
        console.log('📷 Camera fitted to show all scene objects');
    }

    /**
     * Set landmark visibility for all mouse nodes
     */
    setLandmarkVisibility(visible) {
        const mouseNodes = this.getSceneNodesByType('Mouse');
        mouseNodes.forEach(node => {
            node.setData('showLandmarks', visible);
        });
        console.log(`🎯 Landmarks ${visible ? 'shown' : 'hidden'}`);
    }

    /**
     * Toggle wireframe mode for all meshes
     */
    toggleWireframe() {
        if (this.renderingSystem && this.renderingSystem.toggleWireframe) {
            this.renderingSystem.toggleWireframe();
            console.log('🔲 Wireframe mode toggled');
        }
    }

    /**
     * Get current camera position
     */
    getCameraPosition() {
        if (this.camera) {
            return {
                x: this.camera.position.x,
                y: this.camera.position.y,
                z: this.camera.position.z
            };
        }
        return { x: 0, y: 0, z: 0 };
    }

    /**
     * Connect UI parameter controls to scene updates
     */
    _connectParameterControls() {
        console.log('🔗 Connecting parameter controls...');
        
        // Monitor parameters
        this._connectParameter('monitor_orientation', 'monitor.orientation', this._updateMonitor.bind(this));
        this._connectParameter('monitor_width', 'monitor.width', this._updateMonitor.bind(this));
        this._connectParameter('monitor_height', 'monitor.height', this._updateMonitor.bind(this));
        this._connectParameter('monitor_distance', 'monitor.distance', this._updateMonitor.bind(this));
        this._connectParameter('monitor_elevation', 'monitor.elevation', this._updateMonitor.bind(this));
        this._connectParameter('monitor_rotation', 'monitor.rotation', this._updateMonitor.bind(this));
        
        // Mouse parameters
        this._connectParameter('mouse_length', 'mouse.length', this._updateMouse.bind(this));
        this._connectParameter('mouse_eye_height', 'mouse.eyeHeight', this._updateMouse.bind(this));
        this._connectParameter('mouse_visual_field_vertical', 'mouse.visualFieldVertical', this._updateMouse.bind(this));
        this._connectParameter('mouse_visual_field_horizontal', 'mouse.visualFieldHorizontal', this._updateMouse.bind(this));
        this._connectParameter('perpendicular_bisector_height', 'mouse.bisectorHeight', this._updateMouse.bind(this));
        
        // Transform parameters
        this._connectParameter('transform_type', 'transform.type', this._updateTransform.bind(this));
        
        // Landmarks
        this._connectParameter('landmarks-checkbox', 'landmarks.show', this._updateMouse.bind(this));
        
        // Update visualization button
        const updateButton = document.getElementById('visualize-button');
        if (updateButton) {
            updateButton.addEventListener('click', () => {
                console.log('🔄 Manual update requested');
                this._updateAllObjects();
            });
        }
        
        console.log('✅ Parameter controls connected');
    }
    
    /**
     * Connect individual parameter to its update handler
     */
    _connectParameter(elementId, paramPath, updateHandler) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`⚠️ Parameter element not found: ${elementId}`);
            return;
        }
        
        // Read initial value
        this._setParameterValue(paramPath, this._getElementValue(element));
        
        // Connect event listener
        const eventType = element.type === 'checkbox' ? 'change' : 'input';
        element.addEventListener(eventType, () => {
            const value = this._getElementValue(element);
            this._setParameterValue(paramPath, value);
            console.log(`📊 Parameter updated: ${paramPath} = ${value}`);
            updateHandler();
        });
    }
    
    /**
     * Get value from UI element
     */
    _getElementValue(element) {
        if (element.type === 'checkbox') {
            return element.checked;
        } else if (element.type === 'number') {
            return parseFloat(element.value) || 0;
        } else {
            return element.value;
        }
    }
    
    /**
     * Set parameter value using dot notation
     */
    _setParameterValue(path, value) {
        const parts = path.split('.');
        let current = this.parameterValues;
        for (let i = 0; i < parts.length - 1; i++) {
            current = current[parts[i]];
        }
        current[parts[parts.length - 1]] = value;
    }
    
    /**
     * Get parameter value using dot notation
     */
    _getParameterValue(path) {
        const parts = path.split('.');
        let current = this.parameterValues;
        for (const part of parts) {
            current = current[part];
            if (current === undefined) return undefined;
        }
        return current;
    }
    
    /**
     * Update monitor object based on current parameters
     */
    _updateMonitor() {
        const monitorNode = this.getSceneNode('monitor');
        if (!monitorNode) return;
        
        const params = this.parameterValues.monitor;
        
        // Update monitor dimensions and position
        const width = params.orientation === 'landscape' ? params.width : params.height;
        const height = params.orientation === 'landscape' ? params.height : params.width;
        
        monitorNode.setData('width', width);
        monitorNode.setData('height', height);
        monitorNode.setData('depth', 1);
        
        // Calculate position based on distance and elevation
        const distance = params.distance;
        const elevationRad = (params.elevation * Math.PI) / 180;
        const rotationRad = (params.rotation * Math.PI) / 180;
        
        // Position monitor at specified distance from origin with elevation
        const x = -distance * Math.sin(rotationRad);
        const y = height/2 + distance * Math.tan(elevationRad);
        const z = -distance * Math.cos(rotationRad);
        
        monitorNode.transform.position.set(x, y, z);
        monitorNode.transform.rotation.set(elevationRad, rotationRad, 0);
        
        console.log(`📺 Monitor updated: ${width}×${height}cm at (${x.toFixed(1)}, ${y.toFixed(1)}, ${z.toFixed(1)})`);
        
        // Re-render the monitor
        if (this.renderingSystem) {
            this.renderingSystem.renderNode(monitorNode);
        }
    }
    
    /**
     * Update mouse object based on current parameters
     */
    _updateMouse() {
        const mouseNode = this.getSceneNode('mouse');
        if (!mouseNode) return;
        
        const params = this.parameterValues.mouse;
        const landmarkParams = this.parameterValues.landmarks;
        
        // Update mouse properties
        mouseNode.setData('length', params.length);
        mouseNode.setData('eyeHeight', params.eyeHeight);
        mouseNode.setData('visualFieldVertical', params.visualFieldVertical);
        mouseNode.setData('visualFieldHorizontal', params.visualFieldHorizontal);
        mouseNode.setData('showLandmarks', landmarkParams.show);
        
        // Update mouse position (eye height above table)
        mouseNode.transform.position.y = 3 + params.eyeHeight / 10; // Convert cm to units and add table height
        
        console.log(`🐭 Mouse updated: ${params.length}cm length, eye height ${params.eyeHeight}cm`);
        
        // Re-render the mouse
        if (this.renderingSystem) {
            this.renderingSystem.renderNode(mouseNode);
        }
    }
    
    /**
     * Update transform settings
     */
    _updateTransform() {
        const transformType = this.parameterValues.transform.type;
        console.log(`🔄 Transform updated: ${transformType}`);
        // Transform logic would be implemented here for stimulus generation
    }
    
    /**
     * Update all scene objects
     */
    _updateAllObjects() {
        console.log('🔄 Updating all scene objects...');
        this._updateMonitor();
        this._updateMouse();
        this._updateTransform();
        console.log('✅ All objects updated');
    }
}

// =============================================================================
// FACTORY FUNCTION - Canonical Application Creation
// =============================================================================

/**
 * Create application orchestrator with default configuration
 * 
 * Geometric Beauty: Elegant abstraction over application complexity
 * Single Source of Truth: One way to create applications
 */
export function createApplication(canvasElement, config = {}) {
    const app = new ApplicationOrchestrator(canvasElement, config);
    console.log('🎯 Created ISI application orchestrator');
    return app;
} 