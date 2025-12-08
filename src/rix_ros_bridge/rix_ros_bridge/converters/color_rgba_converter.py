"""
Converter for std_msgs/ColorRGBA <-> rix.msg.standard.Color
"""

from std_msgs.msg import ColorRGBA as ROSColorRGBA
from rix.msg.standard import Color as RIXColor


class ColorRGBAConverter:
    """Converts between ROS std_msgs/ColorRGBA and RIX Color"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSColorRGBA) -> RIXColor:
        """
        Convert ROS ColorRGBA to RIX Color
        
        Args:
            ros_msg: ROS std_msgs/ColorRGBA message
            
        Returns:
            RIX Color message
        """
        rix_msg = RIXColor()
        rix_msg.r = ros_msg.r
        rix_msg.g = ros_msg.g
        rix_msg.b = ros_msg.b
        rix_msg.a = ros_msg.a
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXColor) -> ROSColorRGBA:
        """
        Convert RIX Color to ROS ColorRGBA
        
        Args:
            rix_msg: RIX Color message
            
        Returns:
            ROS std_msgs/ColorRGBA message
        """
        ros_msg = ROSColorRGBA()
        ros_msg.r = float(rix_msg.r)
        ros_msg.g = float(rix_msg.g)
        ros_msg.b = float(rix_msg.b)
        ros_msg.a = float(rix_msg.a)
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        """Get the ROS message type"""
        return ROSColorRGBA
    
    @staticmethod
    def get_rix_type() -> type:
        """Get the RIX message type"""
        return RIXColor
