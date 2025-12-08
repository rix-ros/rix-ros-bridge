"""
Unit tests for P2 message type converters (Header, ColorRGBA, Stamped types)
"""

import unittest
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')

from std_msgs.msg import Header as ROSHeader, ColorRGBA as ROSColorRGBA
from geometry_msgs.msg import (
    PoseStamped as ROSPoseStamped,
    PointStamped as ROSPointStamped,
    QuaternionStamped as ROSQuaternionStamped,
    Vector3Stamped as ROSVector3Stamped,
    TransformStamped as ROSTransformStamped,
    TwistStamped as ROSTwistStamped,
    Pose, Point, Quaternion, Vector3, Transform, Twist,
)
from rix.msg.standard import Header as RIXHeader, Color as RIXColor
from rix.msg.geometry import (
    PoseStamped as RIXPoseStamped,
    PointStamped as RIXPointStamped,
    QuaternionStamped as RIXQuaternionStamped,
    Vector3Stamped as RIXVector3Stamped,
    TransformStamped as RIXTransformStamped,
    TwistStamped as RIXTwistStamped,
)

from rix_ros_bridge.converters.header_converter import HeaderConverter
from rix_ros_bridge.converters.color_rgba_converter import ColorRGBAConverter
from rix_ros_bridge.converters.pose_stamped_converter import PoseStampedConverter
from rix_ros_bridge.converters.stamped_converters import (
    PointStampedConverter,
    QuaternionStampedConverter,
    Vector3StampedConverter,
    TransformStampedConverter,
    TwistStampedConverter,
)


class TestHeaderConverter(unittest.TestCase):
    """Test Header converter"""
    
    def test_ros_to_rix(self):
        """Test ROS Header to RIX Header conversion"""
        ros_msg = ROSHeader()
        ros_msg.stamp.sec = 123
        ros_msg.stamp.nanosec = 456789000
        ros_msg.frame_id = "base_link"
        
        rix_msg = HeaderConverter.ros_to_rix(ros_msg)
        
        # Check timestamp conversion
        expected_stamp = 123 + 456789000 * 1e-9
        self.assertAlmostEqual(rix_msg.stamp, expected_stamp, places=6)
        self.assertEqual(rix_msg.frame_id, "base_link")
    
    def test_rix_to_ros(self):
        """Test RIX Header to ROS Header conversion"""
        rix_msg = RIXHeader()
        rix_msg.stamp = 123.456789
        rix_msg.frame_id = "map"
        
        ros_msg = HeaderConverter.rix_to_ros(rix_msg)
        
        # Check timestamp conversion
        self.assertEqual(ros_msg.stamp.sec, 123)
        self.assertEqual(ros_msg.stamp.nanosec, 456789000)
        self.assertEqual(ros_msg.frame_id, "map")
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original = ROSHeader()
        original.stamp.sec = 100
        original.stamp.nanosec = 500000000
        original.frame_id = "odom"
        
        rix_msg = HeaderConverter.ros_to_rix(original)
        result = HeaderConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(result.stamp.sec, original.stamp.sec)
        self.assertEqual(result.stamp.nanosec, original.stamp.nanosec)
        self.assertEqual(result.frame_id, original.frame_id)


class TestColorRGBAConverter(unittest.TestCase):
    """Test ColorRGBA converter"""
    
    def test_ros_to_rix(self):
        """Test ROS ColorRGBA to RIX Color conversion"""
        ros_msg = ROSColorRGBA()
        ros_msg.r = 1.0
        ros_msg.g = 0.5
        ros_msg.b = 0.25
        ros_msg.a = 0.8
        
        rix_msg = ColorRGBAConverter.ros_to_rix(ros_msg)
        
        self.assertEqual(rix_msg.r, 1.0)
        self.assertEqual(rix_msg.g, 0.5)
        self.assertEqual(rix_msg.b, 0.25)
        self.assertEqual(rix_msg.a, 0.8)
    
    def test_rix_to_ros(self):
        """Test RIX Color to ROS ColorRGBA conversion"""
        rix_msg = RIXColor()
        rix_msg.r = 0.1
        rix_msg.g = 0.2
        rix_msg.b = 0.3
        rix_msg.a = 1.0
        
        ros_msg = ColorRGBAConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(ros_msg.r, 0.1)
        self.assertEqual(ros_msg.g, 0.2)
        self.assertEqual(ros_msg.b, 0.3)
        self.assertEqual(ros_msg.a, 1.0)
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original = ROSColorRGBA()
        original.r = 0.7
        original.g = 0.6
        original.b = 0.5
        original.a = 0.9
        
        rix_msg = ColorRGBAConverter.ros_to_rix(original)
        result = ColorRGBAConverter.rix_to_ros(rix_msg)
        
        self.assertAlmostEqual(result.r, original.r, places=6)
        self.assertAlmostEqual(result.g, original.g, places=6)
        self.assertAlmostEqual(result.b, original.b, places=6)
        self.assertAlmostEqual(result.a, original.a, places=6)


class TestPoseStampedConverter(unittest.TestCase):
    """Test PoseStamped converter"""
    
    def test_ros_to_rix(self):
        """Test ROS PoseStamped to RIX PoseStamped conversion"""
        ros_msg = ROSPoseStamped()
        ros_msg.header.stamp.sec = 10
        ros_msg.header.stamp.nanosec = 500000000
        ros_msg.header.frame_id = "map"
        ros_msg.pose.position.x = 1.0
        ros_msg.pose.position.y = 2.0
        ros_msg.pose.position.z = 3.0
        ros_msg.pose.orientation.w = 1.0
        
        rix_msg = PoseStampedConverter.ros_to_rix(ros_msg)
        
        self.assertAlmostEqual(rix_msg.header.stamp, 10.5, places=6)
        self.assertEqual(rix_msg.header.frame_id, "map")
        self.assertEqual(rix_msg.pose.position.x, 1.0)
        self.assertEqual(rix_msg.pose.position.y, 2.0)
        self.assertEqual(rix_msg.pose.position.z, 3.0)
        self.assertEqual(rix_msg.pose.orientation.w, 1.0)
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original = ROSPoseStamped()
        original.header.stamp.sec = 5
        original.header.stamp.nanosec = 250000000
        original.header.frame_id = "base_link"
        original.pose.position.x = 10.0
        original.pose.position.y = 20.0
        original.pose.position.z = 30.0
        original.pose.orientation.x = 0.0
        original.pose.orientation.y = 0.0
        original.pose.orientation.z = 0.0
        original.pose.orientation.w = 1.0
        
        rix_msg = PoseStampedConverter.ros_to_rix(original)
        result = PoseStampedConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(result.header.stamp.sec, original.header.stamp.sec)
        self.assertEqual(result.header.stamp.nanosec, original.header.stamp.nanosec)
        self.assertEqual(result.header.frame_id, original.header.frame_id)
        self.assertAlmostEqual(result.pose.position.x, original.pose.position.x, places=6)
        self.assertAlmostEqual(result.pose.position.y, original.pose.position.y, places=6)
        self.assertAlmostEqual(result.pose.position.z, original.pose.position.z, places=6)


class TestPointStampedConverter(unittest.TestCase):
    """Test PointStamped converter"""
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original = ROSPointStamped()
        original.header.stamp.sec = 1
        original.header.stamp.nanosec = 0
        original.header.frame_id = "sensor"
        original.point.x = 5.0
        original.point.y = 6.0
        original.point.z = 7.0
        
        rix_msg = PointStampedConverter.ros_to_rix(original)
        result = PointStampedConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(result.header.frame_id, original.header.frame_id)
        self.assertAlmostEqual(result.point.x, original.point.x, places=6)
        self.assertAlmostEqual(result.point.y, original.point.y, places=6)
        self.assertAlmostEqual(result.point.z, original.point.z, places=6)


class TestTransformStampedConverter(unittest.TestCase):
    """Test TransformStamped converter"""
    
    def test_ros_to_rix(self):
        """Test ROS TransformStamped to RIX TransformStamped conversion"""
        ros_msg = ROSTransformStamped()
        ros_msg.header.stamp.sec = 2
        ros_msg.header.frame_id = "world"
        ros_msg.child_frame_id = "robot"
        ros_msg.transform.translation.x = 1.0
        ros_msg.transform.translation.y = 2.0
        ros_msg.transform.translation.z = 3.0
        ros_msg.transform.rotation.w = 1.0
        
        rix_msg = TransformStampedConverter.ros_to_rix(ros_msg)
        
        self.assertEqual(rix_msg.header.frame_id, "world")
        self.assertEqual(rix_msg.child_frame_id, "robot")
        self.assertEqual(rix_msg.transform.translation.x, 1.0)
        self.assertEqual(rix_msg.transform.rotation.w, 1.0)


class TestTwistStampedConverter(unittest.TestCase):
    """Test TwistStamped converter"""
    
    def test_round_trip(self):
        """Test round-trip conversion"""
        original = ROSTwistStamped()
        original.header.stamp.sec = 3
        original.header.frame_id = "base"
        original.twist.linear.x = 1.5
        original.twist.linear.y = 0.0
        original.twist.angular.z = 0.5
        
        rix_msg = TwistStampedConverter.ros_to_rix(original)
        result = TwistStampedConverter.rix_to_ros(rix_msg)
        
        self.assertEqual(result.header.frame_id, original.header.frame_id)
        self.assertAlmostEqual(result.twist.linear.x, original.twist.linear.x, places=6)
        self.assertAlmostEqual(result.twist.angular.z, original.twist.angular.z, places=6)


if __name__ == '__main__':
    unittest.main()
