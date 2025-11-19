# RIX-ROS Bridge

Bidirectional message bridge between ROS2 and RIX systems.

## Overview

This package provides a bridge for message passing between ROS2 and RIX (Robotics Interprocess eXchange). It enables seamless communication between the two middleware systems.

## Phase 1 Features (Nov 7 Deadline)

- ✅ Hard-coded bidirectional bridge for `/chatter` topic
- ✅ String message conversion (std_msgs/String <-> rix.msg.standard.String)
- ✅ ROS→RIX: Subscribes to ROS `/chatter`, publishes to RIX `/chatter_from_ros`
- ✅ RIX→ROS: Subscribes to RIX `/chatter`, publishes to ROS `/chatter_from_rix`
- ✅ **Echo-back prevention** using separate topic names
- ✅ Dual spin loop for ROS and RIX event processing
- ✅ Comprehensive error handling and graceful shutdown

## Prerequisites

- ROS2 Jazzy (Ubuntu 24.04)
- RIX C++ library installed
- RIX Python library installed
- rixhub server running

## Installation

```bash
# Build the package
cd ~/Desktop/ROB490/bridge_ws
colcon build --packages-select rix_ros_bridge

# Source the workspace
source install/setup.bash
```

## Usage

### Start rixhub (in separate terminal)
```bash
rixhub
```

### Run the bridge
```bash
ros2 run rix_ros_bridge bridge_node
```

### Test ROS → RIX
```bash
# Terminal 1: Subscribe to RIX output topic
# Use RIX subscriber on /chatter_from_ros

# Terminal 2: Publish from ROS input topic
ros2 topic pub /chatter std_msgs/msg/String "data: 'Hello from ROS'"

# You should see the message bridged to RIX /chatter_from_ros
```

### Test RIX → ROS
```bash
# Terminal 1: Subscribe to ROS output topic
ros2 topic echo /chatter_from_rix

# Terminal 2: Publish from RIX input topic
# Use RIX publisher on /chatter
cd ~/Desktop/ROB490/rix-py
# Modify simple_publisher.py to publish on /chatter
python3 examples/simple_publisher.py

# You should see the message bridged to ROS /chatter_from_rix
```

### View Bridge Topics
```bash
# See all topics (ROS side)
ros2 topic list

# Echo RIX→ROS bridged messages
ros2 topic echo /chatter_from_rix
```

### Stop the Bridge
```bash
# Press Ctrl+C in the bridge terminal
# Bridge will shut down gracefully
```

## Architecture

### Echo-Back Prevention

The bridge uses **separate topic names** for input and output to prevent infinite message loops:

```
ROS System              Bridge               RIX System
    │                                            │
/chatter ────────► ROS→RIX Handle ────────► /chatter_from_ros
    │                                            │
/chatter_from_rix ◄─ RIX→ROS Handle ◄──────  /chatter
```

This ensures:
- ROS→RIX handle only sees external ROS messages (not its own output)
- RIX→ROS handle only sees external RIX messages (not its own output)
- No infinite loop where the bridge echoes its own messages

### Message Flow

**ROS to RIX:**
1. External publisher → ROS `/chatter`
2. Bridge subscribes → converts using StringConverter
3. Bridge publishes → RIX `/chatter_from_ros`

**RIX to ROS:**
1. External publisher → RIX `/chatter`
2. Bridge subscribes → converts using StringConverter  
3. Bridge publishes → ROS `/chatter_from_rix`

## Project Structure

```
rix_ros_bridge/
├── rix_ros_bridge/
│   ├── __init__.py
│   ├── bridge_node.py              # Main bridge node
│   ├── bridge_handle_ros_to_rix.py # ROS→RIX handler
│   ├── bridge_handle_rix_to_ros.py # RIX→ROS handler
│   └── converters/
│       ├── __init__.py
│       └── std_msgs.py             # Message converters
├── test/
│   ├── test_converters.py
│   └── test_bridge.py
├── config/
│   └── simple_bridge.yaml
├── launch/
│   └── bridge.launch.py
└── README.md
```

## Development Status

### Phase 1 (Nov 7, 2025) - COMPLETE ✅

- [x] Project structure created
- [x] Message converters implemented
  - [x] Base MessageConverter interface
  - [x] StringConverter (std_msgs/String ↔ rix.msg.standard.String)
- [x] Bridge handles implemented
  - [x] BridgeHandleRosToRix with echo-back prevention
  - [x] BridgeHandleRixToRos with echo-back prevention
- [x] Main bridge node implemented
  - [x] RixRosBridge class
  - [x] Dual spin loop (ROS + RIX events)
  - [x] Error handling and graceful shutdown
- [x] Unit tests implemented
  - [x] Converter tests (ros_to_rix, rix_to_ros, round-trip)
- [x] Entry point configuration (ros2 run command)

### Future Work
- [ ] Integration tests
- [ ] Additional message types

## Future Work (Phase 2 & 3)

- YAML configuration support
- Multiple message types
- Dynamic message loading
- Custom conversion functions

## Documentation

Detailed implementation guides are available in the workspace:

- **SECTION_3_IMPLEMENTATION_GUIDE.txt** - Message Converters (line-by-line)
- **SECTION_4_IMPLEMENTATION_GUIDE.txt** - Bridge Handles (line-by-line)
- **SECTION_5_IMPLEMENTATION_GUIDE.txt** - Main Bridge Node (line-by-line)
- **CONVERTER_TESTS_GUIDE.txt** - Running converter unit tests
- **RIX_ROS_BRIDGE_ROADMAP_NOV7.txt** - Complete project roadmap

## Troubleshooting

**Bridge not starting:**
- Ensure rixhub is running: `rixhub`
- Check ROS environment: `echo $ROS_DISTRO` (should show "jazzy")
- Rebuild: `colcon build --packages-select rix_ros_bridge`

**Messages not bridging:**
- Verify topics: `ros2 topic list` and check for `/chatter_from_ros` and `/chatter_from_rix`
- Check bridge logs for errors
- Ensure RIX Python is in PYTHONPATH: `export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH`

**Echo-back loop:**
- This should NOT happen with current implementation (separate topic names)
- If it does, check handle configuration in `bridge_node.py`

## License

Apache-2.0

## Maintainer

University of Michigan - ROB 490
dcleeman@umich.edu
