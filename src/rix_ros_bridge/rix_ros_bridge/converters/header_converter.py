"""
Converter for std_msgs/Header <-> rix.msg.standard.Header
"""

from std_msgs.msg import Header as ROSHeader
from rix.msg.standard import Header as RIXHeader


class HeaderConverter:
    """Converts between ROS std_msgs/Header and RIX Header"""
    
    @staticmethod
    def ros_to_rix(ros_msg: ROSHeader) -> RIXHeader:
        """
        Convert ROS Header to RIX Header
        
        Args:
            ros_msg: ROS std_msgs/Header message
            
        Returns:
            RIX Header message
        """
        rix_msg = RIXHeader()
        
        # Convert timestamp (ROS uses nanoseconds in stamp)
        rix_msg.stamp = ros_msg.stamp.sec + ros_msg.stamp.nanosec * 1e-9
        
        # Copy frame_id
        rix_msg.frame_id = ros_msg.frame_id
        
        # RIX Header may have seq field (ROS 2 removed it, but RIX might keep it)
        # We'll set it to 0 or increment manually if needed
        if hasattr(rix_msg, 'seq'):
            rix_msg.seq = 0
        
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg: RIXHeader) -> ROSHeader:
        """
        Convert RIX Header to ROS Header
        
        Args:
            rix_msg: RIX Header message
            
        Returns:
            ROS std_msgs/Header message
        """
        ros_msg = ROSHeader()
        
        # Convert timestamp (split float into sec and nanosec)
        ros_msg.stamp.sec = int(rix_msg.stamp)
        ros_msg.stamp.nanosec = int((rix_msg.stamp - int(rix_msg.stamp)) * 1e9)
        
        # Copy frame_id
        ros_msg.frame_id = str(rix_msg.frame_id)
        
        return ros_msg
    
    @staticmethod
    def get_ros_type() -> type:
        """Get the ROS message type"""
        return ROSHeader
    
    @staticmethod
    def get_rix_type() -> type:
        """Get the RIX message type"""
        return RIXHeader
