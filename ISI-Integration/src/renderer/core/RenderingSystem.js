import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { apiClient } from '../services/UnifiedAPIClient.js';
import { serverReadyManager } from './ServerReadyManager.js';
import { LandmarkDetector } from '../LandmarkDetector.js';

/**
 * Simple, Direct Rendering System
 * 
 * Philosophy: Keep it simple, stupid (KISS)
 * - Direct mapping: SceneNode -> Three.js Object
 * - No complex hierarchy management
 * - No update tracking
 * - Clear, predictable behavior
 */
export class RenderingSystem {
    constructor(scene, camera, renderer) {
        this.scene = scene;
        this.camera = camera;
        this.renderer = renderer;
        
        // Simple object tracking
        this.renderObjects = new Map(); // nodeId -> Three.js Object
        
        // Material/geometry caching for performance
        this.materials = new Map();
        this.geometries = new Map();
        
        // Simple stats
        this.stats = {
            renderCalls: 0,
            objectCount: 0
        };
        
        this._setupLighting();
        
        console.log('🎨 Simple RenderingSystem initialized');
    }
    
    /**
     * Render a single scene node - Simple and Direct
     */
    async renderNode(sceneNode) {
        if (!sceneNode || !sceneNode.visible) {
            return null;
        }
        
        // Get or create render object
        let renderObject = this.renderObjects.get(sceneNode.id);
        
        if (!renderObject) {
            // Create new object (now async)
            renderObject = await this._createRenderObject(sceneNode);
            if (renderObject) {
                this.renderObjects.set(sceneNode.id, renderObject);
                this.scene.add(renderObject);
                console.log(`✅ Created render object for: ${sceneNode.name}`);
            } else if (sceneNode.type !== 'Root') {
                // Only warn if it's not a root node (root nodes don't need render objects)
                console.warn(`⚠️ Could not create render object for: ${sceneNode.name} [${sceneNode.type}]`);
            }
        }
        
        if (renderObject) {
            // Always update transform and properties
            this._updateRenderObject(renderObject, sceneNode);
        }
        
        return renderObject;
    }
    
    /**
     * Render entire scene graph - Simple traversal
     */
    async renderSceneGraph(rootNode) {
        console.log('🎨 Starting scene graph rendering...');
        console.log('🔍 Root node:', rootNode.name, 'Type:', rootNode.type, 'Children:', rootNode.children.size);
        
        // Clear existing objects (temporarily re-enabled for testing)
        this._clearScene();
        
        // Render all nodes
        const renderNode = async (node) => {
            console.log(`🎨 Rendering node: ${node.name} [${node.type}] visible=${node.visible}`);
            const renderObject = await this.renderNode(node);
            if (renderObject) {
                console.log(`✅ Successfully created render object for: ${node.name}`);
            } else {
                console.warn(`❌ Failed to create render object for: ${node.name}`);
            }
            
            // Render children
            for (const child of node.children.values()) {
                await renderNode(child);
            }
        };
        
        await renderNode(rootNode);
        
        this.stats.objectCount = this.renderObjects.size;
        console.log(`🎨 Scene graph rendering complete: ${this.stats.objectCount} objects created`);
        console.log('🔍 Scene.children count:', this.scene.children.length);
    }
    
    /**
     * Create Three.js object for scene node
     */
    async _createRenderObject(sceneNode) {
        switch (sceneNode.type) {
            case 'Root':
                // Don't create a render object for root - it's just a container
                return null;
            case 'FloorPlan':
                return this._createFloorPlan(sceneNode);
            case 'Monitor':
                return this._createMonitor(sceneNode);
            case 'Mouse':
                return await this._createMouse(sceneNode);
            default:
                return this._createGeneric(sceneNode);
        }
    }
    
    /**
     * Update existing render object
     */
    _updateRenderObject(renderObject, sceneNode) {
        // Update transform
        const transform = sceneNode.getTransform();
        renderObject.position.set(transform.position.x, transform.position.y, transform.position.z);
        renderObject.rotation.set(transform.rotation.x, transform.rotation.y, transform.rotation.z);
        renderObject.scale.set(transform.scale.x, transform.scale.y, transform.scale.z);
        renderObject.visible = sceneNode.visible;
    }
    
    /**
     * Create root container
     */
    _createRoot(sceneNode) {
        const group = new THREE.Group();
        group.name = sceneNode.name;
        return group;
    }
    
    /**
     * Create floor plan
     */
    _createFloorPlan(sceneNode) {
        const group = new THREE.Group();
        group.name = sceneNode.name;
        
        // Get dimensions
        const roomWidth = sceneNode.getData('roomWidth') || 80;
        const roomDepth = sceneNode.getData('roomDepth') || 80;
        const tableWidth = sceneNode.getData('tableWidth') || 10;
        const tableDepth = sceneNode.getData('tableDepth') || 10;
        const tableHeight = sceneNode.getData('tableHeight') || 3;
        
        // Floor - Make it clearly visible
        const floorGeometry = new THREE.PlaneGeometry(roomWidth, roomDepth);
        const floorMaterial = new THREE.MeshLambertMaterial({ 
            color: 0xcccccc,  // Much brighter gray
            side: THREE.DoubleSide  // Visible from both sides
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;  // Rotate to be horizontal
        floor.position.y = 0;  // Ensure it's at ground level
        floor.name = 'floor';
        group.add(floor);
        console.log(`🏠 Floor created: ${roomWidth}x${roomDepth} at position (0,0,0)`);
        
        // Table removed - mouse will be positioned directly on floor
        
        // Grid - 10cm x 10cm cells (80cm / 8 divisions = 10cm per cell)
        const gridHelper = new THREE.GridHelper(roomWidth, 8, 0x666666, 0x444444);
        gridHelper.name = 'grid';
        group.add(gridHelper);
        console.log(`🗂️ Grid created: ${roomWidth}cm room with 8 divisions = 10cm cells`);
        
        // Axes helper - exactly 10cm long
        const axesHelper = new THREE.AxesHelper(10);
        axesHelper.name = 'axes';
        group.add(axesHelper);
        console.log(`🎯 Axes helper: 10cm long (Red=X, Green=Y, Blue=Z)`);
        
        return group;
    }
    
    /**
     * Create monitor
     */
    _createMonitor(sceneNode) {
        const group = new THREE.Group();
        group.name = sceneNode.name;
        
        // Get dimensions
        const width = sceneNode.getData('width') || 10;
        const height = sceneNode.getData('height') || 8;
        const depth = sceneNode.getData('depth') || 1;
        
        // Monitor frame
        const frameGeometry = new THREE.BoxGeometry(width, height, depth);
        const frameMaterial = new THREE.MeshLambertMaterial({ color: 0x000000 });
        const frame = new THREE.Mesh(frameGeometry, frameMaterial);
        frame.name = 'frame';
        group.add(frame);
        
        // Screen
        const screenGeometry = new THREE.PlaneGeometry(width * 0.9, height * 0.9);
        const screenMaterial = new THREE.MeshLambertMaterial({ color: 0x001122 });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.z = depth / 2 + 0.01;
        screen.name = 'screen';
        group.add(screen);
        
        return group;
    }
    
    /**
     * Create mouse with STL model
     */
    async _createMouse(sceneNode) {
        const group = new THREE.Group();
        group.name = sceneNode.name;
        
        // Get properties
        const length = sceneNode.getData('length') || 3.0;
        const showLandmarks = sceneNode.getData('showLandmarks') || false;
        const stlPath = sceneNode.getData('stlPath') || './Mouse.stl';
        
        try {
            // Load STL model
            const loader = new STLLoader();
            console.log(`🐭 Loading mouse STL from: ${stlPath}`);
            
            const geometry = await new Promise((resolve, reject) => {
                loader.load(
                    stlPath,
                    (geometry) => {
                        console.log('✅ STL loaded successfully');
                        resolve(geometry);
                    },
                    (progress) => {
                        console.log('📊 STL loading progress:', (progress.loaded / progress.total * 100) + '%');
                    },
                    (error) => {
                        console.error('❌ STL loading failed:', error);
                        reject(error);
                    }
                );
            });
            
            // Create material for mouse
            const mouseMaterial = new THREE.MeshLambertMaterial({ 
                color: 0x8B4513,
                side: THREE.DoubleSide
            });
            
            // Create mesh from STL geometry
            const mouseMesh = new THREE.Mesh(geometry, mouseMaterial);
            mouseMesh.name = 'body';
            
            // Center and scale the geometry
            geometry.computeBoundingBox();
            const bbox = geometry.boundingBox;
            const size = new THREE.Vector3();
            bbox.getSize(size);
            
            // Scale to desired length (assuming STL is in mm, convert to cm)
            const scale = length / Math.max(size.x, size.y, size.z);
            mouseMesh.scale.setScalar(scale);
            
            // Center and orient the mesh properly
            const center = new THREE.Vector3();
            bbox.getCenter(center);
            mouseMesh.position.copy(center).multiplyScalar(-scale);
            
            // Initial rotation will be corrected by landmark detection
            // Landmarks will determine the proper orientation based on nose/tail positions
            
            group.add(mouseMesh);
            
            console.log(`🐭 STL mouse model loaded: scale=${scale.toFixed(3)}, size=${size.x.toFixed(1)}x${size.y.toFixed(1)}x${size.z.toFixed(1)}`);
            
            // Perform landmark detection if enabled - this provides orientation data
            if (showLandmarks) {
                // Queue landmark detection to run when server is ready
                serverReadyManager.queueLandmarkDetection(() => {
                    this._performLandmarkDetection(geometry, group, scale, center, mouseMesh).catch(error => {
                        console.error('❌ Landmark detection failed:', error);
                    });
                }, `Mouse ${sceneNode.name} landmark detection`);
            }
            
        } catch (error) {
            console.warn('⚠️ Failed to load STL, using fallback box geometry:', error);
            
            // Fallback to simple box geometry
            const mouseGeometry = new THREE.BoxGeometry(length, 1.0, 1.5);
            const mouseMaterial = new THREE.MeshLambertMaterial({ color: 0x8B4513 });
            const mouseMesh = new THREE.Mesh(mouseGeometry, mouseMaterial);
            mouseMesh.name = 'body';
            group.add(mouseMesh);
        }
        
        // Landmarks (simple spheres)
        if (showLandmarks) {
            const landmarks = sceneNode.getData('landmarks');
            if (landmarks && Array.isArray(landmarks) && landmarks.length > 0) {
                landmarks.forEach((landmark, index) => {
                    const sphereGeometry = new THREE.SphereGeometry(0.1, 8, 6);
                    const sphereMaterial = new THREE.MeshLambertMaterial({ color: 0xFF0000 });
                    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
                    sphere.position.set(
                        landmark.x || (Math.random() - 0.5) * length,
                        landmark.y || 0.5,
                        landmark.z || (Math.random() - 0.5) * 1.5
                    );
                    sphere.name = `landmark_${index}`;
                    group.add(sphere);
                });
            } else {
                // No landmarks available yet - create placeholder indication
                console.log(`🎯 Mouse ${sceneNode.name}: Landmarks requested but not available yet`);
            }
        }
        
        return group;
    }

    /**
     * Perform landmark detection on STL geometry
     */
    async _performLandmarkDetection(geometry, group, scale, center, mouseMesh) {
        try {
            console.log('🔬 Starting landmark detection...');
            
            // Extract vertices from original geometry (before any transformations)
            const vertices = this._extractVerticesFromGeometry(geometry);
            console.log(`📊 Extracted ${vertices.length} vertices from original geometry for landmark detection`);
            
            // Use unified API client directly for landmark detection
            const landmarkResults = await apiClient.detectLandmarks(vertices);
            
            if (landmarkResults && landmarkResults.landmarks) {
                const landmarks = landmarkResults.landmarks;
                console.log(`✅ Landmark detection successful: ${Object.keys(landmarks).length} landmarks detected`);
                
                // First orient mouse based on detected nose and tail positions
                this._orientMouseFromLandmarks(landmarks, mouseMesh, scale, center);
                
                // Then create 3D landmark markers (as children of mouse mesh)
                this._createLandmarkMarkers(landmarks, mouseMesh, scale, center);
                
                // Store landmarks data in the scene node if available
                if (this.currentSceneNode) {
                    this.currentSceneNode.setData('landmarks', landmarks);
                    this.currentSceneNode.setData('landmarkMetadata', landmarkResults.metadata);
                }
                
            } else {
                console.warn('⚠️ No landmarks detected from anatomy service');
            }
            
        } catch (error) {
            console.error('❌ Landmark detection failed:', error);
            // Continue without landmarks rather than failing the entire mouse creation
        }
    }

    /**
     * Extract vertex coordinates from Three.js geometry
     */
    _extractVerticesFromGeometry(geometry) {
        const vertices = [];
        const positionAttribute = geometry.getAttribute('position');
        
        if (!positionAttribute) {
            throw new Error('Geometry has no position attribute');
        }
        
        // Extract all vertex positions
        for (let i = 0; i < positionAttribute.count; i++) {
            const x = positionAttribute.getX(i);
            const y = positionAttribute.getY(i);
            const z = positionAttribute.getZ(i);
            vertices.push([x, y, z]);
        }
        
        console.log(`📊 Extracted ${vertices.length} vertices from STL geometry`);
        return vertices;
    }

    /**
     * Create 3D landmark markers as children of mouse mesh
     */
    _createLandmarkMarkers(landmarks, mouseMesh, scale, center) {
        console.log('🎯 Creating 3D landmark markers as children of mouse mesh...');
        
        const landmarkGroup = new THREE.Group();
        landmarkGroup.name = 'landmarks';
        
        const landmarkColors = {
            'nose': 0xFF0000,              // Red
            'tail_tip': 0x0000FF,          // Blue  
            'tail_attachment': 0x0088FF,   // Light blue
            // Commented out other landmarks for now
            // 'left_ear': 0x00FF00,          // Green
            // 'right_ear': 0x00FF00,         // Green
            // 'front_left_foot': 0xFFFF00,   // Yellow
            // 'front_right_foot': 0xFFFF00,  // Yellow
            // 'back_left_foot': 0xFF8800,    // Orange
            // 'back_right_foot': 0xFF8800,   // Orange
            // 'whiskers': 0xFFFFFF,          // White
            // 'eye_center': 0xFF00FF         // Magenta
        };
        
        let landmarkCount = 0;
        
        for (const [landmarkName, landmarkData] of Object.entries(landmarks)) {
            try {
                // Handle both array coordinates and object with position
                let position;
                if (Array.isArray(landmarkData)) {
                    position = landmarkData;
                } else if (landmarkData && Array.isArray(landmarkData.position)) {
                    position = landmarkData.position;
                } else {
                    console.warn(`⚠️ Invalid landmark data for ${landmarkName}:`, landmarkData);
                    continue;
                }
                
                if (position.length !== 3) {
                    console.warn(`⚠️ Invalid position for ${landmarkName}:`, position);
                    continue;
                }
                
                // Create landmark marker
                const markerGeometry = new THREE.SphereGeometry(0.15, 8, 6);
                const markerMaterial = new THREE.MeshLambertMaterial({ 
                    color: landmarkColors[landmarkName] || 0xFF0000,
                    transparent: true,
                    opacity: 0.8
                });
                
                const marker = new THREE.Mesh(markerGeometry, markerMaterial);
                
                // Landmarks are now in local mesh space, so use them directly
                // Apply same centering and scaling as mouse mesh
                marker.position.set(
                    (position[0] - center.x) * scale,
                    (position[1] - center.y) * scale,
                    (position[2] - center.z) * scale
                );
                
                console.log(`🎯 Created landmark: ${landmarkName} at local pos (${marker.position.x.toFixed(2)}, ${marker.position.y.toFixed(2)}, ${marker.position.z.toFixed(2)})`);
                
                marker.name = `landmark_${landmarkName}`;
                landmarkGroup.add(marker);
                landmarkCount++;
                
            } catch (error) {
                console.error(`❌ Failed to create landmark ${landmarkName}:`, error);
            }
        }
        
        if (landmarkCount > 0) {
            mouseMesh.add(landmarkGroup);
            console.log(`✅ Created ${landmarkCount} landmark markers as children of mouse mesh`);
        } else {
            console.warn('⚠️ No landmark markers were created');
        }
    }

    /**
     * Orient mouse based on detected landmarks
     */
    _orientMouseFromLandmarks(landmarks, mouseMesh, scale, center) {
        console.log('🧭 Orienting mouse based on landmark detection...');
        
        try {
            const nose = landmarks.nose;
            const tailTip = landmarks.tail_tip;
            // Commented out other landmarks for now
            // const leftEar = landmarks.left_ear;
            // const rightEar = landmarks.right_ear;
            
            if (!nose || !tailTip) {
                console.warn('⚠️ Missing nose or tail landmarks for orientation');
                return;
            }
            
            console.log(`🎯 Landmark positions:
                Nose: [${nose[0].toFixed(3)}, ${nose[1].toFixed(3)}, ${nose[2].toFixed(3)}]
                Tail: [${tailTip[0].toFixed(3)}, ${tailTip[1].toFixed(3)}, ${tailTip[2].toFixed(3)}]`);
            
            // Calculate current nose-to-tail vector in STL coordinates
            const noseVec = new THREE.Vector3(nose[0], nose[1], nose[2]);
            const tailVec = new THREE.Vector3(tailTip[0], tailTip[1], tailTip[2]);
            const currentForward = new THREE.Vector3().subVectors(noseVec, tailVec).normalize();
            
            console.log(`🧭 Current forward vector: [${currentForward.x.toFixed(3)}, ${currentForward.y.toFixed(3)}, ${currentForward.z.toFixed(3)}]`);
            
            // Target forward direction (+Z)
            const targetForward = new THREE.Vector3(0, 0, 1);
            
            // Calculate rotation needed to align current forward with target forward
            const quaternion = new THREE.Quaternion().setFromUnitVectors(currentForward, targetForward);
            mouseMesh.quaternion.copy(quaternion);
            
            // Reset position before applying new positioning
            mouseMesh.position.set(0, 0, 0);
            
            // Simplified positioning - just center the mouse for now
            // Position mouse so feet are on floor (Y=0) - commented out for now since no foot landmarks
            /*
            const pawPositions = [
                landmarks.front_left_foot,
                landmarks.front_right_foot,
                landmarks.back_left_foot,
                landmarks.back_right_foot
            ].filter(Boolean);
            
            if (pawPositions.length > 0) {
                // Find the lowest paw Y coordinate
                const lowestPawY = Math.min(...pawPositions.map(paw => paw[1]));
                // Offset so that the lowest paws touch the floor (Y=0)
                const floorOffset = -lowestPawY * scale;
                mouseMesh.position.y = floorOffset;
                
                console.log(`👾 Positioned mouse with feet on floor: lowest paw at Y=${lowestPawY.toFixed(3)}, offset=${floorOffset.toFixed(3)}`);
            } else {
            */
                // Fallback: estimate foot position from nose/tail difference
                const estimatedFootHeight = Math.abs((nose[1] - tailTip[1]) * 0.3 * scale);
                mouseMesh.position.y = estimatedFootHeight;
                console.log(`👾 Estimated foot position: Y=${estimatedFootHeight.toFixed(3)}`);
            // }
            
            // Center mouse on XZ plane (eye center should be at origin in XZ)
            mouseMesh.position.x = 0;
            mouseMesh.position.z = 0;
            
            console.log(`🧭 Mouse positioned: [${mouseMesh.position.x.toFixed(3)}, ${mouseMesh.position.y.toFixed(3)}, ${mouseMesh.position.z.toFixed(3)}]`);
            console.log(`🔄 Rotation applied: [${(mouseMesh.rotation.x * 180/Math.PI).toFixed(1)}°, ${(mouseMesh.rotation.y * 180/Math.PI).toFixed(1)}°, ${(mouseMesh.rotation.z * 180/Math.PI).toFixed(1)}°]`);
            
        } catch (error) {
            console.error('❌ Failed to orient mouse from landmarks:', error);
        }
    }

    /**
     * Create generic object
     */
    _createGeneric(sceneNode) {
        const group = new THREE.Group();
        group.name = sceneNode.name;
        
        // Simple cube placeholder
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshLambertMaterial({ color: 0xffffff });
        const mesh = new THREE.Mesh(geometry, material);
        group.add(mesh);
        
        return group;
    }
    
    /**
     * Clear all objects from scene
     */
    _clearScene() {
        console.log('🧹 Clearing scene - removing', this.renderObjects.size, 'objects');
        
        // Remove all render objects from scene
        for (const [nodeId, renderObject] of this.renderObjects.entries()) {
            console.log('🗑️ Removing render object:', nodeId, renderObject.name);
            this.scene.remove(renderObject);
            this._disposeObject(renderObject);
        }
        
        // Clear tracking
        this.renderObjects.clear();
        console.log('✅ Scene cleared');
    }
    
    /**
     * Remove specific node
     */
    removeNode(nodeId) {
        const renderObject = this.renderObjects.get(nodeId);
        if (renderObject) {
            this.scene.remove(renderObject);
            this._disposeObject(renderObject);
            this.renderObjects.delete(nodeId);
            console.log(`🗑️ Removed render object: ${nodeId}`);
        }
    }
    
    /**
     * Setup basic lighting
     */
    _setupLighting() {
        // High-performance lighting setup
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Main directional light (no shadows for better performance)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 10);
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
        fillLight.position.set(-10, 10, -10);
        this.scene.add(fillLight);
        
        console.log('💡 High-performance lighting setup complete');
    }
    
    /**
     * Dispose Three.js object
     */
    _disposeObject(object) {
        object.traverse((child) => {
            if (child.geometry) {
                child.geometry.dispose();
            }
            if (child.material) {
                if (Array.isArray(child.material)) {
                    child.material.forEach(material => material.dispose());
                } else {
                    child.material.dispose();
                }
            }
        });
    }
    
    /**
     * Render frame
     */
    render() {
        this.stats.renderCalls++;
        this.renderer.render(this.scene, this.camera);
    }
    
    /**
     * Get stats
     */
    getStats() {
        return {
            ...this.stats,
            renderObjectCount: this.renderObjects.size
        };
    }
    
    /**
     * Clean up
     */
    dispose() {
        this._clearScene();
        this.materials.clear();
        this.geometries.clear();
        console.log('🗑️ RenderingSystem disposed');
    }
}