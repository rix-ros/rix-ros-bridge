"""
std_msgs Converters

Message converters for std_msgs package (String, Header, etc.)
"""

from std_msgs.msg import String as RosString
from rix.msg.standard import String as RixString


class StringConverter:
    """Converter for std_msgs/String <-> rix.msg.standard.String"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """
        Convert ROS String to RIX String.
        
        Args:
            ros_msg: std_msgs.msg.String
            
        Returns:
            rix.msg.standard.String
        """
        rix_msg = RixString()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """
        Convert RIX String to ROS String.
        
        Args:
            rix_msg: rix.msg.standard.String
            
        Returns:
            std_msgs.msg.String
        """
        ros_msg = RosString()
        ros_msg.data = rix_msg.data
        return ros_msg
