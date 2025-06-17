"""
Configuration service implementing IConfigurationManager interface.
Provides centralized configuration management with Pydantic validation.
"""

import json
import os
from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

from ..interfaces.data_interfaces import (
    IConfigurationManager,
    ExperimentConfiguration,
    DataResponse,
)
from ..interfaces.geometry_interfaces import GeometryParameters
from ..interfaces.visualization_interfaces import VisualizationConfig


class ISIConfiguration(BaseModel):
    """Main ISI system configuration with validation."""

    # System info
    version: str = Field("1.0.0", description="Configuration version")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Creation timestamp",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Last update timestamp",
    )

    # Experiment configuration
    experiment: ExperimentConfiguration = Field(
        ..., description="Experiment configuration"
    )

    # Geometry parameters
    geometry: GeometryParameters = Field(
        default_factory=lambda: GeometryParameters(), description="Geometry parameters"
    )

    # Visualization configuration
    visualization: VisualizationConfig = Field(
        default_factory=lambda: VisualizationConfig(),
        description="Visualization configuration",
    )

    # Additional settings
    debug_mode: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")
    auto_save: bool = Field(True, description="Enable auto-save")
    backup_count: int = Field(
        5, ge=0, le=10, description="Number of backup files to keep"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v

    class Config:
        validate_assignment = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now().isoformat()


class ConfigurationService(IConfigurationManager):
    """
    Configuration service implementing IConfigurationManager interface.
    Single Responsibility: Handle configuration loading, saving, and validation.
    """

    def __init__(self, config_dir: str = "config"):
        """Initialize configuration service."""
        self.config_dir = config_dir
        self._ensure_config_dir()
        self._current_config: ISIConfiguration = self._create_default_config()

    def load_configuration(
        self, config_path: str
    ) -> DataResponse[ExperimentConfiguration]:
        """Load configuration from file."""
        try:
            if not os.path.exists(config_path):
                return DataResponse(
                    success=False,
                    error_message=f"Configuration file not found: {config_path}",
                )

            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Parse as ISI configuration
            isi_config = ISIConfiguration(**config_data)
            self._current_config = isi_config

            return DataResponse(
                success=True,
                data=isi_config.experiment,
                metadata={
                    "config_path": config_path,
                    "loaded_at": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            return DataResponse(
                success=False, error_message=f"Failed to load configuration: {str(e)}"
            )

    def save_configuration(
        self, config: ExperimentConfiguration, config_path: str
    ) -> DataResponse[bool]:
        """Save configuration to file."""
        try:
            # Update current configuration
            self._current_config.experiment = config
            self._current_config.update_timestamp()

            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            # Create backup if file exists
            if os.path.exists(config_path) and self._current_config.auto_save:
                self._create_backup(config_path)

            # Save configuration
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._current_config.dict(), f, indent=2, ensure_ascii=False)

            return DataResponse(
                success=True,
                data=True,
                metadata={
                    "config_path": config_path,
                    "saved_at": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to save configuration: {str(e)}",
            )

    def validate_configuration(
        self, config: ExperimentConfiguration
    ) -> DataResponse[Dict[str, Any]]:
        """Validate configuration and return validation results."""
        try:
            # Create temporary ISI config for validation
            temp_config = self._current_config.copy()
            temp_config.experiment = config

            # Pydantic validation will raise if invalid
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "config_summary": {
                    "experiment_name": config.experiment_name,
                    "experiment_type": config.experiment_type,
                    "monitor_config_keys": list(config.monitor_config.keys()),
                    "mouse_config_keys": list(config.mouse_config.keys()),
                    "stimulus_config_keys": list(config.stimulus_config.keys()),
                },
            }

            return DataResponse(success=True, data=validation_result)

        except Exception as e:
            validation_result = {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "config_summary": None,
            }

            return DataResponse(
                success=True,  # Validation completed, even if config is invalid
                data=validation_result,
            )

    def get_default_configuration(self) -> ExperimentConfiguration:
        """Get default configuration."""
        return self._create_default_experiment_config()

    def merge_configurations(
        self, base: ExperimentConfiguration, override: Dict[str, Any]
    ) -> ExperimentConfiguration:
        """Merge configuration with overrides."""
        # Convert base config to dict
        base_dict = base.dict()

        # Deep merge override into base
        merged_dict = self._deep_merge(base_dict, override)

        # Create new configuration from merged dict
        return ExperimentConfiguration(**merged_dict)

    def get_current_config(self) -> ISIConfiguration:
        """Get current ISI configuration."""
        return self._current_config

    def update_geometry_params(self, geometry_params: GeometryParameters) -> None:
        """Update geometry parameters."""
        self._current_config.geometry = geometry_params
        self._current_config.update_timestamp()

    def update_visualization_config(self, vis_config: VisualizationConfig) -> None:
        """Update visualization configuration."""
        self._current_config.visualization = vis_config
        self._current_config.update_timestamp()

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)

    def _create_default_config(self) -> ISIConfiguration:
        """Create default ISI configuration."""
        return ISIConfiguration(
            experiment=self._create_default_experiment_config(),
            geometry=GeometryParameters(),
            visualization=VisualizationConfig(),
        )

    def _create_default_experiment_config(self) -> ExperimentConfiguration:
        """Create default experiment configuration."""
        return ExperimentConfiguration(
            created_at=datetime.now().isoformat(),
            experiment_name="Default Experiment",
            experiment_type="visual_field",
            monitor_config={
                "size": [30.0, 40.0],
                "distance": 10.0,
                "elevation": 20.0,
                "rotation": 0.0,
            },
            mouse_config={
                "eye_height": 5.0,
                "visual_field_vertical": 110.0,
                "visual_field_horizontal": 140.0,
            },
            stimulus_config={
                "type": "drifting-bar",
                "orientation": 0,
                "duration": 5,
                "contrast": 1.0,
            },
        )

    def _create_backup(self, config_path: str) -> None:
        """Create backup of existing configuration."""
        if not os.path.exists(config_path):
            return

        backup_path = f"{config_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Copy file
        with open(config_path, "r", encoding="utf-8") as src:
            with open(backup_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        # Clean old backups
        self._clean_old_backups(config_path)

    def _clean_old_backups(self, config_path: str) -> None:
        """Clean old backup files."""
        config_dir = os.path.dirname(config_path)
        config_name = os.path.basename(config_path)

        # Find backup files
        backup_files = []
        for filename in os.listdir(config_dir):
            if filename.startswith(f"{config_name}.backup."):
                backup_files.append(os.path.join(config_dir, filename))

        # Sort by modification time (newest first)
        backup_files.sort(key=os.path.getmtime, reverse=True)

        # Remove excess backups
        for backup_file in backup_files[self._current_config.backup_count :]:
            try:
                os.remove(backup_file)
            except OSError:
                pass  # Ignore errors when removing backup files

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result
