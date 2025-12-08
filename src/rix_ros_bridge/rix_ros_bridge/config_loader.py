"""
Configuration Loader

Loads and validates bridge configuration from JSON files.
"""

import json
from pathlib import Path
from typing import Dict, List, Any


def load_bridge_config(config_path: str) -> Dict[str, Any]:
    """
    Load bridge configuration from JSON file.
    
    Args:
        config_path: Path to bridge configuration JSON file
    
    Returns:
        Dictionary containing configuration data with 'bridges' list
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
        ValueError: If config structure is invalid
    
    Example:
        >>> config = load_bridge_config("config/bridge_config.json")
        >>> bridges = config['bridges']
        >>> for bridge in bridges:
        ...     print(bridge['name'])
    """
    config_path = Path(config_path)
    
    # Check if file exists
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}"
        )
    
    # Load JSON
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in configuration file: {e.msg}",
            e.doc,
            e.pos
        )
    
    # Validate structure
    if not isinstance(config_data, dict):
        raise ValueError(
            "Configuration must be a JSON object (dictionary)"
        )
    
    if 'bridges' not in config_data:
        raise ValueError(
            "Configuration missing required 'bridges' key"
        )
    
    if not isinstance(config_data['bridges'], list):
        raise ValueError(
            "'bridges' must be a list"
        )
    
    # Validate each bridge config has required fields
    required_fields = ['name', 'message_type', 'ros_topic', 'rix_topic']
    
    for i, bridge in enumerate(config_data['bridges']):
        if not isinstance(bridge, dict):
            raise ValueError(
                f"Bridge at index {i} is not a dictionary"
            )
        
        missing_fields = [f for f in required_fields if f not in bridge]
        if missing_fields:
            bridge_name = bridge.get('name', f'bridge_{i}')
            raise ValueError(
                f"Bridge '{bridge_name}' missing required fields: "
                f"{', '.join(missing_fields)}"
            )
    
    return config_data


def validate_bridge_list(bridges: List[Dict[str, Any]]) -> bool:
    """
    Validate a list of bridge configurations.
    
    Args:
        bridges: List of bridge configuration dictionaries
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If validation fails
    
    Example:
        >>> bridges = [
        ...     {"name": "bridge1", "message_type": "std_msgs/String", ...}
        ... ]
        >>> validate_bridge_list(bridges)
        True
    """
    if not isinstance(bridges, list):
        raise ValueError("bridges must be a list")
    
    if len(bridges) == 0:
        raise ValueError("bridges list cannot be empty")
    
    # Check for duplicate bridge names
    names = [b.get('name', '') for b in bridges]
    duplicates = [name for name in names if names.count(name) > 1]
    
    if duplicates:
        unique_duplicates = list(set(duplicates))
        raise ValueError(
            f"Duplicate bridge names found: {', '.join(unique_duplicates)}"
        )
    
    # Validate each bridge
    required_fields = ['name', 'message_type', 'ros_topic', 'rix_topic']
    
    for i, bridge in enumerate(bridges):
        if not isinstance(bridge, dict):
            raise ValueError(
                f"Bridge at index {i} is not a dictionary"
            )
        
        missing_fields = [f for f in required_fields if f not in bridge]
        if missing_fields:
            bridge_name = bridge.get('name', f'bridge_{i}')
            raise ValueError(
                f"Bridge '{bridge_name}' missing required fields: "
                f"{', '.join(missing_fields)}"
            )
        
        # Validate direction if specified
        if 'direction' in bridge:
            direction = bridge['direction']
            valid_directions = ['bidirectional', 'ros_to_rix', 'rix_to_ros']
            if direction not in valid_directions:
                raise ValueError(
                    f"Bridge '{bridge['name']}' has invalid direction '{direction}'. "
                    f"Must be one of: {', '.join(valid_directions)}"
                )
    
    return True


def get_config_summary(config: Dict[str, Any]) -> str:
    """
    Get a human-readable summary of the configuration.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Formatted summary string
    
    Example:
        >>> config = load_bridge_config("config/bridge_config.json")
        >>> print(get_config_summary(config))
        Configuration Summary
        =====================
        Total bridges: 2
        ...
    """
    bridges = config.get('bridges', [])
    
    summary_lines = [
        "Configuration Summary",
        "=" * 50,
        f"Total bridges: {len(bridges)}",
        ""
    ]
    
    # Count by direction
    direction_counts = {}
    for bridge in bridges:
        direction = bridge.get('direction', 'bidirectional')
        direction_counts[direction] = direction_counts.get(direction, 0) + 1
    
    summary_lines.append("Bridges by direction:")
    for direction, count in sorted(direction_counts.items()):
        summary_lines.append(f"  {direction}: {count}")
    
    summary_lines.append("")
    summary_lines.append("Bridge details:")
    
    for bridge in bridges:
        name = bridge['name']
        msg_type = bridge['message_type']
        direction = bridge.get('direction', 'bidirectional')
        ros_topic = bridge['ros_topic']
        rix_topic = bridge['rix_topic']
        
        summary_lines.append(f"  - {name}")
        summary_lines.append(f"    Type: {msg_type}")
        summary_lines.append(f"    Direction: {direction}")
        summary_lines.append(f"    ROS topic: {ros_topic}")
        summary_lines.append(f"    RIX topic: {rix_topic}")
    
    return "\n".join(summary_lines)


def save_bridge_config(config: Dict[str, Any], output_path: str) -> None:
    """
    Save bridge configuration to JSON file.
    
    Args:
        config: Configuration dictionary
        output_path: Path to save JSON file
    
    Raises:
        ValueError: If config structure is invalid
    
    Example:
        >>> config = {
        ...     "bridges": [
        ...         {"name": "bridge1", "message_type": "std_msgs/String", ...}
        ...     ]
        ... }
        >>> save_bridge_config(config, "output/my_config.json")
    """
    # Validate before saving
    if 'bridges' not in config:
        raise ValueError("Configuration missing required 'bridges' key")
    
    validate_bridge_list(config['bridges'])
    
    output_path = Path(output_path)
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON with pretty formatting
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
