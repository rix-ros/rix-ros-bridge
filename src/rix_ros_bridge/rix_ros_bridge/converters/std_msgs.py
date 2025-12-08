"""
std_msgs Converters

Message converters for std_msgs package.
All std_msgs types have a simple 'data' field structure.
"""

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


class StringConverter:
    """Converter for std_msgs/String <-> rix.msg.standard.String"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS String to RIX String."""
        rix_msg = RixString()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX String to ROS String."""
        ros_msg = RosString()
        ros_msg.data = rix_msg.data
        return ros_msg


class Int32Converter:
    """Converter for std_msgs/Int32 <-> rix.msg.standard.Int32"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Int32 to RIX Int32."""
        rix_msg = RixInt32()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Int32 to ROS Int32."""
        ros_msg = RosInt32()
        ros_msg.data = rix_msg.data
        return ros_msg


class Int64Converter:
    """Converter for std_msgs/Int64 <-> rix.msg.standard.Int64"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Int64 to RIX Int64."""
        rix_msg = RixInt64()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Int64 to ROS Int64."""
        ros_msg = RosInt64()
        ros_msg.data = rix_msg.data
        return ros_msg


class Int8Converter:
    """Converter for std_msgs/Int8 <-> rix.msg.standard.Int8"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Int8 to RIX Int8."""
        rix_msg = RixInt8()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Int8 to ROS Int8."""
        ros_msg = RosInt8()
        ros_msg.data = rix_msg.data
        return ros_msg


class Int16Converter:
    """Converter for std_msgs/Int16 <-> rix.msg.standard.Int16"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Int16 to RIX Int16."""
        rix_msg = RixInt16()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Int16 to ROS Int16."""
        ros_msg = RosInt16()
        ros_msg.data = rix_msg.data
        return ros_msg


class Float32Converter:
    """Converter for std_msgs/Float32 <-> rix.msg.standard.Float"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Float32 to RIX Float."""
        rix_msg = RixFloat()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Float to ROS Float32."""
        ros_msg = RosFloat32()
        ros_msg.data = rix_msg.data
        return ros_msg


class Float64Converter:
    """Converter for std_msgs/Float64 <-> rix.msg.standard.Double"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Float64 to RIX Double."""
        rix_msg = RixDouble()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Double to ROS Float64."""
        ros_msg = RosFloat64()
        ros_msg.data = rix_msg.data
        return ros_msg


class BoolConverter:
    """Converter for std_msgs/Bool <-> rix.msg.standard.Bool"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS Bool to RIX Bool."""
        rix_msg = RixBool()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX Bool to ROS Bool."""
        ros_msg = RosBool()
        ros_msg.data = rix_msg.data
        return ros_msg


class UInt8Converter:
    """Converter for std_msgs/UInt8 <-> rix.msg.standard.UInt8"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS UInt8 to RIX UInt8."""
        rix_msg = RixUInt8()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX UInt8 to ROS UInt8."""
        ros_msg = RosUInt8()
        ros_msg.data = rix_msg.data
        return ros_msg


class UInt16Converter:
    """Converter for std_msgs/UInt16 <-> rix.msg.standard.UInt16"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS UInt16 to RIX UInt16."""
        rix_msg = RixUInt16()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX UInt16 to ROS UInt16."""
        ros_msg = RosUInt16()
        ros_msg.data = rix_msg.data
        return ros_msg


class UInt32Converter:
    """Converter for std_msgs/UInt32 <-> rix.msg.standard.UInt32"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS UInt32 to RIX UInt32."""
        rix_msg = RixUInt32()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX UInt32 to ROS UInt32."""
        ros_msg = RosUInt32()
        ros_msg.data = rix_msg.data
        return ros_msg


class UInt64Converter:
    """Converter for std_msgs/UInt64 <-> rix.msg.standard.UInt64"""
    
    @staticmethod
    def ros_to_rix(ros_msg):
        """Convert ROS UInt64 to RIX UInt64."""
        rix_msg = RixUInt64()
        rix_msg.data = ros_msg.data
        return rix_msg
    
    @staticmethod
    def rix_to_ros(rix_msg):
        """Convert RIX UInt64 to ROS UInt64."""
        ros_msg = RosUInt64()
        ros_msg.data = rix_msg.data
        return ros_msg
