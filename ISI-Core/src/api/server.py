# src/python/server.py

"""
Flask server that serves as the backend for the ISI Electron app.
This server provides APIs for the various ISI components.
"""

import os
import sys
import json
import logging
import numpy as np
from flask import Flask, request, jsonify, Response

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Add the ISI-Stimulus directory to the Python path so we can import modules from there
current_dir = os.path.dirname(os.path.abspath(__file__))
# Move up to the ISI directory and then to ISI-Stimulus
isi_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
stimulus_dir = os.path.join(isi_dir, "ISI-Stimulus")
sys.path.append(stimulus_dir)

# Import ISI modules - FAIL FAST if imports fail
try:
    import view_geometry as vg
    from interactive_setup import InteractiveSetup, visualize_interactive_setup
    from stimulus_generator import StimulusGenerator
    from experimental_model import ExperimentalModel

    logger.info("Successfully imported ISI modules")
except ImportError as e:
    logger.critical(f"Failed to import required ISI modules: {e}")
    raise RuntimeError(f"Critical dependency missing: {e}") from e

# Landmark detection is now handled by ISI-Integration frontend
# ISI-Core provides setup and configuration only - no real-time processing
# GeometricLandmarkDetector = None (removed architectural violation)

# Pose transformation is now handled by ISI-Integration frontend
# ISI-Core provides setup and configuration only - no real-time processing
# PoseTransformer = None (removed architectural violation)


# Debug route to test connection
@app.route("/", methods=["GET"])
def index():
    logger.info("Received request to /")
    resp = Response(json.dumps({"status": "ok", "message": "Flask server is running"}))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


# Catch all OPTIONS requests
@app.route("/", defaults={"path": ""}, methods=["OPTIONS"])
@app.route("/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    logger.info(f"Received OPTIONS request to /{path}")
    resp = Response("")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


# Setup route
@app.route("/setup/parameters", methods=["GET"])
def get_setup_parameters():
    """Get the current setup parameters."""
    logger.info("Received request to /setup/parameters")

    # Create response with parameters
    resp_data = {
        "monitor_size": vg.MONITOR_SIZE,
        "monitor_distance": vg.MONITOR_DISTANCE,
        "monitor_elevation": vg.MONITOR_ELEVATION,
        "monitor_rotation": vg.MONITOR_ROTATION,
        "mouse_eye_height": vg.MOUSE_EYE_HEIGHT,
        "mouse_visual_field_vertical": vg.MOUSE_VISUAL_FIELD_VERTICAL,
        "mouse_visual_field_horizontal": vg.MOUSE_VISUAL_FIELD_HORIZONTAL,
        "perpendicular_bisector_height": vg.PERPENDICULAR_BISECTOR_HEIGHT,
        "monitor_orientation": vg.MONITOR_ORIENTATION,
        "transform_type": vg.TRANSFORM_TYPE,
    }

    # Create response with CORS headers
    resp = Response(json.dumps(resp_data))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/setup/visualization", methods=["POST"])
def create_visualization():
    """Return visualization parameters for the client-side Three.js renderer."""
    logger.info("Received POST to /setup/visualization")
    data = request.get_json(silent=True) or {}

    # Extract parameters with defaults from view_geometry
    monitor_size = data.get("monitor_size", vg.MONITOR_SIZE)
    monitor_distance = data.get("monitor_distance", vg.MONITOR_DISTANCE)
    monitor_elevation = data.get("monitor_elevation", vg.MONITOR_ELEVATION)
    monitor_rotation = data.get("monitor_rotation", vg.MONITOR_ROTATION)
    mouse_eye_height = data.get("mouse_eye_height", vg.MOUSE_EYE_HEIGHT)
    mouse_visual_field_vertical = data.get(
        "mouse_visual_field_vertical", vg.MOUSE_VISUAL_FIELD_VERTICAL
    )
    mouse_visual_field_horizontal = data.get(
        "mouse_visual_field_horizontal", vg.MOUSE_VISUAL_FIELD_HORIZONTAL
    )
    perpendicular_bisector_height = data.get(
        "perpendicular_bisector_height", vg.PERPENDICULAR_BISECTOR_HEIGHT
    )
    monitor_orientation = data.get("monitor_orientation", vg.MONITOR_ORIENTATION)

    try:
        # Instead of generating a Plotly visualization, return the parameters directly
        # which will be used by the Three.js renderer in the frontend
        resp_data = {
            "success": True,
            "params": {
                "monitor_size": monitor_size,
                "monitor_distance": monitor_distance,
                "monitor_elevation": monitor_elevation,
                "monitor_rotation": monitor_rotation,
                "mouse_eye_height": mouse_eye_height,
                "mouse_visual_field_vertical": mouse_visual_field_vertical,
                "mouse_visual_field_horizontal": mouse_visual_field_horizontal,
                "perpendicular_bisector_height": perpendicular_bisector_height,
                "monitor_orientation": monitor_orientation,
            },
        }

        # Create response with CORS headers
        resp = Response(json.dumps(resp_data))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Content-Type"] = "application/json"
        return resp

    except Exception as e:
        logger.error(f"Error creating visualization data: {e}")
        resp_data = {
            "success": False,
            "message": f"Error creating visualization data: {str(e)}",
        }

        # Create response with CORS headers
        resp = Response(json.dumps(resp_data), status=500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Content-Type"] = "application/json"
        return resp


@app.route("/stimulus/generate", methods=["POST"])
def generate_stimulus():
    """Generate a stimulus with the provided parameters."""
    logger.info("Received POST to /stimulus/generate")
    data = request.get_json(silent=True) or {}

    # Extract parameters
    stimulus_type = data.get("stimulus_type", "drifting-bar")

    # Common parameters
    orientation = data.get("orientation", 0)
    duration = data.get("duration", 5)
    contrast = data.get("contrast", 1.0)
    fps = data.get("fps", 60)

    try:
        # For now, just return mock success response without actually generating
        # the stimulus since we've disabled the stimulus generator for WebGL

        # Create output directory
        output_dir = os.path.join(isi_dir, "ISI-Integration", "output")
        os.makedirs(output_dir, exist_ok=True)

        # Mock video path
        video_path = os.path.join(output_dir, f"{stimulus_type}.mp4")

        resp_data = {
            "success": True,
            "message": "Stimulus parameters received successfully",
            "video_path": video_path,
        }

        # Create response with CORS headers
        resp = Response(json.dumps(resp_data))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Content-Type"] = "application/json"
        return resp

    except Exception as e:
        logger.error(f"Error generating stimulus: {e}")
        resp_data = {
            "success": False,
            "message": f"Error generating stimulus: {str(e)}",
        }

        # Create response with CORS headers
        resp = Response(json.dumps(resp_data), status=500)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Content-Type"] = "application/json"
        return resp


@app.route("/acquisition/start", methods=["POST"])
def start_acquisition():
    """Start the acquisition process."""
    logger.info("Received POST to /acquisition/start")

    try:
        # Initialize acquisition service with proper configuration
        acquisition_service = _get_acquisition_service()
        result = acquisition_service.start_acquisition()

        resp_data = {
            "success": True,
            "message": "Acquisition started successfully",
            "acquisition_id": result.get("acquisition_id"),
            "status": result.get("status"),
        }
    except Exception as e:
        logger.error(f"Failed to start acquisition: {e}")
        resp_data = {
            "success": False,
            "message": f"Failed to start acquisition: {str(e)}",
        }

    # Create response with CORS headers
    resp = Response(json.dumps(resp_data))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/acquisition/stop", methods=["POST"])
def stop_acquisition():
    """Stop the acquisition process."""
    logger.info("Received POST to /acquisition/stop")

    try:
        # Stop acquisition through proper service interface
        acquisition_service = _get_acquisition_service()
        result = acquisition_service.stop_acquisition()

        resp_data = {
            "success": True,
            "message": "Acquisition stopped successfully",
            "status": result.get("status"),
        }
    except Exception as e:
        logger.error(f"Failed to stop acquisition: {e}")
        resp_data = {
            "success": False,
            "message": f"Failed to stop acquisition: {str(e)}",
        }

    # Create response with CORS headers
    resp = Response(json.dumps(resp_data))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


@app.route("/analysis/start", methods=["POST"])
def start_analysis():
    """Start the analysis process."""
    logger.info("Received POST to /analysis/start")

    try:
        # Initialize analysis service with proper configuration
        analysis_service = _get_analysis_service()
        result = analysis_service.start_analysis()

        resp_data = {
            "success": True,
            "message": "Analysis started successfully",
            "analysis_id": result.get("analysis_id"),
            "status": result.get("status"),
        }
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        resp_data = {"success": False, "message": f"Failed to start analysis: {str(e)}"}

    # Create response with CORS headers
    resp = Response(json.dumps(resp_data))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Content-Type"] = "application/json"
    return resp


def _get_acquisition_service():
    """Get acquisition service instance - single source of truth."""
    # In production, this would return the properly configured acquisition service
    # For now, return a mock service that implements the interface
    return MockAcquisitionService()


def _get_analysis_service():
    """Get analysis service instance - single source of truth."""
    # In production, this would return the properly configured analysis service
    # For now, return a mock service that implements the interface
    return MockAnalysisService()


class MockAcquisitionService:
    """Mock acquisition service for development."""

    def start_acquisition(self):
        """Start acquisition process."""
        return {"acquisition_id": "acq_001", "status": "running"}

    def stop_acquisition(self):
        """Stop acquisition process."""
        return {"status": "stopped"}


class MockAnalysisService:
    """Mock analysis service for development."""

    def start_analysis(self):
        """Start analysis process."""
        return {"analysis_id": "ana_001", "status": "running"}


# ARCHITECTURAL PURITY: Landmark detection moved to ISI-Integration
# ISI-Core handles setup/configuration only - no frontend processing
# /landmarks/detect endpoint removed (architectural violation)


# ARCHITECTURAL PURITY: Pose transformation moved to ISI-Integration
# ISI-Core handles setup/configuration only - no frontend processing
# /pose/transform endpoint removed (architectural violation)


# Run the server
if __name__ == "__main__":
    # Use port 5001 instead of 5000
    port = 5001
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
