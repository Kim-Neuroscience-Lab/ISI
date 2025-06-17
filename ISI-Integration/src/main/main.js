const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const log = require('electron-log');
const http = require('http');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Keep a global reference of the window object to prevent garbage collection
let mainWindow;
let pythonProcess = null;

// Server port - updated to 8000
const PORT = 8000;

// Check if server is already running
function checkServerRunning(port) {
  return new Promise((resolve) => {
    const req = http.get({
      hostname: 'localhost',
      port: port,
      path: '/',
      timeout: 1000
    }, (res) => {
      if (res.statusCode === 200 || res.statusCode === 404) {
        // If we get any response, server is running
        log.info(`Server already running on port ${port}`);
        resolve(true);
      } else {
        resolve(false);
      }
    });
    
    req.on('error', () => {
      // Error means no server running
      resolve(false);
    });
    
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function startPythonServer() {
  // Check if server is already running
  const isRunning = await checkServerRunning(PORT);
  
  if (isRunning) {
    log.info(`Python server is already running on port ${PORT}, not starting a new one`);
    return;
  }
  
  // Path to Python unified server (anatomy detection + frontend serving)
  const pythonPath = app.isPackaged
    ? path.join(process.resourcesPath, 'python', 'simple_server.py')
    : path.join(__dirname, '..', 'python', 'simple_server.py');
  
  // Path to virtual environment Python interpreter
  const venvPythonPath = app.isPackaged
    ? path.join(process.resourcesPath, 'venv', 'bin', 'python')
    : path.join(__dirname, '..', '..', 'venv', 'bin', 'python');
  
  // Working directory for the wrapper
  const workspaceDir = app.isPackaged 
    ? process.resourcesPath
    : path.join(__dirname, '..', 'python');
  
  // Ensure options for spawn are correctly set
  const options = {
    cwd: workspaceDir, // Set working directory to python folder
    env: {
      ...process.env,
      // Ensure virtual environment variables are set
      VIRTUAL_ENV: app.isPackaged 
        ? path.join(process.resourcesPath, 'venv')
        : path.join(__dirname, '..', '..', 'venv'),
      PATH: `${path.dirname(venvPythonPath)}:${process.env.PATH}`
    }
  };
  
  // Launch Python unified server using virtual environment Python
  log.info(`Starting Python unified server: ${venvPythonPath} ${pythonPath}`);
  log.info(`Working directory: ${workspaceDir}`);
  log.info(`Virtual environment: ${options.env.VIRTUAL_ENV}`);
  pythonProcess = spawn(venvPythonPath, [pythonPath], options);
  
  // Listen for server ready signal
  let serverReady = false;
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    log.info(`Python stdout: ${output}`);
    
    // Check for ready signal
    if (output.includes('SERVER_READY') && !serverReady) {
      serverReady = true;
      log.info('🚀 Python server is ready for connections!');
      
      // Notify renderer process that server is ready
      if (mainWindow && mainWindow.webContents) {
        mainWindow.webContents.send('python-server-ready');
      }
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    log.error(`Python stderr: ${data}`);
  });
  
  pythonProcess.on('close', (code) => {
    log.info(`Python server process exited with code ${code}`);
    pythonProcess = null;
    serverReady = false;
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the original 3D visualization interface
  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
  
  // Open DevTools in development mode
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
  
  // Emitted when the window is closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Called when Electron has finished initialization
app.whenReady().then(() => {
  log.info('App is ready');
  
  // Start Python server if not already running
  startPythonServer();
  
  // Create the main window
  createWindow();
  
  // On macOS, recreate the window when the dock icon is clicked
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Kill Python process when app is quitting
app.on('will-quit', () => {
  if (pythonProcess) {
    log.info('Killing Python server process');
    pythonProcess.kill();
    pythonProcess = null;
  }
});

// IPC event handlers
ipcMain.handle('get-app-path', () => {
  return app.getAppPath();
}); 