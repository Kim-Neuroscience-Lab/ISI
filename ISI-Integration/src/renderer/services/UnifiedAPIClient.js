/**
 * Unified API Client - Single Interface for All Backend Communications
 * 
 * Canonical Architecture:
 * - Single Source of Truth for all backend communication
 * - Proper error handling and response validation
 * - Unified interface patterns across all API endpoints
 */

export class UnifiedAPIClient {
    constructor(config = {}) {
        this.config = {
            baseURL: config.baseURL || 'http://localhost:8000',
            timeout: config.timeout || 30000,
            retryAttempts: config.retryAttempts || 3,
            ...config
        };
        
        console.log('🌐 UnifiedAPIClient initialized:', this.config);
    }

    // =============================================================================
    // ANATOMY DETECTION ENDPOINTS
    // =============================================================================

    /**
     * Detect anatomical landmarks from STL mesh vertices
     * 
     * @param {Array} vertices - Array of [x, y, z] vertex coordinates
     * @returns {Promise<Object>} Landmark detection results
     */
    async detectLandmarks(vertices) {
        console.log(`🔬 Requesting landmark detection for ${vertices.length} vertices`);
        
        try {
            const response = await this._makeRequest('/api/landmarks/detect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    vertices: vertices
                })
            });

            if (response.success) {
                console.log('✅ Landmark detection successful:', response.results);
                return response.results;
            } else {
                throw new Error(response.message || 'Landmark detection failed');
            }

        } catch (error) {
            console.error('❌ Landmark detection failed:', error);
            throw error;
        }
    }

    /**
     * Check if anatomy detection service is available
     * 
     * @returns {Promise<boolean>} Service availability status
     */
    async checkAnatomyService() {
        try {
            console.log('🔍 Checking anatomy service availability...');
            
            const response = await this._makeRequest('/api/status', {
                method: 'GET',
                timeout: 5000 // Quick timeout for availability check
            });
            
            console.log('✅ Anatomy detection service available');
            return true;
            
        } catch (error) {
            console.warn('⚠️ Anatomy detection service not available:', error.message);
            return false;
        }
    }

    // =============================================================================
    // EXPERIMENT ENDPOINTS
    // =============================================================================

    /**
     * Setup experiment configuration
     */
    async setupExperiment(experimentConfig) {
        console.log('🔬 Setting up experiment:', experimentConfig);
        
        try {
            const response = await this._makeRequest('/experiment/setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(experimentConfig)
            });

            return response;

        } catch (error) {
            console.error('❌ Experiment setup failed:', error);
            throw error;
        }
    }

    /**
     * Generate stimulus
     */
    async generateStimulus(stimulusParams) {
        console.log('🎨 Generating stimulus:', stimulusParams);
        
        try {
            const response = await this._makeRequest('/stimulus/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(stimulusParams)
            });

            return response;

        } catch (error) {
            console.error('❌ Stimulus generation failed:', error);
            throw error;
        }
    }

    /**
     * Start acquisition
     */
    async startAcquisition(acquisitionParams) {
        console.log('📹 Starting acquisition:', acquisitionParams);
        
        try {
            const response = await this._makeRequest('/acquisition/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(acquisitionParams)
            });

            return response;

        } catch (error) {
            console.error('❌ Acquisition start failed:', error);
            throw error;
        }
    }

    /**
     * Run analysis
     */
    async runAnalysis(analysisParams) {
        console.log('📊 Running analysis:', analysisParams);
        
        try {
            const response = await this._makeRequest('/analysis/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(analysisParams)
            });

            return response;

        } catch (error) {
            console.error('❌ Analysis failed:', error);
            throw error;
        }
    }

    // =============================================================================
    // PRIVATE METHODS
    // =============================================================================

    /**
     * Make HTTP request with unified error handling
     */
    async _makeRequest(endpoint, options = {}) {
        const url = this.config.baseURL + endpoint;
        const timeout = options.timeout || this.config.timeout;
        
        console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`);
        
        try {
            // Create timeout controller
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            
            // Make request
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Parse JSON response
            const data = await response.json();
            console.log(`✅ API Response: ${options.method || 'GET'} ${url}`, data);
            
            return data;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${timeout}ms`);
            }
            throw error;
        }
    }

    /**
     * Validate response format
     */
    _validateResponse(response, requiredFields = []) {
        if (!response || typeof response !== 'object') {
            throw new Error('Invalid response format');
        }
        
        for (const field of requiredFields) {
            if (!(field in response)) {
                throw new Error(`Missing required field: ${field}`);
            }
        }
        
        return true;
    }
}

// Export singleton instance
export const apiClient = new UnifiedAPIClient(); 