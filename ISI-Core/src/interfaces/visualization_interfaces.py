# ISI-Core/src/interfaces/visualization_interfaces.py

"""
Visualization-related interfaces following the Interface Segregation Principle.
Each interface has a single, well-defined responsibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from .geometry_interfaces import Vector3D, LandmarkSet


class RenderParameters(BaseModel):
    """Parameters for rendering operations with validation."""

    width: int = Field(800, gt=0, le=4096, description="Render width in pixels")
    height: int = Field(600, gt=0, le=4096, description="Render height in pixels")
    background_color: str = Field("#1a1a1a", description="Background color hex code")
    wireframe_mode: bool = Field(False, description="Enable wireframe rendering")
    show_axes: bool = Field(True, description="Show coordinate axes")
    show_grid: bool = Field(True, description="Show grid")

    @validator("background_color")
    def validate_hex_color(cls, v):
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Background color must be a valid hex color (#RRGGBB)")
        try:
            int(v[1:], 16)
        except ValueError:
            raise ValueError("Invalid hex color format")
        return v

    class Config:
        validate_assignment = True


class VisualizationConfig(BaseModel):
    """Configuration for visualization components."""

    monitor_size: tuple[float, float] = Field(
        (30.0, 40.0), description="Monitor dimensions in cm"
    )
    monitor_distance: float = Field(
        10.0, gt=0, description="Distance from eye to monitor in cm"
    )
    monitor_elevation: float = Field(
        20.0, ge=-90, le=90, description="Monitor elevation angle in degrees"
    )
    monitor_rotation: float = Field(
        0.0, ge=-180, le=180, description="Monitor rotation angle in degrees"
    )
    mouse_eye_height: float = Field(5.0, gt=0, description="Mouse eye height in cm")
    scale_factor: float = Field(8.0, gt=0, description="Model scaling factor")

    class Config:
        validate_assignment = True


class SceneNodeData(BaseModel):
    """Data for scene graph nodes."""

    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Display name")
    category: str = Field("General", description="Node category")
    visible: bool = Field(True, description="Node visibility")
    position: Vector3D = Field(
        default_factory=lambda: Vector3D(x=0, y=0, z=0), description="Node position"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        validate_assignment = True


class RenderResult(BaseModel):
    """Result of a rendering operation."""

    success: bool = Field(..., description="Whether rendering succeeded")
    render_time_ms: float = Field(
        ..., ge=0, description="Rendering time in milliseconds"
    )
    objects_rendered: int = Field(..., ge=0, description="Number of objects rendered")
    error_message: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        validate_assignment = True


class IVisualizationRenderer(ABC):
    """
    Handles rendering operations for the visualization system.
    Single Responsibility: Manage rendering pipeline and operations.
    """

    @abstractmethod
    def initialize(self, params: RenderParameters) -> bool:
        """Initialize the renderer with given parameters."""
        pass

    @abstractmethod
    def render_frame(self) -> RenderResult:
        """Render a single frame."""
        pass

    @abstractmethod
    def set_render_parameters(self, params: RenderParameters) -> None:
        """Update rendering parameters."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up rendering resources."""
        pass


class ISceneManager(ABC):
    """
    Manages the scene graph and object hierarchy.
    Single Responsibility: Handle scene organization and traversal.
    """

    @abstractmethod
    def create_node(
        self, node_data: SceneNodeData, parent_id: Optional[str] = None
    ) -> str:
        """Create a new scene node and return its ID."""
        pass

    @abstractmethod
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the scene."""
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[SceneNodeData]:
        """Get node data by ID."""
        pass

    @abstractmethod
    def get_children(self, node_id: str) -> List[SceneNodeData]:
        """Get all children of a node."""
        pass

    @abstractmethod
    def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update node properties."""
        pass


class INodeRenderer(ABC):
    """
    Renders individual scene nodes.
    Single Responsibility: Handle rendering of specific node types.
    """

    @abstractmethod
    def can_render(self, node_data: SceneNodeData) -> bool:
        """Check if this renderer can handle the given node type."""
        pass

    @abstractmethod
    def render_node(
        self, node_data: SceneNodeData, config: VisualizationConfig
    ) -> RenderResult:
        """Render a specific node."""
        pass

    @abstractmethod
    def update_node_properties(
        self, node_data: SceneNodeData, properties: Dict[str, Any]
    ) -> bool:
        """Update properties of a rendered node."""
        pass


class IUIComponent(ABC):
    """
    Handles user interface components.
    Single Responsibility: Manage UI elements and interactions.
    """

    @abstractmethod
    def initialize(self, container_id: str) -> bool:
        """Initialize the UI component in the specified container."""
        pass

    @abstractmethod
    def update_display(self, data: Dict[str, Any]) -> None:
        """Update the component's display with new data."""
        pass

    @abstractmethod
    def set_event_handlers(self, handlers: Dict[str, Any]) -> None:
        """Set event handlers for user interactions."""
        pass

    @abstractmethod
    def show(self) -> None:
        """Show the component."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Hide the component."""
        pass
