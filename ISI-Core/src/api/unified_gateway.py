# ISI-Core/src/api/unified_gateway.py

"""
Unified ISI API Gateway - Single Canonical Interface for All ISI Operations

Following Universal Design Philosophy:
- Geometric Beauty: Mathematical elegance through unified composition
- Canonical Interfaces: Exactly one way to interact with each abstraction
- Architectural Purity: No expedient solutions or workarounds
- Domain Fidelity: Reflects essential structure of experimental workflow

This gateway embodies the "One Way, Many Options" principle:
- ONE canonical way to access each operation
- MANY configuration options for rich behavior variations
- Implementation substitutability via dependency injection
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from pathlib import Path

# Import domain-specific interfaces
from ..interfaces.experiment_interfaces import (
    IExperimentWorkflow,
    IStimulusGenerator,
    IAcquisitionController,
    IDataAnalyzer,
)

logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfiguration:
    """
    Unified configuration for all experimental operations.
    Geometric Beauty: Clean proportions and harmonious relationships.
    """

    # Setup parameters
    setup_params: Dict[str, Any]

    # Stimulus parameters
    stimulus_params: Dict[str, Any]

    # Acquisition parameters
    acquisition_params: Dict[str, Any]

    # Analysis parameters
    analysis_params: Dict[str, Any]

    # Global configuration
    experiment_id: str
    output_directory: Path
    logging_level: str = "INFO"


@dataclass
class OperationResult:
    """
    Unified result structure for all operations.
    Mathematical Elegance: Consistent response pattern across all domains.
    """

    success: bool
    data: Any
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    operation_id: str = ""
    timestamp: str = ""


class UnifiedISIGateway:
    """
    Unified API Gateway - Single Canonical Interface for All ISI Operations

    Architectural Principles:
    - Single Responsibility: Only orchestrates between domain services
    - Open/Closed: Extensible through service registration
    - Liskov Substitution: All domain services are interchangeable
    - Interface Segregation: Clean contracts for each domain
    - Dependency Inversion: Depends on domain abstractions

    Geometric Beauty: Elegant composition of domain services with mathematical symmetry
    """

    def __init__(self, config: ExperimentConfiguration):
        """
        Initialize unified gateway with canonical configuration.

        Args:
            config: Unified experiment configuration
        """
        self.config = config
        self._setup_logging()

        # Domain service interfaces (Dependency Inversion)
        self._stimulus_service: Optional[IStimulusGenerator] = None
        self._acquisition_service: Optional[IAcquisitionController] = None
        self._analysis_service: Optional[IDataAnalyzer] = None
        self._workflow_service: Optional[IExperimentWorkflow] = None

        # Service registry for dependency injection
        self._service_registry: Dict[str, Any] = {}

        logger.info(
            f"🎯 UnifiedISIGateway initialized for experiment: {config.experiment_id}"
        )

    def _setup_logging(self):
        """Configure unified logging across all domains."""
        logging.basicConfig(
            level=getattr(logging, self.config.logging_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    # =============================================================================
    # CANONICAL INTERFACES - Exactly One Way to Interact with Each Domain
    # =============================================================================

    def setup_experiment(self) -> OperationResult:
        """
        Canonical method for experimental setup.

        Geometric Beauty: Single entry point with elegant error handling.
        Domain Fidelity: Reflects essential experimental setup workflow.

        Returns:
            OperationResult with setup validation and configuration
        """
        try:
            logger.info("🔬 Starting canonical experimental setup")

            # Validate configuration (fail-fast principle)
            validation_result = self._validate_configuration()
            if not validation_result.success:
                return validation_result

            # Initialize workflow service
            workflow_service = self._get_workflow_service()

            # Create experiment through canonical interface
            setup_result = workflow_service.create_experiment(
                name=f"Experiment_{self.config.experiment_id}",
                setup_params=self.config.setup_params,
            )

            if setup_result.success:
                logger.info("✅ Experimental setup completed successfully")
                return OperationResult(
                    success=True,
                    data=setup_result.data,
                    metadata={
                        "experiment_id": self.config.experiment_id,
                        "setup_validated": True,
                        "services_initialized": True,
                    },
                    operation_id="setup_experiment",
                )
            else:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message=f"Setup failed: {setup_result.error_message}",
                    operation_id="setup_experiment",
                )

        except Exception as e:
            logger.error(f"❌ Experimental setup failed: {e}")
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e),
                operation_id="setup_experiment",
            )

    def generate_stimulus(self) -> OperationResult:
        """
        Canonical method for stimulus generation.

        Configuration-Driven Flexibility: Rich behavior through structured config.
        Single Source of Truth: All stimulus generation through this interface.

        Returns:
            OperationResult with generated stimulus sequence
        """
        try:
            logger.info("🎬 Starting canonical stimulus generation")

            # Get stimulus service through canonical interface
            stimulus_service = self._get_stimulus_service()

            # Generate stimulus through domain service
            generation_result = stimulus_service.generate_stimulus_frames(
                stimulus_params=self.config.stimulus_params,
                setup_params=self.config.setup_params,
            )

            if generation_result.success:
                logger.info("✅ Stimulus generation completed successfully")
                return OperationResult(
                    success=True,
                    data=generation_result.data,
                    metadata={
                        "stimulus_type": self.config.stimulus_params.get(
                            "stimulus_type"
                        ),
                        "frame_count": (
                            len(generation_result.data) if generation_result.data else 0
                        ),
                        "duration": self.config.stimulus_params.get("duration"),
                    },
                    operation_id="generate_stimulus",
                )
            else:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message=f"Stimulus generation failed: {generation_result.error_message}",
                    operation_id="generate_stimulus",
                )

        except Exception as e:
            logger.error(f"❌ Stimulus generation failed: {e}")
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e),
                operation_id="generate_stimulus",
            )

    def acquire_data(self, stimulus_sequence: List[Any]) -> OperationResult:
        """
        Canonical method for data acquisition.

        Unified Interface: Single way to acquire data regardless of hardware.
        Framework Native: Leverages acquisition framework capabilities.

        Args:
            stimulus_sequence: Generated stimulus sequence

        Returns:
            OperationResult with acquisition session data
        """
        try:
            logger.info("📹 Starting canonical data acquisition")

            # Get acquisition service through canonical interface
            acquisition_service = self._get_acquisition_service()

            # Initialize acquisition
            init_result = acquisition_service.initialize_acquisition(
                self.config.acquisition_params
            )

            if not init_result.success:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message=f"Acquisition initialization failed: {init_result.error_message}",
                    operation_id="acquire_data",
                )

            # Start acquisition with stimulus
            acquisition_result = acquisition_service.start_acquisition(
                stimulus_sequence
            )

            if acquisition_result.success:
                logger.info("✅ Data acquisition completed successfully")
                return OperationResult(
                    success=True,
                    data=acquisition_result.data,
                    metadata={
                        "acquisition_id": acquisition_result.data,
                        "stimulus_frames": len(stimulus_sequence),
                        "camera_params": self.config.acquisition_params,
                    },
                    operation_id="acquire_data",
                )
            else:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message=f"Data acquisition failed: {acquisition_result.error_message}",
                    operation_id="acquire_data",
                )

        except Exception as e:
            logger.error(f"❌ Data acquisition failed: {e}")
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e),
                operation_id="acquire_data",
            )

    def analyze_data(self, acquisition_data: Any) -> OperationResult:
        """
        Canonical method for data analysis.

        Modular Excellence: Complex analysis through principled composition.
        Domain Integrity: Preserves essential analysis relationships.

        Args:
            acquisition_data: Data from acquisition session

        Returns:
            OperationResult with analysis results
        """
        try:
            logger.info("📊 Starting canonical data analysis")

            # Get analysis service through canonical interface
            analysis_service = self._get_analysis_service()

            # Run analysis through domain service
            analysis_result = analysis_service.run_analysis(
                acquisition_data=acquisition_data,
                analysis_params=self.config.analysis_params,
            )

            if analysis_result.success:
                logger.info("✅ Data analysis completed successfully")
                return OperationResult(
                    success=True,
                    data=analysis_result.data,
                    metadata={
                        "analysis_type": self.config.analysis_params.get(
                            "analysis_type"
                        ),
                        "processing_time": analysis_result.metadata.get(
                            "processing_time"
                        ),
                        "results_summary": analysis_result.metadata.get("summary"),
                    },
                    operation_id="analyze_data",
                )
            else:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message=f"Data analysis failed: {analysis_result.error_message}",
                    operation_id="analyze_data",
                )

        except Exception as e:
            logger.error(f"❌ Data analysis failed: {e}")
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e),
                operation_id="analyze_data",
            )

    # =============================================================================
    # COMPLETE WORKFLOW - Seamless Integration of All Domains
    # =============================================================================

    def run_complete_experiment(self) -> OperationResult:
        """
        Canonical method for complete experimental workflow.

        Seamless Integration: Components compose without adaptation layers.
        Natural Structural Flow: Elegant progression through experimental phases.

        Returns:
            OperationResult with complete experimental results
        """
        try:
            logger.info("🚀 Starting complete experimental workflow")

            # Phase 1: Setup
            setup_result = self.setup_experiment()
            if not setup_result.success:
                return setup_result

            # Phase 2: Stimulus Generation
            stimulus_result = self.generate_stimulus()
            if not stimulus_result.success:
                return stimulus_result

            # Phase 3: Data Acquisition
            acquisition_result = self.acquire_data(stimulus_result.data)
            if not acquisition_result.success:
                return acquisition_result

            # Phase 4: Data Analysis
            analysis_result = self.analyze_data(acquisition_result.data)
            if not analysis_result.success:
                return analysis_result

            logger.info("🎉 Complete experimental workflow finished successfully")

            return OperationResult(
                success=True,
                data={
                    "setup": setup_result.data,
                    "stimulus": stimulus_result.data,
                    "acquisition": acquisition_result.data,
                    "analysis": analysis_result.data,
                },
                metadata={
                    "experiment_id": self.config.experiment_id,
                    "workflow_complete": True,
                    "total_phases": 4,
                    "output_directory": str(self.config.output_directory),
                },
                operation_id="run_complete_experiment",
            )

        except Exception as e:
            logger.error(f"❌ Complete experimental workflow failed: {e}")
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e),
                operation_id="run_complete_experiment",
            )

    # =============================================================================
    # SERVICE MANAGEMENT - Dependency Injection with Geometric Beauty
    # =============================================================================

    def register_service(self, service_type: str, service_instance: Any):
        """
        Register domain service implementation.

        Open/Closed Principle: Extend functionality without modification.
        Implementation Substitutability: Services swappable via configuration.

        Args:
            service_type: Type of service (stimulus, acquisition, analysis, workflow)
            service_instance: Concrete service implementation
        """
        self._service_registry[service_type] = service_instance
        logger.info(
            f"🔧 Registered {service_type} service: {type(service_instance).__name__}"
        )

    def _get_stimulus_service(self) -> IStimulusGenerator:
        """Get stimulus service through canonical interface."""
        if self._stimulus_service is None:
            if "stimulus" in self._service_registry:
                self._stimulus_service = self._service_registry["stimulus"]
            else:
                # Default implementation (can be configured)
                from ...services.experiment_service import StimulusGenerator

                self._stimulus_service = StimulusGenerator()
        return self._stimulus_service

    def _get_acquisition_service(self) -> IAcquisitionController:
        """Get acquisition service through canonical interface."""
        if self._acquisition_service is None:
            if "acquisition" in self._service_registry:
                self._acquisition_service = self._service_registry["acquisition"]
            else:
                # Default implementation (can be configured)
                from ...services.experiment_service import AcquisitionController

                self._acquisition_service = AcquisitionController()
        return self._acquisition_service

    def _get_analysis_service(self) -> IDataAnalyzer:
        """Get analysis service through canonical interface."""
        if self._analysis_service is None:
            if "analysis" in self._service_registry:
                self._analysis_service = self._service_registry["analysis"]
            else:
                # Default implementation (can be configured)
                from ...services.experiment_service import DataAnalyzer

                self._analysis_service = DataAnalyzer()
        return self._analysis_service

    def _get_workflow_service(self) -> IExperimentWorkflow:
        """Get workflow service through canonical interface."""
        if self._workflow_service is None:
            if "workflow" in self._service_registry:
                self._workflow_service = self._service_registry["workflow"]
            else:
                # Default implementation (can be configured)
                from ...services.experiment_service import ExperimentWorkflow

                self._workflow_service = ExperimentWorkflow()
        return self._workflow_service

    def _validate_configuration(self) -> OperationResult:
        """
        Validate unified configuration.

        Fail-Fast Principle: Immediate validation with clear error messages.
        """
        try:
            # Validate required parameters
            required_fields = [
                "setup_params",
                "stimulus_params",
                "acquisition_params",
                "analysis_params",
            ]
            for field in required_fields:
                if (
                    not hasattr(self.config, field)
                    or getattr(self.config, field) is None
                ):
                    return OperationResult(
                        success=False,
                        data=None,
                        metadata={},
                        error_message=f"Missing required configuration field: {field}",
                        operation_id="validate_configuration",
                    )

            # Validate experiment ID
            if not self.config.experiment_id or not self.config.experiment_id.strip():
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message="Experiment ID cannot be empty",
                    operation_id="validate_configuration",
                )

            # Validate output directory
            if not self.config.output_directory:
                return OperationResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message="Output directory must be specified",
                    operation_id="validate_configuration",
                )

            return OperationResult(
                success=True,
                data={"validation_passed": True},
                metadata={"validated_fields": required_fields},
                operation_id="validate_configuration",
            )

        except Exception as e:
            return OperationResult(
                success=False,
                data=None,
                metadata={},
                error_message=f"Configuration validation failed: {e}",
                operation_id="validate_configuration",
            )


# =============================================================================
# FACTORY FUNCTION - Canonical Gateway Creation
# =============================================================================


def create_unified_gateway(config: ExperimentConfiguration) -> UnifiedISIGateway:
    """
    Factory function for creating unified gateway.

    Geometric Beauty: Elegant abstraction over gateway complexity.
    Single Source of Truth: One way to create gateways.

    Args:
        config: Unified experiment configuration

    Returns:
        Configured UnifiedISIGateway instance
    """
    gateway = UnifiedISIGateway(config)
    logger.info(f"🎯 Created unified gateway for experiment: {config.experiment_id}")
    return gateway


# =============================================================================
# CONVENIENCE FUNCTIONS - Configuration-Driven Flexibility
# =============================================================================


def create_default_configuration(
    experiment_id: str, output_dir: str
) -> ExperimentConfiguration:
    """
    Create default configuration with sensible defaults.

    Configuration-Driven Flexibility: Rich defaults with override capability.
    """
    return ExperimentConfiguration(
        experiment_id=experiment_id,
        output_directory=Path(output_dir),
        setup_params={
            "monitor_size": [33.53, 59.69],
            "monitor_distance": 10.0,
            "mouse_length": 7.5,
        },
        stimulus_params={
            "stimulus_type": "drifting_bar",
            "duration": 5.0,
            "fps": 60,
            "contrast": 1.0,
        },
        acquisition_params={
            "camera_fps": 30,
            "camera_resolution": [1920, 1080],
            "buffer_size": 1000,
        },
        analysis_params={
            "analysis_type": "response_mapping",
            "spatial_filter_sigma": 2.0,
            "temporal_filter_cutoff": 0.1,
        },
    )
