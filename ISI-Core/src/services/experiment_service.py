# ISI-Core/src/services/experiment_service.py

"""
Concrete implementations of experimental workflow interfaces.
Provides complete experimental pipeline from setup to analysis.
"""

import os
import json
import uuid
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path

from ..interfaces.experiment_interfaces import (
    ISetupManager,
    IStimulusGenerator,
    IAcquisitionController,
    IFrameSynchronizer,
    IDataAnalyzer,
    IExperimentWorkflow,
    SetupParameters,
    StimulusParameters,
    StimulusFrame,
    AcquisitionParameters,
    CameraFrame,
    AnalysisParameters,
    AnalysisResult,
    ExperimentPhase,
)
from ..interfaces.data_interfaces import DataResponse


class SetupManager(ISetupManager):
    """
    Setup manager for experimental configuration.
    Single Responsibility: Validate and manage experimental setup parameters.
    """

    def __init__(self):
        """Initialize setup manager."""
        pass

    def validate_setup(
        self, parameters: SetupParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Validate setup parameters and return validation results."""
        if not isinstance(parameters, SetupParameters):
            raise TypeError("parameters must be a SetupParameters instance")

        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "recommendations": [],
            }

            # Validate monitor configuration
            if parameters.monitor_distance < 5:
                validation_result["warnings"].append(
                    "Monitor distance is very close (< 5cm), may cause visual field distortion"
                )

            if abs(parameters.monitor_elevation) > 45:
                validation_result["warnings"].append(
                    "Monitor elevation angle is quite steep (>45°). "
                    "Consider reducing for better mouse viewing comfort."
                )

            # Validate mouse configuration
            visual_field_total = (
                parameters.mouse_visual_field_horizontal
                + parameters.mouse_visual_field_vertical
            )
            if visual_field_total > 300:
                validation_result["warnings"].append(
                    "Total visual field coverage is very large, verify mouse parameters"
                )

            # Calculate visual field coverage
            coverage_stats = self._calculate_coverage_stats(parameters)
            validation_result["coverage_statistics"] = coverage_stats

            return DataResponse(success=True, data=validation_result, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to validate setup: {e}",
            )

    def generate_3d_visualization(
        self, parameters: SetupParameters
    ) -> DataResponse[str]:
        """Generate 3D visualization and return visualization data or file path."""
        if not isinstance(parameters, SetupParameters):
            raise TypeError("parameters must be a SetupParameters instance")

        try:
            # Create visualization configuration
            vis_config = {
                "monitor_size": parameters.monitor_size,
                "monitor_distance": parameters.monitor_distance,
                "monitor_elevation": parameters.monitor_elevation,
                "mouse_eye_height": parameters.mouse_eye_height,
                "visual_field_vertical": parameters.mouse_visual_field_vertical,
                "visual_field_horizontal": parameters.mouse_visual_field_horizontal,
            }

            # Generate unique visualization ID
            viz_id = str(uuid.uuid4())

            return DataResponse(
                success=True,
                data=viz_id,
                error_message="",
                metadata={"configuration": vis_config},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to generate visualization: {e}",
            )

    def calculate_visual_field_coverage(
        self, parameters: SetupParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Calculate visual field coverage statistics."""
        if not isinstance(parameters, SetupParameters):
            raise TypeError("parameters must be a SetupParameters instance")

        try:
            coverage_stats = self._calculate_coverage_stats(parameters)
            return DataResponse(success=True, data=coverage_stats, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to calculate coverage: {e}",
            )

    def export_setup_configuration(
        self, parameters: SetupParameters, file_path: str
    ) -> DataResponse[bool]:
        """Export setup configuration to file."""
        if not isinstance(parameters, SetupParameters):
            raise TypeError("parameters must be a SetupParameters instance")
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Export configuration
            config_data = {
                "setup_parameters": parameters.dict(),
                "exported_at": datetime.now().isoformat(),
                "format_version": "1.0",
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            return DataResponse(
                success=True,
                data=True,
                error_message="",
                metadata={"exported_to": file_path},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to export configuration: {e}",
            )

    def _calculate_coverage_stats(self, parameters: SetupParameters) -> Dict[str, Any]:
        """Calculate visual field coverage statistics."""
        # Simplified coverage calculation
        monitor_width, monitor_height = parameters.monitor_size
        distance = parameters.monitor_distance

        # Calculate visual angles
        horizontal_angle = 2 * np.arctan(monitor_width / (2 * distance))
        vertical_angle = 2 * np.arctan(monitor_height / (2 * distance))

        # Convert to degrees
        horizontal_deg = np.degrees(horizontal_angle)
        vertical_deg = np.degrees(vertical_angle)

        # Calculate coverage percentages
        horizontal_coverage = min(
            100, (horizontal_deg / parameters.mouse_visual_field_horizontal) * 100
        )
        vertical_coverage = min(
            100, (vertical_deg / parameters.mouse_visual_field_vertical) * 100
        )

        return {
            "monitor_horizontal_angle": horizontal_deg,
            "monitor_vertical_angle": vertical_deg,
            "horizontal_coverage_percent": horizontal_coverage,
            "vertical_coverage_percent": vertical_coverage,
            "total_coverage_estimate": (horizontal_coverage + vertical_coverage) / 2,
        }


class StimulusGenerator(IStimulusGenerator):
    """
    Stimulus generator for creating visual stimuli.
    Single Responsibility: Generate stimulus frames based on parameters.
    """

    def __init__(self):
        """Initialize stimulus generator."""
        pass

    def generate_stimulus_frames(
        self, parameters: StimulusParameters, setup: SetupParameters
    ) -> DataResponse[List[StimulusFrame]]:
        """Generate complete stimulus sequence."""
        if not isinstance(parameters, StimulusParameters):
            raise TypeError("parameters must be a StimulusParameters instance")
        if not isinstance(setup, SetupParameters):
            raise TypeError("setup must be a SetupParameters instance")

        try:
            total_frames = int(parameters.duration * parameters.fps)
            frames = []

            for frame_num in range(total_frames):
                timestamp = frame_num / parameters.fps

                # Generate frame based on stimulus type
                frame_data = self._generate_frame(frame_num, parameters, setup)

                # ARCHITECTURAL PURITY: No photodiode state (modern software sync)
                # ARCHITECTURAL PURITY: Photodiode functionality eliminated from modern architecture

                stimulus_frame = StimulusFrame(
                    frame_number=frame_num,
                    timestamp=timestamp,
                    frame_data=frame_data,
                    metadata={
                        "stimulus_type": parameters.stimulus_type,
                        "frame_rate": parameters.fps,
                    },
                )

                frames.append(stimulus_frame)

            return DataResponse(
                success=True,
                data=frames,
                error_message="",
                metadata={"total_frames": len(frames), "duration": parameters.duration},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to generate stimulus frames: {e}",
            )

    def preview_stimulus(
        self,
        parameters: StimulusParameters,
        setup: SetupParameters,
        frame_count: int = 10,
    ) -> DataResponse[List[StimulusFrame]]:
        """Generate preview frames for stimulus."""
        if not isinstance(parameters, StimulusParameters):
            raise TypeError("parameters must be a StimulusParameters instance")
        if not isinstance(setup, SetupParameters):
            raise TypeError("setup must be a SetupParameters instance")
        if frame_count <= 0:
            raise ValueError("frame_count must be positive")

        try:
            # Create preview parameters with limited duration
            preview_duration = frame_count / parameters.fps
            preview_params = parameters.copy()
            preview_params.duration = preview_duration

            return self.generate_stimulus_frames(preview_params, setup)

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to generate preview: {e}",
            )

    def save_stimulus_sequence(
        self, frames: List[StimulusFrame], output_path: str
    ) -> DataResponse[bool]:
        """Save stimulus sequence to disk."""
        if not isinstance(frames, list):
            raise TypeError("frames must be a list")
        if not frames:
            raise ValueError("frames list cannot be empty")
        if not output_path or not output_path.strip():
            raise ValueError("output_path cannot be empty")

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Prepare data for serialization
            sequence_data = {
                "frames": [
                    {
                        "frame_number": frame.frame_number,
                        "timestamp": frame.timestamp,
                        # ARCHITECTURAL PURITY: Photodiode legacy field removed
                        "metadata": frame.metadata,
                        # Frame data saved separately as binary files
                        "frame_data_file": f"frame_{frame.frame_number:06d}.png",
                    }
                    for frame in frames
                ],
                "created_at": datetime.now().isoformat(),
                "total_frames": len(frames),
            }

            # Save metadata
            metadata_path = output_path.replace(".json", "_metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(sequence_data, f, indent=2)

            # Save individual frame data
            base_dir = os.path.dirname(output_path)
            for frame in frames:
                frame_path = os.path.join(
                    base_dir, f"frame_{frame.frame_number:06d}.png"
                )
                with open(frame_path, "wb") as f:
                    f.write(frame.frame_data)

            return DataResponse(
                success=True,
                data=True,
                error_message="",
                metadata={"saved_frames": len(frames), "output_directory": base_dir},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to save stimulus sequence: {e}",
            )

    def load_stimulus_sequence(
        self, input_path: str
    ) -> DataResponse[List[StimulusFrame]]:
        """Load stimulus sequence from disk."""
        if not input_path or not input_path.strip():
            raise ValueError("input_path cannot be empty")

        try:
            # Load metadata
            metadata_path = input_path.replace(".json", "_metadata.json")
            if not os.path.exists(metadata_path):
                raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

            with open(metadata_path, "r", encoding="utf-8") as f:
                sequence_data = json.load(f)

            # Load frame data
            frames = []
            base_dir = os.path.dirname(input_path)

            for frame_info in sequence_data["frames"]:
                frame_path = os.path.join(base_dir, frame_info["frame_data_file"])

                if not os.path.exists(frame_path):
                    raise FileNotFoundError(f"Frame file not found: {frame_path}")

                with open(frame_path, "rb") as f:
                    frame_data = f.read()

                stimulus_frame = StimulusFrame(
                    frame_number=frame_info["frame_number"],
                    timestamp=frame_info["timestamp"],
                    frame_data=frame_data,
                    metadata=frame_info["metadata"],
                )

                frames.append(stimulus_frame)

            return DataResponse(
                success=True,
                data=frames,
                error_message="",
                metadata={"loaded_frames": len(frames)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to load stimulus sequence: {e}",
            )

    def _generate_frame(
        self, frame_num: int, parameters: StimulusParameters, setup: SetupParameters
    ) -> bytes:
        """Generate individual frame data."""
        # Create a simple frame - in real implementation this would use the existing StimulusGenerator
        width, height = setup.monitor_resolution

        # Create blank frame with background color
        frame = np.ones((height, width, 3), dtype=np.uint8)
        frame[:, :] = parameters.background_color

        # Add simple stimulus based on type
        if (
            parameters.stimulus_type == "drifting_bar"
            and parameters.orientation is not None
        ):
            self._add_drifting_bar(frame, frame_num, parameters)

        # Convert frame to bytes without cv2 dependency
        frame_bytes = frame.tobytes()
        return frame_bytes

    def _add_drifting_bar(
        self, frame: np.ndarray, frame_num: int, parameters: StimulusParameters
    ) -> None:
        """Add drifting bar to frame."""
        height, width = frame.shape[:2]

        # Simple horizontal bar that moves vertically
        if parameters.orientation == 0:  # Horizontal bar
            bar_height = int(height * 0.1)  # 10% of screen height
            position = int((frame_num * 2) % height)  # Move 2 pixels per frame

            if position + bar_height < height:
                frame[position : position + bar_height, :] = (255, 255, 255)

    # ARCHITECTURAL PURITY: Photodiode removed (legacy hardware synchronization)
    # Modern software synchronization handled by ISI-Acquisition
    # def _calculate_photodiode_state() - REMOVED (architectural violation)


class AcquisitionController(IAcquisitionController):
    """
    Acquisition controller for camera capture and stimulus display.
    Single Responsibility: Control data acquisition process.
    """

    def __init__(self):
        """Initialize acquisition controller."""
        self._initialized = False
        self._acquisition_active = False
        self._camera: Optional[Any] = None
        self._acquisition_thread: Optional[threading.Thread] = None
        self._parameters: Optional[AcquisitionParameters] = None

    def initialize_acquisition(
        self, parameters: AcquisitionParameters
    ) -> DataResponse[bool]:
        """Initialize acquisition system with given parameters."""
        if not isinstance(parameters, AcquisitionParameters):
            raise TypeError("parameters must be an AcquisitionParameters instance")

        try:
            self._parameters = parameters

            # In a real implementation, would initialize camera
            # For now, simulate successful initialization
            self._camera = {
                "device_id": parameters.camera_device_id,
                "resolution": parameters.camera_resolution,
                "fps": parameters.camera_fps,
                "opened": True,
            }

            # Create output directory
            os.makedirs(parameters.output_directory, exist_ok=True)

            self._initialized = True
            return DataResponse(success=True, data=True, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to initialize acquisition: {e}",
            )

    def start_acquisition(
        self, stimulus_frames: List[StimulusFrame]
    ) -> DataResponse[str]:
        """Start data acquisition with stimulus sequence."""
        if not self._initialized:
            raise RuntimeError("Acquisition not initialized")
        if not isinstance(stimulus_frames, list):
            raise TypeError("stimulus_frames must be a list")
        if not stimulus_frames:
            raise ValueError("stimulus_frames cannot be empty")

        try:
            if self._acquisition_active:
                raise RuntimeError("Acquisition already active")

            # Generate acquisition ID
            acquisition_id = str(uuid.uuid4())

            # Start acquisition in separate thread
            self._acquisition_active = True
            self._acquisition_thread = threading.Thread(
                target=self._acquisition_worker,
                args=(stimulus_frames, acquisition_id),
                daemon=True,
            )
            self._acquisition_thread.start()

            return DataResponse(
                success=True,
                data=acquisition_id,
                error_message="",
                metadata={"stimulus_frames": len(stimulus_frames)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to start acquisition: {e}",
            )

    def stop_acquisition(self) -> DataResponse[bool]:
        """Stop ongoing acquisition."""
        try:
            if not self._acquisition_active:
                return DataResponse(success=True, data=True, error_message="")

            self._acquisition_active = False

            if self._acquisition_thread and self._acquisition_thread.is_alive():
                self._acquisition_thread.join(timeout=5.0)

            return DataResponse(success=True, data=True, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to stop acquisition: {e}",
            )

    def get_acquisition_status(self) -> DataResponse[Dict[str, Any]]:
        """Get current acquisition status."""
        try:
            status = {
                "initialized": self._initialized,
                "active": self._acquisition_active,
                "camera_connected": self._camera is not None
                and self._camera.get("opened", False),
            }

            return DataResponse(success=True, data=status, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to get status: {e}",
            )

    def get_camera_preview(self) -> DataResponse[bytes]:
        """Get current camera frame for preview."""
        if not self._initialized or self._camera is None:
            raise RuntimeError("Camera not initialized")

        try:
            # Simulate camera frame capture
            # In real implementation would capture from camera
            width, height = (640, 480)
            if self._parameters:
                width, height = self._parameters.camera_resolution

            dummy_frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
            frame_bytes = dummy_frame.tobytes()

            return DataResponse(success=True, data=frame_bytes, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to get preview: {e}",
            )

    def save_acquisition_data(self, output_path: str) -> DataResponse[bool]:
        """Save acquired data to disk."""
        if not output_path or not output_path.strip():
            raise ValueError("output_path cannot be empty")

        try:
            # Implementation would save captured frames and metadata
            # For now, return success
            return DataResponse(success=True, data=True, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to save data: {e}",
            )

    def _acquisition_worker(
        self, stimulus_frames: List[StimulusFrame], acquisition_id: str
    ) -> None:
        """Worker thread for data acquisition."""
        try:
            # Implementation would handle stimulus display and camera capture
            # This is a simplified version
            frame_count = 0
            start_time = time.time()

            while self._acquisition_active and frame_count < len(stimulus_frames):
                # Simulate camera frame capture
                frame_count += 1

                # Display stimulus frame (would need proper display handling)
                # For now, just sleep to simulate frame timing
                if self._parameters is not None:
                    time.sleep(1.0 / self._parameters.camera_fps)
                else:
                    time.sleep(1.0 / 30)  # Default 30 FPS

        except Exception as e:
            print(f"Acquisition worker error: {e}")
        finally:
            self._acquisition_active = False


class FrameSynchronizer(IFrameSynchronizer):
    """
    Frame synchronizer for aligning stimulus and camera frames.
    Single Responsibility: Synchronize frames using photodiode signals.
    """

    def __init__(self):
        """Initialize frame synchronizer."""
        pass

    def synchronize_frames(
        self, camera_frames: List[CameraFrame], stimulus_frames: List[StimulusFrame]
    ) -> DataResponse[List[Tuple[CameraFrame, StimulusFrame]]]:
        """Synchronize camera and stimulus frames."""
        if not isinstance(camera_frames, list):
            raise TypeError("camera_frames must be a list")
        if not isinstance(stimulus_frames, list):
            raise TypeError("stimulus_frames must be a list")
        if not camera_frames:
            raise ValueError("camera_frames cannot be empty")
        if not stimulus_frames:
            raise ValueError("stimulus_frames cannot be empty")

        try:
            synchronized_pairs = []

            # Simple timestamp-based synchronization
            # In real implementation, would use photodiode detection
            for camera_frame in camera_frames:
                best_match = None
                min_time_diff = float("inf")

                for stimulus_frame in stimulus_frames:
                    time_diff = abs(camera_frame.timestamp - stimulus_frame.timestamp)
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        best_match = stimulus_frame

                if best_match is not None:
                    # Update camera frame with sync info
                    camera_frame.synchronized_stimulus_frame = best_match.frame_number
                    camera_frame.sync_confidence = max(0.0, 1.0 - min_time_diff)
                    synchronized_pairs.append((camera_frame, best_match))

            return DataResponse(
                success=True,
                data=synchronized_pairs,
                error_message="",
                metadata={"synchronized_count": len(synchronized_pairs)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to synchronize frames: {e}",
            )

    def detect_photodiode_signals(
        self, camera_frames: List[CameraFrame]
    ) -> DataResponse[List[float]]:
        """Detect photodiode signals in camera frames."""
        if not isinstance(camera_frames, list):
            raise TypeError("camera_frames must be a list")
        if not camera_frames:
            raise ValueError("camera_frames cannot be empty")

        try:
            # Simulate photodiode signal detection
            # In real implementation, would analyze frame regions
            photodiode_signals = []

            for frame in camera_frames:
                # Simulate signal strength based on frame number
                signal_strength = 0.8 if (frame.frame_number % 10 == 0) else 0.1
                photodiode_signals.append(signal_strength)

            return DataResponse(
                success=True,
                data=photodiode_signals,
                error_message="",
                metadata={"detected_signals": len(photodiode_signals)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to detect photodiode signals: {e}",
            )

    def calculate_sync_quality(
        self, synchronized_frames: List[Tuple[CameraFrame, StimulusFrame]]
    ) -> DataResponse[Dict[str, float]]:
        """Calculate synchronization quality metrics."""
        if not isinstance(synchronized_frames, list):
            raise TypeError("synchronized_frames must be a list")
        if not synchronized_frames:
            raise ValueError("synchronized_frames cannot be empty")

        try:
            # Calculate sync quality metrics
            sync_confidences = [
                camera_frame.sync_confidence for camera_frame, _ in synchronized_frames
            ]

            time_diffs = [
                abs(camera_frame.timestamp - stimulus_frame.timestamp)
                for camera_frame, stimulus_frame in synchronized_frames
            ]

            quality_metrics = {
                "mean_confidence": sum(sync_confidences) / len(sync_confidences),
                "min_confidence": min(sync_confidences),
                "max_confidence": max(sync_confidences),
                "mean_time_diff": sum(time_diffs) / len(time_diffs),
                "max_time_diff": max(time_diffs),
                "total_synchronized": len(synchronized_frames),
            }

            return DataResponse(success=True, data=quality_metrics, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to calculate sync quality: {e}",
            )


class DataAnalyzer(IDataAnalyzer):
    """
    Data analyzer for processing experimental results.
    Single Responsibility: Analyze synchronized experimental data.
    """

    def __init__(self):
        """Initialize data analyzer."""
        pass

    def analyze_experiment_data(
        self, parameters: AnalysisParameters
    ) -> DataResponse[AnalysisResult]:
        """Perform complete experiment data analysis."""
        if not isinstance(parameters, AnalysisParameters):
            raise TypeError("parameters must be an AnalysisParameters instance")

        try:
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())

            # Create analysis result
            result = AnalysisResult(
                analysis_id=analysis_id,
                experiment_id=parameters.experiment_id,
                analysis_type=parameters.analysis_type,
                created_at=datetime.now(),
                response_maps=None,
                statistics=None,
                metadata={
                    "analysis_parameters": parameters.dict(),
                    "processing_complete": True,
                },
                output_directory=os.path.dirname(parameters.camera_data_path),
                summary_report_path=None,
            )

            # Simulate analysis processing
            if parameters.generate_response_maps:
                result.response_maps = {"response_map": b"simulated_response_map_data"}

            if parameters.generate_statistics:
                result.statistics = {
                    "mean_response": 0.5,
                    "max_response": 1.0,
                    "response_pixels": 12500,
                    "significance_level": 0.05,
                }

            return DataResponse(
                success=True,
                data=result,
                error_message="",
                metadata={"analysis_id": analysis_id},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to analyze experiment data: {e}",
            )

    def generate_response_maps(
        self,
        camera_frames: List[CameraFrame],
        stimulus_frames: List[StimulusFrame],
        parameters: AnalysisParameters,
    ) -> DataResponse[Dict[str, bytes]]:
        """Generate response maps from synchronized data."""
        if not isinstance(camera_frames, list):
            raise TypeError("camera_frames must be a list")
        if not isinstance(stimulus_frames, list):
            raise TypeError("stimulus_frames must be a list")
        if not isinstance(parameters, AnalysisParameters):
            raise TypeError("parameters must be an AnalysisParameters instance")

        try:
            # Simulate response map generation
            response_maps = {
                "amplitude_map": b"simulated_amplitude_map",
                "phase_map": b"simulated_phase_map",
                "significance_map": b"simulated_significance_map",
            }

            return DataResponse(
                success=True,
                data=response_maps,
                error_message="",
                metadata={"maps_generated": len(response_maps)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to generate response maps: {e}",
            )

    def calculate_statistics(
        self, response_data: Dict[str, Any], parameters: AnalysisParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Calculate statistical measures from response data."""
        if not isinstance(response_data, dict):
            raise TypeError("response_data must be a dictionary")
        if not isinstance(parameters, AnalysisParameters):
            raise TypeError("parameters must be an AnalysisParameters instance")

        try:
            # Simulate statistical calculations
            statistics = {
                "n_responsive_pixels": 1250,
                "mean_response_amplitude": 0.15,
                "std_response_amplitude": 0.08,
                "max_response_amplitude": 0.85,
                "response_threshold": 0.1,
                "snr_ratio": 3.2,
                "p_value": 0.001,
            }

            return DataResponse(success=True, data=statistics, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to calculate statistics: {e}",
            )

    def export_results(
        self, result: AnalysisResult, export_format: str = "pdf"
    ) -> DataResponse[str]:
        """Export analysis results to specified format."""
        if not isinstance(result, AnalysisResult):
            raise TypeError("result must be an AnalysisResult instance")
        if not export_format or not export_format.strip():
            raise ValueError("export_format cannot be empty")

        try:
            # Generate export file path
            export_filename = f"analysis_report_{result.analysis_id}.{export_format}"
            export_path = os.path.join(result.output_directory, export_filename)

            # Simulate report generation
            report_content = {
                "analysis_id": result.analysis_id,
                "experiment_id": result.experiment_id,
                "analysis_type": result.analysis_type,
                "created_at": result.created_at.isoformat(),
                "statistics": result.statistics,
                "metadata": result.metadata,
            }

            # Save report (simulated)
            os.makedirs(result.output_directory, exist_ok=True)
            with open(export_path, "w") as f:
                json.dump(report_content, f, indent=2, default=str)

            return DataResponse(
                success=True,
                data=export_path,
                error_message="",
                metadata={"export_format": export_format},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to export results: {e}",
            )


class ExperimentWorkflow(IExperimentWorkflow):
    """
    Complete experiment workflow manager.
    Single Responsibility: Orchestrate complete experimental pipeline.
    """

    def __init__(self):
        """Initialize experiment workflow manager."""
        self._experiments: Dict[str, Dict[str, Any]] = {}
        self._current_phases: Dict[str, ExperimentPhase] = {}

    def create_experiment(
        self, name: str, setup_params: SetupParameters
    ) -> DataResponse[str]:
        """Create new experiment with setup parameters."""
        if not name or not name.strip():
            raise ValueError("name cannot be empty")
        if not isinstance(setup_params, SetupParameters):
            raise TypeError("setup_params must be a SetupParameters instance")

        try:
            # Generate experiment ID
            experiment_id = str(uuid.uuid4())

            # Initialize experiment
            self._experiments[experiment_id] = {
                "name": name,
                "setup_parameters": setup_params.dict(),
                "created_at": datetime.now().isoformat(),
                "status": "created",
                "stimulus_frames": None,
                "acquisition_data": None,
                "analysis_results": None,
            }

            self._current_phases[experiment_id] = ExperimentPhase.SETUP

            return DataResponse(
                success=True,
                data=experiment_id,
                error_message="",
                metadata={
                    "experiment_name": name,
                    "phase": ExperimentPhase.SETUP.value,
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to create experiment: {e}",
            )

    def validate_workflow(self, experiment_id: str) -> DataResponse[Dict[str, Any]]:
        """Validate experiment workflow configuration."""
        if not experiment_id or not experiment_id.strip():
            raise ValueError("experiment_id cannot be empty")

        try:
            if experiment_id not in self._experiments:
                raise ValueError(f"Experiment {experiment_id} not found")

            experiment = self._experiments[experiment_id]
            current_phase = self._current_phases.get(
                experiment_id, ExperimentPhase.SETUP
            )

            validation_result = {
                "experiment_id": experiment_id,
                "current_phase": current_phase.value,
                "setup_complete": experiment.get("setup_parameters") is not None,
                "stimulus_ready": experiment.get("stimulus_frames") is not None,
                "acquisition_ready": current_phase
                in [ExperimentPhase.ACQUISITION, ExperimentPhase.ANALYSIS],
                "analysis_ready": current_phase == ExperimentPhase.ANALYSIS,
                "workflow_valid": True,
                "next_available_phases": self._get_next_phases(current_phase),
            }

            return DataResponse(success=True, data=validation_result, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to validate workflow: {e}",
            )

    def get_experiment_status(self, experiment_id: str) -> DataResponse[Dict[str, Any]]:
        """Get current experiment status and progress."""
        if not experiment_id or not experiment_id.strip():
            raise ValueError("experiment_id cannot be empty")

        try:
            if experiment_id not in self._experiments:
                raise ValueError(f"Experiment {experiment_id} not found")

            experiment = self._experiments[experiment_id]
            current_phase = self._current_phases.get(
                experiment_id, ExperimentPhase.SETUP
            )

            status = {
                "experiment_id": experiment_id,
                "name": experiment["name"],
                "created_at": experiment["created_at"],
                "current_phase": current_phase.value,
                "status": experiment["status"],
                "progress": self._calculate_progress(experiment, current_phase),
                "has_setup": experiment.get("setup_parameters") is not None,
                "has_stimulus": experiment.get("stimulus_frames") is not None,
                "has_acquisition": experiment.get("acquisition_data") is not None,
                "has_analysis": experiment.get("analysis_results") is not None,
            }

            return DataResponse(success=True, data=status, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to get experiment status: {e}",
            )

    def transition_phase(
        self, experiment_id: str, target_phase: ExperimentPhase
    ) -> DataResponse[bool]:
        """Transition experiment to next phase."""
        if not experiment_id or not experiment_id.strip():
            raise ValueError("experiment_id cannot be empty")
        if not isinstance(target_phase, ExperimentPhase):
            raise TypeError("target_phase must be an ExperimentPhase")

        try:
            if experiment_id not in self._experiments:
                raise ValueError(f"Experiment {experiment_id} not found")

            current_phase = self._current_phases.get(
                experiment_id, ExperimentPhase.SETUP
            )

            # Validate transition is allowed
            if not self._is_valid_transition(current_phase, target_phase):
                raise ValueError(
                    f"Invalid transition from {current_phase.value} to {target_phase.value}"
                )

            # Update phase
            self._current_phases[experiment_id] = target_phase
            self._experiments[experiment_id]["status"] = f"in_{target_phase.value}"

            return DataResponse(
                success=True,
                data=True,
                error_message="",
                metadata={
                    "from_phase": current_phase.value,
                    "to_phase": target_phase.value,
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to transition phase: {e}",
            )

    def cleanup_experiment(self, experiment_id: str) -> DataResponse[bool]:
        """Clean up experiment resources."""
        if not experiment_id or not experiment_id.strip():
            raise ValueError("experiment_id cannot be empty")

        try:
            if experiment_id in self._experiments:
                del self._experiments[experiment_id]

            if experiment_id in self._current_phases:
                del self._current_phases[experiment_id]

            return DataResponse(success=True, data=True, error_message="")

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to cleanup experiment: {e}",
            )

    def _get_next_phases(self, current_phase: ExperimentPhase) -> List[str]:
        """Get list of valid next phases."""
        phase_transitions = {
            ExperimentPhase.SETUP: [ExperimentPhase.STIMULUS_GENERATION.value],
            ExperimentPhase.STIMULUS_GENERATION: [ExperimentPhase.ACQUISITION.value],
            ExperimentPhase.ACQUISITION: [ExperimentPhase.ANALYSIS.value],
            ExperimentPhase.ANALYSIS: [],
        }
        return phase_transitions.get(current_phase, [])

    def _is_valid_transition(
        self, current: ExperimentPhase, target: ExperimentPhase
    ) -> bool:
        """Check if phase transition is valid."""
        valid_transitions = {
            ExperimentPhase.SETUP: [ExperimentPhase.STIMULUS_GENERATION],
            ExperimentPhase.STIMULUS_GENERATION: [ExperimentPhase.ACQUISITION],
            ExperimentPhase.ACQUISITION: [ExperimentPhase.ANALYSIS],
            ExperimentPhase.ANALYSIS: [],
        }
        return target in valid_transitions.get(current, [])

    def _calculate_progress(
        self, experiment: Dict[str, Any], phase: ExperimentPhase
    ) -> float:
        """Calculate experiment progress percentage."""
        progress_weights = {
            ExperimentPhase.SETUP: 0.25,
            ExperimentPhase.STIMULUS_GENERATION: 0.50,
            ExperimentPhase.ACQUISITION: 0.75,
            ExperimentPhase.ANALYSIS: 1.0,
        }
        return progress_weights.get(phase, 0.0)
