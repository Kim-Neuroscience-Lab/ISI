// panelManager.js - Shared Panel Management Module
// ARCHITECTURAL PURITY: Single source of truth for panel behavior across all pages

export class PanelManager {
    constructor() {
        this.PANEL_INITIAL_STATES = {
            'left-panel': false,    // false = visible, true = collapsed
            'right-panel': false    // false = visible, true = collapsed  
        };
    }

    init() {
        console.log('CANONICAL PANEL ARCHITECTURE - Single Source of Truth');
        
        const cornerToggleLeft = document.getElementById('corner-toggle-left');
        const cornerToggleRight = document.getElementById('corner-toggle-right');
        
        console.log('CANONICAL PANEL DISCOVERY:');
        console.log('  corner-toggle-left:', !!cornerToggleLeft);
        console.log('  corner-toggle-right:', !!cornerToggleRight);
        
        // SoC ARCHITECTURE: Initialize all panels to explicit state using CSS classes only
        Object.entries(this.PANEL_INITIAL_STATES).forEach(([panelId, shouldBeCollapsed]) => {
            const panel = document.getElementById(panelId);
            if (panel) {
                // SoC ARCHITECTURE: Clean slate - remove all state classes
                panel.classList.remove('js-hidden', 'js-visible');
                
                // SoC: Set explicit initial state with proper CSS classes
                if (shouldBeCollapsed) {
                    panel.classList.add('js-hidden');
                } else {
                    panel.classList.add('js-visible');
                }
                
                console.log(`SoC STATE: ${panelId} = ${shouldBeCollapsed ? 'COLLAPSED' : 'VISIBLE'}`);
                console.log(`SoC VERIFICATION: ${panelId}`, {
                    hasHiddenClass: panel.classList.contains('js-hidden'),
                    hasVisibleClass: panel.classList.contains('js-visible'),
                    computedDisplay: getComputedStyle(panel).display,
                    classList: panel.classList.toString()
                });
            } else {
                console.error(`ARCHITECTURAL VIOLATION: Panel ${panelId} not found in DOM`);
            }
        });
        
        // Initialize corner toggle button visibility
        this.updateCornerToggleVisibility();
        
        // ARCHITECTURAL PURITY: Direct button assignments (no iteration ambiguity)
        if (cornerToggleLeft) {
            cornerToggleLeft.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.togglePanelCanonical('left-panel', 'corner-toggle-left');
            });
            console.log('CANONICAL BINDING: corner-toggle-left → left-panel');
        }
        
        if (cornerToggleRight) {
            cornerToggleRight.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.togglePanelCanonical('right-panel', 'corner-toggle-right');
            });
            console.log('CANONICAL BINDING: corner-toggle-right → right-panel');
        }
        
        // ARCHITECTURAL PRINCIPLE: Generic panel toggles (X buttons) use same canonical system
        const panelToggles = document.querySelectorAll('.panel-toggle');
        console.log(`CANONICAL X-TOGGLES: Found ${panelToggles.length} generic toggles`);
        
        panelToggles.forEach((button, index) => {
            const targetId = button.getAttribute('data-target');
            if (targetId) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.togglePanelCanonical(targetId, `x-button-${index}`);
                });
                console.log(`CANONICAL X-BINDING: panel-toggle[${index}] → ${targetId}`);
            } else {
                console.error(`ARCHITECTURAL VIOLATION: panel-toggle[${index}] missing data-target`);
            }
        });
        
        console.log('CANONICAL PANEL ARCHITECTURE COMPLETE - Geometric purity achieved');
    }

    // ARCHITECTURAL PURITY: JavaScript handles behavioral logic, CSS handles visual styling
    togglePanelCanonical(panelId, sourceButtonId) {
        console.log(`CANONICAL TOGGLE: ${panelId} (source: ${sourceButtonId})`);
        
        const panel = document.getElementById(panelId);
        if (!panel) {
            console.error(`ARCHITECTURAL VIOLATION: Panel ${panelId} does not exist`);
            return;
        }
        
        // SoC ARCHITECTURE: JavaScript controls behavior via CSS classes only
        const isCurrentlyVisible = !panel.classList.contains('js-hidden');
        
        console.log(`BEFORE TOGGLE:`, {
            hasHiddenClass: panel.classList.contains('js-hidden'),
            hasVisibleClass: panel.classList.contains('js-visible'),
            isVisible: isCurrentlyVisible,
            computedDisplay: getComputedStyle(panel).display,
            classList: panel.classList.toString()
        });
        
        // PERFECT SoC: JavaScript only manages CSS classes, never style properties
        // ARCHITECTURAL FIX: Explicit state management to prevent inconsistent states
        if (isCurrentlyVisible) {
            // Hide panel - Pure CSS class management
            panel.classList.remove('js-visible');
            panel.classList.add('js-hidden');
        } else {
            // Show panel - Pure CSS class management with explicit visibility
            panel.classList.remove('js-hidden');
            panel.classList.add('js-visible');
        }
        
        const isNowVisible = !panel.classList.contains('js-hidden');
        
        console.log(`AFTER TOGGLE:`, {
            hasHiddenClass: panel.classList.contains('js-hidden'),
            hasVisibleClass: panel.classList.contains('js-visible'),
            isVisible: isNowVisible,
            computedDisplay: getComputedStyle(panel).display,
            classList: panel.classList.toString()
        });
        
        console.log(`CANONICAL STATE TRANSITION: ${panelId}`);
        console.log(`   BEFORE: ${isCurrentlyVisible ? 'VISIBLE' : 'HIDDEN'}`);
        console.log(`   AFTER:  ${isNowVisible ? 'VISIBLE' : 'HIDDEN'}`);
        console.log(`   BEHAVIORAL LOGIC: ${isCurrentlyVisible ? 'HIDE' : 'SHOW'} via explicit CSS classes`);
        
        // Update corner toggle button visibility
        this.updateCornerToggleVisibility();
        
        // Update status message if function exists
        if (typeof updateStatusMessage === 'function') {
            updateStatusMessage(`${panelId.replace('-', ' ')} ${isNowVisible ? 'expanded' : 'collapsed'}`, 'info');
        }
    }
    
    // ARCHITECTURAL PRINCIPLE: Corner toggle button management
    updateCornerToggleVisibility() {
        const leftPanel = document.getElementById('left-panel');
        const rightPanel = document.getElementById('right-panel');
        const cornerToggleLeft = document.getElementById('corner-toggle-left');
        const cornerToggleRight = document.getElementById('corner-toggle-right');
        
        // Show corner toggle when corresponding panel is hidden
        if (leftPanel && cornerToggleLeft) {
            const leftPanelHidden = leftPanel.classList.contains('js-hidden');
            if (leftPanelHidden) {
                cornerToggleLeft.classList.remove('js-hidden');
                cornerToggleLeft.classList.add('js-visible');
            } else {
                cornerToggleLeft.classList.remove('js-visible');
                cornerToggleLeft.classList.add('js-hidden');
            }
        }
        
        if (rightPanel && cornerToggleRight) {
            const rightPanelHidden = rightPanel.classList.contains('js-hidden');
            if (rightPanelHidden) {
                cornerToggleRight.classList.remove('js-hidden');
                cornerToggleRight.classList.add('js-visible');
            } else {
                cornerToggleRight.classList.remove('js-visible');
                cornerToggleRight.classList.add('js-hidden');
            }
        }
    }
}

// Export for use in other modules
export default PanelManager; 