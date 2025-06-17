/**
 * Unified API Client - Single Canonical Interface for Backend Communication
 * 
 * Following Universal Design Philosophy:
 * - Geometric Beauty: Mathematical elegance through unified HTTP abstraction
 * - Canonical Interfaces: Exactly one way to communicate with each backend domain
 * - Architectural Purity: No expedient solutions or HTTP complexity leakage
 * - Domain Fidelity: Reflects essential structure of experimental workflow
 * 
 * This client embodies the "One Way, Many Options" principle:
 * - ONE canonical way to call each backend operation
 * - MANY configuration options for request customization
 * - Implementation substitutability via endpoint configuration
 */

/**
 * Unified API Client - Single source of truth for all backend communication
 * 
 * SOLID Principles:
 * - Single Responsibility: Only handles HTTP communication with backend
 * - Open/Closed: Extensible through endpoint registration
 * - Liskov Substitution: Can replace any HTTP client interface
 * - Interface Segregation: Clean methods for each domain
 * - Dependency Inversion: Depends on fetch abstraction, not specific HTTP library
 * 
 * Geometric Beauty: Elegant composition of HTTP operations with mathematical symmetry
 */
export class UnifiedAPIClient {
    constructor(config = {}) {
        // Canonical configuration with elegant defaults
        this.config = {
            baseURL: config.baseURL || 'http://localhost:8000',
            timeout: config.timeout || 30000,
            retryAttempts: config.retryAttempts || 3,
            retryDelay: config.retryDelay || 1000,
            ...config
        };
        
        // Domain endpoint mapping (Configuration-Driven Flexibility)
        this.endpoints = {
            // Core workflow endpoints
            core: {
                setup: '/api/setup',
                workflow: '/api/workflow'
            },
            
            // Stimulus generation endpoints (ISI-Stimulus domain)
            stimulus: {
                detect_landmarks: '/api/stimulus/landmarks/detect',
                generate: '/api/stimulus/generate',
                preview: '/api/stimulus/preview',
                coordinate_system: '/api/stimulus/coordinate_system'
            },
            
            // Data acquisition endpoints (ISI-Acquisition domain)
            acquisition: {
                initialize: '/api/acquisition/initialize',
                start: '/api/acquisition/start',
                stop: '/api/acquisition/stop',
                status: '/api/acquisition/status',
                preview: '/api/acquisition/preview'
            },
            
            // Data analysis endpoints (ISI-Analysis domain)
            analysis: {
                run: '/api/analysis/run',
                results: '/api/analysis/results',
                reports: '/api/analysis/reports'
            }
        };
        
        // Request interceptors for unified behavior
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        
        console.log('🌐 UnifiedAPIClient initialized with canonical endpoints');
    }
    
    // =============================================================================
    // CANONICAL INTERFACE METHODS - Exactly One Way to Call Each Domain
    // =============================================================================
    
    /**
     * Canonical method for experimental setup operations
     * 
     * Unified Interface: Single way to setup experiments regardless of complexity
     * Domain Fidelity: Reflects essential experimental setup workflow
     */
    async setupExperiment(setupParams) {
        return this._makeCanonicalRequest('core', 'setup', {
            method: 'POST',
            data: setupParams,
            operation: 'setup_experiment'
        });
    }
    
    /**
     * Canonical method for landmark detection (ISI-Stimulus domain)
     * 
     * Single Source of Truth: All landmark detection through this interface
     * Geometric Beauty: Elegant abstraction over mesh processing complexity
     */
    async detectLandmarks(meshVertices, landmarkTypes = null) {
        return this._makeCanonicalRequest('stimulus', 'detect_landmarks', {
            method: 'POST',
            data: {
                vertices: meshVertices,
                landmark_types: landmarkTypes
            },
            operation: 'detect_landmarks'
        });
    }
    
    /**
     * Canonical method for stimulus generation (ISI-Stimulus domain)
     * 
     * Configuration-Driven Flexibility: Rich stimulus variations through config
     * Framework Native: Leverages backend stimulus generation capabilities
     */
    async generateStimulus(stimulusParams, setupParams) {
        return this._makeCanonicalRequest('stimulus', 'generate', {
            method: 'POST',
            data: {
                stimulus_parameters: stimulusParams,
                setup_parameters: setupParams
            },
            operation: 'generate_stimulus'
        });
    }
    
    /**
     * Canonical method for stimulus preview (ISI-Stimulus domain)
     * 
     * Modular Excellence: Preview functionality through principled composition
     */
    async previewStimulus(stimulusParams, setupParams, frameCount = 10) {
        return this._makeCanonicalRequest('stimulus', 'preview', {
            method: 'POST',
            data: {
                stimulus_parameters: stimulusParams,
                setup_parameters: setupParams,
                frame_count: frameCount
            },
            operation: 'preview_stimulus'
        });
    }
    
    /**
     * Canonical method for coordinate system generation (ISI-Stimulus domain)
     * 
     * Domain Integrity: Preserves essential coordinate relationships
     */
    async getStimulusCoordinateSystem(landmarks) {
        return this._makeCanonicalRequest('stimulus', 'coordinate_system', {
            method: 'POST',
            data: { landmarks },
            operation: 'get_coordinate_system'
        });
    }
    
    /**
     * Canonical method for acquisition initialization (ISI-Acquisition domain)
     * 
     * Unified Interface: Single way to initialize acquisition regardless of hardware
     */
    async initializeAcquisition(acquisitionParams) {
        return this._makeCanonicalRequest('acquisition', 'initialize', {
            method: 'POST',
            data: acquisitionParams,
            operation: 'initialize_acquisition'
        });
    }
    
    /**
     * Canonical method for starting data acquisition (ISI-Acquisition domain)
     * 
     * Seamless Integration: Acquisition integrates naturally with stimulus
     */
    async startAcquisition(stimulusFrames) {
        return this._makeCanonicalRequest('acquisition', 'start', {
            method: 'POST',
            data: { stimulus_frames: stimulusFrames },
            operation: 'start_acquisition'
        });
    }
    
    /**
     * Canonical method for stopping data acquisition (ISI-Acquisition domain)
     */
    async stopAcquisition() {
        return this._makeCanonicalRequest('acquisition', 'stop', {
            method: 'POST',
            data: {},
            operation: 'stop_acquisition'
        });
    }
    
    /**
     * Canonical method for acquisition status (ISI-Acquisition domain)
     */
    async getAcquisitionStatus() {
        return this._makeCanonicalRequest('acquisition', 'status', {
            method: 'GET',
            operation: 'get_acquisition_status'
        });
    }
    
    /**
     * Canonical method for camera preview (ISI-Acquisition domain)
     */
    async getCameraPreview() {
        return this._makeCanonicalRequest('acquisition', 'preview', {
            method: 'GET',
            operation: 'get_camera_preview'
        });
    }
    
    /**
     * Canonical method for data analysis (ISI-Analysis domain)
     * 
     * Single Source of Truth: All analysis operations through this interface
     */
    async runAnalysis(acquisitionData, analysisParams) {
        return this._makeCanonicalRequest('analysis', 'run', {
            method: 'POST',
            data: {
                acquisition_data: acquisitionData,
                analysis_parameters: analysisParams
            },
            operation: 'run_analysis'
        });
    }
    
    /**
     * Canonical method for getting analysis results (ISI-Analysis domain)
     */
    async getAnalysisResults(analysisId) {
        return this._makeCanonicalRequest('analysis', 'results', {
            method: 'GET',
            urlParams: { analysis_id: analysisId },
            operation: 'get_analysis_results'
        });
    }
    
    // =============================================================================
    // UNIFIED REQUEST PROCESSING - Mathematical Elegance in HTTP Operations
    // =============================================================================
    
    /**
     * Make canonical request with unified error handling and retry logic
     * 
     * Geometric Beauty: Elegant abstraction over HTTP complexity
     * Fail-Fast Principle: Immediate error detection with clear messages
     */
    async _makeCanonicalRequest(domain, endpoint, options) {
        const startTime = performance.now();
        
        try {
            // Build canonical URL
            const url = this._buildCanonicalURL(domain, endpoint, options.urlParams);
            
            // Prepare canonical request
            const requestConfig = await this._prepareCanonicalRequest(options);
            
            // Execute request with retry logic
            const response = await this._executeWithRetry(url, requestConfig);
            
            // Process canonical response
            const result = await this._processCanonicalResponse(response, options.operation);
            
            // Add timing metadata
            result.metadata = {
                ...result.metadata,
                request_time_ms: performance.now() - startTime,
                domain,
                endpoint,
                operation: options.operation
            };
            
            return result;
            
        } catch (error) {
            console.error(`❌ Canonical request failed [${domain}.${endpoint}]:`, error);
            
            return {
                success: false,
                data: null,
                metadata: {
                    request_time_ms: performance.now() - startTime,
                    domain,
                    endpoint,
                    operation: options.operation,
                    error_type: error.name
                },
                error: error.message
            };
        }
    }
    
    /**
     * Build canonical URL with elegant parameter handling
     */
    _buildCanonicalURL(domain, endpoint, urlParams = {}) {
        let url = `${this.config.baseURL}${this.endpoints[domain][endpoint]}`;
        
        // Handle URL parameters with mathematical precision
        if (urlParams && Object.keys(urlParams).length > 0) {
            const params = new URLSearchParams();
            Object.entries(urlParams).forEach(([key, value]) => {
                if (value !== null && value !== undefined) {
                    params.append(key, value.toString());
                }
            });
            
            if (params.toString()) {
                url += `?${params.toString()}`;
            }
        }
        
        return url;
    }
    
    /**
     * Prepare canonical request with unified configuration
     */
    async _prepareCanonicalRequest(options) {
        const config = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                ...this.config.defaultHeaders
            }
        };
        
        // Add request body for non-GET requests
        if (options.data && options.method !== 'GET') {
            config.body = JSON.stringify(options.data);
        }
        
        // Apply request interceptors
        for (const interceptor of this.requestInterceptors) {
            await interceptor(config, options);
        }
        
        return config;
    }
    
    /**
     * Execute request with elegant retry logic
     */
    async _executeWithRetry(url, config) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
                
                const response = await fetch(url, {
                    ...config,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return response;
                
            } catch (error) {
                lastError = error;
                
                if (attempt < this.config.retryAttempts) {
                    console.warn(`⚠️ Request attempt ${attempt} failed, retrying in ${this.config.retryDelay}ms...`);
                    await this._delay(this.config.retryDelay * attempt); // Exponential backoff
                }
            }
        }
        
        throw lastError;
    }
    
    /**
     * Process canonical response with unified format
     */
    async _processCanonicalResponse(response, operation) {
        try {
            const data = await response.json();
            
            // Apply response interceptors
            for (const interceptor of this.responseInterceptors) {
                await interceptor(data, operation);
            }
            
            // Ensure canonical response format
            if (typeof data.success === 'boolean') {
                return data; // Already in canonical format
            } else {
                // Transform to canonical format
                return {
                    success: true,
                    data: data,
                    metadata: {
                        operation,
                        response_size: JSON.stringify(data).length
                    },
                    error: null
                };
            }
            
        } catch (error) {
            throw new Error(`Failed to parse response: ${error.message}`);
        }
    }
    
    /**
     * Elegant delay utility for retry logic
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // =============================================================================
    // EXTENSIBILITY - Open/Closed Principle Implementation
    // =============================================================================
    
    /**
     * Register request interceptor for unified behavior modification
     * 
     * Open/Closed Principle: Extend functionality without modification
     */
    addRequestInterceptor(interceptor) {
        this.requestInterceptors.push(interceptor);
    }
    
    /**
     * Register response interceptor for unified response processing
     */
    addResponseInterceptor(interceptor) {
        this.responseInterceptors.push(interceptor);
    }
    
    /**
     * Register custom endpoint for domain extension
     * 
     * Configuration-Driven Flexibility: New endpoints without code changes
     */
    registerEndpoint(domain, name, path) {
        if (!this.endpoints[domain]) {
            this.endpoints[domain] = {};
        }
        this.endpoints[domain][name] = path;
        console.log(`🔧 Registered custom endpoint: ${domain}.${name} -> ${path}`);
    }
    
    /**
     * Update configuration for runtime flexibility
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        console.log('⚙️ API client configuration updated');
    }
}

// =============================================================================
// FACTORY FUNCTION - Canonical Client Creation
// =============================================================================

/**
 * Factory function for creating unified API client
 * 
 * Geometric Beauty: Elegant abstraction over client complexity
 * Single Source of Truth: One way to create API clients
 */
export function createUnifiedAPIClient(config = {}) {
    const client = new UnifiedAPIClient(config);
    console.log('🌐 Created unified API client with canonical endpoints');
    return client;
}

// =============================================================================
// SINGLETON INSTANCE - Global Access Pattern
// =============================================================================

let globalAPIClient = null;

/**
 * Get global API client instance (singleton pattern)
 * 
 * Unified Interface: Single global access point for API operations
 * Dependency Inversion: Components depend on this abstraction
 */
export function getGlobalAPIClient(config = {}) {
    if (!globalAPIClient) {
        globalAPIClient = createUnifiedAPIClient(config);
    }
    return globalAPIClient;
}

/**
 * Reset global API client (useful for testing)
 */
export function resetGlobalAPIClient() {
    globalAPIClient = null;
}

// =============================================================================
// CONVENIENCE FUNCTIONS - Configuration-Driven Flexibility
// =============================================================================

/**
 * Create API client with development configuration
 */
export function createDevelopmentAPIClient() {
    return createUnifiedAPIClient({
        baseURL: 'http://localhost:8000',
        timeout: 10000,
        retryAttempts: 2,
        retryDelay: 500
    });
}

/**
 * Create API client with production configuration
 */
export function createProductionAPIClient(baseURL) {
    return createUnifiedAPIClient({
        baseURL,
        timeout: 30000,
        retryAttempts: 3,
        retryDelay: 1000,
        defaultHeaders: {
            'X-Client-Version': '1.0.0'
        }
    });
} 