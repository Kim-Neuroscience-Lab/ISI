# ISI-Core/src/services/data_service.py

"""
Concrete implementations of data interfaces.
Provides file system and data management operations.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..interfaces.data_interfaces import (
    IDataRepository,
    IFileHandler,
    ExperimentConfiguration,
    FileMetadata,
    QueryParameters,
    DataResponse,
)


class ExperimentDataRepository(IDataRepository[ExperimentConfiguration]):
    """
    File system-based repository for ExperimentConfiguration.
    Single Responsibility: Handle experiment configuration persistence.
    """

    def __init__(self, base_directory: str):
        """Initialize repository with base directory."""
        if not base_directory or not base_directory.strip():
            raise ValueError("base_directory cannot be empty")

        self.base_directory = Path(base_directory)
        if not self.base_directory.exists():
            try:
                self.base_directory.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise RuntimeError(f"Failed to create base directory: {e}") from e

    def save(self, data: ExperimentConfiguration, identifier: str) -> DataResponse[str]:
        """Save experiment configuration with the given identifier."""
        if not identifier or not identifier.strip():
            raise ValueError("identifier cannot be empty")
        if not isinstance(data, ExperimentConfiguration):
            raise TypeError("data must be an ExperimentConfiguration instance")

        try:
            file_path = self.base_directory / f"{identifier}.json"

            # Use Pydantic's dict method
            json_data = data.dict()

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            return DataResponse(
                success=True,
                data=str(file_path),
                metadata={"saved_at": file_path.stat().st_mtime},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to save data for identifier '{identifier}': {e}",
            )

    def load(self, identifier: str) -> DataResponse[ExperimentConfiguration]:
        """Load experiment configuration by identifier."""
        if not identifier or not identifier.strip():
            raise ValueError("identifier cannot be empty")

        file_path = self.base_directory / f"{identifier}.json"

        if not file_path.exists():
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Data file not found for identifier: {identifier}",
            )

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data_dict = json.load(f)

            # Create ExperimentConfiguration from loaded data
            experiment_config = ExperimentConfiguration(**data_dict)

            return DataResponse(
                success=True,
                data=experiment_config,
                metadata={
                    "loaded_from": str(file_path),
                    "size": file_path.stat().st_size,
                },
            )

        except json.JSONDecodeError as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Invalid JSON in data file for identifier '{identifier}': {e}",
            )
        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to load data for identifier '{identifier}': {e}",
            )

    def delete(self, identifier: str) -> DataResponse[bool]:
        """Delete experiment configuration by identifier."""
        if not identifier or not identifier.strip():
            raise ValueError("identifier cannot be empty")

        file_path = self.base_directory / f"{identifier}.json"

        if not file_path.exists():
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Data file not found for identifier: {identifier}",
            )

        try:
            file_path.unlink()
            return DataResponse(
                success=True, data=True, metadata={"deleted_file": str(file_path)}
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to delete data for identifier '{identifier}': {e}",
            )

    def list_all(
        self, params: QueryParameters
    ) -> DataResponse[List[ExperimentConfiguration]]:
        """List all experiment configurations matching query parameters."""
        if not isinstance(params, QueryParameters):
            raise TypeError("params must be a QueryParameters instance")

        try:
            json_files = list(self.base_directory.glob("*.json"))

            # Apply limit and offset
            if params.offset > len(json_files):
                return DataResponse(
                    success=False,
                    data=None,
                    error_message=(
                        f"Offset {params.offset} exceeds available data count "
                        f"{len(json_files)}"
                    ),
                )

            start_idx = params.offset
            end_idx = start_idx + params.limit if params.limit else len(json_files)
            selected_files = json_files[start_idx:end_idx]

            # Load selected files
            loaded_data = []
            for file_path in selected_files:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data_dict = json.load(f)
                        experiment_config = ExperimentConfiguration(**data_dict)
                        loaded_data.append(experiment_config)
                except Exception as e:
                    return DataResponse(
                        success=False,
                        data=None,
                        error_message=f"Failed to load file {file_path}: {e}",
                    )

            return DataResponse(
                success=True,
                data=loaded_data,
                metadata={
                    "total_files": len(json_files),
                    "returned_count": len(loaded_data),
                    "offset": params.offset,
                    "limit": params.limit,
                },
            )

        except Exception as e:
            return DataResponse(
                success=False, data=None, error_message=f"Failed to list data: {e}"
            )

    def exists(self, identifier: str) -> bool:
        """Check if experiment configuration exists for the given identifier."""
        if not identifier or not identifier.strip():
            raise ValueError("identifier cannot be empty")

        file_path = self.base_directory / f"{identifier}.json"
        return file_path.exists() and file_path.is_file()


class SecureFileHandler(IFileHandler):
    """
    Secure file handler with validation.
    Single Responsibility: Handle file I/O operations with security checks.
    """

    def __init__(self, allowed_extensions: Optional[List[str]] = None):
        """Initialize with allowed file extensions."""
        self.allowed_extensions = allowed_extensions or [
            ".json",
            ".txt",
            ".csv",
            ".log",
        ]

    def read_file(self, file_path: str) -> DataResponse[bytes]:
        """Read file content as bytes."""
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        path = Path(file_path)

        if not path.exists():
            return DataResponse(
                success=False, data=None, error_message=f"File not found: {file_path}"
            )

        if not path.is_file():
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Path is not a file: {file_path}",
            )

        validation_error = self._validate_file_extension(path)
        if validation_error:
            return DataResponse(
                success=False, data=None, error_message=validation_error
            )

        try:
            with open(path, "rb") as f:
                content = f.read()

            return DataResponse(
                success=True,
                data=content,
                metadata={
                    "file_size": len(content),
                    "file_path": str(path),
                    "modified_time": path.stat().st_mtime,
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to read file '{file_path}': {e}",
            )

    def write_file(self, file_path: str, content: bytes) -> DataResponse[bool]:
        """Write bytes to file."""
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")
        if content is None:
            raise ValueError("content cannot be None")

        path = Path(file_path)
        validation_error = self._validate_file_extension(path)
        if validation_error:
            return DataResponse(
                success=False, data=False, error_message=validation_error
            )

        # Ensure parent directory exists
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to create parent directory: {e}",
            )

        try:
            with open(path, "wb") as f:
                f.write(content)

            return DataResponse(
                success=True,
                data=True,
                metadata={"bytes_written": len(content), "file_path": str(path)},
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to write file '{file_path}': {e}",
            )

    def read_text_file(
        self, file_path: str, encoding: str = "utf-8"
    ) -> DataResponse[str]:
        """Read file content as text."""
        if not encoding or not encoding.strip():
            raise ValueError("encoding cannot be empty")

        binary_response = self.read_file(file_path)

        if not binary_response.success or binary_response.data is None:
            return DataResponse(
                success=False,
                data=None,
                error_message=binary_response.error_message
                or "Failed to read binary data",
            )

        try:
            text_content = binary_response.data.decode(encoding)

            return DataResponse(
                success=True,
                data=text_content,
                metadata={
                    **binary_response.metadata,
                    "encoding": encoding,
                    "character_count": len(text_content),
                },
            )

        except UnicodeDecodeError as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to decode file with encoding '{encoding}': {e}",
            )

    def write_text_file(
        self, file_path: str, content: str, encoding: str = "utf-8"
    ) -> DataResponse[bool]:
        """Write text to file."""
        if content is None:
            raise ValueError("content cannot be None")
        if not encoding or not encoding.strip():
            raise ValueError("encoding cannot be empty")

        try:
            byte_content = content.encode(encoding)
            return self.write_file(file_path, byte_content)

        except UnicodeEncodeError as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to encode content with encoding '{encoding}': {e}",
            )

    def get_file_metadata(self, file_path: str) -> DataResponse[FileMetadata]:
        """Get file metadata."""
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        path = Path(file_path)

        if not path.exists():
            return DataResponse(
                success=False, data=None, error_message=f"File not found: {file_path}"
            )

        if not path.is_file():
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Path is not a file: {file_path}",
            )

        try:
            stat = path.stat()

            # Calculate checksum
            checksum = self._calculate_checksum(path)

            metadata = FileMetadata(
                filename=path.name,
                file_path=str(path),
                file_size=stat.st_size,
                file_type=path.suffix,
                checksum=checksum,
            )

            return DataResponse(
                success=True,
                data=metadata,
                metadata={
                    "created_time": stat.st_ctime,
                    "modified_time": stat.st_mtime,
                    "accessed_time": stat.st_atime,
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=None,
                error_message=f"Failed to get metadata for file '{file_path}': {e}",
            )

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        path = Path(file_path)
        return path.exists() and path.is_file()

    def create_directory(self, dir_path: str) -> DataResponse[bool]:
        """Create directory if it doesn't exist."""
        if not dir_path or not dir_path.strip():
            raise ValueError("dir_path cannot be empty")

        path = Path(dir_path)

        try:
            path.mkdir(parents=True, exist_ok=True)

            return DataResponse(
                success=True,
                data=True,
                metadata={
                    "directory_path": str(path),
                    "already_existed": path.exists(),
                },
            )

        except Exception as e:
            return DataResponse(
                success=False,
                data=False,
                error_message=f"Failed to create directory '{dir_path}': {e}",
            )

    def _validate_file_extension(self, path: Path) -> Optional[str]:
        """Validate file extension against allowed list. Returns error message if invalid."""
        if self.allowed_extensions and path.suffix not in self.allowed_extensions:
            return f"File extension '{path.suffix}' not allowed. Allowed: {self.allowed_extensions}"
        return None

    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA-256 checksum of file."""
        sha256_hash = hashlib.sha256()

        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            return sha256_hash.hexdigest()

        except Exception as e:
            raise RuntimeError(f"Failed to calculate checksum: {e}") from e
