# ISI Python APIs

This directory contains two Python API implementations for the ISI application:

## 📦 **Files**

### `experiment_api_wrapper.py` ✅ **ACTIVE**

- **Purpose**: Simplified API wrapper for the 3D visualization interface
- **Dependencies**: Flask, flask-cors (basic dependencies only)
- **Status**: Currently used by Electron app
- **Features**:
  - Basic setup parameter management
  - 3D visualization data generation
  - Simple validation and coverage calculations
  - Health check endpoints

### `experiment_api.py` 🚀 **READY FOR FUTURE USE**

- **Purpose**: Complete experimental workflow API with advanced features
- **Dependencies**: Requires ISI-Core services, Pydantic, comprehensive scientific libraries
- **Status**: Available for when full workflow features are needed
- **Features**:
  - Complete experimental workflow (Setup → Stimulus → Acquisition → Analysis)
  - Advanced data analysis and processing
  - Real-time acquisition control
  - Frame synchronization and analysis
  - Comprehensive validation and error handling

## 🔄 **Current Integration**

```bash
Electron App → experiment_api_wrapper.py (Port 5001)
```

The wrapper provides all necessary endpoints for the current 3D visualization interface without complex dependencies.

## 🚀 **Future Migration**

When ready for full experimental capabilities:

1. Update `ISI-Integration/src/main/main.js`
2. Change Python script from `experiment_api_wrapper.py` to `experiment_api.py`
3. Ensure ISI-Core dependencies are available in the environment
4. Extend the frontend interface as needed

## 📝 **API Compatibility**

Both APIs implement compatible endpoints for basic functionality, ensuring a smooth transition path when upgrading to the full experimental workflow system.
