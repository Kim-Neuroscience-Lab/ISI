# ISI-Core/src/interfaces/geometry_interfaces.py

"""
Geometry-related interfaces following the Interface Segregation Principle.
Each interface has a single, well-defined responsibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
from pydantic import BaseModel, Field, validator


class Vector3D(BaseModel):
    """3D vector value object with validation."""

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")

    @validator("x", "y", "z")
    def validate_finite(cls, v):
        if not isinstance(v, (int, float)) or not (-1e10 <= v <= 1e10):
            raise ValueError("Coordinate must be a finite number")
        return float(v)

    class Config:
        frozen = True  # Immutable value object
        json_encoders = {float: lambda v: round(v, 6)}  # Limit precision for JSON


class TransformationMatrix(BaseModel):
    """Transformation matrix value object with validation."""

    matrix: List[List[float]] = Field(..., description="4x4 transformation matrix")

    @validator("matrix")
    def validate_matrix_dimensions(cls, v):
        if len(v) != 4 or any(len(row) != 4 for row in v):
            raise ValueError("Matrix must be 4x4")
        return v

    @validator("matrix")
    def validate_matrix_values(cls, v):
        for row in v:
            for val in row:
                if not isinstance(val, (int, float)) or not (-1e10 <= val <= 1e10):
                    raise ValueError("Matrix values must be finite numbers")
        return [[float(val) for val in row] for row in v]

    class Config:
        frozen = True
        json_encoders = {float: lambda v: round(v, 6)}


class LandmarkSet(BaseModel):
    """Set of detected landmarks with validation."""

    nose: Vector3D = Field(..., description="Nose position")
    tail: Vector3D = Field(..., description="Tail position")
    left_ear: Vector3D = Field(..., description="Left ear position")
    right_ear: Vector3D = Field(..., description="Right ear position")
    face_center: Optional[Vector3D] = Field(None, description="Face center position")

    @validator("face_center", always=True)
    def validate_face_center(cls, v, values):
        # Could add validation logic here if needed
        return v

    class Config:
        frozen = True
        validate_assignment = True


class GeometryParameters(BaseModel):
    """Parameters for geometry calculations with validation."""

    scale_factor: float = Field(8.0, gt=0, description="Scaling factor in cm")
    alignment_tolerance: float = Field(
        0.5, gt=0, le=5.0, description="Alignment tolerance in degrees"
    )
    ear_alignment_axis: str = Field("x", description="Axis for ear alignment")
    nose_tail_axis: str = Field("z", description="Axis for nose-tail alignment")

    @validator("ear_alignment_axis", "nose_tail_axis")
    def validate_axis(cls, v):
        if v not in ["x", "y", "z"]:
            raise ValueError("Axis must be x, y, or z")
        return v

    class Config:
        validate_assignment = True


class AlignmentResult(BaseModel):
    """Result of alignment calculation with validation."""

    transformation_matrix: TransformationMatrix = Field(
        ..., description="Calculated transformation matrix"
    )
    alignment_errors: Dict[str, float] = Field(
        ..., description="Alignment error measurements"
    )
    is_valid: bool = Field(..., description="Whether alignment meets tolerance")

    @validator("alignment_errors")
    def validate_errors(cls, v):
        required_keys = {"nose_tail_alignment", "ear_alignment", "overall_error"}
        if not all(key in v for key in required_keys):
            raise ValueError(f"alignment_errors must contain keys: {required_keys}")
        return v

    class Config:
        validate_assignment = True


class IGeometryProvider(ABC):
    """
    Provides basic geometric calculations and utilities.
    Single Responsibility: Handle fundamental geometric operations.
    """

    @abstractmethod
    def calculate_distance(self, point1: Vector3D, point2: Vector3D) -> float:
        """Calculate Euclidean distance between two points."""
        pass

    @abstractmethod
    def calculate_midpoint(self, point1: Vector3D, point2: Vector3D) -> Vector3D:
        """Calculate midpoint between two points."""
        pass

    @abstractmethod
    def normalize_vector(self, vector: Vector3D) -> Vector3D:
        """Normalize a vector to unit length."""
        pass


class ITransformationCalculator(ABC):
    """
    Calculates transformation matrices for geometric operations.
    Single Responsibility: Handle coordinate transformations.
    """

    @abstractmethod
    def calculate_rotation_matrix(
        self, from_vector: Vector3D, to_vector: Vector3D
    ) -> TransformationMatrix:
        """Calculate rotation matrix to align one vector with another."""
        pass

    @abstractmethod
    def calculate_alignment_matrix(
        self, landmarks: LandmarkSet, params: GeometryParameters
    ) -> TransformationMatrix:
        """Calculate complete alignment matrix from landmarks."""
        pass

    @abstractmethod
    def apply_transformation(
        self, matrix: TransformationMatrix, points: List[Vector3D]
    ) -> List[Vector3D]:
        """Apply transformation matrix to a list of points."""
        pass


class ILandmarkDetector(ABC):
    """
    Detects landmarks on 3D models.
    Single Responsibility: Extract feature points from models.
    """

    @abstractmethod
    def detect_landmarks(self, model_data: Any) -> LandmarkSet:
        """Detect all landmarks from model data."""
        pass

    @abstractmethod
    def detect_ears(self, model_data: Any) -> Tuple[Vector3D, Vector3D]:
        """Detect left and right ear positions."""
        pass

    @abstractmethod
    def detect_nose_tail(self, model_data: Any) -> Tuple[Vector3D, Vector3D]:
        """Detect nose and tail positions."""
        pass


class IAlignmentCalculator(ABC):
    """
    Calculates alignment operations for models.
    Single Responsibility: Handle model alignment calculations.
    """

    @abstractmethod
    def calculate_nose_tail_alignment(
        self, nose: Vector3D, tail: Vector3D, params: GeometryParameters
    ) -> TransformationMatrix:
        """Calculate alignment to position nose-tail along specified axis."""
        pass

    @abstractmethod
    def calculate_ear_alignment(
        self, left_ear: Vector3D, right_ear: Vector3D, params: GeometryParameters
    ) -> TransformationMatrix:
        """Calculate alignment to position ears along specified axis."""
        pass

    @abstractmethod
    def verify_alignment(
        self,
        landmarks: LandmarkSet,
        matrix: TransformationMatrix,
        params: GeometryParameters,
    ) -> AlignmentResult:
        """Verify that alignment meets specified tolerances."""
        pass
