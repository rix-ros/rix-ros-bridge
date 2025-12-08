"""
Test Message Converters

Unit tests for message conversion functions.
Tests all 18 converters (12 std_msgs + 6 geometry_msgs).
"""

import unittest

# ROS imports
from std_msgs.msg import (
    String as RosString,
    Int32 as RosInt32,
    Int64 as RosInt64,
    Int8 as RosInt8,
    Int16 as RosInt16,
    Float32 as RosFloat32,
    Float64 as RosFloat64,
    Bool as RosBool,
    UInt8 as RosUInt8,
    UInt16 as RosUInt16,
    UInt32 as RosUInt32,
    UInt64 as RosUInt64,
)
from geometry_msgs.msg import (
    Point as RosPoint,
    Pose as RosPose,
    Quaternion as RosQuaternion,
    Vector3 as RosVector3,
    Twist as RosTwist,
    Transform as RosTransform,
)

# RIX imports
from rix.msg.standard import (
    String as RixString,
    Int32 as RixInt32,
    Int64 as RixInt64,
    Int8 as RixInt8,
    Int16 as RixInt16,
    Float as RixFloat,
    Double as RixDouble,
    Bool as RixBool,
    UInt8 as RixUInt8,
    UInt16 as RixUInt16,
    UInt32 as RixUInt32,
    UInt64 as RixUInt64,
)
from rix.msg.geometry import (
    Point as RixPoint,
    Pose as RixPose,
    Quaternion as RixQuaternion,
    Vector3 as RixVector3,
    Twist as RixTwist,
    Transform as RixTransform,
)

# Converter imports
from rix_ros_bridge.converters.std_msgs import (
    StringConverter,
    Int32Converter,
    Int64Converter,
    Int8Converter,
    Int16Converter,
    Float32Converter,
    Float64Converter,
    BoolConverter,
    UInt8Converter,
    UInt16Converter,
    UInt32Converter,
    UInt64Converter,
)
from rix_ros_bridge.converters.geometry_msgs import (
    PointConverter,
    QuaternionConverter,
    Vector3Converter,
    PoseConverter,
    TwistConverter,
    TransformConverter,
)


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


class TestInt32Converter(unittest.TestCase):
    """Test Int32 message converter."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosInt32()
        ros_msg.data = 42
        rix_msg = Int32Converter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixInt32)
        self.assertEqual(rix_msg.data, 42)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixInt32()
        rix_msg.data = -123
        ros_msg = Int32Converter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosInt32)
        self.assertEqual(ros_msg.data, -123)
    
    def test_roundtrip_conversion(self):
        original_ros = RosInt32()
        original_ros.data = 999
        rix_msg = Int32Converter.ros_to_rix(original_ros)
        final_ros = Int32Converter.rix_to_ros(rix_msg)
        self.assertEqual(original_ros.data, final_ros.data)


class TestFloat32Converter(unittest.TestCase):
    """Test Float32 message converter."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosFloat32()
        ros_msg.data = 3.14159
        rix_msg = Float32Converter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixFloat)
        self.assertAlmostEqual(rix_msg.data, 3.14159, places=5)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixFloat()
        rix_msg.data = -2.71828
        ros_msg = Float32Converter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosFloat32)
        self.assertAlmostEqual(ros_msg.data, -2.71828, places=5)
    
    def test_roundtrip_conversion(self):
        original_ros = RosFloat32()
        original_ros.data = 1.41421
        rix_msg = Float32Converter.ros_to_rix(original_ros)
        final_ros = Float32Converter.rix_to_ros(rix_msg)
        self.assertAlmostEqual(original_ros.data, final_ros.data, places=5)


class TestBoolConverter(unittest.TestCase):
    """Test Bool message converter."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosBool()
        ros_msg.data = True
        rix_msg = BoolConverter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixBool)
        self.assertEqual(rix_msg.data, True)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixBool()
        rix_msg.data = False
        ros_msg = BoolConverter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosBool)
        self.assertEqual(ros_msg.data, False)
    
    def test_roundtrip_conversion(self):
        original_ros = RosBool()
        original_ros.data = True
        rix_msg = BoolConverter.ros_to_rix(original_ros)
        final_ros = BoolConverter.rix_to_ros(rix_msg)
        self.assertEqual(original_ros.data, final_ros.data)


class TestPointConverter(unittest.TestCase):
    """Test Point message converter."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosPoint()
        ros_msg.x = 1.0
        ros_msg.y = 2.0
        ros_msg.z = 3.0
        rix_msg = PointConverter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixPoint)
        self.assertEqual(rix_msg.x, 1.0)
        self.assertEqual(rix_msg.y, 2.0)
        self.assertEqual(rix_msg.z, 3.0)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixPoint()
        rix_msg.x = -1.5
        rix_msg.y = 2.5
        rix_msg.z = -3.5
        ros_msg = PointConverter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosPoint)
        self.assertEqual(ros_msg.x, -1.5)
        self.assertEqual(ros_msg.y, 2.5)
        self.assertEqual(ros_msg.z, -3.5)
    
    def test_roundtrip_conversion(self):
        original_ros = RosPoint()
        original_ros.x = 10.0
        original_ros.y = 20.0
        original_ros.z = 30.0
        rix_msg = PointConverter.ros_to_rix(original_ros)
        final_ros = PointConverter.rix_to_ros(rix_msg)
        self.assertEqual(original_ros.x, final_ros.x)
        self.assertEqual(original_ros.y, final_ros.y)
        self.assertEqual(original_ros.z, final_ros.z)


class TestQuaternionConverter(unittest.TestCase):
    """Test Quaternion message converter."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosQuaternion()
        ros_msg.x = 0.0
        ros_msg.y = 0.0
        ros_msg.z = 0.0
        ros_msg.w = 1.0
        rix_msg = QuaternionConverter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixQuaternion)
        self.assertEqual(rix_msg.x, 0.0)
        self.assertEqual(rix_msg.y, 0.0)
        self.assertEqual(rix_msg.z, 0.0)
        self.assertEqual(rix_msg.w, 1.0)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixQuaternion()
        rix_msg.x = 0.5
        rix_msg.y = 0.5
        rix_msg.z = 0.5
        rix_msg.w = 0.5
        ros_msg = QuaternionConverter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosQuaternion)
        self.assertEqual(ros_msg.x, 0.5)
        self.assertEqual(ros_msg.y, 0.5)
        self.assertEqual(ros_msg.z, 0.5)
        self.assertEqual(ros_msg.w, 0.5)
    
    def test_roundtrip_conversion(self):
        original_ros = RosQuaternion()
        original_ros.x = 0.1
        original_ros.y = 0.2
        original_ros.z = 0.3
        original_ros.w = 0.9
        rix_msg = QuaternionConverter.ros_to_rix(original_ros)
        final_ros = QuaternionConverter.rix_to_ros(rix_msg)
        self.assertAlmostEqual(original_ros.x, final_ros.x)
        self.assertAlmostEqual(original_ros.y, final_ros.y)
        self.assertAlmostEqual(original_ros.z, final_ros.z)
        self.assertAlmostEqual(original_ros.w, final_ros.w)


class TestPoseConverter(unittest.TestCase):
    """Test Pose message converter (nested structure)."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosPose()
        ros_msg.position.x = 1.0
        ros_msg.position.y = 2.0
        ros_msg.position.z = 3.0
        ros_msg.orientation.x = 0.0
        ros_msg.orientation.y = 0.0
        ros_msg.orientation.z = 0.0
        ros_msg.orientation.w = 1.0
        
        rix_msg = PoseConverter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixPose)
        self.assertEqual(rix_msg.position.x, 1.0)
        self.assertEqual(rix_msg.position.y, 2.0)
        self.assertEqual(rix_msg.position.z, 3.0)
        self.assertEqual(rix_msg.orientation.w, 1.0)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixPose()
        rix_msg.position.x = 5.0
        rix_msg.position.y = 6.0
        rix_msg.position.z = 7.0
        rix_msg.orientation.x = 0.5
        rix_msg.orientation.y = 0.5
        rix_msg.orientation.z = 0.5
        rix_msg.orientation.w = 0.5
        
        ros_msg = PoseConverter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosPose)
        self.assertEqual(ros_msg.position.x, 5.0)
        self.assertEqual(ros_msg.position.y, 6.0)
        self.assertEqual(ros_msg.position.z, 7.0)
        self.assertEqual(ros_msg.orientation.x, 0.5)
    
    def test_roundtrip_conversion(self):
        original_ros = RosPose()
        original_ros.position.x = 1.0
        original_ros.position.y = 2.0
        original_ros.position.z = 3.0
        original_ros.orientation.w = 1.0
        
        rix_msg = PoseConverter.ros_to_rix(original_ros)
        final_ros = PoseConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(original_ros.position.x, final_ros.position.x)
        self.assertEqual(original_ros.position.y, final_ros.position.y)
        self.assertEqual(original_ros.position.z, final_ros.position.z)
        self.assertEqual(original_ros.orientation.w, final_ros.orientation.w)


class TestTwistConverter(unittest.TestCase):
    """Test Twist message converter (nested structure)."""
    
    def test_ros_to_rix_conversion(self):
        ros_msg = RosTwist()
        ros_msg.linear.x = 1.0
        ros_msg.linear.y = 0.0
        ros_msg.linear.z = 0.0
        ros_msg.angular.x = 0.0
        ros_msg.angular.y = 0.0
        ros_msg.angular.z = 0.5
        
        rix_msg = TwistConverter.ros_to_rix(ros_msg)
        self.assertIsInstance(rix_msg, RixTwist)
        self.assertEqual(rix_msg.linear.x, 1.0)
        self.assertEqual(rix_msg.angular.z, 0.5)
    
    def test_rix_to_ros_conversion(self):
        rix_msg = RixTwist()
        rix_msg.linear.x = 2.0
        rix_msg.linear.y = 0.0
        rix_msg.linear.z = 0.0
        rix_msg.angular.x = 0.0
        rix_msg.angular.y = 0.0
        rix_msg.angular.z = 1.0
        
        ros_msg = TwistConverter.rix_to_ros(rix_msg)
        self.assertIsInstance(ros_msg, RosTwist)
        self.assertEqual(ros_msg.linear.x, 2.0)
        self.assertEqual(ros_msg.angular.z, 1.0)
    
    def test_roundtrip_conversion(self):
        original_ros = RosTwist()
        original_ros.linear.x = 1.5
        original_ros.angular.z = 0.75
        
        rix_msg = TwistConverter.ros_to_rix(original_ros)
        final_ros = TwistConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(original_ros.linear.x, final_ros.linear.x)
        self.assertEqual(original_ros.angular.z, final_ros.angular.z)


if __name__ == '__main__':
    unittest.main()
