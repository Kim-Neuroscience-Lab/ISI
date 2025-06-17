// app.js - ISI Application Entry Point with Canonical Architecture
import PanelManager from './panelManager.js';

// Lazy import for ApplicationOrchestrator (only when needed for 3D visualization)
let ApplicationOrchestrator = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Starting ISI Application');
    // Initialize the application
    initApp();
});

// Global application orchestrator instance
let orchestrator = null;
let stats = {
    fps: 0,
    nodeCount: 0,
    triangles: 0
};
let panelManager = null;

async function initApp() {
    try {
        console.log('Initializing ISI Application with Canonical Architecture...');
        
        // Initialize panel management
        panelManager = new PanelManager();
        panelManager.init();
        
        // Ensure scene tree is visible and properly configured
        ensureSceneTreeVisible();
        
        // Initialize 3D visualization with slight delay to allow layout
        await new Promise(resolve => setTimeout(resolve, 100));
        await initVisualization();
        
        // Initialize other controls
        initControls();
        
        // Initialize tab functionality
        initTabs();
        
        // Initialize keyboard shortcuts
        initKeyboardShortcuts();
        
        // Start performance monitoring
        startStatsMonitoring();
        
        console.log('ISI Application initialized successfully');
        
    } catch (error) {
        console.error('Failed to initialize ISI Application:', error);
        updateStatusMessage('Application initialization failed', 'error');
    }
}

function ensureSceneTreeVisible() {
    console.log('CANONICAL SCENE TREE ARCHITECTURE');
    
    const rightPanel = document.getElementById('right-panel');
    if (!rightPanel) {
        console.error('ARCHITECTURAL VIOLATION: right-panel element not found');
        return;
    }
    
    // ARCHITECTURAL PRINCIPLE: Explicit state verification
    console.log('CANONICAL SCENE TREE STATE VERIFICATION:');
    console.log('  Initial classList:', rightPanel.classList.toString());
    console.log('  Initial computed width:', getComputedStyle(rightPanel).width);
    console.log('  Initial computed transform:', getComputedStyle(rightPanel).transform);
    console.log('  Initial computed display:', getComputedStyle(rightPanel).display);
    
    // CANONICAL STATE: Ensure explicit visibility
    // SoC ARCHITECTURE: Ensure panel is visible via proper CSS class management
    rightPanel.classList.remove('js-hidden');
    rightPanel.classList.add('js-visible');
    
    const sceneTreeContainer = document.getElementById('scene-tree-container');
    if (!sceneTreeContainer) {
        console.error('ARCHITECTURAL VIOLATION: scene-tree-container not found');
        return;
    }
    
    // SoC ARCHITECTURE: Pure HTML structure with CSS classes only
    const CANONICAL_SCENE_TREE_CONTENT = `
        <div class="scene-tree-header">
            <div class="scene-tree-stats">
                Scene Objects: 0
            </div>
        </div>
        <div class="scene-tree-placeholder">
            <div class="scene-tree-placeholder-icon">Scene Tree</div>
            <div class="scene-tree-placeholder-title">Scene Tree</div>
            <div class="scene-tree-placeholder-description">Objects will appear here when loaded</div>
        </div>
    `;
    
    // ARCHITECTURAL PURITY: Set deterministic content
    sceneTreeContainer.innerHTML = CANONICAL_SCENE_TREE_CONTENT;
    console.log('Scene tree content set. Container HTML:', sceneTreeContainer.innerHTML.substring(0, 100) + '...');
    
    // GEOMETRIC VERIFICATION: Final state confirmation
    console.log('CANONICAL SCENE TREE FINAL STATE:');
    console.log('  Final classList:', rightPanel.classList.toString());
    console.log('  Final computed width:', getComputedStyle(rightPanel).width);
    console.log('  Final computed transform:', getComputedStyle(rightPanel).transform);
    console.log('  Content length:', sceneTreeContainer.innerHTML.length);
    
    console.log('CANONICAL SCENE TREE ARCHITECTURE COMPLETE');
}

function debugCanvasState() {
    console.log('🔍 CANVAS DEBUG STATE:');
    
    const container = document.getElementById('visualization-container');
    if (!container) {
        console.log('❌ Container not found');
        return;
    }
    
    console.log('📦 Container:', {
        exists: !!container,
        children: container.children.length,
        clientWidth: container.clientWidth,
        clientHeight: container.clientHeight,
        style: container.style.cssText
    });
    
    // Look for canvas elements
    const canvases = container.querySelectorAll('canvas');
    console.log(`🎨 Found ${canvases.length} canvas elements`);
    
    canvases.forEach((canvas, index) => {
        console.log(`Canvas ${index}:`, {
            width: canvas.width,
            height: canvas.height,
            clientWidth: canvas.clientWidth,
            clientHeight: canvas.clientHeight,
            style: canvas.style.cssText,
            visible: canvas.offsetParent !== null
        });
    });
    
    // Check if orchestrator exists and has renderer
    if (orchestrator) {
        console.log('🎭 Orchestrator state:', {
            exists: !!orchestrator,
            initialized: orchestrator.state?.initialized,
            running: orchestrator.state?.running,
            sceneChildren: orchestrator.scene?.children?.length,
            rendererExists: !!orchestrator.renderer,
            cameraPosition: orchestrator.camera?.position
        });
    } else {
        console.log('❌ Orchestrator not found');
    }
}

async function initVisualization() {
    console.log('🎬 Initializing 3D visualization with canonical architecture...');
    
    // Get the actual DOM element, not just the ID string
    const containerElement = document.getElementById('visualization-container');
    console.log('🔍 Found container element:', containerElement);
    console.log('🔍 Container in DOM:', !!containerElement);
    console.log('🔍 Container parent:', containerElement?.parentElement);
    
    if (!containerElement) {
        console.error('❌ Visualization container element not found - cannot initialize 3D visualization');
        return;
    }
    
    // Check if container has dimensions
    const rect = containerElement.getBoundingClientRect();
    console.log('🔍 Container dimensions:', { width: rect.width, height: rect.height });
    console.log('🔍 Container computed style:', containerElement ? getComputedStyle(containerElement) : 'null');
    
    // Container check already done above - this is redundant
    // Remove this duplicate check
    
    // Dynamically import ApplicationOrchestrator only when needed
    if (!ApplicationOrchestrator) {
        try {
            console.log('📦 Loading ApplicationOrchestrator module...');
            const module = await import('./core/ApplicationOrchestrator.js');
            ApplicationOrchestrator = module.ApplicationOrchestrator;
            console.log('✅ ApplicationOrchestrator module loaded successfully');
        } catch (error) {
            console.error('❌ Failed to load ApplicationOrchestrator:', error);
            updateStatusMessage('3D visualization not available', 'warning');
            return;
        }
    }
    
    try {
        // Prevent multiple orchestrator creation
        if (orchestrator) {
            console.warn('⚠️ Orchestrator already exists, disposing old one first');
            orchestrator.dispose();
            orchestrator = null;
        }
        
        // Create application orchestrator instance
        console.log('🏗️ Creating ApplicationOrchestrator instance...');
        orchestrator = new ApplicationOrchestrator();
        console.log('✅ ApplicationOrchestrator instance created');
        
        // Initialize the orchestrator to set up the default scene
        console.log('🚀 Initializing ApplicationOrchestrator...');
        await orchestrator.initialize(containerElement);
        console.log('✅ ApplicationOrchestrator initialized successfully');
        
        // Debug canvas state after initialization
        debugCanvasState();
        
        // Force an immediate render to ensure objects appear
        console.log('🎯 Forcing immediate render after initialization...');
        if (orchestrator && orchestrator.renderingSystem) {
            orchestrator.renderingSystem.render();
            console.log('✅ Initial render completed');
        }
        
        console.log('📋 Loading setup parameters...');
        // Load current parameters
        await loadSetupParameters();
        console.log('✅ Setup parameters loaded');
        
        console.log('🎉 3D visualization initialized successfully');
        
        // Force an immediate scene tree update
        console.log('🌳 Forcing initial scene tree update...');
        updateSceneTree();
        
        // Debug canvas state again after everything is done
        setTimeout(() => {
            console.log('🔍 FINAL CANVAS STATE CHECK:');
            debugCanvasState();
        }, 1000);
        
    } catch (error) {
        console.error('❌ Failed to initialize 3D visualization:', error);
        updateStatusMessage('3D visualization initialization failed', 'error');
    }
}

function initControls() {
    console.log('Initializing other controls...');
    
    const visualizeButton = document.getElementById('visualize-button');
    const landmarksCheckbox = document.getElementById('landmarks-checkbox');
    const wireframeToggle = document.getElementById('wireframe-toggle');
    const fullscreenToggle = document.getElementById('fullscreen-toggle');
    const resetCameraBtn = document.getElementById('reset-camera');
    
    // Main visualization update (keep button for manual refresh if needed)
    if (visualizeButton) {
        visualizeButton.addEventListener('click', debounce(updateVisualization, 300));
    }
    
    // Landmark visibility toggle
    if (landmarksCheckbox) {
        landmarksCheckbox.addEventListener('change', (e) => {
            if (orchestrator) {
                // Control landmark visibility through the canonical architecture
                orchestrator.setLandmarkVisibility(e.target.checked);
                updateStatusMessage(`Landmarks ${e.target.checked ? 'shown' : 'hidden'}`, 'info');
            }
        });
    }
    
    // Wireframe toggle
    if (wireframeToggle) {
        wireframeToggle.addEventListener('click', toggleWireframe);
    }
    
    // Fullscreen toggle
    if (fullscreenToggle) {
        fullscreenToggle.addEventListener('click', toggleFullscreen);
    }
    
    // Reset camera button
    if (resetCameraBtn) {
        resetCameraBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('CANONICAL CAMERA RESET');
            if (orchestrator) {
                orchestrator.resetCamera();
                updateStatusMessage('Camera reset to canonical position', 'info');
            }
        });
        console.log('CANONICAL BINDING: reset-camera → orchestrator.resetCamera');
    }
    
    // AUTOMATIC PARAMETER UPDATES - Real-time visualization updates
    initParameterListeners();
    
    console.log('Other controls initialized');
}

function initParameterListeners() {
    console.log('Setting up automatic parameter update listeners...');
    
    // Get all parameter input elements
    const parameterInputs = [
        // Monitor parameters
        'monitor_orientation',
        'monitor_width', 
        'monitor_height',
        'monitor_distance',
        'monitor_elevation',
        'monitor_rotation',
        
        // Mouse parameters
        'mouse_length',
        'mouse_eye_height',
        'mouse_visual_field_vertical',
        'mouse_visual_field_horizontal',
        'perpendicular_bisector_height',
        
        // Transform parameters
        'transform_type'
    ];
    
    // Debounced update function for smooth real-time updates
    const debouncedUpdate = debounce(updateVisualization, 150);
    
    parameterInputs.forEach(paramId => {
        const element = document.getElementById(paramId);
        if (element) {
            // Handle different input types
            if (element.type === 'range' || element.type === 'number') {
                // For sliders and number inputs, update on input (real-time)
                element.addEventListener('input', () => {
                    console.log(`Parameter changed: ${paramId} = ${element.value}`);
                    debouncedUpdate();
                });
            } else if (element.tagName.toLowerCase() === 'select') {
                // For dropdowns, update immediately on change
                element.addEventListener('change', () => {
                    console.log(`Parameter changed: ${paramId} = ${element.value}`);
                    updateVisualization();
                });
            } else {
                // For other inputs, update on change
                element.addEventListener('change', () => {
                    console.log(`Parameter changed: ${paramId} = ${element.value}`);
                    debouncedUpdate();
                });
            }
            
            console.log(`✅ Auto-update listener added for: ${paramId}`);
        } else {
            console.warn(`⚠️ Parameter input not found: ${paramId}`);
        }
    });
    
    console.log('Automatic parameter update listeners configured');
}

function initTabs() {
    console.log('Initializing tab functionality...');
    
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`Found ${tabButtons.length} tab buttons and ${tabContents.length} tab contents`);
    
    if (tabButtons.length === 0) {
        console.log('No tab buttons found - using single page layout');
        return;
    }
    
    // ARCHITECTURAL FIX: Ensure initial state is correct
    // Make sure only the setup tab is active initially
    tabContents.forEach(content => {
        content.classList.remove('js-active');
    });
    
    const setupTab = document.getElementById('setup-tab');
    if (setupTab) {
        setupTab.classList.add('js-active');
    }
    
    // SoC ARCHITECTURE: Pure CSS class-based state management
    tabButtons.forEach(button => {
        button.addEventListener('mouseenter', (e) => {
            if (!e.currentTarget.classList.contains('js-active')) {
                e.currentTarget.classList.add('js-hover');
            }
        });
        
        button.addEventListener('mouseleave', (e) => {
            if (!e.currentTarget.classList.contains('js-active')) {
                e.currentTarget.classList.remove('js-hover');
            }
        });
        
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = e.currentTarget.dataset.tab;
            console.log(`Tab clicked: ${targetTab}`);
            
            if (!targetTab) {
                console.error('Tab button missing data-tab attribute');
                return;
            }
            
            // SoC: Remove active state from all tabs using CSS classes only
            tabButtons.forEach(btn => {
                btn.classList.remove('js-active', 'js-hover');
            });
            
            // SoC: Hide all tab contents using CSS classes only
            tabContents.forEach(content => {
                content.classList.remove('js-active');
            });
            
            // SoC: Activate clicked tab using CSS classes only
            e.currentTarget.classList.add('js-active');
            e.currentTarget.classList.remove('js-hover');
            
            // SoC: Show corresponding content using CSS classes only
            const targetContent = document.getElementById(`${targetTab}-tab`);
            if (targetContent) {
                targetContent.classList.add('js-active');
                console.log(`Activated tab content: ${targetTab}-tab`);
            } else {
                console.error(`Tab content not found: ${targetTab}-tab`);
            }
            
            // Update status message
            const tabName = targetTab.charAt(0).toUpperCase() + targetTab.slice(1);
            updateStatusMessage(`Switched to ${tabName} tab`, 'info');
            
            console.log(`Switched to ${tabName} tab`);
        });
    });
    
    console.log('Tab functionality initialized');
}

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Don't trigger when typing in inputs
        if (event.target.tagName.toLowerCase() === 'input' || 
            event.target.tagName.toLowerCase() === 'select') return;
        
        switch (event.key.toLowerCase()) {
            case 'h':
                event.preventDefault();
                if (orchestrator) {
                    const checkbox = document.getElementById('landmarks-checkbox');
                    if (checkbox) {
                        checkbox.checked = !checkbox.checked;
                        orchestrator.setLandmarkVisibility(checkbox.checked);
                        updateStatusMessage(`Landmarks ${checkbox.checked ? 'shown' : 'hidden'}`, 'info');
                    }
                }
                break;
                
            case 'r':
                event.preventDefault();
                if (orchestrator) {
                    orchestrator.resetCamera();
                    updateStatusMessage('Camera reset', 'info');
                }
                break;
                
            case 'w':
                event.preventDefault();
                toggleWireframe();
                break;
                
            case 'f':
                event.preventDefault();
                toggleFullscreen();
                break;
                
            case '?':
                event.preventDefault();
                showHelp();
                break;
        }
    });
}

// Utility function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function updateVisualization() {
    if (!orchestrator) {
        console.error('ApplicationOrchestrator not initialized');
        return;
    }
    
    try {
        console.log('Updating visualization...');
        
        // Get current parameters from UI
        const params = getSetupParameters();
        
        // Update visualization through canonical architecture
        await orchestrator.updateVisualization(params);
        
        updateStatusMessage('Visualization updated successfully', 'success');
        console.log('Visualization updated successfully');
    } catch (error) {
        console.error('Failed to update visualization:', error);
        updateStatusMessage('Failed to update visualization', 'error');
    }
}

async function loadSetupParameters() {
    // Load default parameters - this could be from localStorage or API
    const defaultParams = getSetupParameters();
    populateUIFromParameters(defaultParams);
}

function populateUIFromParameters(params) {
    // Populate UI controls with parameter values
    Object.keys(params).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = params[key];
            } else {
                element.value = params[key];
            }
        }
    });
}

function getSetupParameters() {
    return {
        // Monitor parameters
        monitor_orientation: document.getElementById('monitor_orientation')?.value || 'landscape',
        monitor_width: parseFloat(document.getElementById('monitor_width')?.value || '33.53'),
        monitor_height: parseFloat(document.getElementById('monitor_height')?.value || '59.69'),
        monitor_distance: parseFloat(document.getElementById('monitor_distance')?.value || '10'),
        monitor_elevation: parseFloat(document.getElementById('monitor_elevation')?.value || '20'),
        monitor_rotation: parseFloat(document.getElementById('monitor_rotation')?.value || '0'),
        
        // Mouse parameters
        mouse_length: parseFloat(document.getElementById('mouse_length')?.value || '7.5'),
        mouse_eye_height: parseFloat(document.getElementById('mouse_eye_height')?.value || '5'),
        mouse_visual_field_vertical: parseFloat(document.getElementById('mouse_visual_field_vertical')?.value || '110'),
        mouse_visual_field_horizontal: parseFloat(document.getElementById('mouse_visual_field_horizontal')?.value || '140'),
        perpendicular_bisector_height: parseFloat(document.getElementById('perpendicular_bisector_height')?.value || '30'),
        
        // Transform parameters
        transform_type: document.getElementById('transform_type')?.value || 'angular-grid',
        
        // Display parameters
        show_landmarks: document.getElementById('landmarks-checkbox')?.checked || true
    };
}

function toggleWireframe() {
    if (orchestrator) {
        orchestrator.toggleWireframe();
        updateStatusMessage('Wireframe toggled', 'info');
    }
}

function toggleFullscreen() {
    const container = document.getElementById('visualization-container');
    if (!document.fullscreenElement) {
        container.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function startStatsMonitoring() {
    setInterval(updateStats, 1000);
}

function updateStats() {
    if (orchestrator) {
        const sceneStats = orchestrator.getSceneStats();
        
        const newNodeCount = sceneStats.nodeCount || 0;
        const newTriangles = sceneStats.triangles || 0;
        
        // Only update if stats have changed
        const statsChanged = (stats.nodeCount !== newNodeCount) || (stats.triangles !== newTriangles);
        
        stats.nodeCount = newNodeCount;
        stats.triangles = newTriangles;
        
        // Update UI
        const fpsElement = document.getElementById('fps-counter');
        const nodeCountElement = document.getElementById('node-count');
        const renderStatsElement = document.getElementById('render-stats');
        
        if (fpsElement) {
            // FPS would need to be calculated from render loop
            fpsElement.textContent = '60 FPS';
        }
        
        if (nodeCountElement) {
            nodeCountElement.textContent = `${stats.nodeCount} Objects`;
        }
        
        if (renderStatsElement) {
            renderStatsElement.textContent = `Triangles: ${stats.triangles}`;
        }
        
        // Update camera position
        const cameraPos = orchestrator.getCameraPosition();
        const cameraPosElement = document.getElementById('camera-position');
        if (cameraPosElement && cameraPos) {
            cameraPosElement.textContent = `Position: (${cameraPos.x.toFixed(1)}, ${cameraPos.y.toFixed(1)}, ${cameraPos.z.toFixed(1)})`;
        }
        
        // Only update scene tree if stats changed
        if (statsChanged) {
            console.log('📊 Stats changed, updating scene tree...');
            updateSceneTree();
        }
    }
}

function updateSceneTree() {
    const sceneTreeContainer = document.getElementById('scene-tree-container');
    if (!sceneTreeContainer || !orchestrator) {
        return;
    }
    
    // Get all scene nodes from orchestrator
    const allNodes = orchestrator.getAllSceneNodes();
    
    console.log('🌳 Updating scene tree with nodes:', allNodes.map(n => `${n.name} [${n.type}]`));
    
    if (allNodes.length === 0) {
        // Show placeholder
        sceneTreeContainer.innerHTML = `
            <div class="scene-tree-header">
                <div class="scene-tree-stats">Scene Objects: 0</div>
            </div>
            <div class="scene-tree-placeholder">
                <div class="scene-tree-placeholder-icon">Scene Tree</div>
                <div class="scene-tree-placeholder-title">Scene Tree</div>
                <div class="scene-tree-placeholder-description">Objects will appear here when loaded</div>
            </div>
        `;
        return;
    }
    
    // Build scene tree HTML
    let treeHTML = `
        <div class="scene-tree-header">
            <div class="scene-tree-stats">Scene Objects: ${allNodes.length}</div>
        </div>
        <div class="scene-tree-nodes">
    `;
    
    // Add each node to the tree
    allNodes.forEach(node => {
        const visibilityIcon = node.visible ? '👁' : '🚫';
        const categoryClass = `category-${node.type}`;
        
        treeHTML += `
            <div class="scene-tree-node ${categoryClass}" data-node-id="${node.id}">
                <button class="node-visibility" data-node-id="${node.id}" title="Toggle visibility">
                    ${visibilityIcon}
                </button>
                <span class="node-name">${node.name}</span>
                <span class="node-type">[${node.type}]</span>
            </div>
        `;
    });
    
    treeHTML += `
        </div>
        <button class="scene-tree-export">Export Scene Data</button>
    `;
    
    sceneTreeContainer.innerHTML = treeHTML;
    
    // Add event listeners for visibility toggles
    const visibilityButtons = sceneTreeContainer.querySelectorAll('.node-visibility');
    visibilityButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const nodeId = button.getAttribute('data-node-id');
            toggleNodeVisibility(nodeId);
        });
    });
    
    // Add event listeners for node selection
    const nodeElements = sceneTreeContainer.querySelectorAll('.scene-tree-node');
    nodeElements.forEach(element => {
        element.addEventListener('click', (e) => {
            if (e.target.classList.contains('node-visibility')) return;
            
            const nodeId = element.getAttribute('data-node-id');
            selectSceneNode(nodeId);
        });
    });
}

function toggleNodeVisibility(nodeId) {
    if (!orchestrator) return;
    
    const node = orchestrator.getSceneNode(nodeId);
    if (node) {
        node.visible = !node.visible;
        node.emit('visibilityChanged');
        updateSceneTree();
        updateStatusMessage(`${node.name} ${node.visible ? 'shown' : 'hidden'}`, 'info');
        console.log(`🎯 Node visibility toggled: ${node.name} = ${node.visible}`);
    }
}

function selectSceneNode(nodeId) {
    if (!orchestrator) return;
    
    const node = orchestrator.getSceneNode(nodeId);
    if (node) {
        // Remove previous selection
        document.querySelectorAll('.scene-tree-node.selected').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selection to clicked node
        const nodeElement = document.querySelector(`[data-node-id="${nodeId}"]`);
        if (nodeElement) {
            nodeElement.classList.add('selected');
        }
        
        updateStatusMessage(`Selected: ${node.name}`, 'info');
        console.log(`🎯 Node selected: ${node.name} [${node.type}]`);
        
        // Debug: Log node details
        console.log('🔍 Node details:', node.getDebugInfo());
    }
}

function updateStatusMessage(message, type = 'info') {
    const statusElement = document.getElementById('status-message');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `status-${type}`;
        
        // Clear status after 3 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                statusElement.textContent = 'Ready - Press ? for help';
                statusElement.className = '';
            }, 3000);
        }
    }
}

function showHelp() {
    const modal = document.getElementById('help-modal');
    if (modal) {
        modal.classList.remove('hidden');
        
        // Close modal on escape key
        const handleModalEscape = (event) => {
            if (event.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleModalEscape);
            }
        };
        document.addEventListener('keydown', handleModalEscape);
    }
}

function closeModal() {
    const modal = document.getElementById('help-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
    
    // Remove escape key listener
    function handleModalEscape(event) {
        if (event.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', handleModalEscape);
        }
    }
}

// Close modal when clicking the close button or outside the modal
document.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal-close') || 
        event.target.classList.contains('modal')) {
        closeModal();
    }
});