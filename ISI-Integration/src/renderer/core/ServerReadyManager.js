/**
 * Server Ready Manager - Coordinates server startup and landmark detection
 */
export class ServerReadyManager {
    constructor() {
        this.isServerReady = false;
        this.pendingLandmarkDetections = [];
        this.readyCallbacks = [];
        
        // Listen for server ready signal from main process
        if (window.api && window.api.onServerReady) {
            window.api.onServerReady(() => {
                console.log('🚀 Server ready signal received!');
                this.markServerReady();
            });
        }
    }
    
    /**
     * Mark server as ready and process pending operations
     */
    markServerReady() {
        this.isServerReady = true;
        
        // Execute all ready callbacks
        this.readyCallbacks.forEach(callback => {
            try {
                callback();
            } catch (error) {
                console.error('❌ Error in server ready callback:', error);
            }
        });
        this.readyCallbacks = [];
        
        // Process pending landmark detections
        console.log(`📋 Processing ${this.pendingLandmarkDetections.length} pending landmark detections...`);
        this.pendingLandmarkDetections.forEach(detection => {
            try {
                detection.callback();
            } catch (error) {
                console.error('❌ Error in pending landmark detection:', error);
            }
        });
        this.pendingLandmarkDetections = [];
    }
    
    /**
     * Register a callback to execute when server is ready
     */
    onServerReady(callback) {
        if (this.isServerReady) {
            // Server already ready, execute immediately
            callback();
        } else {
            // Queue for when server becomes ready
            this.readyCallbacks.push(callback);
        }
    }
    
    /**
     * Queue landmark detection to run when server is ready
     */
    queueLandmarkDetection(callback, description = 'Unknown') {
        if (this.isServerReady) {
            // Server ready, execute immediately
            console.log(`🔬 Server ready - executing landmark detection: ${description}`);
            callback();
        } else {
            // Queue for when server becomes ready
            console.log(`⏳ Server not ready - queuing landmark detection: ${description}`);
            this.pendingLandmarkDetections.push({ callback, description });
        }
    }
    
    /**
     * Check if server is ready
     */
    isReady() {
        return this.isServerReady;
    }
}

// Export singleton instance
export const serverReadyManager = new ServerReadyManager(); 