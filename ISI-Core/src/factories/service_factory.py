"""
Service factory for ISI experimental workflow.
Implements dependency injection and service registration patterns.
"""

from typing import Dict, Type, Any, Optional
from abc import ABC, abstractmethod

from ..interfaces.data_interfaces import IDataStore, IConfigurationService
from ..interfaces.experiment_interfaces import (
    ISetupManager,
    IStimulusGenerator,
    IAcquisitionController,
    IFrameSynchronizer,
    IDataAnalyzer,
    IExperimentWorkflow,
)


class ServiceRegistry:
    """
    Service registry for managing service instances.
    Single Responsibility: Manage service registration and creation.
    """

    def __init__(self):
        """Initialize service registry."""
        self._services: Dict[str, Dict[str, Type]] = {}
        self._instances: Dict[str, Dict[str, Any]] = {}

    def register_service(
        self, service_name: str, variant: str, service_class: Type
    ) -> None:
        """Register a service implementation."""
        if not service_name or not service_name.strip():
            raise ValueError("service_name cannot be empty")
        if not variant or not variant.strip():
            raise ValueError("variant cannot be empty")
        if not service_class:
            raise ValueError("service_class cannot be None")

        if service_name not in self._services:
            self._services[service_name] = {}

        self._services[service_name][variant] = service_class

    def create_service_instance(self, service_name: str, variant: str) -> Any:
        """Create or retrieve service instance."""
        if not service_name or not service_name.strip():
            raise ValueError("service_name cannot be empty")
        if not variant or not variant.strip():
            raise ValueError("variant cannot be empty")

        # Check if instance already exists (singleton pattern)
        if service_name in self._instances and variant in self._instances[service_name]:
            return self._instances[service_name][variant]

        # Get service class
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not registered")
        if variant not in self._services[service_name]:
            raise ValueError(
                f"Variant '{variant}' for service '{service_name}' not registered"
            )

        service_class = self._services[service_name][variant]

        # Create instance
        instance = service_class()

        # Store instance for singleton pattern
        if service_name not in self._instances:
            self._instances[service_name] = {}
        self._instances[service_name][variant] = instance

        return instance

    def get_registered_services(self) -> Dict[str, list]:
        """Get list of all registered services."""
        return {
            service_name: list(variants.keys())
            for service_name, variants in self._services.items()
        }

    def clear_instances(self) -> None:
        """Clear all cached instances."""
        self._instances.clear()


class ServiceFactory:
    """
    Main service factory for ISI experimental workflow.
    Single Responsibility: Provide centralized service creation and dependency injection.
    """

    def __init__(self):
        """Initialize service factory."""
        self._registry = ServiceRegistry()
        self._initialize_default_services()

    def _initialize_default_services(self) -> None:
        """Initialize default service registrations."""
        # Import services here to avoid circular imports
        from ..services.data_service import JSONDataStore, ConfigurationService
        from ..services.experiment_service import (
            SetupManager,
            StimulusGenerator,
            AcquisitionController,
            FrameSynchronizer,
            DataAnalyzer,
            ExperimentWorkflow,
        )

        # Register data services
        self._registry.register_service("data_store", "json", JSONDataStore)
        self._registry.register_service(
            "data_store", "memory", JSONDataStore
        )  # Fallback
        self._registry.register_service(
            "configuration", "default", ConfigurationService
        )

        # Register experiment services
        self._registry.register_service("setup_manager", "default", SetupManager)
        self._registry.register_service(
            "stimulus_generator", "default", StimulusGenerator
        )
        self._registry.register_service(
            "acquisition_controller", "default", AcquisitionController
        )
        self._registry.register_service(
            "frame_synchronizer", "default", FrameSynchronizer
        )
        self._registry.register_service("data_analyzer", "default", DataAnalyzer)
        self._registry.register_service(
            "experiment_workflow", "default", ExperimentWorkflow
        )

    def register_service(
        self, service_name: str, variant: str, service_class: Type
    ) -> None:
        """Register a service implementation."""
        self._registry.register_service(service_name, variant, service_class)

    def create_service_instance(
        self, service_name: str, variant: str = "default"
    ) -> Any:
        """Create or retrieve service instance."""
        return self._registry.create_service_instance(service_name, variant)

    def get_data_store(self, variant: str = "json") -> IDataStore:
        """Get data store service instance."""
        return self._registry.create_service_instance("data_store", variant)

    def get_configuration_service(
        self, variant: str = "default"
    ) -> IConfigurationService:
        """Get configuration service instance."""
        return self._registry.create_service_instance("configuration", variant)

    def get_setup_manager(self, variant: str = "default") -> ISetupManager:
        """Get setup manager service instance."""
        return self._registry.create_service_instance("setup_manager", variant)

    def get_stimulus_generator(self, variant: str = "default") -> IStimulusGenerator:
        """Get stimulus generator service instance."""
        return self._registry.create_service_instance("stimulus_generator", variant)

    def get_acquisition_controller(
        self, variant: str = "default"
    ) -> IAcquisitionController:
        """Get acquisition controller service instance."""
        return self._registry.create_service_instance("acquisition_controller", variant)

    def get_frame_synchronizer(self, variant: str = "default") -> IFrameSynchronizer:
        """Get frame synchronizer service instance."""
        return self._registry.create_service_instance("frame_synchronizer", variant)

    def get_data_analyzer(self, variant: str = "default") -> IDataAnalyzer:
        """Get data analyzer service instance."""
        return self._registry.create_service_instance("data_analyzer", variant)

    def get_experiment_workflow(self, variant: str = "default") -> IExperimentWorkflow:
        """Get experiment workflow service instance."""
        return self._registry.create_service_instance("experiment_workflow", variant)

    def create_complete_workflow(self) -> Dict[str, Any]:
        """Create a complete workflow with all services."""
        return {
            "setup_manager": self.get_setup_manager(),
            "stimulus_generator": self.get_stimulus_generator(),
            "acquisition_controller": self.get_acquisition_controller(),
            "frame_synchronizer": self.get_frame_synchronizer(),
            "data_analyzer": self.get_data_analyzer(),
            "experiment_workflow": self.get_experiment_workflow(),
            "data_store": self.get_data_store(),
            "configuration": self.get_configuration_service(),
        }

    def get_registered_services(self) -> Dict[str, list]:
        """Get list of all registered services."""
        return self._registry.get_registered_services()

    def clear_instances(self) -> None:
        """Clear all cached service instances."""
        self._registry.clear_instances()


# Global service factory instance
service_factory = ServiceFactory()
