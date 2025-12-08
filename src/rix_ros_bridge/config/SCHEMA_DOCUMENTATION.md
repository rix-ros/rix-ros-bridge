# Configuration File Schemas

This document describes the JSON schemas used by the RIX-ROS Bridge for configuration.

## message_mappings.json

**Purpose:** Registry of message type mappings between ROS and RIX

**Location:** `config/message_mappings.json`

### Root Level Fields

- `comment` (string): Human-readable description
- `description` (string): Purpose of the file
- `version` (string): Schema version (semantic versioning)
- `last_updated` (string): Date of last update (YYYY-MM-DD)
- `verified_types_count` (integer): Number of verified message types
- `message_mappings` (object): Map of message type definitions

### Message Type Key Format

**Format:** `{ros_package}/{ros_type}`

**Examples:**
- `std_msgs/String`
- `geometry_msgs/Pose`
- `sensor_msgs/Image`

**Rationale:** This matches ROS2 topic type naming conventions

### Message Mapping Object

Each entry in `message_mappings` has the following structure:

```json
"std_msgs/String": {
  "ros_package": "std_msgs",           // ROS package name
  "ros_type": "String",                 // ROS message type name
  "ros_import": "std_msgs.msg.String",  // Python import path for ROS type
  "rix_package": "standard",            // RIX package name
  "rix_type": "String",                 // RIX message type name
  "rix_import": "rix.msg.standard.String",  // Python import path for RIX type
  "converter": "StringConverter",       // Converter class name
  "verified": true,                     // Field compatibility verified?
  "phase": 1                            // Implementation phase (1, 2, or 3)
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ros_package` | string | Yes | ROS package containing the message type |
| `ros_type` | string | Yes | ROS message type name (without package) |
| `ros_import` | string | Yes | Full Python import path for ROS message class |
| `rix_package` | string | Yes | RIX package containing the message type |
| `rix_type` | string | Yes | RIX message type name (without package) |
| `rix_import` | string | Yes | Full Python import path for RIX message class |
| `converter` | string | Yes | Name of converter class (must exist in converters/) |
| `verified` | boolean | Yes | Whether field structures have been verified compatible |
| `phase` | integer | Yes | Implementation phase (1=complete, 2=current, 3=future) |

### Import Path Format

**ROS Import Path:**
```
{ros_package}.msg.{ros_type}
```
Example: `std_msgs.msg.String` → imports `std_msgs.msg.String`

**RIX Import Path:**
```
rix.msg.{rix_package}.{rix_type}
```
Example: `rix.msg.standard.String` → imports `rix.msg.standard.String`

### Converter Naming Convention

**Format:** `{Type}Converter`

**Examples:**
- `StringConverter` for String types
- `PoseConverter` for Pose types
- `Float32Converter` for Float32 types

**Location:** Must exist in `rix_ros_bridge/converters/` directory

### Adding New Message Types

To add a new message type to the registry:

1. **Verify compatibility** using `verify_message_compatibility.py`
2. **Add entry** to `message_mappings` with all required fields
3. **Implement converter** in appropriate converters file
4. **Register converter** in `converters/__init__.py`
5. **Set verified** to `true` if field structures match
6. **Set phase** to current phase (2 for Phase 2)

### Example: Adding a New Type

```json
"geometry_msgs/PoseStamped": {
  "ros_package": "geometry_msgs",
  "ros_type": "PoseStamped",
  "ros_import": "geometry_msgs.msg.PoseStamped",
  "rix_package": "geometry",
  "rix_type": "PoseStamped",
  "rix_import": "rix.msg.geometry.PoseStamped",
  "converter": "PoseStampedConverter",
  "verified": false,  // Set to true after verification
  "phase": 2
}
```

### Validation

The configuration loader (`config_loader.py`) validates:
- ✓ All required fields are present
- ✓ Import paths are valid Python module paths
- ✓ Converter exists in registry
- ✓ Verified flag is boolean
- ✓ Phase is integer

### Current Statistics (Phase 2.0)

- **Total types:** 18
- **std_msgs:** 12 types
- **geometry_msgs:** 6 types
- **Verified:** 18/18 (100%)
- **Phase 1 complete:** 1 type (String)
- **Phase 2 target:** 18 types

---

## bridge_config.json

**Purpose:** User-facing configuration for bridge instances

**Location:** User-specified (e.g., `config/bridge_config.json`)

### Schema

```json
{
  "bridges": [
    {
      "name": "string_bridge",
      "ros_topic": "/chatter",
      "rix_topic": "/chatter_from_ros",
      "message_type": "std_msgs/String",
      "direction": "bidirectional",
      "queue_size": 10
    }
  ]
}
```

### Bridge Configuration Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for this bridge |
| `ros_topic` | string | Yes | ROS topic name |
| `rix_topic` | string | Yes | RIX topic name |
| `message_type` | string | Yes | Message type key (must exist in message_mappings.json) |
| `direction` | string | Yes | Bridge direction: "bidirectional", "ros_to_rix", "rix_to_ros" |
| `queue_size` | integer | No | Queue size for publishers/subscribers (default: 10) |

### Direction Values

- `"bidirectional"` - Messages flow both ROS→RIX and RIX→ROS
- `"ros_to_rix"` - Messages flow only ROS→RIX
- `"rix_to_ros"` - Messages flow only RIX→ROS

### Example Configuration

```json
{
  "bridges": [
    {
      "name": "string_bridge",
      "ros_topic": "/chatter",
      "rix_topic": "/chatter_from_ros",
      "message_type": "std_msgs/String",
      "direction": "ros_to_rix",
      "queue_size": 10
    },
    {
      "name": "pose_bridge",
      "ros_topic": "/robot_pose",
      "rix_topic": "/robot_pose",
      "message_type": "geometry_msgs/Pose",
      "direction": "bidirectional",
      "queue_size": 1
    }
  ]
}
```

### Validation Rules

The configuration loader validates:
- ✓ All required fields present
- ✓ `name` is unique across all bridges
- ✓ `message_type` exists in message_mappings.json
- ✓ `direction` is one of: "bidirectional", "ros_to_rix", "rix_to_ros"
- ✓ `queue_size` is positive integer (if specified)
- ✓ Topic names follow naming conventions (start with `/`)

### Example Configurations

Multiple example configurations are provided in `config/examples/`:

1. **simple_bridge.json** - Single direction String bridge
2. **bidirectional_bridge.json** - Two-way communication example
3. **multi_type_bridge.json** - Multiple types simultaneously
4. **robot_control_bridge.json** - Realistic robot control scenario

### Usage

```bash
# Use default config
ros2 run rix_ros_bridge bridge_node

# Use custom config
ros2 run rix_ros_bridge bridge_node --config path/to/config.json

# Use example config
ros2 run rix_ros_bridge bridge_node --config config/examples/simple_bridge.json
```

---

## Version History

- **v0.2.0** (2025-11-19): Initial Phase 2 schema with 18 verified types
- **v0.1.0** (2025-11-07): Phase 1 with hard-coded String type
