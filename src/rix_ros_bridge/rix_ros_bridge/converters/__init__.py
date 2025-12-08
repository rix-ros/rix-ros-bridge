"""
Message Converters Package

Contains message conversion functions between ROS2 and RIX message types.
Provides a registry for dynamic converter lookup.
"""

# Import all converters
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


# Converter Registry - Maps converter name to converter class
CONVERTER_REGISTRY = {
    # std_msgs converters (14 - added Header, ColorRGBA)
    "StringConverter": StringConverter,
    "Int32Converter": Int32Converter,
    "Int64Converter": Int64Converter,
    "Int8Converter": Int8Converter,
    "Int16Converter": Int16Converter,
    "Float32Converter": Float32Converter,
    "Float64Converter": Float64Converter,
    "BoolConverter": BoolConverter,
    "UInt8Converter": UInt8Converter,
    "UInt16Converter": UInt16Converter,
    "UInt32Converter": UInt32Converter,
    "UInt64Converter": UInt64Converter,
    "HeaderConverter": HeaderConverter,
    "ColorRGBAConverter": ColorRGBAConverter,
    
    # geometry_msgs converters (12 - 6 base + 6 stamped)
    "PointConverter": PointConverter,
    "QuaternionConverter": QuaternionConverter,
    "Vector3Converter": Vector3Converter,
    "PoseConverter": PoseConverter,
    "TwistConverter": TwistConverter,
    "TransformConverter": TransformConverter,
    "PoseStampedConverter": PoseStampedConverter,
    "PointStampedConverter": PointStampedConverter,
    "QuaternionStampedConverter": QuaternionStampedConverter,
    "Vector3StampedConverter": Vector3StampedConverter,
    "TransformStampedConverter": TransformStampedConverter,
    "TwistStampedConverter": TwistStampedConverter,
}


def get_converter(converter_name):
    """
    Get converter class by name.
    
    Args:
        converter_name: Name of the converter (e.g., "StringConverter")
        
    Returns:
        Converter class
        
    Raises:
        KeyError: If converter name is not found in registry
    """
    if converter_name not in CONVERTER_REGISTRY:
        available = ", ".join(sorted(CONVERTER_REGISTRY.keys()))
        raise KeyError(
            f"Converter '{converter_name}' not found in registry. "
            f"Available converters: {available}"
        )
    return CONVERTER_REGISTRY[converter_name]


def list_converters():
    """
    Get list of all available converter names.
    
    Returns:
        List of converter names (sorted)
    """
    return sorted(CONVERTER_REGISTRY.keys())
