# ISI-Core/README.md

# ISI Core Module

A shared core module providing common interfaces, abstractions, and utilities for the ISI (Intrinsic Signal Imaging) project. This module follows SOLID principles and provides a foundation for all other ISI modules.

## Architecture

The ISI-Core module is designed with the following principles:

### SOLID Principles

- **S**ingle Responsibility Principle: Each class has one reason to change
- **O**pen/Closed Principle: Open for extension, closed for modification
- **L**iskov Substitution Principle: Derived classes are substitutable for base classes
- **I**nterface Segregation Principle: Clients depend only on interfaces they use
- **D**ependency Inversion Principle: Depend on abstractions, not concretions

### Design Patterns

- **Strategy Pattern**: For algorithms (alignment, detection, rendering)
- **Observer Pattern**: For event handling and notifications
- **Factory Pattern**: For object creation
- **Command Pattern**: For operations and undo functionality
- **Repository Pattern**: For data access abstraction

## Module Structure

```
ISI-Core/
├── src/
│   ├── interfaces/          # Abstract interfaces and contracts
│   ├── entities/           # Domain entities and value objects
│   ├── services/           # Core business logic services
│   ├── events/             # Event system and publishers
│   ├── factories/          # Object factories
│   ├── exceptions/         # Custom exception classes
│   └── utils/              # Shared utilities
├── tests/                  # Unit and integration tests
└── docs/                   # Documentation
```

## Key Interfaces

- `IGeometryProvider`: Provides geometric calculations and transformations
- `IVisualizationRenderer`: Abstracts rendering operations
- `IDataRepository`: Abstracts data persistence
- `IEventPublisher`: Handles event publishing and subscription
- `IConfigurationManager`: Manages application configuration

## Usage

```python
from isi_core.interfaces import IGeometryProvider
from isi_core.services import GeometryService
from isi_core.factories import ServiceFactory

# Use dependency injection
geometry_service = ServiceFactory.create_geometry_service()
result = geometry_service.calculate_alignment(parameters)
```

## Dependencies

- Python 3.8+
- NumPy for mathematical operations
- Pydantic for data validation
- ABC for abstract base classes
