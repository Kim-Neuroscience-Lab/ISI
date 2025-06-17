# ISI-Core/src/interfaces/data_interfaces.py

"""
Data-related interfaces following the Interface Segregation Principle.
Each interface has a single, well-defined responsibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Generic, TypeVar
from pydantic import BaseModel, Field, validator
from pathlib import Path
import json

T = TypeVar("T")


class ConfigurationData(BaseModel):
    """Base configuration data with validation."""

    version: str = Field("1.0.0", description="Configuration version")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        validate_assignment = True


class ExperimentConfiguration(ConfigurationData):
    """Configuration for experiments with validation."""

    experiment_name: str = Field(..., min_length=1, description="Experiment name")
    experiment_type: str = Field(..., description="Type of experiment")
    monitor_config: Dict[str, Any] = Field(..., description="Monitor configuration")
    mouse_config: Dict[str, Any] = Field(..., description="Mouse configuration")
    stimulus_config: Dict[str, Any] = Field(..., description="Stimulus configuration")

    @validator("experiment_type")
    def validate_experiment_type(cls, v):
        valid_types = ["visual_field", "stimulus_response", "alignment_test"]
        if v not in valid_types:
            raise ValueError(f"Experiment type must be one of: {valid_types}")
        return v

    class Config:
        validate_assignment = True


class FileMetadata(BaseModel):
    """Metadata for files with validation."""

    filename: str = Field(..., description="File name")
    file_path: str = Field(..., description="Full file path")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    file_type: str = Field(..., description="File type/extension")
    checksum: Optional[str] = Field(None, description="File checksum")

    @validator("file_path")
    def validate_path(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("File path cannot be empty")
        return v

    class Config:
        validate_assignment = True


class QueryParameters(BaseModel):
    """Parameters for data queries with validation."""

    filters: Dict[str, Any] = Field(default_factory=dict, description="Query filters")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", description="Sort order")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Result limit")
    offset: int = Field(0, ge=0, description="Result offset")

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be asc or desc")
        return v

    class Config:
        validate_assignment = True


class DataResponse(BaseModel, Generic[T]):
    """Generic response wrapper for data operations."""

    success: bool = Field(..., description="Operation success status")
    data: Optional[T] = Field(None, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )

    class Config:
        validate_assignment = True


class IDataRepository(ABC, Generic[T]):
    """
    Generic repository interface for data persistence.
    Single Responsibility: Handle data storage and retrieval operations.
    """

    @abstractmethod
    def save(self, data: T, identifier: str) -> DataResponse[str]:
        """Save data with the given identifier."""
        pass

    @abstractmethod
    def load(self, identifier: str) -> DataResponse[T]:
        """Load data by identifier."""
        pass

    @abstractmethod
    def delete(self, identifier: str) -> DataResponse[bool]:
        """Delete data by identifier."""
        pass

    @abstractmethod
    def list_all(self, params: QueryParameters) -> DataResponse[List[T]]:
        """List all data matching query parameters."""
        pass

    @abstractmethod
    def exists(self, identifier: str) -> bool:
        """Check if data exists for the given identifier."""
        pass


class IConfigurationManager(ABC):
    """
    Manages application configuration.
    Single Responsibility: Handle configuration loading, saving, and validation.
    """

    @abstractmethod
    def load_configuration(
        self, config_path: str
    ) -> DataResponse[ExperimentConfiguration]:
        """Load configuration from file."""
        pass

    @abstractmethod
    def save_configuration(
        self, config: ExperimentConfiguration, config_path: str
    ) -> DataResponse[bool]:
        """Save configuration to file."""
        pass

    @abstractmethod
    def validate_configuration(
        self, config: ExperimentConfiguration
    ) -> DataResponse[Dict[str, Any]]:
        """Validate configuration and return validation results."""
        pass

    @abstractmethod
    def get_default_configuration(self) -> ExperimentConfiguration:
        """Get default configuration."""
        pass

    @abstractmethod
    def merge_configurations(
        self, base: ExperimentConfiguration, override: Dict[str, Any]
    ) -> ExperimentConfiguration:
        """Merge configuration with overrides."""
        pass


class IFileHandler(ABC):
    """
    Handles file operations.
    Single Responsibility: Manage file I/O operations.
    """

    @abstractmethod
    def read_file(self, file_path: str) -> DataResponse[bytes]:
        """Read file content as bytes."""
        pass

    @abstractmethod
    def write_file(self, file_path: str, content: bytes) -> DataResponse[bool]:
        """Write bytes to file."""
        pass

    @abstractmethod
    def read_text_file(
        self, file_path: str, encoding: str = "utf-8"
    ) -> DataResponse[str]:
        """Read file content as text."""
        pass

    @abstractmethod
    def write_text_file(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> DataResponse[bool]:
        """Write text to file."""
        pass

    @abstractmethod
    def get_file_metadata(self, file_path: str) -> DataResponse[FileMetadata]:
        """Get file metadata."""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    def create_directory(self, dir_path: str) -> DataResponse[bool]:
        """Create directory if it doesn't exist."""
        pass
