# RIX-ROS Bridge

A bidirectional message bridge between ROS2 and RIX robotics middleware.

## Project Overview

This bridge enables seamless communication between ROS2 (Robot Operating System 2) and RIX (a modern robotics middleware system), allowing robots to leverage ecosystems from both platforms.

**Institution:** University of Michigan - ROB 490  
**Project Status:** Phase 1 Complete (Nov 7, 2025)

## Features

### Phase 1 (Complete ✓)
- Bidirectional bridge for `std_msgs/String` messages
- ROS2 → RIX message conversion
- RIX → ROS2 message conversion
- Echo-back prevention through separate topic naming
- Comprehensive unit and integration tests

### Phase 2 (In Progress - Target: Nov 28, 2025)
- Configuration-driven multi-type bridge
- Support for 15-25 message types (std_msgs, geometry_msgs, sensor_msgs)
- JSON-based configuration system
- Dynamic message type loading
- Scalable architecture for easy addition of new types

## Verified Compatible Message Types

**Standard Types (12):**
- String, Int32, Int64, Float32, Float64, Bool
- UInt8, UInt16, UInt32, UInt64, Int8, Int16

**Geometry Types (6):**
- Point, Pose, Quaternion, Vector3, Twist, Transform

See `ROS_RIX_MESSAGE_MAPPINGS.txt` for complete mapping table.

## Installation

### Prerequisites
- ROS2 (tested on Humble)
- RIX-cpp and RIX-py installed
- Python 3.x
- rixhub running on port 48104

### Build
```bash
cd bridge_ws
colcon build --packages-select rix_ros_bridge
source install/setup.bash
```

## Usage

### Phase 1 (Current)
```bash
# Terminal 1: Start rixhub
rixhub

# Terminal 2: Start bridge
ros2 run rix_ros_bridge bridge_node

# Terminal 3: Publish from ROS
ros2 topic pub /chatter std_msgs/String "data: 'Hello from ROS'"

# Terminal 4: Subscribe from RIX
# (See test scripts in test/ directory)
```

### Phase 2 (Coming Soon)
```bash
ros2 run rix_ros_bridge bridge_node --config config/bridge_config.json
```

## Testing

### Unit Tests
```bash
cd src/rix_ros_bridge
pytest test/test_converters.py -v
```

### Integration Tests
```bash
# See SECTION_6_TESTING_GUIDE.txt for detailed test procedures
```

## Architecture

### Phase 1 Architecture
- `bridge_node.py` - Main bridge node
- `bridge_handle_ros_to_rix.py` - ROS → RIX message handler
- `bridge_handle_rix_to_ros.py` - RIX → ROS message handler
- `converters/std_msgs.py` - Message type converters

### Phase 2 Architecture (In Development)
- `message_loader.py` - Dynamic message class loading
- `bridge_factory.py` - Factory pattern for bridge creation
- `config_loader.py` - JSON configuration parser
- `config/message_mappings.json` - Message type registry
- `config/bridge_config.json` - User-facing bridge configuration

## Documentation

- `ROS_RIX_MESSAGE_MAPPINGS.txt` - Complete ROS↔RIX message type mapping
- `PHASE_2_DESIGN_EXPLANATION.txt` - Phase 2 architecture overview
- `SECTION_*_IMPLEMENTATION_GUIDE.txt` - Implementation guides for each section
- `verify_message_compatibility.py` - Message compatibility verification tool

## Project Timeline

- **Phase 1:** Oct 2025 - Nov 7, 2025 ✓ Complete
- **Phase 2:** Nov 7, 2025 - Nov 28, 2025 (In Progress)
- **Phase 3:** Dec 2025 - Custom message type support

## Contributing

This is an academic project. For questions or collaboration:
- University of Michigan - ROB 490 Course

## License

[To be determined]

## Acknowledgments

- RIX robotics middleware development team
- ROS2 community
- ros_gz_bridge project (architectural inspiration)
