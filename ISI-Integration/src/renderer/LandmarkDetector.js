// ISI-Integration/src/renderer/LandmarkDetector.js

import * as THREE from 'three';
import { UnifiedAPIClient } from './services/UnifiedAPIClient.js';

// Create API client instance
const apiClient = new UnifiedAPIClient();

/**
 * Handles communication with Python backend for landmark detection
 * ALL computation is done in Python - this only handles API calls and data marshaling
 */
export class LandmarkDetector {
    /**
     * Detect anatomical landmarks using Python backend
     * @param {THREE.Mesh} mouseMesh - The mouse model mesh
     * @returns {Object} Object containing detected landmarks
     */
    static async findMouseAnatomicalLandmarks(mouseMesh) {
        console.log("🔍 Detecting landmarks via Python backend...");
        
        try {
            // Validate input mesh
            if (!mouseMesh || !mouseMesh.geometry || !mouseMesh.geometry.attributes.position) {
                throw new Error("Invalid mesh provided for landmark detection");
            }

            // Extract mesh vertices for backend processing
            const vertices = this.extractMeshVertices(mouseMesh);
            console.log(`📊 Extracted ${vertices.length} vertices for backend processing`);

            // Use unified API client for landmark detection
            const landmarks = await apiClient.detectLandmarks(vertices);
            
            if (!landmarks) {
                throw new Error("Backend returned no landmarks");
            }

            console.log("✅ Landmark detection completed via Python backend");
            return landmarks;

        } catch (error) {
            console.error("❌ Python backend landmark detection failed:", error);
            throw error;
        }
    }

    /**
     * Extract vertices from THREE.js mesh for backend processing
     * @param {THREE.Mesh} mesh - Three.js mesh
     * @returns {Array} Array of [x, y, z] vertex coordinates
     */
    static extractMeshVertices(mesh) {
        const vertices = [];
        const geometry = mesh.geometry;
        const positionAttribute = geometry.attributes.position;
        
        // Extract vertices in local mesh space (no world transform)
        // This ensures landmarks are returned in the same coordinate space as the mesh
        for (let i = 0; i < positionAttribute.count; i++) {
            const vertex = new THREE.Vector3();
            vertex.fromBufferAttribute(positionAttribute, i);
            // DO NOT apply world matrix - keep in local space
            vertices.push([vertex.x, vertex.y, vertex.z]);
        }
        
        return vertices;
    }
} 