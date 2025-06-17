# ISI-Core/src/interfaces/__init__.py

"""
Core interfaces for the ISI system.
All interfaces follow the Interface Segregation Principle - clients should not depend on interfaces they don't use.
"""

from .geometry_interfaces import (
    IGeometryProvider,
    ITransformationCalculator,
    ILandmarkDetector,
    IAlignmentCalculator,
)

from .visualization_interfaces import (
    IVisualizationRenderer,
    ISceneManager,
    INodeRenderer,
    IUIComponent,
)

from .data_interfaces import IDataRepository, IConfigurationManager, IFileHandler

from .event_interfaces import IEventPublisher, IEventSubscriber, ICommand

__all__ = [
    # Geometry interfaces
    "IGeometryProvider",
    "ITransformationCalculator",
    "ILandmarkDetector",
    "IAlignmentCalculator",
    # Visualization interfaces
    "IVisualizationRenderer",
    "ISceneManager",
    "INodeRenderer",
    "IUIComponent",
    # Data interfaces
    "IDataRepository",
    "IConfigurationManager",
    "IFileHandler",
    # Event interfaces
    "IEventPublisher",
    "IEventSubscriber",
    "ICommand",
]
