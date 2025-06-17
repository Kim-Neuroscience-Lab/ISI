/**
 * ServiceManager - Unified Service Registry and Lifecycle Management
 * 
 * Following Universal Design Philosophy:
 * - Geometric Beauty: Elegant service composition and lifecycle management
 * - Single Responsibility: Only manages service registration and access
 * - Canonical Interface: Exactly one way to access each service type
 * - Architectural Purity: Clean service boundaries and dependencies
 * 
 * CRITICAL PRINCIPLE: All services follow unified patterns
 * - Lazy initialization for performance
 * - Singleton pattern for shared resources
 * - Clean disposal for memory management
 * - Configuration-driven behavior
 */

/**
 * Unified Service Manager - Single source of truth for all services
 * 
 * SOLID Principles:
 * - Single Responsibility: Only manages service lifecycle
 * - Open/Closed: Extensible through service registration
 * - Liskov Substitution: All services follow same interface contract
 * - Interface Segregation: Clean service access patterns
 * - Dependency Inversion: Services depend on abstractions
 */
export class ServiceManager {
    constructor() {
        // Service registry (class constructors)
        this.serviceRegistry = new Map();
        
        // Service instances (lazy-initialized)
        this.serviceInstances = new Map();
        
        // Service configuration
        this.serviceConfigs = new Map();
        
        // Register core services
        this._registerCoreServices();
        
        console.log('🔧 ServiceManager initialized - Unified service architecture');
    }
    
    /**
     * Register core services (architectural foundation)
     */
    _registerCoreServices() {
        // Core services are now integrated into RenderingSystem
        // No separate geometry or rendering services needed
        console.log('🏗️ Core services integrated into unified architecture');
    }
    
    /**
     * Register a service class
     */
    registerService(name, ServiceClass, config = {}) {
        this.serviceRegistry.set(name, ServiceClass);
        this.serviceConfigs.set(name, config);
        
        console.log(`📝 Service registered: ${name}`);
    }
    
    /**
     * Get service instance (lazy initialization)
     */
    getService(name, config = {}) {
        // Check if instance already exists
        if (this.serviceInstances.has(name)) {
            return this.serviceInstances.get(name);
        }
        
        // Get service class from registry
        const ServiceClass = this.serviceRegistry.get(name);
        if (!ServiceClass) {
            throw new Error(`Service not registered: ${name}`);
        }
        
        // Merge configuration
        const defaultConfig = this.serviceConfigs.get(name) || {};
        const finalConfig = { ...defaultConfig, ...config };
        
        // Create and cache instance
        const instance = new ServiceClass(finalConfig);
        this.serviceInstances.set(name, instance);
        
        console.log(`🔧 Service instantiated: ${name}`);
        return instance;
    }
    
    /**
     * Check if service is registered
     */
    hasService(name) {
        return this.serviceRegistry.has(name);
    }
    
    /**
     * Get all registered service names
     */
    getRegisteredServices() {
        return Array.from(this.serviceRegistry.keys());
    }
    
    /**
     * Dispose of service instance
     */
    disposeService(name) {
        const instance = this.serviceInstances.get(name);
        if (instance && typeof instance.dispose === 'function') {
            instance.dispose();
        }
        
        this.serviceInstances.delete(name);
        console.log(`🗑️ Service disposed: ${name}`);
    }
    
    /**
     * Dispose of all services
     */
    disposeAll() {
        for (const name of this.serviceInstances.keys()) {
            this.disposeService(name);
        }
        
        console.log('🗑️ All services disposed');
    }
    
    /**
     * Get singleton instance
     */
    static getInstance() {
        if (!ServiceManager._instance) {
            ServiceManager._instance = new ServiceManager();
        }
        return ServiceManager._instance;
    }
    
    /**
     * Reset singleton (for testing)
     */
    static resetInstance() {
        if (ServiceManager._instance) {
            ServiceManager._instance.disposeAll();
            ServiceManager._instance = null;
        }
    }
} 