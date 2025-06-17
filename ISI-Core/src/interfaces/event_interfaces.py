# ISI-Core/src/interfaces/event_interfaces.py

"""
Event-related interfaces following the Interface Segregation Principle.
Each interface has a single, well-defined responsibility.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Enumeration of event types."""

    GEOMETRY_UPDATED = "geometry_updated"
    ALIGNMENT_COMPLETED = "alignment_completed"
    VISUALIZATION_CHANGED = "visualization_changed"
    CONFIG_LOADED = "config_loaded"
    ERROR_OCCURRED = "error_occurred"
    USER_INTERACTION = "user_interaction"


class EventPriority(str, Enum):
    """Event priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventData(BaseModel):
    """Base event data with validation."""

    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Event timestamp"
    )
    priority: EventPriority = Field(EventPriority.NORMAL, description="Event priority")
    source: str = Field(..., description="Event source identifier")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        validate_assignment = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class CommandData(BaseModel):
    """Base command data with validation."""

    command_id: str = Field(..., description="Unique command identifier")
    command_type: str = Field(..., description="Type of command")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Command timestamp"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Command parameters"
    )
    can_undo: bool = Field(False, description="Whether command can be undone")

    class Config:
        validate_assignment = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class CommandResult(BaseModel):
    """Result of command execution."""

    success: bool = Field(..., description="Command execution success")
    result_data: Optional[Dict[str, Any]] = Field(
        None, description="Command result data"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: float = Field(
        ..., ge=0, description="Execution time in milliseconds"
    )

    class Config:
        validate_assignment = True


class SubscriptionConfig(BaseModel):
    """Configuration for event subscriptions."""

    event_types: List[EventType] = Field(
        ..., description="List of event types to subscribe to"
    )
    priority_filter: Optional[EventPriority] = Field(
        None, description="Minimum priority filter"
    )
    source_filter: Optional[str] = Field(None, description="Source filter pattern")
    active: bool = Field(True, description="Whether subscription is active")

    class Config:
        validate_assignment = True


class IEventPublisher(ABC):
    """
    Publishes events to subscribers.
    Single Responsibility: Handle event publishing and distribution.
    """

    @abstractmethod
    def publish(self, event: EventData) -> bool:
        """Publish an event to all relevant subscribers."""
        pass

    @abstractmethod
    def publish_async(self, event: EventData) -> None:
        """Publish an event asynchronously."""
        pass

    @abstractmethod
    def subscribe(
        self,
        subscriber_id: str,
        config: SubscriptionConfig,
        callback: Callable[[EventData], None],
    ) -> bool:
        """Subscribe to events with given configuration."""
        pass

    @abstractmethod
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from events."""
        pass

    @abstractmethod
    def get_subscriber_count(self) -> int:
        """Get the number of active subscribers."""
        pass


class IEventSubscriber(ABC):
    """
    Subscribes to and handles events.
    Single Responsibility: Handle event reception and processing.
    """

    @abstractmethod
    def handle_event(self, event: EventData) -> None:
        """Handle a received event."""
        pass

    @abstractmethod
    def get_subscription_config(self) -> SubscriptionConfig:
        """Get the subscription configuration."""
        pass

    @abstractmethod
    def can_handle_event(self, event: EventData) -> bool:
        """Check if this subscriber can handle the given event."""
        pass


class ICommand(ABC):
    """
    Represents a command that can be executed.
    Single Responsibility: Encapsulate a single operation.
    """

    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> CommandResult:
        """Undo the command (if supported)."""
        pass

    @abstractmethod
    def can_undo(self) -> bool:
        """Check if the command can be undone."""
        pass

    @abstractmethod
    def get_command_data(self) -> CommandData:
        """Get the command data."""
        pass
