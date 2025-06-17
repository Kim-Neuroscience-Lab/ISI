const { contextBridge, ipcRenderer } = require('electron');

// Define the server URL with the new port
const API_BASE_URL = 'http://localhost:5001';

// Helper function to handle errors
const handleError = (error) => {
  console.error('API Error:', error);
  if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
    return { error: true, message: `Cannot connect to Python backend. Make sure the server is running on port 5001.` };
  } else if (error.message.includes('Unexpected end of JSON input')) {
    return { error: true, message: 'Invalid JSON response from server. Check server logs for details.' };
  }
  return { error: true, message: error.message };
};

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('api', {
  // Send data to Python backend and get response
  sendToPython: async (endpoint, data) => {
    console.log(`Sending POST request to ${API_BASE_URL}/${endpoint} with data:`, data);
    try {
      // Try to connect to the server first
      try {
        const testResponse = await fetch(`${API_BASE_URL}/`, { method: 'GET' });
        console.log('Server connectivity test:', testResponse.status, testResponse.ok);
      } catch (testError) {
        console.error('Server connectivity test failed:', testError);
      }
      
      // Proceed with the actual request
      const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      console.log(`Response from ${endpoint}:`, response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Server error (${response.status}):`, errorText || response.statusText);
        return { 
          error: true, 
          status: response.status,
          message: `Server error: ${response.status} ${response.statusText}` 
        };
      }
      
      const result = await response.json();
      console.log(`Data from ${endpoint}:`, result);
      return result;
    } catch (error) {
      console.error(`Error in sendToPython for ${endpoint}:`, error);
      return handleError(error);
    }
  },
  
  // Get data from Python backend
  getFromPython: async (endpoint) => {
    console.log(`Sending GET request to ${API_BASE_URL}/${endpoint}`);
    try {
      // Try to connect to the server first
      try {
        const testResponse = await fetch(`${API_BASE_URL}/`, { method: 'GET' });
        console.log('Server connectivity test:', testResponse.status, testResponse.ok);
      } catch (testError) {
        console.error('Server connectivity test failed:', testError);
      }
      
      // Proceed with the actual request
      const response = await fetch(`${API_BASE_URL}/${endpoint}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      
      console.log(`Response from ${endpoint}:`, response.status, response.statusText);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Server error (${response.status}):`, errorText || response.statusText);
        return { 
          error: true, 
          status: response.status,
          message: `Server error: ${response.status} ${response.statusText}` 
        };
      }
      
      const result = await response.json();
      console.log(`Data from ${endpoint}:`, result);
      return result;
    } catch (error) {
      console.error(`Error in getFromPython for ${endpoint}:`, error);
      return handleError(error);
    }
  },
  
  // Get application path from main process
  getAppPath: () => ipcRenderer.invoke('get-app-path'),
  
  // Listen for server ready events
  onServerReady: (callback) => {
    ipcRenderer.on('python-server-ready', callback);
  },
  
  // Remove server ready event listener
  removeServerReadyListener: (callback) => {
    ipcRenderer.removeListener('python-server-ready', callback);
  },
}); 