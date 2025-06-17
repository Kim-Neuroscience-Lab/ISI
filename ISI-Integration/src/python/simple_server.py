#!/usr/bin/env python3
"""
Unified Flask server for both frontend serving and landmark detection
"""

import json
import logging
import numpy as np
import os
from flask import Flask, request, Response, send_from_directory, send_file
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
renderer_dir = os.path.join(project_root, "src", "renderer")

# Import landmark detector
try:
    from density_landmark_detector import DensityLandmarkDetector

    logger.info("Successfully imported DensityLandmarkDetector")
    DETECTOR_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import DensityLandmarkDetector: {e}")
    DETECTOR_AVAILABLE = False


# =============================================================================
# FRONTEND SERVING ROUTES
# =============================================================================


@app.route("/")
def serve_index():
    """Serve the main application page"""
    return send_file(os.path.join(renderer_dir, "setup.html"))


@app.route("/<path:filename>")
def serve_static(filename):
    """Serve static files from renderer directory"""
    return send_from_directory(renderer_dir, filename)


@app.route("/src/renderer/<path:filename>")
def serve_renderer_files(filename):
    """Serve files from renderer subdirectories"""
    return send_from_directory(renderer_dir, filename)


# =============================================================================
# API ROUTES
# =============================================================================


@app.route("/api/status", methods=["GET"])
def api_status():
    return {
        "status": "ok",
        "message": "Unified ISI server running",
        "detector_available": DETECTOR_AVAILABLE,
    }


@app.route("/api/landmarks/detect", methods=["POST"])
def detect_landmarks():
    """Detect anatomical landmarks using pure geometric analysis."""
    logger.info("Received POST to /landmarks/detect")

    if not DETECTOR_AVAILABLE:
        return {
            "success": False,
            "message": "DensityLandmarkDetector not available",
        }, 500

    try:
        # Get mesh data from request
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data provided")

        # Extract vertices
        vertices_data = data.get("vertices")
        if not vertices_data:
            raise ValueError("No vertices provided in request")

        # Convert to numpy array
        vertices = np.array(vertices_data)
        logger.info(f"Received mesh with {len(vertices)} vertices")

        # Validate vertices format
        if len(vertices.shape) != 2 or vertices.shape[1] != 3:
            raise ValueError(f"Vertices must be Nx3 array, got shape {vertices.shape}")

        # Create detector and run detection
        detector = DensityLandmarkDetector()
        results = detector.detect_landmarks(vertices)

        logger.info(
            f"Landmark detection successful: {len(results.get('landmarks', {}))} landmarks detected"
        )

        return {
            "success": True,
            "message": "Landmark detection completed successfully",
            "results": results,
        }

    except Exception as e:
        logger.error(f"Landmark detection failed: {e}")
        return {
            "success": False,
            "message": f"Landmark detection failed: {str(e)}",
            "error_type": type(e).__name__,
        }, 400


def run_server():
    """Run the Flask server and signal when ready"""
    import sys
    import threading
    import time
    import requests

    port = 8000
    logger.info(f"Starting unified ISI server (frontend + API) on port {port}")

    def check_server_ready():
        """Check if server is ready and signal when it is"""
        time.sleep(0.5)  # Give Flask a moment to start
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    f"http://localhost:{port}/api/status", timeout=1
                )
                if response.status_code == 200:
                    # Server is ready, send signal
                    sys.stdout.write("SERVER_READY\n")
                    sys.stdout.flush()
                    logger.info("🚀 Server ready signal sent to Electron")
                    return
            except:
                pass
            time.sleep(0.2)

        logger.warning("Failed to detect server readiness after all attempts")

    # Start readiness checker in background
    threading.Thread(target=check_server_ready, daemon=True).start()

    # Start Flask server
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    run_server()
