"""
Message Converters Package

Contains message conversion functions between ROS2 and RIX message types.
"""


class MessageConverter:
    """Base converter interface."""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """
        Convert ROS message to RIX message.
        
        Args:
            ros_msg: ROS2 message instance
            
        Returns:
            RIX message instance
        """
        raise NotImplementedError("Subclass must implement ros_to_rix")
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """
        Convert RIX message to ROS message.
        
        Args:
            rix_msg: RIX message instance
            
        Returns:
            ROS2 message instance
        """
        raise NotImplementedError("Subclass must implement rix_to_ros")
