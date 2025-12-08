"""
Converters for all Stamped geometry message types
Uses composition of Header and base type converters
"""

from geometry_msgs.msg import (
    PointStamped as ROSPointStamped,
    QuaternionStamped as ROSQuaternionStamped,
    Vector3Stamped as ROSVector3Stamped,
    TransformStamped as ROSTransformStamped,
    TwistStamped as ROSTwistStamped,
)
from rix.msg.geometry import (
    PointStamped as RIXPointStamped,
    QuaternionStamped as RIXQuaternionStamped,
    Vector3Stamped as RIXVector3Stamped,
    TransformStamped as RIXTransformStamped,
    TwistStamped as RIXTwistStamped,
)
from .header_converter import HeaderConverter
from .geometry_msgs import (
    PointConverter,
    QuaternionConverter,
    Vector3Converter,
    TransformConverter,
    TwistConverter,
)


class PointStampedConverter:
    """Converts between ROS geometry_msgs/PointStamped and RIX PointStamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSPointStamped) -> RIXPointStamped:
        rix_msg = RIXPointStamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.point = PointConverter.ros_to_rix(ros_msg.point)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXPointStamped) -> ROSPointStamped:
        ros_msg = ROSPointStamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.point = PointConverter.rix_to_ros(rix_msg.point)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        return ROSPointStamped
    
    @staticmethod
    def get_rix_type() -> type:
        return RIXPointStamped


class QuaternionStampedConverter:
    """Converts between ROS geometry_msgs/QuaternionStamped and RIX QuaternionStamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSQuaternionStamped) -> RIXQuaternionStamped:
        rix_msg = RIXQuaternionStamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.quaternion = QuaternionConverter.ros_to_rix(ros_msg.quaternion)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXQuaternionStamped) -> ROSQuaternionStamped:
        ros_msg = ROSQuaternionStamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.quaternion = QuaternionConverter.rix_to_ros(rix_msg.quaternion)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        return ROSQuaternionStamped
    
    @staticmethod
    def get_rix_type() -> type:
        return RIXQuaternionStamped


class Vector3StampedConverter:
    """Converts between ROS geometry_msgs/Vector3Stamped and RIX Vector3Stamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSVector3Stamped) -> RIXVector3Stamped:
        rix_msg = RIXVector3Stamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.vector = Vector3Converter.ros_to_rix(ros_msg.vector)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXVector3Stamped) -> ROSVector3Stamped:
        ros_msg = ROSVector3Stamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.vector = Vector3Converter.rix_to_ros(rix_msg.vector)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        return ROSVector3Stamped
    
    @staticmethod
    def get_rix_type() -> type:
        return RIXVector3Stamped


class TransformStampedConverter:
    """Converts between ROS geometry_msgs/TransformStamped and RIX TransformStamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSTransformStamped) -> RIXTransformStamped:
        rix_msg = RIXTransformStamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.child_frame_id = ros_msg.child_frame_id
        rix_msg.transform = TransformConverter.ros_to_rix(ros_msg.transform)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXTransformStamped) -> ROSTransformStamped:
        ros_msg = ROSTransformStamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.child_frame_id = str(rix_msg.child_frame_id)
        ros_msg.transform = TransformConverter.rix_to_ros(rix_msg.transform)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        return ROSTransformStamped
    
    @staticmethod
    def get_rix_type() -> type:
        return RIXTransformStamped


class TwistStampedConverter:
    """Converts between ROS geometry_msgs/TwistStamped and RIX TwistStamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSTwistStamped) -> RIXTwistStamped:
        rix_msg = RIXTwistStamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.twist = TwistConverter.ros_to_rix(ros_msg.twist)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXTwistStamped) -> ROSTwistStamped:
        ros_msg = ROSTwistStamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.twist = TwistConverter.rix_to_ros(rix_msg.twist)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        return ROSTwistStamped
    
    @staticmethod
    def get_rix_type() -> type:
        return RIXTwistStamped
