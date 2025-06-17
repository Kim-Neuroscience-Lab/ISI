// stimulus.js - Stimulus Generation Tab
import PanelManager from './panelManager.js';

let panelManager = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Stimulus Generation Tab Loaded');
    initStimulusTab();
});

function initStimulusTab() {
    console.log('Initializing Stimulus Generation functionality...');
    
    // Initialize panels using shared manager
    panelManager = new PanelManager();
    panelManager.init();
    
    // Initialize stimulus controls
    initStimulusControls();
    
    // Initialize preview functionality
    initPreview();
    
    console.log('Stimulus Generation tab initialized successfully');
}



function initStimulusControls() {
    // Stimulus type change handler
    const stimulusType = document.getElementById('stimulus_type');
    if (stimulusType) {
        stimulusType.addEventListener('change', handleStimulusTypeChange);
        handleStimulusTypeChange(); // Initialize
    }
    
    // Generate button
    const generateButton = document.getElementById('generate-button');
    if (generateButton) {
        generateButton.addEventListener('click', generateStimulus);
    }
    
    // Header buttons
    const generateStimulusBtn = document.getElementById('generate-stimulus');
    const previewStimulusBtn = document.getElementById('preview-stimulus');
    const saveStimulusBtn = document.getElementById('save-stimulus');
    
    if (generateStimulusBtn) {
        generateStimulusBtn.addEventListener('click', generateStimulus);
    }
    
    if (previewStimulusBtn) {
        previewStimulusBtn.addEventListener('click', previewStimulus);
    }
    
    if (saveStimulusBtn) {
        saveStimulusBtn.addEventListener('click', saveStimulus);
    }
    
    // Template buttons
    const loadTemplateBtn = document.getElementById('load-template');
    const saveTemplateBtn = document.getElementById('save-template');
    
    if (loadTemplateBtn) {
        loadTemplateBtn.addEventListener('click', loadTemplate);
    }
    
    if (saveTemplateBtn) {
        saveTemplateBtn.addEventListener('click', saveTemplate);
    }
    
    // Export button
    const exportStimulusBtn = document.getElementById('export-stimulus');
    if (exportStimulusBtn) {
        exportStimulusBtn.addEventListener('click', exportStimulus);
    }
}

function handleStimulusTypeChange() {
    const stimulusType = document.getElementById('stimulus_type');
    const gratingParams = document.getElementById('grating-params');
    
    if (!stimulusType || !gratingParams) return;
    
    // Show/hide parameter sections based on stimulus type
    if (stimulusType.value === 'grating' || stimulusType.value === 'checkerboard_drift') {
        gratingParams.style.display = 'block';
    } else {
        gratingParams.style.display = 'none';
    }
}

function initPreview() {
    // Preview controls
    const playBtn = document.getElementById('play-preview');
    const pauseBtn = document.getElementById('pause-preview');
    const stopBtn = document.getElementById('stop-preview');
    
    if (playBtn) {
        playBtn.addEventListener('click', playPreview);
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pausePreview);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopPreview);
    }
}

function generateStimulus() {
    console.log('Generating stimulus...');
    updateStatusMessage('Generating stimulus...', 'info');
    
    // Get parameters
    const params = getStimulusParameters();
    console.log('Stimulus parameters:', params);
    
    // Simulate stimulus generation
    setTimeout(() => {
        updateStimulusProperties(params);
        updatePreview(params);
        updateStatusMessage('Stimulus generated successfully', 'success');
    }, 1000);
}

function getStimulusParameters() {
    return {
        type: document.getElementById('stimulus_type')?.value || 'grating',
        spatial_frequency: parseFloat(document.getElementById('spatial_frequency')?.value || '0.04'),
        temporal_frequency: parseFloat(document.getElementById('temporal_frequency')?.value || '2'),
        orientation: parseFloat(document.getElementById('orientation')?.value || '0'),
        contrast: parseFloat(document.getElementById('contrast')?.value || '100'),
        duration: parseFloat(document.getElementById('duration')?.value || '5'),
        isi: parseFloat(document.getElementById('isi')?.value || '2'),
        repetitions: parseInt(document.getElementById('repetitions')?.value || '10'),
        background_luminance: parseFloat(document.getElementById('background_luminance')?.value || '50'),
        gamma: parseFloat(document.getElementById('gamma')?.value || '2.2')
    };
}

function updateStimulusProperties(params) {
    const propType = document.getElementById('prop-type');
    const propDuration = document.getElementById('prop-duration');
    const propFramerate = document.getElementById('prop-framerate');
    const propFrames = document.getElementById('prop-frames');
    const propSize = document.getElementById('prop-size');
    
    if (propType) propType.textContent = params.type.charAt(0).toUpperCase() + params.type.slice(1);
    if (propDuration) propDuration.textContent = `${params.duration}s`;
    if (propFramerate) propFramerate.textContent = '60 fps';
    if (propFrames) propFrames.textContent = Math.round(params.duration * 60).toString();
    if (propSize) propSize.textContent = `${(params.duration * 60 * 0.1).toFixed(1)} MB`;
    
    // Update frame counters
    const totalFrames = document.getElementById('total-frames');
    if (totalFrames) totalFrames.textContent = Math.round(params.duration * 60).toString();
}

function updatePreview(params) {
    const previewContainer = document.getElementById('stimulus-preview');
    if (!previewContainer) return;
    
    // Replace placeholder with preview content
    previewContainer.innerHTML = `
        <div class="stimulus-preview-content">
            <div class="preview-info">
                <h4>${params.type.charAt(0).toUpperCase() + params.type.slice(1)} Stimulus</h4>
                <p>Duration: ${params.duration}s | Contrast: ${params.contrast}%</p>
            </div>
            <div class="preview-canvas">
                <canvas id="stimulus-canvas" width="400" height="300"></canvas>
            </div>
        </div>
    `;
    
    // Draw simple preview on canvas
    const canvas = document.getElementById('stimulus-canvas');
    if (canvas) {
        drawStimulusPreview(canvas, params);
    }
}

function drawStimulusPreview(canvas, params) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.fillStyle = `rgb(${params.background_luminance * 2.55}, ${params.background_luminance * 2.55}, ${params.background_luminance * 2.55})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw stimulus preview based on type
    switch (params.type) {
        case 'grating':
            drawGratingPreview(ctx, canvas, params);
            break;
        case 'checkerboard_drift':
            drawCheckerboardDriftPreview(ctx, canvas, params);
            break;
        case 'checkerboard':
            drawCheckerboardPreview(ctx, canvas, params);
            break;
        case 'flash':
            drawFlashPreview(ctx, canvas, params);
            break;
        default:
            drawNoisePreview(ctx, canvas, params);
    }
}

function drawGratingPreview(ctx, canvas, params) {
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) / 3;
    
    // Draw circular grating
    for (let angle = 0; angle < 360; angle += 2) {
        const rad = (angle * Math.PI) / 180;
        const x = centerX + Math.cos(rad) * radius;
        const y = centerY + Math.sin(rad) * radius;
        
        const intensity = Math.sin((angle + params.orientation) * params.spatial_frequency * 10) * params.contrast / 100;
        const gray = params.background_luminance + intensity * 50;
        
        ctx.fillStyle = `rgb(${gray * 2.55}, ${gray * 2.55}, ${gray * 2.55})`;
        ctx.fillRect(x - 1, y - 1, 2, 2);
    }
}

function drawCheckerboardDriftPreview(ctx, canvas, params) {
    const squareSize = 20;
    const cols = Math.floor(canvas.width / squareSize);
    const rows = Math.floor(canvas.height / squareSize);
    
    // Draw checkerboard background
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const isWhite = (row + col) % 2 === 0;
            const intensity = isWhite ? params.background_luminance + params.contrast / 4 : params.background_luminance - params.contrast / 4;
            
            ctx.fillStyle = `rgb(${intensity * 2.55}, ${intensity * 2.55}, ${intensity * 2.55})`;
            ctx.fillRect(col * squareSize, row * squareSize, squareSize, squareSize);
        }
    }
    
    // Draw drifting bar overlay
    const barWidth = 40;
    const barPosition = (Date.now() * params.temporal_frequency / 10) % (canvas.width + barWidth) - barWidth;
    const barIntensity = params.background_luminance + params.contrast / 2;
    
    ctx.fillStyle = `rgb(${barIntensity * 2.55}, ${barIntensity * 2.55}, ${barIntensity * 2.55})`;
    
    // Rotate context for orientation
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((params.orientation * Math.PI) / 180);
    ctx.translate(-canvas.width / 2, -canvas.height / 2);
    
    ctx.fillRect(barPosition, 0, barWidth, canvas.height);
    ctx.restore();
}

function drawCheckerboardPreview(ctx, canvas, params) {
    const squareSize = 20;
    const cols = Math.floor(canvas.width / squareSize);
    const rows = Math.floor(canvas.height / squareSize);
    
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const isWhite = (row + col) % 2 === 0;
            const intensity = isWhite ? params.background_luminance + params.contrast / 2 : params.background_luminance - params.contrast / 2;
            
            ctx.fillStyle = `rgb(${intensity * 2.55}, ${intensity * 2.55}, ${intensity * 2.55})`;
            ctx.fillRect(col * squareSize, row * squareSize, squareSize, squareSize);
        }
    }
}

function drawFlashPreview(ctx, canvas, params) {
    const intensity = params.background_luminance + params.contrast / 2;
    ctx.fillStyle = `rgb(${intensity * 2.55}, ${intensity * 2.55}, ${intensity * 2.55})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawNoisePreview(ctx, canvas, params) {
    const imageData = ctx.createImageData(canvas.width, canvas.height);
    const data = imageData.data;
    
    for (let i = 0; i < data.length; i += 4) {
        const noise = (Math.random() - 0.5) * params.contrast;
        const intensity = (params.background_luminance + noise) * 2.55;
        
        data[i] = intensity;     // Red
        data[i + 1] = intensity; // Green
        data[i + 2] = intensity; // Blue
        data[i + 3] = 255;       // Alpha
    }
    
    ctx.putImageData(imageData, 0, 0);
}

function previewStimulus() {
    console.log('Previewing stimulus...');
    updateStatusMessage('Starting stimulus preview...', 'info');
}

function saveStimulus() {
    console.log('Saving stimulus...');
    updateStatusMessage('Saving stimulus...', 'info');
}

function loadTemplate() {
    console.log('Loading template...');
    updateStatusMessage('Loading template...', 'info');
}

function saveTemplate() {
    console.log('Saving template...');
    updateStatusMessage('Saving template...', 'info');
}

function exportStimulus() {
    console.log('Exporting stimulus...');
    const format = document.getElementById('export_format')?.value || 'mp4';
    updateStatusMessage(`Exporting stimulus as ${format.toUpperCase()}...`, 'info');
}

function playPreview() {
    console.log('Playing preview...');
    updateStatusMessage('Playing stimulus preview', 'info');
}

function pausePreview() {
    console.log('Pausing preview...');
    updateStatusMessage('Preview paused', 'info');
}

function stopPreview() {
    console.log('Stopping preview...');
    updateStatusMessage('Preview stopped', 'info');
}

function updateStatusMessage(message, type = 'info') {
    const statusMessage = document.getElementById('status-message');
    if (statusMessage) {
        statusMessage.textContent = message;
        statusMessage.className = `status-${type}`;
    }
} 