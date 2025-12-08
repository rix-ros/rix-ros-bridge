"""
Converter for geometry_msgs/PoseStamped <-> rix.msg.geometry.PoseStamped
"""

from geometry_msgs.msg import PoseStamped as ROSPoseStamped
from rix.msg.geometry import PoseStamped as RIXPoseStamped
from .header_converter import HeaderConverter
from .geometry_msgs import PoseConverter


class PoseStampedConverter:
    """Converts between ROS geometry_msgs/PoseStamped and RIX PoseStamped"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSPoseStamped) -> RIXPoseStamped:
        """
        Convert ROS PoseStamped to RIX PoseStamped
        
        Args:
            ros_msg: ROS geometry_msgs/PoseStamped message
            
        Returns:
            RIX PoseStamped message
        """
        rix_msg = RIXPoseStamped()
        rix_msg.header = HeaderConverter.ros_to_rix(ros_msg.header)
        rix_msg.pose = PoseConverter.ros_to_rix(ros_msg.pose)
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXPoseStamped) -> ROSPoseStamped:
        """
        Convert RIX PoseStamped to ROS PoseStamped
        
        Args:
            rix_msg: RIX PoseStamped message
            
        Returns:
            ROS geometry_msgs/PoseStamped message
        """
        ros_msg = ROSPoseStamped()
        ros_msg.header = HeaderConverter.rix_to_ros(rix_msg.header)
        ros_msg.pose = PoseConverter.rix_to_ros(rix_msg.pose)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        """Get the ROS message type"""
        return ROSPoseStamped
    
    @staticmethod
    def get_rix_type() -> type:
        """Get the RIX message type"""
        return RIXPoseStamped
