"""
Concrete implementations of event interfaces.
Provides event publishing and command execution functionality.
"""

import asyncio
from typing import Dict, Callable, Optional, Any
from datetime import datetime
import uuid

from ..interfaces.event_interfaces import (
    IEventPublisher,
    IEventSubscriber,
    ICommand,
    EventData,
    CommandData,
    CommandResult,
    SubscriptionConfig,
    EventType,
    EventPriority,
)


class InMemoryEventPublisher(IEventPublisher):
    """
    In-memory event publisher implementation.
    Single Responsibility: Handle event distribution to subscribers.
    """

    def __init__(self):
        """Initialize event publisher."""
        self._subscribers: Dict[
            str, tuple[SubscriptionConfig, Callable[[EventData], None]]
        ] = {}

    def publish(self, event: EventData) -> bool:
        """Publish an event to all relevant subscribers."""
        if not isinstance(event, EventData):
            raise TypeError("event must be an EventData instance")

        try:
            for subscriber_id, (config, callback) in self._subscribers.items():
                if self._should_deliver_event(event, config):
                    try:
                        callback(event)
                    except Exception as e:
                        # Log error but continue delivering to other subscribers
                        print(
                            f"Error delivering event to subscriber {subscriber_id}: {e}"
                        )

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to publish event: {e}") from e

    def publish_async(self, event: EventData) -> None:
        """Publish an event asynchronously."""
        if not isinstance(event, EventData):
            raise TypeError("event must be an EventData instance")

        # Create a simple async task
        async def _async_publish():
            try:
                self.publish(event)
            except Exception as e:
                print(f"Error in async event publishing: {e}")

        # Run in background if event loop exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_async_publish())
            else:
                loop.run_until_complete(_async_publish())
        except RuntimeError:
            # No event loop, run synchronously
            self.publish(event)

    def subscribe(
        self,
        subscriber_id: str,
        config: SubscriptionConfig,
        callback: Callable[[EventData], None],
    ) -> bool:
        """Subscribe to events with given configuration."""
        if not subscriber_id or not subscriber_id.strip():
            raise ValueError("subscriber_id cannot be empty")
        if not isinstance(config, SubscriptionConfig):
            raise TypeError("config must be a SubscriptionConfig instance")
        if not callable(callback):
            raise TypeError("callback must be callable")

        if subscriber_id in self._subscribers:
            raise ValueError(f"Subscriber {subscriber_id} is already registered")

        self._subscribers[subscriber_id] = (config, callback)
        return True

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from events."""
        if not subscriber_id or not subscriber_id.strip():
            raise ValueError("subscriber_id cannot be empty")

        if subscriber_id not in self._subscribers:
            return False

        del self._subscribers[subscriber_id]
        return True

    def get_subscriber_count(self) -> int:
        """Get the number of active subscribers."""
        return len(self._subscribers)

    def _should_deliver_event(
        self, event: EventData, config: SubscriptionConfig
    ) -> bool:
        """Check if event should be delivered based on subscription config."""
        # Check if subscription is active
        if not config.active:
            return False

        # Check event type filter
        if event.event_type not in config.event_types:
            return False

        # Check priority filter
        if config.priority_filter:
            priority_levels = {
                EventPriority.LOW: 0,
                EventPriority.NORMAL: 1,
                EventPriority.HIGH: 2,
                EventPriority.CRITICAL: 3,
            }
            if priority_levels.get(event.priority, 0) < priority_levels.get(
                config.priority_filter, 0
            ):
                return False

        # Check source filter (basic pattern matching)
        if config.source_filter:
            if config.source_filter not in event.source:
                return False

        return True


class BaseEventSubscriber(IEventSubscriber):
    """
    Base implementation of event subscriber.
    Single Responsibility: Handle event reception and basic processing.
    """

    def __init__(self, subscriber_id: str, config: SubscriptionConfig):
        """Initialize event subscriber."""
        if not subscriber_id or not subscriber_id.strip():
            raise ValueError("subscriber_id cannot be empty")
        if not isinstance(config, SubscriptionConfig):
            raise TypeError("config must be a SubscriptionConfig instance")

        self.subscriber_id = subscriber_id
        self._config = config

    def handle_event(self, event: EventData) -> None:
        """Handle a received event."""
        if not isinstance(event, EventData):
            raise TypeError("event must be an EventData instance")

        if not self.can_handle_event(event):
            return

        try:
            self._process_event(event)
        except Exception as e:
            raise RuntimeError(f"Failed to handle event {event.event_id}: {e}") from e

    def get_subscription_config(self) -> SubscriptionConfig:
        """Get the subscription configuration."""
        return self._config

    def can_handle_event(self, event: EventData) -> bool:
        """Check if this subscriber can handle the given event."""
        if not isinstance(event, EventData):
            return False

        # Basic filtering based on configuration
        return event.event_type in self._config.event_types and self._config.active

    def _process_event(self, event: EventData) -> None:
        """Process the event (to be overridden by subclasses)."""
        # Default implementation just logs the event
        print(f"Subscriber {self.subscriber_id} received event: {event.event_type}")


class BaseCommand(ICommand):
    """
    Base implementation of command pattern.
    Single Responsibility: Encapsulate a single operation with undo support.
    """

    def __init__(self, command_data: CommandData):
        """Initialize command."""
        if not isinstance(command_data, CommandData):
            raise TypeError("command_data must be a CommandData instance")

        self._command_data = command_data
        self._executed = False
        self._execution_result: Optional[CommandResult] = None

    def execute(self) -> CommandResult:
        """Execute the command."""
        if self._executed:
            raise RuntimeError("Command has already been executed")

        start_time = datetime.now()

        try:
            result_data = self._execute_implementation()

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            self._execution_result = CommandResult(
                success=True,
                result_data=result_data,
                execution_time_ms=execution_time,
                error_message=None,
            )

            self._executed = True
            return self._execution_result

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            self._execution_result = CommandResult(
                success=False,
                result_data=None,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

            raise RuntimeError(f"Command execution failed: {e}") from e

    def undo(self) -> CommandResult:
        """Undo the command (if supported)."""
        if not self._executed:
            raise RuntimeError("Cannot undo command that hasn't been executed")

        if not self.can_undo():
            raise RuntimeError("Command does not support undo")

        start_time = datetime.now()

        try:
            self._undo_implementation()

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            self._executed = False
            return CommandResult(
                success=True,
                result_data={"operation": "undo"},
                execution_time_ms=execution_time,
                error_message=None,
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000

            return CommandResult(
                success=False,
                result_data=None,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

    def can_undo(self) -> bool:
        """Check if the command can be undone."""
        return self._command_data.can_undo

    def get_command_data(self) -> CommandData:
        """Get the command data."""
        return self._command_data

    def _execute_implementation(self) -> Optional[Dict[str, Any]]:
        """Execute the command implementation (to be overridden by subclasses)."""
        raise NotImplementedError("Subclasses must implement _execute_implementation")

    def _undo_implementation(self) -> None:
        """Undo the command implementation (to be overridden by subclasses)."""
        raise NotImplementedError("Subclasses must implement _undo_implementation")


class GeometryUpdateCommand(BaseCommand):
    """
    Command for updating geometry parameters.
    Single Responsibility: Handle geometry parameter updates.
    """

    def __init__(self, new_parameters: Dict[str, Any]):
        """Initialize geometry update command."""
        if not isinstance(new_parameters, dict):
            raise TypeError("new_parameters must be a dictionary")

        command_data = CommandData(
            command_id=str(uuid.uuid4()),
            command_type="geometry_update",
            parameters=new_parameters,
            can_undo=True,
        )

        super().__init__(command_data)
        self._previous_state: Optional[Dict[str, Any]] = None

    def _execute_implementation(self) -> Optional[Dict[str, Any]]:
        """Execute geometry parameter update."""
        # Store current state for undo capability
        self._previous_state = self._capture_current_state()

        # Apply new parameters through proper service interface
        self._apply_parameters(self._command_data.parameters)

        return {
            "updated_parameters": self._command_data.parameters,
            "command_id": self._command_data.command_id,
        }

    def _undo_implementation(self) -> None:
        """Undo geometry parameter update."""
        if self._previous_state is None:
            raise RuntimeError("No previous state available for undo")

        # Restore previous state through proper service interface
        self._apply_parameters(self._previous_state)

    def _capture_current_state(self) -> Dict[str, Any]:
        """Capture current geometry state for undo capability."""
        # In production, this would interface with the geometry service
        # to capture the actual current state
        return {"geometry_state": "captured"}

    def _apply_parameters(self, parameters: Dict[str, Any]) -> None:
        """Apply parameters through proper service interface."""
        # In production, this would interface with the geometry service
        # to apply the parameters
        print(f"Applying geometry parameters: {parameters}")


class EventLogger(BaseEventSubscriber):
    """
    Event subscriber that logs all events.
    Single Responsibility: Log events for debugging and auditing.
    """

    def __init__(self, log_file: Optional[str] = None):
        """Initialize event logger."""
        config = SubscriptionConfig(
            event_types=[
                EventType.GEOMETRY_UPDATED,
                EventType.ALIGNMENT_COMPLETED,
                EventType.VISUALIZATION_CHANGED,
                EventType.CONFIG_LOADED,
                EventType.ERROR_OCCURRED,
                EventType.USER_INTERACTION,
            ],
            active=True,
            priority_filter=None,
            source_filter=None,
        )

        super().__init__("event_logger", config)
        self.log_file = log_file

    def _process_event(self, event: EventData) -> None:
        """Process and log the event."""
        log_message = (
            f"[{event.timestamp.isoformat()}] "
            f"{event.event_type.value} from {event.source} "
            f"(Priority: {event.priority.value}) - "
            f"ID: {event.event_id}"
        )

        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"Failed to write to log file: {e}")
                print(log_message)  # Fallback to console
        else:
            print(log_message)
