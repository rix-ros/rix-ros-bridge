"""
geometry_msgs Converters

Message converters for geometry_msgs package.
These types have nested structures (Point, Quaternion, Vector3, etc.)
"""

# ROS imports
from geometry_msgs.msg import (
    Point as RosPoint,
    Pose as RosPose,
    Quaternion as RosQuaternion,
    Vector3 as RosVector3,
    Twist as RosTwist,
    Transform as RosTransform,
)

# RIX imports
from rix.msg.geometry import (
    Point as RixPoint,
    Pose as RixPose,
    Quaternion as RixQuaternion,
    Vector3 as RixVector3,
    Twist as RixTwist,
    Transform as RixTransform,
)


class PointConverter:
    """Converter for geometry_msgs/Point <-> rix.msg.geometry.Point"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Point to RIX Point."""
        rix_msg = RixPoint()
        rix_msg.x = ros_msg.x
        rix_msg.y = ros_msg.y
        rix_msg.z = ros_msg.z
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Point to ROS Point."""
        ros_msg = RosPoint()
        ros_msg.x = rix_msg.x
        ros_msg.y = rix_msg.y
        ros_msg.z = rix_msg.z
        return ros_msg


class QuaternionConverter:
    """Converter for geometry_msgs/Quaternion <-> rix.msg.geometry.Quaternion"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Quaternion to RIX Quaternion."""
        rix_msg = RixQuaternion()
        rix_msg.x = ros_msg.x
        rix_msg.y = ros_msg.y
        rix_msg.z = ros_msg.z
        rix_msg.w = ros_msg.w
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Quaternion to ROS Quaternion."""
        ros_msg = RosQuaternion()
        ros_msg.x = rix_msg.x
        ros_msg.y = rix_msg.y
        ros_msg.z = rix_msg.z
        ros_msg.w = rix_msg.w
        return ros_msg


class Vector3Converter:
    """Converter for geometry_msgs/Vector3 <-> rix.msg.geometry.Vector3"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Vector3 to RIX Vector3."""
        rix_msg = RixVector3()
        rix_msg.x = ros_msg.x
        rix_msg.y = ros_msg.y
        rix_msg.z = ros_msg.z
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Vector3 to ROS Vector3."""
        ros_msg = RosVector3()
        ros_msg.x = rix_msg.x
        ros_msg.y = rix_msg.y
        ros_msg.z = rix_msg.z
        return ros_msg


class PoseConverter:
    """Converter for geometry_msgs/Pose <-> rix.msg.geometry.Pose"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """
        Convert ROS Pose to RIX Pose.
        
        Pose contains:
        - position: Point (x, y, z)
        - orientation: Quaternion (x, y, z, w)
        """
        rix_msg = RixPose()
        
        # Convert position (Point)
        rix_msg.position = PointConverter.ros_to_rix(ros_msg.position)
        
        # Convert orientation (Quaternion)
        rix_msg.orientation = QuaternionConverter.ros_to_rix(ros_msg.orientation)
        
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """
        Convert RIX Pose to ROS Pose.
        
        Pose contains:
        - position: Point (x, y, z)
        - orientation: Quaternion (x, y, z, w)
        """
        ros_msg = RosPose()
        
        # Convert position (Point)
        ros_msg.position = PointConverter.rix_to_ros(rix_msg.position)
        
        # Convert orientation (Quaternion)
        ros_msg.orientation = QuaternionConverter.rix_to_ros(rix_msg.orientation)
        
        return ros_msg


class TwistConverter:
    """Converter for geometry_msgs/Twist <-> rix.msg.geometry.Twist"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """
        Convert ROS Twist to RIX Twist.
        
        Twist contains:
        - linear: Vector3 (x, y, z velocities)
        - angular: Vector3 (x, y, z angular velocities)
        """
        rix_msg = RixTwist()
        
        # Convert linear velocity
        rix_msg.linear = Vector3Converter.ros_to_rix(ros_msg.linear)
        
        # Convert angular velocity
        rix_msg.angular = Vector3Converter.ros_to_rix(ros_msg.angular)
        
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """
        Convert RIX Twist to ROS Twist.
        
        Twist contains:
        - linear: Vector3 (x, y, z velocities)
        - angular: Vector3 (x, y, z angular velocities)
        """
        ros_msg = RosTwist()
        
        # Convert linear velocity
        ros_msg.linear = Vector3Converter.rix_to_ros(rix_msg.linear)
        
        # Convert angular velocity
        ros_msg.angular = Vector3Converter.rix_to_ros(rix_msg.angular)
        
        return ros_msg


class TransformConverter:
    """Converter for geometry_msgs/Transform <-> rix.msg.geometry.Transform"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """
        Convert ROS Transform to RIX Transform.
        
        Transform contains:
        - translation: Vector3 (x, y, z)
        - rotation: Quaternion (x, y, z, w)
        """
        rix_msg = RixTransform()
        
        # Convert translation (Vector3)
        rix_msg.translation = Vector3Converter.ros_to_rix(ros_msg.translation)
        
        # Convert rotation (Quaternion)
        rix_msg.rotation = QuaternionConverter.ros_to_rix(ros_msg.rotation)
        
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """
        Convert RIX Transform to ROS Transform.
        
        Transform contains:
        - translation: Vector3 (x, y, z)
        - rotation: Quaternion (x, y, z, w)
        """
        ros_msg = RosTransform()
        
        # Convert translation (Vector3)
        ros_msg.translation = Vector3Converter.rix_to_ros(rix_msg.translation)
        
        # Convert rotation (Quaternion)
        ros_msg.rotation = QuaternionConverter.rix_to_ros(rix_msg.rotation)
        
        return ros_msg
