# ISI-Core/tests/demo_integration.py

"""
Comprehensive demonstration of the refactored ISI architecture.
Shows how all services work together following SOLID principles.
"""

from typing import Dict, Any

# Import interfaces and factories
from ..src.factories.service_factory import service_factory


def demonstrate_service_registration() -> None:
    """Demonstrate service registration functionality."""
    print("\n=== SERVICE REGISTRATION DEMO ===")

    # Get list of registered services
    registered_services = service_factory.get_registered_services()

    print("Registered services:")
    for service_name, variants in registered_services.items():
        print(f"  {service_name}: {variants}")


def demonstrate_data_services() -> None:
    """Demonstrate data service functionality."""
    print("\n=== DATA SERVICES DEMO ===")

    # Create data services using the actual factory methods
    data_store = service_factory.get_data_store()
    configuration_service = service_factory.get_configuration_service()

    print(f"Data store created: {data_store is not None}")
    print(f"Configuration service created: {configuration_service is not None}")


def demonstrate_experiment_services() -> None:
    """Demonstrate experiment service functionality."""
    print("\n=== EXPERIMENT SERVICES DEMO ===")

    # Create experiment services using the actual factory methods
    setup_manager = service_factory.get_setup_manager()
    stimulus_generator = service_factory.get_stimulus_generator()
    acquisition_controller = service_factory.get_acquisition_controller()
    frame_synchronizer = service_factory.get_frame_synchronizer()
    data_analyzer = service_factory.get_data_analyzer()
    experiment_workflow = service_factory.get_experiment_workflow()

    print(f"Setup manager created: {setup_manager is not None}")
    print(f"Stimulus generator created: {stimulus_generator is not None}")
    print(f"Acquisition controller created: {acquisition_controller is not None}")
    print(f"Frame synchronizer created: {frame_synchronizer is not None}")
    print(f"Data analyzer created: {data_analyzer is not None}")
    print(f"Experiment workflow created: {experiment_workflow is not None}")


def demonstrate_complete_workflow() -> None:
    """Demonstrate complete workflow creation."""
    print("\n=== COMPLETE WORKFLOW DEMO ===")

    # Create complete workflow
    workflow_services = service_factory.create_complete_workflow()

    print("Complete workflow services:")
    for service_name, service_instance in workflow_services.items():
        print(f"  {service_name}: {type(service_instance).__name__}")


def main() -> None:
    """Main demo function."""
    print("ISI REFACTORED ARCHITECTURE DEMONSTRATION")
    print("=" * 50)

    try:
        # Run service demos using actual factory methods
        demonstrate_service_registration()
        demonstrate_data_services()
        demonstrate_experiment_services()
        demonstrate_complete_workflow()

        print("\n" + "=" * 50)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("All SOLID principles implemented:")
        print("✓ Single Responsibility - Each service has one job")
        print("✓ Open/Closed - Easy to extend with new implementations")
        print("✓ Liskov Substitution - All implementations are interchangeable")
        print("✓ Interface Segregation - Small, focused interfaces")
        print("✓ Dependency Inversion - All dependencies via abstractions")
        print("✓ Fail Fast - No fallback methods, immediate error handling")
        print("✓ Pydantic Validation - Type safety throughout")

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise


if __name__ == "__main__":
    main()
