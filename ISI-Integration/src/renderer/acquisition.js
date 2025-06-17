// acquisition.js - Acquisition Tab
import PanelManager from './panelManager.js';

let panelManager = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Acquisition Tab Loaded');
    initAcquisitionTab();
});

let acquisitionState = {
    isRecording: false,
    isPaused: false,
    startTime: null,
    frameCount: 0,
    currentTrial: 0,
    totalTrials: 0
};

function initAcquisitionTab() {
    console.log('Initializing Acquisition functionality...');
    
    // Initialize panels using shared manager
    panelManager = new PanelManager();
    panelManager.init();
    
    // Initialize acquisition controls
    initAcquisitionControls();
    
    // Initialize camera controls
    initCameraControls();
    
    // Start monitoring
    startAcquisitionMonitoring();
    
    console.log('Acquisition tab initialized successfully');
}

function initAcquisitionControls() {
    // Header buttons
    const startAcquisitionBtn = document.getElementById('start-acquisition');
    const stopAcquisitionBtn = document.getElementById('stop-acquisition');
    const saveDataBtn = document.getElementById('save-data');
    
    if (startAcquisitionBtn) {
        startAcquisitionBtn.addEventListener('click', startAcquisition);
    }
    
    if (stopAcquisitionBtn) {
        stopAcquisitionBtn.addEventListener('click', stopAcquisition);
    }
    
    if (saveDataBtn) {
        saveDataBtn.addEventListener('click', saveAcquisitionData);
    }
    
    // Recording controls
    const recordBtn = document.getElementById('record-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    
    if (recordBtn) {
        recordBtn.addEventListener('click', toggleRecording);
    }
    
    if (pauseBtn) {
        pauseBtn.addEventListener('click', pauseRecording);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopRecording);
    }
    
    // Action buttons
    const testCameraBtn = document.getElementById('test-camera');
    const calibrateBtn = document.getElementById('calibrate');
    const startRecordingBtn = document.getElementById('start-recording');
    
    if (testCameraBtn) {
        testCameraBtn.addEventListener('click', testCamera);
    }
    
    if (calibrateBtn) {
        calibrateBtn.addEventListener('click', calibrateCamera);
    }
    
    if (startRecordingBtn) {
        startRecordingBtn.addEventListener('click', startRecording);
    }
    
    // Save session button
    const saveSessionBtn = document.getElementById('save-session');
    if (saveSessionBtn) {
        saveSessionBtn.addEventListener('click', saveSession);
    }
}

function initCameraControls() {
    // Camera parameter change handlers
    const cameraSelect = document.getElementById('camera_select');
    const resolution = document.getElementById('resolution');
    const frameRate = document.getElementById('frame_rate');
    const exposure = document.getElementById('exposure');
    
    if (cameraSelect) {
        cameraSelect.addEventListener('change', handleCameraChange);
    }
    
    if (resolution) {
        resolution.addEventListener('change', handleResolutionChange);
    }
    
    if (frameRate) {
        frameRate.addEventListener('change', handleFrameRateChange);
    }
    
    if (exposure) {
        exposure.addEventListener('change', handleExposureChange);
    }
    
    // Initialize live view
    initLiveView();
}

function initLiveView() {
    const liveView = document.getElementById('live-view');
    if (!liveView) return;
    
    // Replace placeholder with live view content
    liveView.innerHTML = `
        <div class="live-view-content">
            <div class="camera-feed">
                <canvas id="camera-canvas" width="640" height="480"></canvas>
            </div>
            <div class="camera-info">
                <span>Camera: Ready</span>
                <span>Resolution: 1024x1024</span>
                <span>FPS: 30</span>
            </div>
        </div>
    `;
    
    // Start simulated camera feed
    startSimulatedFeed();
}

function startSimulatedFeed() {
    const canvas = document.getElementById('camera-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Simulate camera feed with noise
    setInterval(() => {
        if (!acquisitionState.isRecording) return;
        
        const imageData = ctx.createImageData(canvas.width, canvas.height);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const noise = Math.random() * 50 + 100;
            data[i] = noise;     // Red
            data[i + 1] = noise; // Green
            data[i + 2] = noise; // Blue
            data[i + 3] = 255;   // Alpha
        }
        
        ctx.putImageData(imageData, 0, 0);
        
        // Update frame count
        acquisitionState.frameCount++;
        updateFrameCount();
    }, 33); // ~30 FPS
}

function startAcquisitionMonitoring() {
    // Update acquisition data every second
    setInterval(() => {
        updateAcquisitionData();
    }, 1000);
}

function startAcquisition() {
    console.log('Starting acquisition...');
    acquisitionState.isRecording = true;
    acquisitionState.startTime = Date.now();
    acquisitionState.frameCount = 0;
    acquisitionState.currentTrial = 1;
    acquisitionState.totalTrials = parseInt(document.getElementById('num_trials')?.value || '10');
    
    // Save acquisition session info for analysis
    const sessionData = {
        startTime: acquisitionState.startTime,
        resolution: document.getElementById('resolution')?.value || '1024x1024',
        frameRate: document.getElementById('frame_rate')?.value || '30',
        duration: document.getElementById('acquisition_duration')?.value || '60',
        trials: acquisitionState.totalTrials,
        status: 'recording'
    };
    localStorage.setItem('isi_acquisition_data', JSON.stringify(sessionData));
    
    updateStatusMessage('Acquisition started', 'success');
    updateSessionStatus('Recording');
}

function stopAcquisition() {
    console.log('Stopping acquisition...');
    acquisitionState.isRecording = false;
    acquisitionState.isPaused = false;
    
    // Update acquisition session status
    const sessionData = JSON.parse(localStorage.getItem('isi_acquisition_data') || '{}');
    sessionData.status = 'completed';
    sessionData.endTime = Date.now();
    sessionData.totalFrames = acquisitionState.frameCount;
    sessionData.actualDuration = (Date.now() - acquisitionState.startTime) / 1000;
    localStorage.setItem('isi_acquisition_data', JSON.stringify(sessionData));
    
    updateStatusMessage('Acquisition stopped', 'info');
    updateSessionStatus('Stopped');
}

function toggleRecording() {
    if (acquisitionState.isRecording) {
        pauseRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    console.log('Starting recording...');
    startAcquisition();
}

function pauseRecording() {
    console.log('Pausing recording...');
    acquisitionState.isPaused = !acquisitionState.isPaused;
    
    const status = acquisitionState.isPaused ? 'Paused' : 'Recording';
    updateStatusMessage(`Recording ${status.toLowerCase()}`, 'info');
    updateSessionStatus(status);
}

function stopRecording() {
    console.log('Stopping recording...');
    stopAcquisition();
}

function testCamera() {
    console.log('Testing camera...');
    updateStatusMessage('Testing camera connection...', 'info');
    
    setTimeout(() => {
        updateStatusMessage('Camera test completed successfully', 'success');
    }, 2000);
}

function calibrateCamera() {
    console.log('Calibrating camera...');
    updateStatusMessage('Calibrating camera...', 'info');
    
    setTimeout(() => {
        updateStatusMessage('Camera calibration completed', 'success');
    }, 3000);
}

function saveAcquisitionData() {
    console.log('Saving acquisition data...');
    const format = document.getElementById('save_format')?.value || 'hdf5';
    updateStatusMessage(`Saving data as ${format.toUpperCase()}...`, 'info');
    
    setTimeout(() => {
        updateStatusMessage('Data saved successfully', 'success');
    }, 2000);
}

function saveSession() {
    console.log('Saving session...');
    saveAcquisitionData();
}

function handleCameraChange() {
    const camera = document.getElementById('camera_select')?.value;
    console.log('Camera changed to:', camera);
    updateStatusMessage(`Switched to ${camera}`, 'info');
}

function handleResolutionChange() {
    const resolution = document.getElementById('resolution')?.value;
    console.log('Resolution changed to:', resolution);
    updateStatusMessage(`Resolution set to ${resolution}`, 'info');
}

function handleFrameRateChange() {
    const frameRate = document.getElementById('frame_rate')?.value;
    console.log('Frame rate changed to:', frameRate);
    updateStatusMessage(`Frame rate set to ${frameRate} fps`, 'info');
}

function handleExposureChange() {
    const exposure = document.getElementById('exposure')?.value;
    console.log('Exposure changed to:', exposure);
    updateStatusMessage(`Exposure set to ${exposure} ms`, 'info');
}

function updateAcquisitionData() {
    if (!acquisitionState.isRecording) return;
    
    // Update elapsed time
    const elapsed = Date.now() - acquisitionState.startTime;
    const elapsedTime = document.getElementById('elapsed-time');
    if (elapsedTime) {
        elapsedTime.textContent = formatTime(elapsed);
    }
    
    // Update recording time
    const recordingTime = document.getElementById('recording-time');
    if (recordingTime) {
        recordingTime.textContent = formatTime(elapsed, true);
    }
    
    // Update data size (simulated)
    const dataSize = document.getElementById('data-size');
    if (dataSize) {
        const sizeMB = (elapsed / 1000 * 2.5).toFixed(1); // ~2.5 MB/s
        dataSize.textContent = `${sizeMB} MB`;
    }
    
    // Update trial info
    const currentTrial = document.getElementById('current-trial');
    if (currentTrial) {
        currentTrial.textContent = `${acquisitionState.currentTrial} / ${acquisitionState.totalTrials}`;
    }
    
    // Update signal quality (simulated)
    updateSignalQuality();
}

function updateFrameCount() {
    const frameCount = document.getElementById('frame-count');
    if (frameCount) {
        frameCount.textContent = acquisitionState.frameCount.toString();
    }
}

function updateSessionStatus(status) {
    const sessionStatus = document.getElementById('session-status');
    if (sessionStatus) {
        sessionStatus.textContent = status;
    }
}

function updateSignalQuality() {
    // Simulate signal quality metrics
    const snr = document.getElementById('snr-value');
    const baselineStd = document.getElementById('baseline-std');
    const motionLevel = document.getElementById('motion-level');
    
    if (snr) {
        const snrValue = (Math.random() * 10 + 15).toFixed(1);
        snr.textContent = `${snrValue} dB`;
    }
    
    if (baselineStd) {
        const stdValue = (Math.random() * 0.5 + 0.1).toFixed(3);
        baselineStd.textContent = stdValue;
    }
    
    if (motionLevel) {
        const levels = ['Low', 'Medium', 'High'];
        const level = levels[Math.floor(Math.random() * 3)];
        motionLevel.textContent = level;
    }
}

function formatTime(milliseconds, shortFormat = false) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (shortFormat) {
        return `${String(minutes % 60).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
    } else {
        return `${String(hours).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
    }
}

function updateStatusMessage(message, type = 'info') {
    const statusMessage = document.getElementById('status-message');
    if (statusMessage) {
        statusMessage.textContent = message;
        statusMessage.className = `status-${type}`;
    }
} 