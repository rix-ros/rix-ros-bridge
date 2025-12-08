"""
Test Bridge Factory

Unit tests for BridgeFactory class.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from rix_ros_bridge.bridge_factory import BridgeFactory
from rix_ros_bridge.bridge_handle_ros_to_rix import BridgeHandleRosToRix
from rix_ros_bridge.bridge_handle_rix_to_ros import BridgeHandleRixToRos


class TestBridgeFactory(unittest.TestCase):
    """Test BridgeFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Path to the actual message_mappings.json file
        self.mappings_path = Path(__file__).parent.parent / 'config' / 'message_mappings.json'
        
        # Create factory instance
        self.factory = BridgeFactory(str(self.mappings_path))
        
        # Create mock nodes
        self.ros_node = Mock()
        self.ros_node.get_logger = Mock(return_value=Mock())
        self.rix_node = Mock()
    
    def test_factory_initialization(self):
        """Test factory initializes correctly."""
        self.assertIsNotNone(self.factory.mappings)
        self.assertIsInstance(self.factory.mappings, dict)
        
        # Should have 18 message types
        self.assertEqual(len(self.factory.mappings), 18)
    
    def test_load_mappings_file_not_found(self):
        """Test error when mappings file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            BridgeFactory("/nonexistent/path/mappings.json")
    
    def test_validate_config_valid(self):
        """Test validation passes for valid config."""
        config = {
            "name": "test_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/test",
            "rix_topic": "/test"
        }
        
        result = self.factory.validate_config(config)
        self.assertTrue(result)
    
    def test_validate_config_missing_fields(self):
        """Test validation fails when required fields are missing."""
        # Missing 'name'
        config = {
            "message_type": "std_msgs/String",
            "ros_topic": "/test",
            "rix_topic": "/test"
        }
        
        with self.assertRaises(ValueError) as context:
            self.factory.validate_config(config)
        
        self.assertIn("missing required fields", str(context.exception))
        self.assertIn("name", str(context.exception))
    
    def test_validate_config_invalid_message_type(self):
        """Test validation fails for unknown message type."""
        config = {
            "name": "test_bridge",
            "message_type": "fake_msgs/NonExistent",
            "ros_topic": "/test",
            "rix_topic": "/test"
        }
        
        with self.assertRaises(ValueError) as context:
            self.factory.validate_config(config)
        
        self.assertIn("Unknown message type", str(context.exception))
    
    def test_validate_config_invalid_direction(self):
        """Test validation fails for invalid direction."""
        config = {
            "name": "test_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/test",
            "rix_topic": "/test",
            "direction": "invalid_direction"
        }
        
        with self.assertRaises(ValueError) as context:
            self.factory.validate_config(config)
        
        self.assertIn("Invalid direction", str(context.exception))
    
    def test_create_bridge_bidirectional(self):
        """Test creating bidirectional bridge."""
        config = {
            "name": "string_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/chatter",
            "rix_topic": "/chatter",
            "direction": "bidirectional"
        }
        
        handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
        
        # Should create 2 handles (ROS→RIX and RIX→ROS)
        self.assertEqual(len(handles), 2)
        self.assertIsInstance(handles[0], BridgeHandleRosToRix)
        self.assertIsInstance(handles[1], BridgeHandleRixToRos)
    
    def test_create_bridge_ros_to_rix_only(self):
        """Test creating ROS→RIX only bridge."""
        config = {
            "name": "string_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/chatter",
            "rix_topic": "/chatter",
            "direction": "ros_to_rix"
        }
        
        handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
        
        # Should create 1 handle (ROS→RIX only)
        self.assertEqual(len(handles), 1)
        self.assertIsInstance(handles[0], BridgeHandleRosToRix)
    
    def test_create_bridge_rix_to_ros_only(self):
        """Test creating RIX→ROS only bridge."""
        config = {
            "name": "string_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/chatter",
            "rix_topic": "/chatter",
            "direction": "rix_to_ros"
        }
        
        handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
        
        # Should create 1 handle (RIX→ROS only)
        self.assertEqual(len(handles), 1)
        self.assertIsInstance(handles[0], BridgeHandleRixToRos)
    
    def test_create_bridge_default_direction(self):
        """Test creating bridge with default direction (bidirectional)."""
        config = {
            "name": "string_bridge",
            "message_type": "std_msgs/String",
            "ros_topic": "/chatter",
            "rix_topic": "/chatter"
            # No direction specified - should default to bidirectional
        }
        
        handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
        
        # Should create 2 handles (default is bidirectional)
        self.assertEqual(len(handles), 2)
    
    def test_create_bridge_different_message_types(self):
        """Test creating bridges for different message types."""
        message_types = [
            "std_msgs/String",
            "std_msgs/Int32",
            "geometry_msgs/Point",
            "geometry_msgs/Pose"
        ]
        
        for msg_type in message_types:
            config = {
                "name": f"{msg_type.replace('/', '_')}_bridge",
                "message_type": msg_type,
                "ros_topic": "/test",
                "rix_topic": "/test"
            }
            
            handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
            self.assertEqual(len(handles), 2)  # Bidirectional by default
    
    def test_list_supported_types(self):
        """Test listing all supported message types."""
        types = self.factory.list_supported_types()
        
        # Should be a sorted list
        self.assertIsInstance(types, list)
        self.assertEqual(types, sorted(types))
        
        # Should contain our known types
        self.assertIn("std_msgs/String", types)
        self.assertIn("geometry_msgs/Point", types)
        self.assertIn("geometry_msgs/Pose", types)
        
        # Should have 18 types
        self.assertEqual(len(types), 18)
    
    def test_get_mapping_info(self):
        """Test getting mapping info for a message type."""
        info = self.factory.get_mapping_info("std_msgs/String")
        
        # Should have required fields
        self.assertIn("ros_import", info)
        self.assertIn("rix_import", info)
        self.assertIn("converter", info)
        
        # Check values
        self.assertEqual(info["ros_import"], "std_msgs.msg.String")
        self.assertEqual(info["rix_import"], "rix.msg.standard.String")
        self.assertEqual(info["converter"], "StringConverter")
    
    def test_get_mapping_info_invalid_type(self):
        """Test error when getting info for invalid message type."""
        with self.assertRaises(KeyError):
            self.factory.get_mapping_info("fake_msgs/NonExistent")
    
    def test_create_multiple_bridges(self):
        """Test creating multiple bridges at once."""
        configs = [
            {
                "name": "string_bridge",
                "message_type": "std_msgs/String",
                "ros_topic": "/chatter",
                "rix_topic": "/chatter"
            },
            {
                "name": "pose_bridge",
                "message_type": "geometry_msgs/Pose",
                "ros_topic": "/robot_pose",
                "rix_topic": "/robot_pose",
                "direction": "ros_to_rix"
            }
        ]
        
        handles = self.factory.create_multiple_bridges(configs, self.ros_node, self.rix_node)
        
        # First bridge: bidirectional (2 handles)
        # Second bridge: ros_to_rix (1 handle)
        # Total: 3 handles
        self.assertEqual(len(handles), 3)
    
    def test_create_multiple_bridges_with_error(self):
        """Test error handling when one bridge config is invalid."""
        configs = [
            {
                "name": "valid_bridge",
                "message_type": "std_msgs/String",
                "ros_topic": "/test",
                "rix_topic": "/test"
            },
            {
                "name": "invalid_bridge",
                "message_type": "fake_msgs/Invalid",  # Invalid type
                "ros_topic": "/test",
                "rix_topic": "/test"
            }
        ]
        
        with self.assertRaises(ValueError) as context:
            self.factory.create_multiple_bridges(configs, self.ros_node, self.rix_node)
        
        # Error message should mention which bridge failed
        self.assertIn("invalid_bridge", str(context.exception))


class TestBridgeFactoryIntegration(unittest.TestCase):
    """Integration tests for BridgeFactory with real message types."""
    
    def setUp(self):
        """Set up test fixtures."""
        mappings_path = Path(__file__).parent.parent / 'config' / 'message_mappings.json'
        self.factory = BridgeFactory(str(mappings_path))
        
        # Create mock nodes
        self.ros_node = Mock()
        self.ros_node.get_logger = Mock(return_value=Mock())
        self.rix_node = Mock()
    
    def test_all_mapped_types_loadable(self):
        """Test that all message types in mappings can be loaded."""
        for message_type in self.factory.list_supported_types():
            config = {
                "name": f"test_{message_type.replace('/', '_')}",
                "message_type": message_type,
                "ros_topic": "/test",
                "rix_topic": "/test",
                "direction": "ros_to_rix"
            }
            
            # Should not raise any exceptions
            handles = self.factory.create_bridge(config, self.ros_node, self.rix_node)
            self.assertEqual(len(handles), 1)


if __name__ == '__main__':
    unittest.main()
