"""
Test Message Type Loader

Unit tests for dynamic message type loading.
"""

import unittest
from rix_ros_bridge.message_loader import MessageTypeLoader, load_message_types

# Import expected types for validation
from std_msgs.msg import String as RosString
from geometry_msgs.msg import Point as RosPoint
from rix.msg.standard import String as RixString
from rix.msg.geometry import Point as RixPoint
from rix_ros_bridge.converters.std_msgs import StringConverter
from rix_ros_bridge.converters.geometry_msgs import PointConverter


class TestMessageTypeLoader(unittest.TestCase):
    """Test MessageTypeLoader class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = MessageTypeLoader()
    
    def test_load_ros_string_class(self):
        """Test loading ROS String class."""
        ros_class = self.loader.load_ros_class("std_msgs.msg.String")
        
        # Verify it's the correct class
        self.assertEqual(ros_class, RosString)
        
        # Verify we can instantiate it
        msg = ros_class()
        self.assertIsInstance(msg, RosString)
    
    def test_load_ros_point_class(self):
        """Test loading ROS Point class."""
        ros_class = self.loader.load_ros_class("geometry_msgs.msg.Point")
        
        self.assertEqual(ros_class, RosPoint)
        msg = ros_class()
        self.assertIsInstance(msg, RosPoint)
    
    def test_load_rix_string_class(self):
        """Test loading RIX String class."""
        rix_class = self.loader.load_rix_class("rix.msg.standard.String")
        
        # Verify it's the correct class
        self.assertEqual(rix_class, RixString)
        
        # Verify we can instantiate it
        msg = rix_class()
        self.assertIsInstance(msg, RixString)
    
    def test_load_rix_point_class(self):
        """Test loading RIX Point class."""
        rix_class = self.loader.load_rix_class("rix.msg.geometry.Point")
        
        self.assertEqual(rix_class, RixPoint)
        msg = rix_class()
        self.assertIsInstance(msg, RixPoint)
    
    def test_load_string_converter(self):
        """Test loading StringConverter."""
        converter = self.loader.load_converter("StringConverter")
        
        # Verify it's the correct class
        self.assertEqual(converter, StringConverter)
        
        # Verify it has required methods
        self.assertTrue(hasattr(converter, 'ros_to_rix'))
        self.assertTrue(hasattr(converter, 'rix_to_ros'))
    
    def test_load_point_converter(self):
        """Test loading PointConverter."""
        converter = self.loader.load_converter("PointConverter")
        
        self.assertEqual(converter, PointConverter)
        self.assertTrue(hasattr(converter, 'ros_to_rix'))
        self.assertTrue(hasattr(converter, 'rix_to_ros'))
    
    def test_invalid_ros_import_path(self):
        """Test error handling for invalid ROS import path."""
        with self.assertRaises(ValueError):
            self.loader.load_ros_class("")
        
        with self.assertRaises(ValueError):
            self.loader.load_ros_class("InvalidPath")
    
    def test_nonexistent_ros_module(self):
        """Test error handling for non-existent ROS module."""
        with self.assertRaises(ImportError):
            self.loader.load_ros_class("fake_package.msg.FakeMessage")
    
    def test_nonexistent_ros_class(self):
        """Test error handling for non-existent ROS class."""
        with self.assertRaises(ImportError):
            self.loader.load_ros_class("std_msgs.msg.NonExistentClass")
    
    def test_invalid_rix_import_path(self):
        """Test error handling for invalid RIX import path."""
        with self.assertRaises(ValueError):
            self.loader.load_rix_class("")
        
        with self.assertRaises(ValueError):
            self.loader.load_rix_class("InvalidPath")
    
    def test_nonexistent_converter(self):
        """Test error handling for non-existent converter."""
        with self.assertRaises(KeyError):
            self.loader.load_converter("NonExistentConverter")
    
    def test_empty_converter_name(self):
        """Test error handling for empty converter name."""
        with self.assertRaises(ValueError):
            self.loader.load_converter("")
    
    def test_validate_converter(self):
        """Test converter validation."""
        converter = StringConverter
        result = self.loader.validate_converter(converter)
        self.assertTrue(result)
    
    def test_validate_invalid_converter(self):
        """Test validation fails for invalid converter."""
        class InvalidConverter:
            # Missing ros_to_rix and rix_to_ros methods
            pass
        
        with self.assertRaises(AttributeError):
            self.loader.validate_converter(InvalidConverter)
    
    def test_list_available_converters(self):
        """Test listing all available converters."""
        converters = self.loader.list_available_converters()
        
        # Should be a sorted list
        self.assertIsInstance(converters, list)
        self.assertEqual(converters, sorted(converters))
        
        # Should contain our known converters
        self.assertIn("StringConverter", converters)
        self.assertIn("PointConverter", converters)
        self.assertIn("PoseConverter", converters)
        
        # Should have all 18 converters
        self.assertEqual(len(converters), 18)


class TestLoadMessageTypesFunction(unittest.TestCase):
    """Test the convenience load_message_types function."""
    
    def test_load_string_message_types(self):
        """Test loading all components for String bridge."""
        ros_class, rix_class, converter = load_message_types(
            "std_msgs.msg.String",
            "rix.msg.standard.String",
            "StringConverter"
        )
        
        # Verify correct classes returned
        self.assertEqual(ros_class, RosString)
        self.assertEqual(rix_class, RixString)
        self.assertEqual(converter, StringConverter)
        
        # Verify converter works
        ros_msg = ros_class()
        ros_msg.data = "test"
        rix_msg = converter.ros_to_rix(ros_msg)
        self.assertEqual(rix_msg.data, "test")
    
    def test_load_point_message_types(self):
        """Test loading all components for Point bridge."""
        ros_class, rix_class, converter = load_message_types(
            "geometry_msgs.msg.Point",
            "rix.msg.geometry.Point",
            "PointConverter"
        )
        
        self.assertEqual(ros_class, RosPoint)
        self.assertEqual(rix_class, RixPoint)
        self.assertEqual(converter, PointConverter)
        
        # Verify converter works
        ros_msg = ros_class()
        ros_msg.x = 1.0
        ros_msg.y = 2.0
        ros_msg.z = 3.0
        rix_msg = converter.ros_to_rix(ros_msg)
        self.assertEqual(rix_msg.x, 1.0)
        self.assertEqual(rix_msg.y, 2.0)
        self.assertEqual(rix_msg.z, 3.0)


if __name__ == '__main__':
    unittest.main()
