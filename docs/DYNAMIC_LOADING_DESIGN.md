# Dynamic Loading Architecture Design

This document describes the architecture for dynamically loading ROS/RIX message classes and converters at runtime based on JSON configuration.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Bridge Node                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Configuration Loader                       │   │
│  │  - Loads bridge_config.json                          │   │
│  │  - Loads message_mappings.json                       │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Bridge Factory                             │   │
│  │  - Creates bridge instances from config              │   │
│  │  - Validates message types                           │   │
│  │  - Uses MessageTypeLoader                            │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        MessageTypeLoader                             │   │
│  │  - Dynamically imports ROS message classes           │   │
│  │  - Dynamically imports RIX message classes           │   │
│  │  - Loads converter from registry                     │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│                     ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        ConverterRegistry                             │   │
│  │  - CONVERTER_REGISTRY dict                           │   │
│  │  - Maps converter names to classes                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        Bridge Handles (Multiple)                     │   │
│  │  - BridgeHandleRosToRix                              │   │
│  │  - BridgeHandleRixToRos                              │   │
│  │  - Each created by BridgeFactory                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component 1: MessageTypeLoader

**Responsibility:** Dynamically load Python classes at runtime using importlib

### Class Design

```python
class MessageTypeLoader:
    """
    Utility class for dynamically loading ROS/RIX message classes
    and converters at runtime.
    """
    
    @staticmethod
    def load_ros_class(import_path: str):
        """
        Dynamically import a ROS message class.
        
        Args:
            import_path: Python import path (e.g., "std_msgs.msg.String")
            
        Returns:
            The imported ROS message class
            
        Raises:
            ImportError: If the module or class cannot be imported
            
        Example:
            >>> String = MessageTypeLoader.load_ros_class("std_msgs.msg.String")
            >>> msg = String()
        """
        
    @staticmethod
    def load_rix_class(import_path: str):
        """
        Dynamically import a RIX message class.
        
        Args:
            import_path: Python import path (e.g., "rix.msg.standard.String")
            
        Returns:
            The imported RIX message class
            
        Raises:
            ImportError: If the module or class cannot be imported
            
        Example:
            >>> String = MessageTypeLoader.load_rix_class("rix.msg.standard.String")
            >>> msg = String()
        """
    
    @staticmethod
    def load_converter(converter_name: str):
        """
        Get converter class from the registry.
        
        Args:
            converter_name: Name of converter (e.g., "StringConverter")
            
        Returns:
            The converter class from CONVERTER_REGISTRY
            
        Raises:
            KeyError: If converter not found in registry
            
        Example:
            >>> converter = MessageTypeLoader.load_converter("StringConverter")
            >>> ros_msg = converter.rix_to_ros(rix_msg)
        """
```

### Implementation Strategy

**Using importlib:**
```python
import importlib

def load_ros_class(import_path: str):
    # Example: "std_msgs.msg.String"
    # Split into: module_path="std_msgs.msg", class_name="String"
    
    parts = import_path.rsplit('.', 1)
    module_path = parts[0]  # "std_msgs.msg"
    class_name = parts[1]   # "String"
    
    # Import the module
    module = importlib.import_module(module_path)
    
    # Get the class from the module
    msg_class = getattr(module, class_name)
    
    return msg_class
```

### Error Handling

```python
try:
    ros_class = MessageTypeLoader.load_ros_class("std_msgs.msg.String")
except ImportError as e:
    logger.error(f"Failed to import ROS class: {e}")
    raise
except AttributeError as e:
    logger.error(f"Class not found in module: {e}")
    raise
```

---

## Component 2: ConverterRegistry

**Responsibility:** Central registry mapping converter names to converter classes

### Design

```python
# In converters/__init__.py

from .std_msgs import StringConverter, Int32Converter, BoolConverter, ...
from .geometry_msgs import PointConverter, PoseConverter, ...

# Central registry
CONVERTER_REGISTRY = {
    "StringConverter": StringConverter,
    "Int32Converter": Int32Converter,
    "Int64Converter": Int64Converter,
    "Float32Converter": Float32Converter,
    "Float64Converter": Float64Converter,
    "BoolConverter": BoolConverter,
    "UInt8Converter": UInt8Converter,
    "UInt16Converter": UInt16Converter,
    "UInt32Converter": UInt32Converter,
    "UInt64Converter": UInt64Converter,
    "Int8Converter": Int8Converter,
    "Int16Converter": Int16Converter,
    "PointConverter": PointConverter,
    "PoseConverter": PoseConverter,
    "QuaternionConverter": QuaternionConverter,
    "Vector3Converter": Vector3Converter,
    "TwistConverter": TwistConverter,
    "TransformConverter": TransformConverter,
}

def get_converter(converter_name: str):
    """
    Get converter class from registry.
    
    Args:
        converter_name: Name of converter
        
    Returns:
        Converter class
        
    Raises:
        KeyError: If converter not found
    """
    if converter_name not in CONVERTER_REGISTRY:
        available = ", ".join(CONVERTER_REGISTRY.keys())
        raise KeyError(
            f"Converter '{converter_name}' not found in registry. "
            f"Available converters: {available}"
        )
    return CONVERTER_REGISTRY[converter_name]
```

### Adding New Converters

```python
# When adding a new converter:
# 1. Implement converter class
# 2. Import it in converters/__init__.py
# 3. Add to CONVERTER_REGISTRY

from .sensor_msgs import ImageConverter  # ← Step 1 & 2

CONVERTER_REGISTRY = {
    # ... existing converters ...
    "ImageConverter": ImageConverter,    # ← Step 3
}
```

---

## Component 3: BridgeFactory

**Responsibility:** Create bridge instances from configuration

### Class Design

```python
class BridgeFactory:
    """
    Factory for creating bridge instances from configuration.
    """
    
    def __init__(self, ros_node, rix_node):
        """
        Initialize factory with ROS and RIX nodes.
        
        Args:
            ros_node: ROS2 node instance
            rix_node: RIX node instance
        """
        self.ros_node = ros_node
        self.rix_node = rix_node
        self.message_mappings = {}
        self.bridges = []
        
    def load_message_mappings(self, json_path: str) -> dict:
        """
        Load message type mappings from JSON file.
        
        Args:
            json_path: Path to message_mappings.json
            
        Returns:
            Dictionary of message mappings
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        
    def validate_message_type(self, message_type: str) -> bool:
        """
        Check if message type is supported.
        
        Args:
            message_type: Message type key (e.g., "std_msgs/String")
            
        Returns:
            True if supported, False otherwise
        """
        
    def create_bridge(self, bridge_config: dict):
        """
        Create a bridge instance from configuration.
        
        Args:
            bridge_config: Single bridge configuration dict
            
        Returns:
            Tuple of bridge handles (ros_to_rix, rix_to_ros) or None
            
        Raises:
            ValueError: If configuration is invalid
            KeyError: If message type not found
        
        Process:
        1. Validate bridge configuration
        2. Get message type info from mappings
        3. Load ROS message class dynamically
        4. Load RIX message class dynamically
        5. Load converter from registry
        6. Create bridge handle(s) based on direction
        7. Return bridge handle(s)
        """
```

### Implementation Pseudocode

```python
def create_bridge(self, bridge_config: dict):
    # 1. Validate configuration
    required = ["name", "ros_topic", "rix_topic", "message_type", "direction"]
    for field in required:
        if field not in bridge_config:
            raise ValueError(f"Missing required field: {field}")
    
    # 2. Get message type info
    msg_type = bridge_config["message_type"]
    if not self.validate_message_type(msg_type):
        raise KeyError(f"Message type {msg_type} not supported")
    
    type_info = self.message_mappings[msg_type]
    
    # 3. Load ROS class
    ros_class = MessageTypeLoader.load_ros_class(type_info["ros_import"])
    
    # 4. Load RIX class
    rix_class = MessageTypeLoader.load_rix_class(type_info["rix_import"])
    
    # 5. Load converter
    converter = MessageTypeLoader.load_converter(type_info["converter"])
    
    # 6. Create bridge handle(s) based on direction
    direction = bridge_config["direction"]
    ros_topic = bridge_config["ros_topic"]
    rix_topic = bridge_config["rix_topic"]
    queue_size = bridge_config.get("queue_size", 10)
    
    ros_to_rix_handle = None
    rix_to_ros_handle = None
    
    if direction in ["ros_to_rix", "bidirectional"]:
        ros_to_rix_handle = BridgeHandleRosToRix(
            ros_node=self.ros_node,
            rix_node=self.rix_node,
            ros_topic=ros_topic,
            rix_topic=rix_topic,
            ros_msg_class=ros_class,
            rix_msg_class=rix_class,
            converter=converter,
            queue_size=queue_size
        )
    
    if direction in ["rix_to_ros", "bidirectional"]:
        rix_to_ros_handle = BridgeHandleRixToRos(
            ros_node=self.ros_node,
            rix_node=self.rix_node,
            ros_topic=ros_topic,
            rix_topic=rix_topic,
            ros_msg_class=ros_class,
            rix_msg_class=rix_class,
            converter=converter,
            queue_size=queue_size
        )
    
    # 7. Store and return handles
    self.bridges.append((ros_to_rix_handle, rix_to_ros_handle))
    return (ros_to_rix_handle, rix_to_ros_handle)
```

---

## Component 4: Configuration Loader

**Responsibility:** Load and parse JSON configuration files

### Design

```python
def load_message_mappings(json_path: str) -> dict:
    """
    Load message_mappings.json file.
    
    Returns:
        Dictionary with message type mappings
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data["message_mappings"]

def load_bridge_config(json_path: str) -> dict:
    """
    Load bridge_config.json file.
    
    Returns:
        Dictionary with bridge configurations
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data
```

---

## Integration: How It All Works Together

### Startup Sequence

```python
def main():
    # 1. Initialize ROS and RIX
    rclpy.init()
    ros_node = Node('rix_ros_bridge')
    rix_node = rix.Node('rix_ros_bridge')
    
    # 2. Create factory
    factory = BridgeFactory(ros_node, rix_node)
    
    # 3. Load message mappings (the "dictionary")
    mappings = load_message_mappings('config/message_mappings.json')
    factory.message_mappings = mappings
    
    # 4. Load bridge configuration (the "to-do list")
    config = load_bridge_config('config/bridge_config.json')
    
    # 5. Create all bridges
    for bridge_config in config["bridges"]:
        try:
            factory.create_bridge(bridge_config)
            print(f"✓ Created bridge: {bridge_config['name']}")
        except Exception as e:
            print(f"✗ Failed to create bridge {bridge_config['name']}: {e}")
            # Continue with other bridges or exit?
    
    # 6. Spin
    rclpy.spin(ros_node)
```

---

## Benefits of This Architecture

### ✅ **Extensibility**
- Add new types: just update JSON + add converter
- No changes to core bridge code

### ✅ **Type Safety**
- Validates message types at startup
- Clear error messages for unsupported types

### ✅ **Flexibility**
- Users configure bridges via JSON
- Multiple bridges from one config file

### ✅ **Maintainability**
- Clear separation of concerns
- Each component has single responsibility

### ✅ **Testability**
- Each component can be unit tested
- Mock JSON configs for testing

---

## Error Handling Strategy

### Level 1: Configuration Validation
```python
# Check config syntax and required fields
if "message_type" not in config:
    raise ValueError("Missing message_type field")
```

### Level 2: Message Type Validation
```python
# Check if type is supported
if msg_type not in message_mappings:
    raise KeyError(f"Unsupported type: {msg_type}")
```

### Level 3: Dynamic Loading
```python
# Handle import errors
try:
    ros_class = MessageTypeLoader.load_ros_class(import_path)
except ImportError as e:
    raise ImportError(f"Failed to import ROS class: {e}")
```

### Level 4: Converter Loading
```python
# Check converter exists
if converter_name not in CONVERTER_REGISTRY:
    raise KeyError(f"Converter not found: {converter_name}")
```

---

## Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement MessageTypeLoader
3. ⏳ Implement ConverterRegistry
4. ⏳ Implement BridgeFactory
5. ⏳ Update bridge_node.py to use factory
6. ⏳ Test with simple_bridge.json
