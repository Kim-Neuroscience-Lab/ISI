# Hierarchical Scene Graph Architecture

## Overview

The ISI (Intrinsic Signal Imaging) visualization system now uses a modern hierarchical scene graph architecture that provides enhanced mouse anatomy detection, proper parent-child relationships, and clean separation of concerns.

## Architecture Components

### Core Classes

#### BaseSceneNode (`core/BaseSceneNode.js`)

- **Foundation class** for all scene objects
- Provides hierarchical parent-child relationships
- Event system for inter-node communication
- Transform management with proper inheritance
- Lifecycle management (initialize, update, destroy)
- Memory management with proper cleanup

**Key Features:**

- Unique ID generation for all nodes
- Map-based children management for fast lookups
- Transform synchronization with Three.js objects
- Event-driven architecture

#### SceneManager (`core/SceneManager.js`)

- **Central manager** for the entire scene graph
- Node registry and type-based organization
- Update loop management
- Raycasting support for interaction
- Scene statistics and debugging

**Key Features:**

- Automatic node registration/unregistration
- Type-based node queries
- Hierarchical scene export/import
- Performance monitoring

### Specialized Nodes

#### MouseAnatomyNode (`nodes/MouseAnatomyNode.js`)

- **Specialized node** for mouse brain anatomy visualization
- Enhanced anatomy region detection with invisible spheres
- Reference point management as child nodes
- Interactive region highlighting and selection
- STL model loading and processing

**Key Features:**

- 6 predefined brain regions (Frontal, Parietal, Occipital, Temporal, Cerebellum, Brainstem)
- Material states (normal, hover, selected)
- World-to-local coordinate transformation
- Raycasting for precise interaction

#### ReferencePointNode (`nodes/MouseAnatomyNode.js`)

- **Child nodes** for anatomical reference points
- Color-coded by type (bregma, lambda, electrode, injection)
- Inherits transformations from parent mouse
- Individual visibility control

## Scene Hierarchy Structure

```
SceneRoot
├── MouseAnatomy (MouseAnatomyNode)
│   ├── MouseMesh (Three.js Mesh)
│   ├── DetectionSphere_FrontalCortex (invisible interaction sphere)
│   ├── DetectionSphere_ParietalCortex
│   ├── ... (other anatomy regions)
│   ├── Bregma (ReferencePointNode)
│   ├── Lambda (ReferencePointNode)
│   └── ... (other reference points)
└── ... (other scene objects)
```

## Interaction System

### Mouse Interaction

- **Hover Detection**: Raycast against invisible detection spheres
- **Click Selection**: Select anatomy regions for detailed information
- **Visual Feedback**: Color changes and opacity for hover/selection states

### Keyboard Shortcuts

- `H` - Toggle anatomy regions visibility
- `P` - Toggle reference points visibility
- `R` - Reset camera position
- `D` - Print debug information to console
- `T` - Toggle scene tree panel
- `C` - Toggle controls panel
- `ESC` - Clear current selection

## Enhanced Features

### Anatomy Detection

1. **Region-based Detection**: Each brain region has a 3D sphere for precise detection
2. **Hierarchical Selection**: Regions are organized by anatomical hierarchy
3. **Visual Feedback**: Real-time highlighting during interaction
4. **Information Display**: Dynamic info panel showing region details

### Reference Points

1. **Type-based Coloring**: Different colors for different point types
2. **Parent Inheritance**: Points move with mouse transformations
3. **Individual Control**: Each point can be shown/hidden independently
4. **Anatomical Accuracy**: Positioned relative to mouse coordinate system

### Memory Management

1. **Automatic Cleanup**: Proper disposal of Three.js objects
2. **Event Cleanup**: Removal of all event listeners on destruction
3. **Hierarchy Cleanup**: Recursive destruction of child nodes
4. **Material Disposal**: Texture and material cleanup

## Usage Example

```javascript
// Create scene manager
const sceneManager = new SceneManager(scene, camera, renderer);
await sceneManager.initialize();

// Create mouse anatomy node
const mouseNode = await sceneManager.createMouseAnatomyNode("Mouse Brain");

// Load STL model
await mouseNode.loadSTLModel("./3d_models/Mouse-stl.stl");

// Add reference points
const referencePoints = [
  { name: "Bregma", x: 0, y: 0.5, z: 1.0, type: "bregma" },
  { name: "Lambda", x: 0, y: 0.2, z: -0.8, type: "lambda" },
];
sceneManager.addReferencePointsToMouse(mouseNode, referencePoints);

// Set up event listeners
mouseNode.on("regionSelected", (data) => {
  console.log("Selected region:", data.region);
});
```

## Benefits

### SOLID Principles

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend with new node types
- **Liskov Substitution**: All nodes extend BaseSceneNode consistently
- **Interface Segregation**: Clean, focused interfaces
- **Dependency Inversion**: High-level modules don't depend on low-level details

### Design Patterns

- **Composite Pattern**: Hierarchical node structure
- **Observer Pattern**: Event-driven communication
- **Factory Pattern**: SceneManager creates specialized nodes
- **Strategy Pattern**: Different node types handle updates differently

### Performance

- **Efficient Updates**: Only enabled nodes are updated
- **Smart Raycasting**: Type-based filtering for interaction testing
- **Memory Efficiency**: Proper cleanup prevents memory leaks
- **Scene Optimization**: Hierarchical culling and LOD support

## Future Extensions

### Planned Features

1. **Additional Node Types**: Electrode arrays, injection sites, imaging regions
2. **Animation System**: Smooth transitions and procedural animations
3. **Serialization**: Save/load complete scene configurations
4. **Multi-mouse Support**: Multiple mouse models in one scene
5. **Real-time Updates**: Live data integration from acquisition systems

### Extensibility

The architecture is designed for easy extension. New node types can be created by extending `BaseSceneNode` and implementing the required lifecycle methods:

```javascript
class CustomNode extends BaseSceneNode {
  constructor(name) {
    super(name, "CustomType");
  }

  async onInitialize() {
    // Custom initialization logic
  }

  onUpdate(deltaTime) {
    // Custom update logic
  }

  onDestroy() {
    // Custom cleanup logic
  }
}
```

## File Structure

```
src/renderer/
├── core/
│   ├── BaseSceneNode.js      # Foundation class
│   └── SceneManager.js       # Scene management
├── nodes/
│   ├── MouseAnatomyNode.js   # Mouse anatomy + reference points
│   ├── MouseNode.js          # Legacy mouse node
│   └── MonitorNode.js        # Monitor visualization
├── visualization.js          # Main visualizer class
├── app.js                   # Application entry point
└── index.html               # Main interface
```

This architecture provides a solid foundation for the ISI visualization system with proper separation of concerns, enhanced interactivity, and excellent extensibility for future features.
