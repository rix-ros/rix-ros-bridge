"""
Test Configuration Loader

Unit tests for configuration loading and validation.
"""

import unittest
import json
import tempfile
from pathlib import Path

from rix_ros_bridge.config_loader import (
    load_bridge_config,
    validate_bridge_list,
    get_config_summary,
    save_bridge_config
)


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Path to actual config file
        self.config_path = Path(__file__).parent.parent / 'config' / 'bridge_config.json'
        
        # Valid test config
        self.valid_config = {
            "bridges": [
                {
                    "name": "test_bridge",
                    "message_type": "std_msgs/String",
                    "ros_topic": "/test",
                    "rix_topic": "/test"
                }
            ]
        }
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config = load_bridge_config(str(self.config_path))
        
        self.assertIsInstance(config, dict)
        self.assertIn('bridges', config)
        self.assertIsInstance(config['bridges'], list)
        
        # Should have at least 1 bridge
        self.assertGreater(len(config['bridges']), 0)
    
    def test_load_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            load_bridge_config("/nonexistent/config.json")
    
    def test_load_config_invalid_json(self):
        """Test error when config contains invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json")
            temp_path = f.name
        
        try:
            with self.assertRaises(json.JSONDecodeError):
                load_bridge_config(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_not_dict(self):
        """Test error when config is not a dictionary."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["not", "a", "dict"], f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                load_bridge_config(temp_path)
            self.assertIn("must be a JSON object", str(context.exception))
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_missing_bridges_key(self):
        """Test error when config is missing 'bridges' key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"other_key": "value"}, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                load_bridge_config(temp_path)
            self.assertIn("missing required 'bridges' key", str(context.exception))
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_bridges_not_list(self):
        """Test error when 'bridges' is not a list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"bridges": "not a list"}, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                load_bridge_config(temp_path)
            self.assertIn("'bridges' must be a list", str(context.exception))
        finally:
            Path(temp_path).unlink()
    
    def test_load_config_missing_required_fields(self):
        """Test error when bridge is missing required fields."""
        config = {
            "bridges": [
                {
                    "name": "incomplete_bridge",
                    "message_type": "std_msgs/String"
                    # Missing ros_topic and rix_topic
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError) as context:
                load_bridge_config(temp_path)
            self.assertIn("missing required fields", str(context.exception))
        finally:
            Path(temp_path).unlink()


class TestValidateBridgeList(unittest.TestCase):
    """Test bridge list validation."""
    
    def test_validate_valid_list(self):
        """Test validation passes for valid bridge list."""
        bridges = [
            {
                "name": "bridge1",
                "message_type": "std_msgs/String",
                "ros_topic": "/test1",
                "rix_topic": "/test1"
            },
            {
                "name": "bridge2",
                "message_type": "geometry_msgs/Pose",
                "ros_topic": "/test2",
                "rix_topic": "/test2"
            }
        ]
        
        result = validate_bridge_list(bridges)
        self.assertTrue(result)
    
    def test_validate_not_list(self):
        """Test error when bridges is not a list."""
        with self.assertRaises(ValueError) as context:
            validate_bridge_list("not a list")
        self.assertIn("must be a list", str(context.exception))
    
    def test_validate_empty_list(self):
        """Test error when bridges list is empty."""
        with self.assertRaises(ValueError) as context:
            validate_bridge_list([])
        self.assertIn("cannot be empty", str(context.exception))
    
    def test_validate_duplicate_names(self):
        """Test error when bridge names are duplicated."""
        bridges = [
            {
                "name": "duplicate_name",
                "message_type": "std_msgs/String",
                "ros_topic": "/test1",
                "rix_topic": "/test1"
            },
            {
                "name": "duplicate_name",
                "message_type": "geometry_msgs/Pose",
                "ros_topic": "/test2",
                "rix_topic": "/test2"
            }
        ]
        
        with self.assertRaises(ValueError) as context:
            validate_bridge_list(bridges)
        self.assertIn("Duplicate bridge names", str(context.exception))
    
    def test_validate_invalid_direction(self):
        """Test error when bridge has invalid direction."""
        bridges = [
            {
                "name": "bridge1",
                "message_type": "std_msgs/String",
                "ros_topic": "/test",
                "rix_topic": "/test",
                "direction": "invalid_direction"
            }
        ]
        
        with self.assertRaises(ValueError) as context:
            validate_bridge_list(bridges)
        self.assertIn("invalid direction", str(context.exception))
    
    def test_validate_missing_required_fields(self):
        """Test error when bridge is missing required fields."""
        bridges = [
            {
                "name": "incomplete_bridge",
                "message_type": "std_msgs/String"
                # Missing ros_topic and rix_topic
            }
        ]
        
        with self.assertRaises(ValueError) as context:
            validate_bridge_list(bridges)
        self.assertIn("missing required fields", str(context.exception))


class TestGetConfigSummary(unittest.TestCase):
    """Test configuration summary generation."""
    
    def test_summary_single_bridge(self):
        """Test summary for single bridge."""
        config = {
            "bridges": [
                {
                    "name": "test_bridge",
                    "message_type": "std_msgs/String",
                    "ros_topic": "/chatter",
                    "rix_topic": "/chatter",
                    "direction": "bidirectional"
                }
            ]
        }
        
        summary = get_config_summary(config)
        
        self.assertIn("Total bridges: 1", summary)
        self.assertIn("test_bridge", summary)
        self.assertIn("std_msgs/String", summary)
        self.assertIn("bidirectional", summary)
    
    def test_summary_multiple_bridges(self):
        """Test summary for multiple bridges."""
        config = {
            "bridges": [
                {
                    "name": "bridge1",
                    "message_type": "std_msgs/String",
                    "ros_topic": "/test1",
                    "rix_topic": "/test1",
                    "direction": "ros_to_rix"
                },
                {
                    "name": "bridge2",
                    "message_type": "geometry_msgs/Pose",
                    "ros_topic": "/test2",
                    "rix_topic": "/test2",
                    "direction": "rix_to_ros"
                }
            ]
        }
        
        summary = get_config_summary(config)
        
        self.assertIn("Total bridges: 2", summary)
        self.assertIn("bridge1", summary)
        self.assertIn("bridge2", summary)


class TestSaveBridgeConfig(unittest.TestCase):
    """Test configuration saving."""
    
    def test_save_valid_config(self):
        """Test saving a valid configuration."""
        config = {
            "bridges": [
                {
                    "name": "test_bridge",
                    "message_type": "std_msgs/String",
                    "ros_topic": "/test",
                    "rix_topic": "/test"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.json"
            save_bridge_config(config, str(output_path))
            
            # Verify file was created
            self.assertTrue(output_path.exists())
            
            # Verify content is valid JSON
            with open(output_path, 'r') as f:
                loaded_config = json.load(f)
            
            self.assertEqual(loaded_config, config)
    
    def test_save_invalid_config(self):
        """Test error when saving invalid configuration."""
        config = {
            "bridges": [
                {
                    "name": "incomplete_bridge"
                    # Missing required fields
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test_config.json"
            
            with self.assertRaises(ValueError):
                save_bridge_config(config, str(output_path))
    
    def test_save_creates_directories(self):
        """Test that save creates parent directories."""
        config = {
            "bridges": [
                {
                    "name": "test_bridge",
                    "message_type": "std_msgs/String",
                    "ros_topic": "/test",
                    "rix_topic": "/test"
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test_config.json"
            save_bridge_config(config, str(output_path))
            
            # Verify file was created in subdirectory
            self.assertTrue(output_path.exists())


if __name__ == '__main__':
    unittest.main()
