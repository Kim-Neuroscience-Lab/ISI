# ISI-Core/src/interfaces/experiment_interfaces.py

"""
Interfaces for complete ISI experimental workflow.
Defines contracts for setup, stimulus generation, acquisition, and analysis phases.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .data_interfaces import DataResponse


class ExperimentPhase(str, Enum):
    """Enumeration of experiment phases."""

    SETUP = "setup"
    STIMULUS_GENERATION = "stimulus_generation"
    ACQUISITION = "acquisition"
    ANALYSIS = "analysis"


class SetupParameters(BaseModel):
    """Parameters for experimental setup configuration."""

    # Monitor configuration
    monitor_size: Tuple[float, float] = Field(
        ..., description="Monitor size (width, height) in cm"
    )
    monitor_resolution: Tuple[int, int] = Field(
        ..., description="Monitor resolution (width, height) in pixels"
    )
    monitor_distance: float = Field(
        ..., gt=0, description="Distance from eye to monitor in cm"
    )
    monitor_elevation: float = Field(
        ..., description="Monitor elevation angle in degrees (positive tilts upward)"
    )
    monitor_rotation: float = Field(
        0.0, description="Monitor rotation angle in degrees (around viewing axis)"
    )

    # Mouse configuration
    mouse_eye_height: float = Field(..., gt=0, description="Mouse eye height in cm")
    mouse_visual_field_vertical: float = Field(
        ..., gt=0, le=180, description="Vertical visual field in degrees"
    )
    mouse_visual_field_horizontal: float = Field(
        ..., gt=0, le=360, description="Horizontal visual field in degrees"
    )

    # Environment
    table_width: float = Field(..., gt=0, description="Table width in cm")
    table_depth: float = Field(..., gt=0, description="Table depth in cm")
    table_height: float = Field(..., gt=0, description="Table height in cm")

    # ARCHITECTURAL PURITY: Hardware synchronization removed
    # Modern software synchronization handled by ISI-Acquisition

    class Config:
        validate_assignment = True


class StimulusParameters(BaseModel):
    """Parameters for stimulus generation."""

    # Basic properties
    stimulus_type: str = Field(..., description="Type of stimulus")
    duration: float = Field(..., gt=0, description="Duration in seconds")
    fps: int = Field(60, gt=0, le=120, description="Frames per second")
    contrast: float = Field(1.0, ge=0, le=1, description="Contrast value")

    # Drifting bar specific
    orientation: Optional[float] = Field(None, description="Orientation in degrees")
    width: Optional[float] = Field(None, gt=0, description="Bar width in degrees")
    speed: Optional[float] = Field(
        None, gt=0, description="Speed in degrees per second"
    )

    # Grating specific
    spatial_frequency: Optional[float] = Field(
        None, gt=0, description="Spatial frequency in cycles per degree"
    )
    temporal_frequency: Optional[float] = Field(
        None, gt=0, description="Temporal frequency in Hz"
    )
    phase_shift: Optional[float] = Field(0.0, description="Phase shift in radians")
    square_wave: bool = Field(
        False, description="Use square wave instead of sinusoidal"
    )

    # Retinotopy specific
    retinotopy_mode: Optional[str] = Field(
        None, description="Retinotopy mode: bar or expanding_ring"
    )
    cycles: Optional[int] = Field(None, gt=0, description="Number of complete cycles")

    # Color configuration
    background_color: Tuple[int, int, int] = Field(
        (128, 128, 128), description="Background RGB color"
    )
    bar_color: Optional[Tuple[int, int, int]] = Field(None, description="Bar RGB color")

    # ARCHITECTURAL PURITY: Synchronization removed (modern software approach)
    # Timing/sync handled by ISI-Acquisition in pure software

    class Config:
        validate_assignment = True


class StimulusFrame(BaseModel):
    """Individual stimulus frame data."""

    frame_number: int = Field(..., ge=0, description="Frame sequence number")
    timestamp: float = Field(..., description="Frame timestamp in seconds")
    frame_data: bytes = Field(..., description="Frame image data")
    # ARCHITECTURAL PURITY: Photodiode functionality removed from modern implementation
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional frame metadata"
    )

    class Config:
        validate_assignment = True


class AcquisitionParameters(BaseModel):
    """Parameters for data acquisition."""

    # Camera configuration
    camera_device_id: int = Field(0, ge=0, description="Camera device ID")
    camera_resolution: Tuple[int, int] = Field(
        (1920, 1080), description="Camera resolution"
    )
    camera_fps: int = Field(30, gt=0, le=60, description="Camera capture FPS")
    camera_exposure: Optional[float] = Field(
        None, description="Camera exposure in milliseconds"
    )
    camera_gain: Optional[float] = Field(None, description="Camera gain")

    # Display configuration
    stimulus_monitor_id: int = Field(
        1, ge=0, description="Monitor ID for stimulus display"
    )
    main_monitor_id: int = Field(0, ge=0, description="Monitor ID for main interface")
    fullscreen_stimulus: bool = Field(
        True, description="Display stimulus in fullscreen"
    )

    # Synchronization
    sync_tolerance_ms: float = Field(
        16.67, gt=0, description="Frame sync tolerance in milliseconds"
    )
    buffer_size: int = Field(1000, gt=0, description="Frame buffer size")

    # Recording
    save_camera_frames: bool = Field(True, description="Save camera frames to disk")
    save_stimulus_frames: bool = Field(True, description="Save stimulus frames to disk")
    output_directory: str = Field(..., description="Output directory for saved data")
    compression_quality: int = Field(
        95, ge=0, le=100, description="Image compression quality"
    )

    class Config:
        validate_assignment = True


class CameraFrame(BaseModel):
    """Individual camera frame data."""

    frame_number: int = Field(..., ge=0, description="Frame sequence number")
    timestamp: float = Field(..., description="Frame timestamp")
    camera_timestamp: float = Field(..., description="Camera-reported timestamp")
    frame_data: bytes = Field(..., description="Camera frame data")
    synchronized_stimulus_frame: Optional[int] = Field(
        None, description="Synchronized stimulus frame number"
    )
    sync_confidence: float = Field(
        0.0, ge=0, le=1, description="Synchronization confidence"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional frame metadata"
    )

    class Config:
        validate_assignment = True


class AnalysisParameters(BaseModel):
    """Parameters for data analysis."""

    # Input data
    experiment_id: str = Field(..., description="Experiment identifier")
    camera_data_path: str = Field(..., description="Path to camera data")
    stimulus_data_path: str = Field(..., description="Path to stimulus data")

    # Analysis type
    analysis_type: str = Field(..., description="Type of analysis")

    # Processing parameters
    spatial_filter_sigma: float = Field(2.0, gt=0, description="Spatial filter sigma")
    temporal_filter_cutoff: float = Field(
        0.1, gt=0, description="Temporal filter cutoff frequency"
    )
    baseline_frames: int = Field(10, gt=0, description="Number of baseline frames")
    response_window_ms: Tuple[float, float] = Field(
        (100, 500), description="Response window in milliseconds"
    )

    # Output configuration
    generate_response_maps: bool = Field(True, description="Generate response maps")
    generate_statistics: bool = Field(True, description="Generate statistical analysis")
    generate_plots: bool = Field(True, description="Generate visualization plots")
    output_format: str = Field("png", description="Output format")

    class Config:
        validate_assignment = True


class AnalysisResult(BaseModel):
    """Results from data analysis."""

    analysis_id: str = Field(..., description="Analysis identifier")
    experiment_id: str = Field(..., description="Source experiment identifier")
    analysis_type: str = Field(..., description="Type of analysis performed")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Analysis creation time"
    )

    # Results data
    response_maps: Optional[Dict[str, bytes]] = Field(
        None, description="Response map image data"
    )
    statistics: Optional[Dict[str, Any]] = Field(
        None, description="Statistical analysis results"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Analysis metadata"
    )

    # File paths
    output_directory: str = Field(..., description="Directory containing result files")
    summary_report_path: Optional[str] = Field(
        None, description="Path to summary report"
    )

    class Config:
        validate_assignment = True


# Abstract Interfaces


class ISetupManager(ABC):
    """Interface for experimental setup management."""

    @abstractmethod
    def validate_setup(
        self, parameters: SetupParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Validate setup parameters and return validation results."""
        pass

    @abstractmethod
    def generate_3d_visualization(
        self, parameters: SetupParameters
    ) -> DataResponse[str]:
        """Generate 3D visualization and return visualization data or file path."""
        pass

    @abstractmethod
    def calculate_visual_field_coverage(
        self, parameters: SetupParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Calculate visual field coverage statistics."""
        pass

    @abstractmethod
    def export_setup_configuration(
        self, parameters: SetupParameters, file_path: str
    ) -> DataResponse[bool]:
        """Export setup configuration to file."""
        pass


class IStimulusGenerator(ABC):
    """Interface for stimulus generation."""

    @abstractmethod
    def generate_stimulus_frames(
        self, parameters: StimulusParameters, setup: SetupParameters
    ) -> DataResponse[List[StimulusFrame]]:
        """Generate complete stimulus sequence."""
        pass

    @abstractmethod
    def preview_stimulus(
        self,
        parameters: StimulusParameters,
        setup: SetupParameters,
        frame_count: int = 10,
    ) -> DataResponse[List[StimulusFrame]]:
        """Generate preview frames for stimulus."""
        pass

    @abstractmethod
    def save_stimulus_sequence(
        self, frames: List[StimulusFrame], output_path: str
    ) -> DataResponse[bool]:
        """Save stimulus sequence to disk."""
        pass

    @abstractmethod
    def load_stimulus_sequence(
        self, input_path: str
    ) -> DataResponse[List[StimulusFrame]]:
        """Load stimulus sequence from disk."""
        pass


class IAcquisitionController(ABC):
    """Interface for data acquisition control."""

    @abstractmethod
    def initialize_acquisition(
        self, parameters: AcquisitionParameters
    ) -> DataResponse[bool]:
        """Initialize acquisition system with given parameters."""
        pass

    @abstractmethod
    def start_acquisition(
        self, stimulus_frames: List[StimulusFrame]
    ) -> DataResponse[str]:
        """Start data acquisition with stimulus sequence."""
        pass

    @abstractmethod
    def stop_acquisition(self) -> DataResponse[bool]:
        """Stop ongoing acquisition."""
        pass

    @abstractmethod
    def get_acquisition_status(self) -> DataResponse[Dict[str, Any]]:
        """Get current acquisition status."""
        pass

    @abstractmethod
    def get_camera_preview(self) -> DataResponse[bytes]:
        """Get current camera frame for preview."""
        pass

    @abstractmethod
    def save_acquisition_data(self, output_path: str) -> DataResponse[bool]:
        """Save acquired data to disk."""
        pass


class IFrameSynchronizer(ABC):
    """Interface for modern software frame synchronization."""

    @abstractmethod
    def synchronize_frames(
        self, camera_frames: List[CameraFrame], stimulus_frames: List[StimulusFrame]
    ) -> DataResponse[List[Tuple[CameraFrame, StimulusFrame]]]:
        """Synchronize camera and stimulus frames using software timing."""
        pass

    @abstractmethod
    def calculate_timing_accuracy(
        self, synchronized_frames: List[Tuple[CameraFrame, StimulusFrame]]
    ) -> DataResponse[Dict[str, float]]:
        """Calculate software synchronization accuracy."""
        pass

    @abstractmethod
    def calculate_sync_quality(
        self, synchronized_frames: List[Tuple[CameraFrame, StimulusFrame]]
    ) -> DataResponse[Dict[str, float]]:
        """Calculate synchronization quality metrics."""
        pass


class IDataAnalyzer(ABC):
    """Interface for data analysis."""

    @abstractmethod
    def analyze_experiment_data(
        self, parameters: AnalysisParameters
    ) -> DataResponse[AnalysisResult]:
        """Perform complete experiment data analysis."""
        pass

    @abstractmethod
    def generate_response_maps(
        self,
        camera_frames: List[CameraFrame],
        stimulus_frames: List[StimulusFrame],
        parameters: AnalysisParameters,
    ) -> DataResponse[Dict[str, bytes]]:
        """Generate response maps from synchronized data."""
        pass

    @abstractmethod
    def calculate_statistics(
        self, response_data: Dict[str, Any], parameters: AnalysisParameters
    ) -> DataResponse[Dict[str, Any]]:
        """Calculate statistical measures from response data."""
        pass

    @abstractmethod
    def export_results(
        self, result: AnalysisResult, export_format: str = "pdf"
    ) -> DataResponse[str]:
        """Export analysis results to specified format."""
        pass


class IExperimentWorkflow(ABC):
    """Interface for complete experiment workflow management."""

    @abstractmethod
    def create_experiment(
        self, name: str, setup_params: SetupParameters
    ) -> DataResponse[str]:
        """Create new experiment with setup parameters."""
        pass

    @abstractmethod
    def validate_workflow(self, experiment_id: str) -> DataResponse[Dict[str, Any]]:
        """Validate experiment workflow configuration."""
        pass

    @abstractmethod
    def get_experiment_status(self, experiment_id: str) -> DataResponse[Dict[str, Any]]:
        """Get current experiment status and progress."""
        pass

    @abstractmethod
    def transition_phase(
        self, experiment_id: str, target_phase: ExperimentPhase
    ) -> DataResponse[bool]:
        """Transition experiment to next phase."""
        pass

    @abstractmethod
    def cleanup_experiment(self, experiment_id: str) -> DataResponse[bool]:
        """Clean up experiment resources."""
        pass
