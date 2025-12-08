# Bridge Node Architecture Design - Phase 2

This document describes the updated bridge node architecture that uses configuration files and dynamic loading.

## Overview

The Phase 2 bridge node transitions from hard-coded single-type bridging to config-driven multi-type bridging while maintaining the core ROS2/RIX integration.

---

## Architecture Comparison

### Phase 1 Architecture (Hard-coded)
```python
class RixRosBridge(RosNode):
    def __init__(self):
        # Hard-coded String type
        from std_msgs.msg import String as RosString
        from rix.msg.standard import String as RixString
        from converters.std_msgs import StringConverter
        
        # Create single bridge
        self.ros_to_rix = BridgeHandleRosToRix(
            ros_msg_class=RosString,
            rix_msg_class=RixString,
            converter=StringConverter,
            ...
        )
```

### Phase 2 Architecture (Config-driven)
```python
class ConfigurableBridgeNode(RosNode):
    def __init__(self, config_path):
        # Load configuration
        config = load_bridge_config(config_path)
        mappings = load_message_mappings()
        
        # Create factory
        factory = BridgeFactory(self, rix_node)
        factory.message_mappings = mappings
        
        # Create multiple bridges dynamically
        for bridge_cfg in config["bridges"]:
            factory.create_bridge(bridge_cfg)
```

---

## ConfigurableBridgeNode Class Design

```python
class ConfigurableBridgeNode(RosNode):
    """
    ROS2 node that creates multiple ROS-RIX bridges based on JSON configuration.
    
    Features:
    - Reads bridge_config.json at startup
    - Creates multiple bridges dynamically
    - Manages lifecycle of all bridges
    - Supports bidirectional and unidirectional bridges
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configurable bridge node.
        
        Args:
            config_path: Path to bridge_config.json (optional)
                        If None, uses default config location
        """
        
    def load_configuration(self, config_path: str):
        """
        Load bridge configuration from JSON file.
        
        Args:
            config_path: Path to bridge_config.json
            
        Returns:
            Dictionary containing bridge configurations
        """
        
    def setup_factory(self):
        """
        Initialize the BridgeFactory with message mappings.
        
        Loads message_mappings.json and prepares factory for bridge creation.
        """
        
    def create_bridges(self, bridge_configs: list):
        """
        Create all bridges from configuration.
        
        Args:
            bridge_configs: List of bridge configuration dicts
            
        Creates bridges sequentially and logs success/failure for each.
        """
        
    def shutdown_bridges(self):
        """
        Clean shutdown of all active bridges.
        
        Called on node shutdown to properly close all ROS/RIX resources.
        """
```

---

## Initialization Flow

```
1. Node Creation
   └─→ rclpy.init()
   └─→ ConfigurableBridgeNode(config_path)
   
2. ROS Node Setup
   └─→ super().__init__('rix_ros_bridge')
   └─→ self.get_logger().info("Starting bridge...")
   
3. RIX Node Setup
   └─→ rix.core.init()
   └─→ rix_node = rix.Node('rix_ros_bridge')
   
4. Configuration Loading
   └─→ config = load_bridge_config(config_path)
   └─→ mappings = load_message_mappings()
   
5. Factory Setup
   └─→ factory = BridgeFactory(ros_node, rix_node)
   └─→ factory.message_mappings = mappings
   
6. Bridge Creation
   └─→ for bridge_cfg in config["bridges"]:
       └─→ try:
           └─→ factory.create_bridge(bridge_cfg)
           └─→ logger.info(f"✓ Created {bridge_cfg['name']}")
       └─→ except Exception as e:
           └─→ logger.error(f"✗ Failed {bridge_cfg['name']}: {e}")
           └─→ # Continue or exit based on error severity?
   
7. Spin
   └─→ rclpy.spin(ros_node)
```

---

## Implementation Pseudocode

```python
import rclpy
from rclpy.node import Node as RosNode
import rix.core
import rix

from .bridge_factory import BridgeFactory
from .config_loader import load_bridge_config, load_message_mappings

class ConfigurableBridgeNode(RosNode):
    """Configurable multi-bridge ROS-RIX node."""
    
    def __init__(self, config_path: str = None):
        """Initialize node with configuration."""
        # Initialize ROS node
        super().__init__('rix_ros_bridge')
        
        # Initialize RIX
        rix.core.init()
        self.rix_node = rix.Node('rix_ros_bridge')
        
        # Set default config path if not provided
        if config_path is None:
            pkg_path = get_package_share_directory('rix_ros_bridge')
            config_path = os.path.join(pkg_path, 'config', 'bridge_config.json')
        
        # Load configuration
        self.get_logger().info(f"Loading configuration from: {config_path}")
        self.config = load_bridge_config(config_path)
        
        # Setup factory
        self.get_logger().info("Setting up bridge factory...")
        self.factory = BridgeFactory(self, self.rix_node)
        
        mappings_path = os.path.join(pkg_path, 'config', 'message_mappings.json')
        self.factory.message_mappings = load_message_mappings(mappings_path)
        
        # Create bridges
        self.get_logger().info(f"Creating {len(self.config['bridges'])} bridge(s)...")
        self.create_bridges(self.config['bridges'])
        
        self.get_logger().info("Bridge node ready!")
    
    def create_bridges(self, bridge_configs: list):
        """Create all bridges from config."""
        success_count = 0
        fail_count = 0
        
        for bridge_cfg in bridge_configs:
            try:
                self.factory.create_bridge(bridge_cfg)
                self.get_logger().info(
                    f"✓ Created bridge '{bridge_cfg['name']}': "
                    f"{bridge_cfg['ros_topic']} ↔ {bridge_cfg['rix_topic']} "
                    f"({bridge_cfg['message_type']}, {bridge_cfg['direction']})"
                )
                success_count += 1
            except KeyError as e:
                self.get_logger().error(
                    f"✗ Failed to create bridge '{bridge_cfg['name']}': "
                    f"Message type not supported: {e}"
                )
                fail_count += 1
            except Exception as e:
                self.get_logger().error(
                    f"✗ Failed to create bridge '{bridge_cfg['name']}': {e}"
                )
                fail_count += 1
        
        self.get_logger().info(
            f"Bridge creation complete: {success_count} succeeded, {fail_count} failed"
        )
        
        if success_count == 0:
            raise RuntimeError("No bridges were successfully created!")
    
    def shutdown_bridges(self):
        """Shutdown all bridges cleanly."""
        self.get_logger().info("Shutting down bridges...")
        # Factory handles cleanup
        self.factory.shutdown_all()


def main(args=None):
    """Main entry point."""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='RIX-ROS Bridge Node')
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to bridge configuration JSON file'
    )
    parsed_args = parser.parse_args(args)
    
    # Initialize ROS
    rclpy.init(args=args)
    
    try:
        # Create node
        node = ConfigurableBridgeNode(config_path=parsed_args.config)
        
        # Spin
        rclpy.spin(node)
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        # Cleanup
        if 'node' in locals():
            node.shutdown_bridges()
            node.destroy_node()
        rclpy.shutdown()
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
```

---

## Command-Line Interface

### Default Configuration
```bash
ros2 run rix_ros_bridge bridge_node
# Uses: install/rix_ros_bridge/share/rix_ros_bridge/config/bridge_config.json
```

### Custom Configuration
```bash
ros2 run rix_ros_bridge bridge_node --config path/to/my_config.json
```

### Example Configurations
```bash
# Simple string bridge
ros2 run rix_ros_bridge bridge_node --config config/examples/simple_bridge.json

# Multiple types
ros2 run rix_ros_bridge bridge_node --config config/examples/multi_type_bridge.json

# Robot control
ros2 run rix_ros_bridge bridge_node --config config/examples/robot_control_bridge.json
```

---

## Error Handling Strategy

### Startup Errors (Fatal - Exit)

**1. Configuration File Not Found**
```
ERROR: Configuration file not found: config/bridge_config.json
Please provide a valid config file using --config option.
Exiting...
```

**2. Invalid JSON Syntax**
```
ERROR: Failed to parse configuration file: Invalid JSON at line 12
Check your JSON syntax.
Exiting...
```

**3. Message Mappings Not Found**
```
ERROR: Message mappings file not found: config/message_mappings.json
This is a core file required for bridge operation.
Exiting...
```

### Bridge Creation Errors (Partial - Continue)

**4. Unsupported Message Type**
```
WARNING: Bridge 'image_bridge' uses unsupported type 'sensor_msgs/Image'
Skipping this bridge. Other bridges will continue.
```

**5. Invalid Configuration**
```
WARNING: Bridge 'bad_bridge' has invalid config: Missing 'direction' field
Skipping this bridge. Other bridges will continue.
```

**6. No Bridges Created**
```
ERROR: Failed to create any bridges!
At least one bridge must be successfully created.
Exiting...
```

---

## Logging Output Example

```
[INFO] [1700000000.000] [rix_ros_bridge]: Starting RIX-ROS Bridge Node
[INFO] [1700000000.100] [rix_ros_bridge]: Loading configuration from: config/bridge_config.json
[INFO] [1700000000.200] [rix_ros_bridge]: Setting up bridge factory...
[INFO] [1700000000.300] [rix_ros_bridge]: Loaded 18 message type mappings
[INFO] [1700000000.400] [rix_ros_bridge]: Creating 3 bridge(s)...
[INFO] [1700000000.500] [rix_ros_bridge]: ✓ Created bridge 'string_bridge': /chatter ↔ /chatter_rix (std_msgs/String, bidirectional)
[INFO] [1700000000.600] [rix_ros_bridge]: ✓ Created bridge 'pose_bridge': /robot_pose ↔ /pose_rix (geometry_msgs/Pose, ros_to_rix)
[INFO] [1700000000.700] [rix_ros_bridge]: ✓ Created bridge 'twist_bridge': /cmd_vel ↔ /cmd_vel_rix (geometry_msgs/Twist, bidirectional)
[INFO] [1700000000.800] [rix_ros_bridge]: Bridge creation complete: 3 succeeded, 0 failed
[INFO] [1700000000.900] [rix_ros_bridge]: Bridge node ready!
```

---

## Phase 1 Compatibility

### Option 1: No Backward Compatibility (Recommended)
- Phase 2 completely replaces Phase 1
- Old hard-coded bridge_node.py is archived
- All usage must use configuration files
- **Benefit:** Cleaner, no technical debt

### Option 2: Keep Phase 1 as Fallback
- If no config file provided, use hard-coded String bridge
- **Benefit:** Backward compatible
- **Drawback:** Maintains old code, more complex

### Recommendation: Option 1
Phase 1 is a proof-of-concept. Phase 2 should be a clean implementation without legacy baggage. Users can easily create a String-only config if needed:

```json
{
  "bridges": [{
    "name": "string_bridge",
    "ros_topic": "/chatter",
    "rix_topic": "/chatter_from_ros",
    "message_type": "std_msgs/String",
    "direction": "bidirectional"
  }]
}
```

This provides same functionality as Phase 1 but through the new architecture.

---

## File Structure

```
rix_ros_bridge/
├── bridge_node.py              ← ConfigurableBridgeNode (new)
├── bridge_node_phase1.py       ← Old implementation (archived)
├── bridge_factory.py           ← BridgeFactory class (new)
├── message_loader.py           ← MessageTypeLoader (new)
├── config_loader.py            ← Config loading utilities (new)
├── bridge_handle_ros_to_rix.py ← Updated for dynamic types
├── bridge_handle_rix_to_ros.py ← Updated for dynamic types
├── converters/
│   ├── __init__.py             ← CONVERTER_REGISTRY (updated)
│   ├── std_msgs.py             ← All std_msgs converters
│   └── geometry_msgs.py        ← All geometry_msgs converters
└── config/
    ├── message_mappings.json   ← Type registry
    ├── bridge_config.json      ← Default config
    └── examples/               ← Example configs
```

---

## Testing Strategy

### Unit Tests
```python
# test_bridge_node.py
def test_node_initialization():
    """Test node can be created with valid config."""
    
def test_invalid_config():
    """Test node handles invalid config gracefully."""
    
def test_multiple_bridges():
    """Test node can create multiple bridges."""
```

### Integration Tests
```bash
# Launch bridge with test config
ros2 run rix_ros_bridge bridge_node --config test_config.json

# Verify bridges are created
ros2 topic list  # Should show ROS topics
rix topic list   # Should show RIX topics

# Send test messages
ros2 topic pub /test_topic std_msgs/String "data: 'test'"

# Verify messages received on RIX side
```

---

## Migration from Phase 1

### For Users:
1. Create `bridge_config.json` with desired bridges
2. Run new command: `ros2 run rix_ros_bridge bridge_node --config config.json`
3. Old Phase 1 usage no longer supported

### For Developers:
1. Archive `bridge_node.py` → `bridge_node_phase1.py`
2. Implement new `bridge_node.py` with ConfigurableBridgeNode
3. Update package.xml entry point to use new main()

---

## Performance Considerations

### Startup Time
- Loading JSON configs: ~10ms
- Creating 18 converters: ~50ms
- Creating 5 bridges: ~100ms
- **Total startup overhead: ~160ms** (acceptable)

### Runtime Performance
- Dynamic loading happens once at startup
- Runtime performance identical to Phase 1 (no overhead)
- Each bridge is independent, no cross-bridge overhead

---

## Future Enhancements (Phase 3+)

### Dynamic Reconfiguration
- Reload config without restarting node
- Add/remove bridges at runtime
- ROS2 parameter server integration

### Monitoring
- Bridge status topic (which bridges active)
- Message count statistics
- Error rate monitoring

### Advanced Features
- Message filtering/transformation
- Topic remapping
- Quality of Service (QoS) configuration

---

## Summary

**Key Changes from Phase 1:**
- ✅ Config-driven instead of hard-coded
- ✅ Multiple bridges instead of single
- ✅ Dynamic type loading instead of static imports
- ✅ Factory pattern instead of direct instantiation
- ✅ Extensible architecture for future types

**Benefits:**
- ✅ Add new types without code changes
- ✅ Configure bridges without recompiling
- ✅ Support multiple simultaneous bridges
- ✅ Clear error messages and validation
- ✅ Scalable and maintainable

**Next Steps:**
1. ✅ Design complete (this document)
2. ⏳ Implement message_loader.py (Section 3)
3. ⏳ Implement bridge_factory.py (Section 4)
4. ⏳ Implement config_loader.py (Section 5)
5. ⏳ Update bridge_node.py (Section 6)
6. ⏳ Test and validate (Section 7)
