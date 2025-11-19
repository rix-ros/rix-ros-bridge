"""
Test Message Converters

Unit tests for message conversion functions.
"""

import unittest
from std_msgs.msg import String as RosString
from rix.msg.standard import String as RixString
from rix_ros_bridge.converters.std_msgs import StringConverter


class TestStringConverter(unittest.TestCase):
    """Test String message converter."""
    
    def test_ros_to_rix_conversion(self):
        """Test ROS to RIX String conversion."""
        # Create a ROS String message
        ros_msg = RosString()
        ros_msg.data = "Hello from ROS"
        
        # Convert to RIX
        rix_msg = StringConverter.ros_to_rix(ros_msg)
        
        # Verify the conversion
        self.assertIsInstance(rix_msg, RixString)
        self.assertEqual(rix_msg.data, "Hello from ROS")
    
    def test_rix_to_ros_conversion(self):
        """Test RIX to ROS String conversion."""
        # Create a RIX String message
        rix_msg = RixString()
        rix_msg.data = "Hello from RIX"
        
        # Convert to ROS
        ros_msg = StringConverter.rix_to_ros(rix_msg)
        
        # Verify the conversion
        self.assertIsInstance(ros_msg, RosString)
        self.assertEqual(ros_msg.data, "Hello from RIX")
    
    def test_roundtrip_conversion(self):
        """Test round-trip conversion preserves data."""
        # Create original ROS message
        original_ros = RosString()
        original_ros.data = "Round-trip test data"
        
        # Convert ROS -> RIX -> ROS
        rix_msg = StringConverter.ros_to_rix(original_ros)
        final_ros = StringConverter.rix_to_ros(rix_msg)
        
        # Verify data is preserved
        self.assertEqual(original_ros.data, final_ros.data)
        
        # Test reverse direction: RIX -> ROS -> RIX
        original_rix = RixString()
        original_rix.data = "Reverse round-trip test"
        
        ros_msg = StringConverter.rix_to_ros(original_rix)
        final_rix = StringConverter.ros_to_rix(ros_msg)
        
        # Verify data is preserved
        self.assertEqual(original_rix.data, final_rix.data)


if __name__ == '__main__':
    unittest.main()
