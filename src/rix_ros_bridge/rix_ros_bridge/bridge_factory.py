"""
Bridge Factory

Creates bridge handles dynamically based on configuration.
Loads message types and converters from message mappings.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from rix_ros_bridge.message_loader import MessageTypeLoader
from rix_ros_bridge.bridge_handle_ros_to_rix import BridgeHandleRosToRix
from rix_ros_bridge.bridge_handle_rix_to_ros import BridgeHandleRixToRos


class BridgeFactory:
    """
    Factory for creating bridge handles from configuration.
    
    Loads message type mappings and creates bridge handles dynamically
    based on bridge configuration dictionaries.
    """
    
    def __init__(self, mappings_path: str):
        """
        Initialize the bridge factory.
        
        Args:
            mappings_path: Path to message_mappings.json file
        
        Raises:
            FileNotFoundError: If mappings file doesn't exist
            json.JSONDecodeError: If mappings file is invalid JSON
            KeyError: If mappings file is missing required fields
        """
        self.mappings_path = Path(mappings_path)
        self.loader = MessageTypeLoader()
        self.mappings = self._load_mappings()
    
    def _load_mappings(self) -> Dict[str, Any]:
        """
        Load message type mappings from JSON file.
        
        Returns:
            Dictionary of message type mappings
        
        Raises:
            FileNotFoundError: If mappings file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            KeyError: If required 'message_mappings' key is missing
        """
        if not self.mappings_path.exists():
            raise FileNotFoundError(
                f"Message mappings file not found: {self.mappings_path}"
            )
        
        with open(self.mappings_path, 'r') as f:
            data = json.load(f)
        
        if 'message_mappings' not in data:
            raise KeyError(
                "Invalid mappings file: missing 'message_mappings' key"
            )
        
        return data['message_mappings']
    
    def validate_config(self, bridge_config: Dict[str, Any]) -> bool:
        """
        Validate a bridge configuration dictionary.
        
        Args:
            bridge_config: Bridge configuration dict
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        # Check required fields
        required_fields = ['name', 'message_type', 'ros_topic', 'rix_topic']
        missing_fields = [f for f in required_fields if f not in bridge_config]
        
        if missing_fields:
            raise ValueError(
                f"Bridge config missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate message type exists in mappings
        message_type = bridge_config['message_type']
        if message_type not in self.mappings:
            available = ', '.join(sorted(self.mappings.keys()))
            raise ValueError(
                f"Unknown message type '{message_type}'. "
                f"Available types: {available}"
            )
        
        # Validate direction if specified
        if 'direction' in bridge_config:
            direction = bridge_config['direction']
            valid_directions = ['bidirectional', 'ros_to_rix', 'rix_to_ros']
            if direction not in valid_directions:
                raise ValueError(
                    f"Invalid direction '{direction}'. "
                    f"Must be one of: {', '.join(valid_directions)}"
                )
        
        return True
    
    def create_bridge(
        self, 
        bridge_config: Dict[str, Any], 
        ros_node, 
        rix_node
    ) -> List[Any]:
        """
        Create bridge handle(s) from configuration.
        
        Args:
            bridge_config: Bridge configuration dictionary with fields:
                - name: Bridge name
                - message_type: Message type key (e.g., "std_msgs/String")
                - ros_topic: ROS topic name
                - rix_topic: RIX topic name
                - direction: (optional) "bidirectional", "ros_to_rix", or "rix_to_ros"
                             Default: "bidirectional"
            ros_node: ROS2 node instance
            rix_node: RIX node instance
        
        Returns:
            List of bridge handles (1 or 2 depending on direction)
        
        Raises:
            ValueError: If configuration is invalid
            ImportError: If message types or converter cannot be loaded
        
        Example:
            >>> factory = BridgeFactory("config/message_mappings.json")
            >>> config = {
            ...     "name": "string_bridge",
            ...     "message_type": "std_msgs/String",
            ...     "ros_topic": "/chatter",
            ...     "rix_topic": "/chatter",
            ...     "direction": "bidirectional"
            ... }
            >>> handles = factory.create_bridge(config, ros_node, rix_node)
        """
        # Validate configuration
        self.validate_config(bridge_config)
        
        # Extract configuration
        name = bridge_config['name']
        message_type = bridge_config['message_type']
        ros_topic = bridge_config['ros_topic']
        rix_topic = bridge_config['rix_topic']
        direction = bridge_config.get('direction', 'bidirectional')
        
        # Get mapping for this message type
        mapping = self.mappings[message_type]
        
        # Load message classes and converter
        ros_class = self.loader.load_ros_class(mapping['ros_import'])
        rix_class = self.loader.load_rix_class(mapping['rix_import'])
        converter = self.loader.load_converter(mapping['converter'])
        
        # Validate converter
        self.loader.validate_converter(converter)
        
        # Create bridge handle(s) based on direction
        handles = []
        
        if direction in ['bidirectional', 'ros_to_rix']:
            # ROS → RIX bridge
            handle_ros_to_rix = BridgeHandleRosToRix(
                ros_node=ros_node,
                rix_node=rix_node,
                ros_topic=ros_topic,
                rix_topic=rix_topic,
                ros_msg_class=ros_class,
                rix_msg_class=rix_class,
                converter=converter
            )
            handles.append(handle_ros_to_rix)
        
        if direction in ['bidirectional', 'rix_to_ros']:
            # RIX → ROS bridge
            handle_rix_to_ros = BridgeHandleRixToRos(
                ros_node=ros_node,
                rix_node=rix_node,
                ros_topic=ros_topic,
                rix_topic=rix_topic,
                ros_msg_class=ros_class,
                rix_msg_class=rix_class,
                converter=converter
            )
            handles.append(handle_rix_to_ros)
        
        return handles
    
    def list_supported_types(self) -> List[str]:
        """
        Get list of all supported message types.
        
        Returns:
            Sorted list of message type keys
        
        Example:
            >>> factory = BridgeFactory("config/message_mappings.json")
            >>> types = factory.list_supported_types()
            >>> print(types)
            ['geometry_msgs/Point', 'geometry_msgs/Pose', ...]
        """
        return sorted(self.mappings.keys())
    
    def get_mapping_info(self, message_type: str) -> Dict[str, Any]:
        """
        Get detailed mapping information for a message type.
        
        Args:
            message_type: Message type key (e.g., "std_msgs/String")
        
        Returns:
            Mapping dictionary with ros_import, rix_import, converter, etc.
        
        Raises:
            KeyError: If message type not found
        
        Example:
            >>> factory = BridgeFactory("config/message_mappings.json")
            >>> info = factory.get_mapping_info("std_msgs/String")
            >>> print(info['converter'])
            'StringConverter'
        """
        if message_type not in self.mappings:
            available = ', '.join(sorted(self.mappings.keys()))
            raise KeyError(
                f"Unknown message type '{message_type}'. "
                f"Available types: {available}"
            )
        
        return self.mappings[message_type]
    
    def create_multiple_bridges(
        self,
        bridge_configs: List[Dict[str, Any]],
        ros_node,
        rix_node
    ) -> List[Any]:
        """
        Create multiple bridges from a list of configurations.
        
        Args:
            bridge_configs: List of bridge configuration dicts
            ros_node: ROS2 node instance
            rix_node: RIX node instance
        
        Returns:
            List of all created bridge handles
        
        Raises:
            ValueError: If any configuration is invalid
            ImportError: If any message type or converter cannot be loaded
        
        Example:
            >>> factory = BridgeFactory("config/message_mappings.json")
            >>> configs = [
            ...     {"name": "bridge1", "message_type": "std_msgs/String", ...},
            ...     {"name": "bridge2", "message_type": "geometry_msgs/Pose", ...}
            ... ]
            >>> handles = factory.create_multiple_bridges(configs, ros_node, rix_node)
        """
        all_handles = []
        
        for config in bridge_configs:
            try:
                handles = self.create_bridge(config, ros_node, rix_node)
                all_handles.extend(handles)
            except Exception as e:
                # Add context about which bridge failed
                bridge_name = config.get('name', 'unknown')
                raise ValueError(
                    f"Failed to create bridge '{bridge_name}': {e}"
                ) from e
        
        return all_handles
