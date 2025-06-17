// analysis.js - Analysis Tab
import PanelManager from './panelManager.js';

let panelManager = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Analysis Tab Loaded');
    initAnalysisTab();
});

let analysisState = {
    dataLoaded: false,
    currentFrame: 0,
    totalFrames: 0,
    isPlaying: false,
    rois: []
};

function initAnalysisTab() {
    console.log('Initializing Analysis functionality...');
    
    // Initialize panels using shared manager
    panelManager = new PanelManager();
    panelManager.init();
    
    // Initialize analysis controls
    initAnalysisControls();
    
    // Initialize data loading
    initDataLoading();
    
    // Initialize visualization
    initAnalysisVisualization();
    
    console.log('Analysis tab initialized successfully');
}

function initAnalysisControls() {
    // Header buttons
    const loadDataBtn = document.getElementById('load-data');
    const runAnalysisBtn = document.getElementById('run-analysis');
    const exportResultsBtn = document.getElementById('export-results');
    
    if (loadDataBtn) {
        loadDataBtn.addEventListener('click', loadAnalysisData);
    }
    
    if (runAnalysisBtn) {
        runAnalysisBtn.addEventListener('click', runAnalysis);
    }
    
    if (exportResultsBtn) {
        exportResultsBtn.addEventListener('click', exportResults);
    }
    
    // Analysis controls
    const prevFrameBtn = document.getElementById('prev-frame');
    const playAnalysisBtn = document.getElementById('play-analysis');
    const nextFrameBtn = document.getElementById('next-frame');
    const frameSlider = document.getElementById('frame-slider');
    
    if (prevFrameBtn) {
        prevFrameBtn.addEventListener('click', previousFrame);
    }
    
    if (playAnalysisBtn) {
        playAnalysisBtn.addEventListener('click', togglePlayback);
    }
    
    if (nextFrameBtn) {
        nextFrameBtn.addEventListener('click', nextFrame);
    }
    
    if (frameSlider) {
        frameSlider.addEventListener('input', handleFrameSlider);
    }
    
    // Action buttons
    const preprocessBtn = document.getElementById('preprocess-data');
    const analyzeBtn = document.getElementById('analyze-data');
    const saveAnalysisBtn = document.getElementById('save-analysis');
    
    if (preprocessBtn) {
        preprocessBtn.addEventListener('click', preprocessData);
    }
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeData);
    }
    
    if (saveAnalysisBtn) {
        saveAnalysisBtn.addEventListener('click', saveAnalysis);
    }
    
    // ROI buttons
    const addRoiBtn = document.getElementById('add-roi');
    const clearRoisBtn = document.getElementById('clear-rois');
    
    if (addRoiBtn) {
        addRoiBtn.addEventListener('click', addROI);
    }
    
    if (clearRoisBtn) {
        clearRoisBtn.addEventListener('click', clearROIs);
    }
    
    // Export analysis button
    const exportAnalysisBtn = document.getElementById('export-analysis');
    if (exportAnalysisBtn) {
        exportAnalysisBtn.addEventListener('click', exportAnalysis);
    }
}

function initDataLoading() {
    // Data source change handler
    const dataSource = document.getElementById('data_source');
    if (dataSource) {
        dataSource.addEventListener('change', handleDataSourceChange);
        handleDataSourceChange(); // Initialize
    }
    
    // File input handler
    const dataFile = document.getElementById('data_file');
    if (dataFile) {
        dataFile.addEventListener('change', handleFileLoad);
    }
    
    // Analysis method change handler
    const analysisMethod = document.getElementById('analysis_method');
    if (analysisMethod) {
        analysisMethod.addEventListener('change', handleAnalysisMethodChange);
    }
    
    // Check for acquisition data on load
    checkAcquisitionData();
}

function initAnalysisVisualization() {
    const analysisView = document.getElementById('analysis-view');
    if (!analysisView) return;
    
    // Initialize with placeholder
    updateAnalysisView();
}

function handleFileLoad(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    console.log('Loading data file:', file.name);
    updateStatusMessage(`Loading ${file.name}...`, 'info');
    
    // Simulate file loading
    setTimeout(() => {
        analysisState.dataLoaded = true;
        analysisState.totalFrames = 300; // Simulated
        
        updateDataSummary(file);
        updateAnalysisView();
        updateFrameControls();
        
        updateStatusMessage('Data loaded successfully', 'success');
    }, 2000);
}

function updateDataSummary(file) {
    // Update data summary in right panel
    const dataDimensions = document.getElementById('data-dimensions');
    const dataDuration = document.getElementById('data-duration');
    const dataFramerate = document.getElementById('data-framerate');
    const dataTrials = document.getElementById('data-trials');
    
    if (dataDimensions) dataDimensions.textContent = '512 x 512 x 300';
    if (dataDuration) dataDuration.textContent = '10.0s';
    if (dataFramerate) dataFramerate.textContent = '30 fps';
    if (dataTrials) dataTrials.textContent = '5';
}

function updateAnalysisView() {
    const analysisView = document.getElementById('analysis-view');
    if (!analysisView) return;
    
    if (!analysisState.dataLoaded) {
        // Show placeholder
        analysisView.innerHTML = `
            <div class="analysis-placeholder">
                <div class="analysis-icon">Analysis</div>
                <div class="analysis-title">Data Visualization</div>
                <div class="analysis-description">Load data to begin analysis</div>
            </div>
        `;
    } else {
        // Show analysis visualization
        analysisView.innerHTML = `
            <div class="analysis-content">
                <div class="analysis-canvas-container">
                    <canvas id="analysis-canvas" width="600" height="400"></canvas>
                </div>
                <div class="analysis-info">
                    <span>Frame: ${analysisState.currentFrame + 1} / ${analysisState.totalFrames}</span>
                    <span>Method: ${getAnalysisMethod()}</span>
                </div>
            </div>
        `;
        
        // Draw analysis visualization
        drawAnalysisVisualization();
    }
}

function drawAnalysisVisualization() {
    const canvas = document.getElementById('analysis-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw simulated brain imaging data
    const method = getAnalysisMethod();
    
    switch (method) {
        case 'response_map':
            drawIntrinsicSignalMap(ctx, canvas);
            break;
        case 'time_course':
            drawHemodynamicTimeCourse(ctx, canvas);
            break;
        case 'optical_imaging':
            drawOpticalImagingAnalysis(ctx, canvas);
            break;
        case 'retinotopy':
            drawRetinotopicMap(ctx, canvas);
            break;
        default:
            drawIntrinsicSignalMap(ctx, canvas);
    }
    
    // Draw ROIs if any
    drawROIs(ctx, canvas);
}

function drawIntrinsicSignalMap(ctx, canvas) {
    // Draw simulated intrinsic signal response map
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 120;
    
    // Create gradient for intrinsic signal response (typically shows as darkening)
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    gradient.addColorStop(0, 'rgba(0, 50, 150, 0.9)'); // Strong response (blue/dark)
    gradient.addColorStop(0.3, 'rgba(0, 100, 200, 0.7)'); // Medium response
    gradient.addColorStop(0.6, 'rgba(100, 150, 255, 0.4)'); // Weak response
    gradient.addColorStop(1, 'rgba(200, 200, 200, 0.1)'); // Background
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fill();
    
    // Add cortical column-like structure
    for (let i = 0; i < 30; i++) {
        const angle = (i / 30) * 2 * Math.PI;
        const x = centerX + Math.cos(angle) * (radius * 0.7);
        const y = centerY + Math.sin(angle) * (radius * 0.7);
        const columnRadius = 8;
        
        ctx.fillStyle = `rgba(0, 30, 120, 0.6)`;
        ctx.beginPath();
        ctx.arc(x, y, columnRadius, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    // Add scale bar
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText('1mm', canvas.width - 50, canvas.height - 20);
    ctx.fillRect(canvas.width - 50, canvas.height - 15, 20, 2);
}

function drawHemodynamicTimeCourse(ctx, canvas) {
    // Draw hemodynamic response time course (typical ISI signal)
    ctx.strokeStyle = '#0088ff';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const points = 100;
    const baseline = canvas.height * 0.7; // Higher baseline for negative deflection
    
    for (let i = 0; i < points; i++) {
        const t = (i / points) * 10; // 10 second window
        const x = (i / points) * canvas.width;
        
        // Simulate hemodynamic response: initial dip, then positive response
        let y = baseline;
        if (t > 1 && t < 8) {
            // Initial dip (0.5-1% decrease)
            const dip = -20 * Math.exp(-(t - 1) * 2) * Math.sin((t - 1) * 3);
            // Positive response (slower, longer)
            const positive = 15 * Math.exp(-(t - 3) * 0.5) * Math.sin((t - 2) * 1.5);
            y = baseline + dip + positive;
        }
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    
    ctx.stroke();
    
    // Add stimulus period indicator
    ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
    ctx.fillRect(canvas.width * 0.1, 0, canvas.width * 0.2, canvas.height);
    
    // Add axis labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText('Time (s)', canvas.width - 60, canvas.height - 10);
    ctx.save();
    ctx.translate(15, canvas.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('ΔR/R (%)', 0, 0);
    ctx.restore();
    
    // Add zero line
    ctx.strokeStyle = '#666666';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, baseline);
    ctx.lineTo(canvas.width, baseline);
    ctx.stroke();
    ctx.setLineDash([]);
}

function drawOpticalImagingAnalysis(ctx, canvas) {
    // Draw optical imaging analysis with blood vessel overlay
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    // Draw cortical surface
    ctx.fillStyle = 'rgba(150, 150, 150, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw blood vessels (typical ISI feature)
    ctx.strokeStyle = '#800000';
    ctx.lineWidth = 3;
    
    // Major vessels
    for (let i = 0; i < 5; i++) {
        ctx.beginPath();
        const startX = Math.random() * canvas.width;
        const startY = Math.random() * canvas.height;
        const endX = startX + (Math.random() - 0.5) * 200;
        const endY = startY + (Math.random() - 0.5) * 200;
        
        ctx.moveTo(startX, startY);
        ctx.quadraticCurveTo(
            startX + (Math.random() - 0.5) * 100,
            startY + (Math.random() - 0.5) * 100,
            endX, endY
        );
        ctx.stroke();
    }
    
    // Draw activity patches
    for (let i = 0; i < 8; i++) {
        const x = Math.random() * canvas.width;
        const y = Math.random() * canvas.height;
        const radius = 20 + Math.random() * 30;
        
        const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
        gradient.addColorStop(0, 'rgba(0, 100, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(0, 100, 255, 0.1)');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    // Add labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText('Optical Imaging Analysis', 10, 20);
    ctx.fillText('Blood vessels + Activity', 10, 35);
}

function drawRetinotopicMap(ctx, canvas) {
    // Draw retinotopic mapping visualization
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.4;
    
    // Draw visual field representation
    for (let angle = 0; angle < 2 * Math.PI; angle += 0.1) {
        for (let r = 0; r < radius; r += 10) {
            const x = centerX + Math.cos(angle) * r;
            const y = centerY + Math.sin(angle) * r;
            
            // Color based on polar angle (hue) and eccentricity (saturation)
            const hue = (angle / (2 * Math.PI)) * 360;
            const saturation = (r / radius) * 100;
            const lightness = 50;
            
            ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
            ctx.fillRect(x - 2, y - 2, 4, 4);
        }
    }
    
    // Draw iso-eccentricity rings
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    
    for (let r = radius * 0.25; r < radius; r += radius * 0.25) {
        ctx.beginPath();
        ctx.arc(centerX, centerY, r, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    // Draw iso-angle lines
    for (let angle = 0; angle < 2 * Math.PI; angle += Math.PI / 4) {
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(
            centerX + Math.cos(angle) * radius,
            centerY + Math.sin(angle) * radius
        );
        ctx.stroke();
    }
    
    ctx.setLineDash([]);
    
    // Add labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText('Retinotopic Map', 10, 20);
    ctx.fillText('Polar angle (hue) × Eccentricity (saturation)', 10, 35);
}

function drawROIs(ctx, canvas) {
    // Draw ROIs
    ctx.strokeStyle = '#ffff00';
    ctx.lineWidth = 2;
    
    analysisState.rois.forEach((roi, index) => {
        ctx.beginPath();
        ctx.arc(roi.x, roi.y, roi.radius, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Label ROI
        ctx.fillStyle = '#ffff00';
        ctx.font = '12px Arial';
        ctx.fillText(`ROI ${index + 1}`, roi.x + roi.radius + 5, roi.y);
    });
}

function updateFrameControls() {
    const frameSlider = document.getElementById('frame-slider');
    const currentFrameSpan = document.getElementById('current-analysis-frame');
    const totalFramesSpan = document.getElementById('total-analysis-frames');
    
    if (frameSlider) {
        frameSlider.max = analysisState.totalFrames - 1;
        frameSlider.value = analysisState.currentFrame;
    }
    
    if (currentFrameSpan) {
        currentFrameSpan.textContent = analysisState.currentFrame.toString();
    }
    
    if (totalFramesSpan) {
        totalFramesSpan.textContent = analysisState.totalFrames.toString();
    }
}

function getAnalysisMethod() {
    const methodSelect = document.getElementById('analysis_method');
    return methodSelect ? methodSelect.value : 'response_map';
}

function handleAnalysisMethodChange() {
    if (analysisState.dataLoaded) {
        updateAnalysisView();
    }
}

function handleFrameSlider(event) {
    analysisState.currentFrame = parseInt(event.target.value);
    updateFrameControls();
    if (analysisState.dataLoaded) {
        updateAnalysisView();
    }
}

function previousFrame() {
    if (analysisState.currentFrame > 0) {
        analysisState.currentFrame--;
        updateFrameControls();
        if (analysisState.dataLoaded) {
            updateAnalysisView();
        }
    }
}

function nextFrame() {
    if (analysisState.currentFrame < analysisState.totalFrames - 1) {
        analysisState.currentFrame++;
        updateFrameControls();
        if (analysisState.dataLoaded) {
            updateAnalysisView();
        }
    }
}

function togglePlayback() {
    analysisState.isPlaying = !analysisState.isPlaying;
    
    const playBtn = document.getElementById('play-analysis');
    if (playBtn) {
        playBtn.textContent = analysisState.isPlaying ? 'Pause' : 'Play';
    }
    
    if (analysisState.isPlaying) {
        startPlayback();
    }
}

function startPlayback() {
    if (!analysisState.isPlaying) return;
    
    setTimeout(() => {
        if (analysisState.isPlaying) {
            nextFrame();
            if (analysisState.currentFrame < analysisState.totalFrames - 1) {
                startPlayback();
            } else {
                analysisState.isPlaying = false;
                const playBtn = document.getElementById('play-analysis');
                if (playBtn) playBtn.textContent = 'Play';
            }
        }
    }, 100); // 10 FPS playback
}

function handleDataSourceChange() {
    const dataSource = document.getElementById('data_source');
    const fileUploadSection = document.getElementById('file-upload-section');
    const acquisitionStatus = document.getElementById('acquisition-status');
    
    if (!dataSource || !fileUploadSection || !acquisitionStatus) return;
    
    if (dataSource.value === 'file') {
        fileUploadSection.style.display = 'block';
        acquisitionStatus.textContent = 'File upload mode selected';
        acquisitionStatus.className = 'status-display';
    } else {
        fileUploadSection.style.display = 'none';
        checkAcquisitionData();
    }
}

function checkAcquisitionData() {
    const acquisitionStatus = document.getElementById('acquisition-status');
    if (!acquisitionStatus) return;
    
    // Check if there's acquisition data available (simulated)
    // In a real implementation, this would check localStorage, sessionStorage, or API
    const hasAcquisitionData = localStorage.getItem('isi_acquisition_data') !== null;
    
    if (hasAcquisitionData) {
        acquisitionStatus.textContent = 'Acquisition data available - Ready to analyze';
        acquisitionStatus.className = 'status-display success';
        
        // Auto-load acquisition data
        setTimeout(() => {
            loadAcquisitionData();
        }, 500);
    } else {
        acquisitionStatus.textContent = 'No acquisition data found - Run acquisition first or upload data file';
        acquisitionStatus.className = 'status-display warning';
    }
}

function loadAcquisitionData() {
    console.log('Loading data from acquisition session...');
    updateStatusMessage('Loading acquisition data...', 'info');
    
    // Simulate loading acquisition data
    setTimeout(() => {
        analysisState.dataLoaded = true;
        analysisState.totalFrames = 450; // Simulated acquisition data
        
        // Update data summary with acquisition info
        updateAcquisitionDataSummary();
        updateAnalysisView();
        updateFrameControls();
        
        updateStatusMessage('Acquisition data loaded successfully', 'success');
    }, 1500);
}

function updateAcquisitionDataSummary() {
    // Update data summary with acquisition session info
    const dataDimensions = document.getElementById('data-dimensions');
    const dataDuration = document.getElementById('data-duration');
    const dataFramerate = document.getElementById('data-framerate');
    const dataTrials = document.getElementById('data-trials');
    
    if (dataDimensions) dataDimensions.textContent = '1024 x 1024 x 450';
    if (dataDuration) dataDuration.textContent = '15.0s';
    if (dataFramerate) dataFramerate.textContent = '30 fps';
    if (dataTrials) dataTrials.textContent = '3';
}

function loadAnalysisData() {
    const dataSource = document.getElementById('data_source');
    
    if (dataSource && dataSource.value === 'acquisition') {
        loadAcquisitionData();
    } else {
        const dataFile = document.getElementById('data_file');
        if (dataFile) {
            dataFile.click();
        }
    }
}

function runAnalysis() {
    console.log('Running analysis...');
    updateStatusMessage('Running analysis...', 'info');
    
    setTimeout(() => {
        updateAnalysisResults();
        updateStatusMessage('Analysis completed successfully', 'success');
    }, 3000);
}

function preprocessData() {
    console.log('Preprocessing data...');
    updateStatusMessage('Preprocessing data...', 'info');
    
    setTimeout(() => {
        updateStatusMessage('Data preprocessing completed', 'success');
    }, 2000);
}

function analyzeData() {
    runAnalysis();
}

function saveAnalysis() {
    console.log('Saving analysis...');
    updateStatusMessage('Saving analysis results...', 'info');
    
    setTimeout(() => {
        updateStatusMessage('Analysis saved successfully', 'success');
    }, 1000);
}

function addROI() {
    // Add a random ROI for demonstration
    const roi = {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 50,
        radius: 30
    };
    
    analysisState.rois.push(roi);
    updateROIList();
    
    if (analysisState.dataLoaded) {
        updateAnalysisView();
    }
    
    updateStatusMessage(`ROI ${analysisState.rois.length} added`, 'info');
}

function clearROIs() {
    analysisState.rois = [];
    updateROIList();
    
    if (analysisState.dataLoaded) {
        updateAnalysisView();
    }
    
    updateStatusMessage('All ROIs cleared', 'info');
}

function updateROIList() {
    const roiList = document.getElementById('roi-list');
    if (!roiList) return;
    
    if (analysisState.rois.length === 0) {
        roiList.innerHTML = '<div class="roi-placeholder">No ROIs selected</div>';
    } else {
        const roiItems = analysisState.rois.map((roi, index) => 
            `<div class="roi-item">ROI ${index + 1} (${roi.x.toFixed(0)}, ${roi.y.toFixed(0)})</div>`
        ).join('');
        
        roiList.innerHTML = roiItems;
    }
}

function updateAnalysisResults() {
    // Update response statistics with simulated values
    const peakResponse = document.getElementById('peak-response');
    const responseLatency = document.getElementById('response-latency');
    const responseArea = document.getElementById('response-area');
    const analysisSnr = document.getElementById('analysis-snr');
    
    if (peakResponse) peakResponse.textContent = (Math.random() * 5 + 2).toFixed(2) + '%';
    if (responseLatency) responseLatency.textContent = (Math.random() * 200 + 100).toFixed(0) + ' ms';
    if (responseArea) responseArea.textContent = (Math.random() * 50 + 20).toFixed(1) + ' mm²';
    if (analysisSnr) analysisSnr.textContent = (Math.random() * 10 + 15).toFixed(1) + ' dB';
}

function exportResults() {
    console.log('Exporting results...');
    updateStatusMessage('Exporting analysis results...', 'info');
    
    setTimeout(() => {
        updateStatusMessage('Results exported successfully', 'success');
    }, 1500);
}

function exportAnalysis() {
    const format = document.getElementById('export_format')?.value || 'pdf';
    console.log('Exporting analysis as:', format);
    updateStatusMessage(`Exporting as ${format.toUpperCase()}...`, 'info');
    
    setTimeout(() => {
        updateStatusMessage(`Analysis exported as ${format.toUpperCase()}`, 'success');
    }, 2000);
}

function updateStatusMessage(message, type = 'info') {
    const statusMessage = document.getElementById('status-message');
    if (statusMessage) {
        statusMessage.textContent = message;
        statusMessage.className = `status-${type}`;
    }
} 