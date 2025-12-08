"""
Message Type Loader

Dynamically loads ROS2 and RIX message classes and converters
based on import paths specified in configuration files.
"""

import importlib
from typing import Type, Any

from rix_ros_bridge.converters import get_converter, CONVERTER_REGISTRY


class MessageTypeLoader:
    """
    Loads message classes and converters dynamically.
    
    Enables configuration-driven bridge creation by loading
    message types and converters from string import paths.
    """
    
    @staticmethod
    def load_ros_class(import_path: str) -> Type[Any]:
        """
        Load a ROS2 message class dynamically.
        
        Args:
            import_path: Full import path (e.g., "std_msgs.msg.String")
        
        Returns:
            ROS message class
        
        Raises:
            ImportError: If module or class cannot be found
            ValueError: If import path format is invalid
        
        Example:
            >>> loader = MessageTypeLoader()
            >>> String = loader.load_ros_class("std_msgs.msg.String")
            >>> msg = String()
        """
        if not import_path:
            raise ValueError("Import path cannot be empty")
        
        # Split module path from class name
        # Example: "std_msgs.msg.String" -> module="std_msgs.msg", class="String"
        parts = import_path.rsplit('.', 1)
        
        if len(parts) != 2:
            raise ValueError(
                f"Invalid import path format: '{import_path}'. "
                f"Expected format: 'module.path.ClassName'"
            )
        
        module_path, class_name = parts
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            raise ImportError(
                f"Cannot import ROS module '{module_path}'. "
                f"Make sure ROS2 is sourced and the package is installed. "
                f"Original error: {e}"
            )
        
        # Get the class from the module
        if not hasattr(module, class_name):
            available = [name for name in dir(module) if not name.startswith('_')]
            raise ImportError(
                f"Class '{class_name}' not found in module '{module_path}'. "
                f"Available classes: {', '.join(available)}"
            )
        
        message_class = getattr(module, class_name)
        return message_class
    
    @staticmethod
    def load_rix_class(import_path: str) -> Type[Any]:
        """
        Load a RIX message class dynamically.
        
        Args:
            import_path: Full import path (e.g., "rix.msg.standard.String")
        
        Returns:
            RIX message class
        
        Raises:
            ImportError: If module or class cannot be found
            ValueError: If import path format is invalid
        
        Example:
            >>> loader = MessageTypeLoader()
            >>> String = loader.load_rix_class("rix.msg.standard.String")
            >>> msg = String()
        """
        if not import_path:
            raise ValueError("Import path cannot be empty")
        
        # Split module path from class name
        # Example: "rix.msg.standard.String" -> module="rix.msg.standard", class="String"
        parts = import_path.rsplit('.', 1)
        
        if len(parts) != 2:
            raise ValueError(
                f"Invalid import path format: '{import_path}'. "
                f"Expected format: 'module.path.ClassName'"
            )
        
        module_path, class_name = parts
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as e:
            raise ImportError(
                f"Cannot import RIX module '{module_path}'. "
                f"Make sure RIX is installed and PYTHONPATH is set correctly. "
                f"Original error: {e}"
            )
        
        # Get the class from the module
        if not hasattr(module, class_name):
            available = [name for name in dir(module) if not name.startswith('_')]
            raise ImportError(
                f"Class '{class_name}' not found in module '{module_path}'. "
                f"Available classes: {', '.join(available)}"
            )
        
        message_class = getattr(module, class_name)
        return message_class
    
    @staticmethod
    def load_converter(converter_name: str) -> Type[Any]:
        """
        Load a converter class from the registry.
        
        Args:
            converter_name: Name of the converter (e.g., "StringConverter")
        
        Returns:
            Converter class
        
        Raises:
            KeyError: If converter name is not found in registry
            ValueError: If converter name is empty
        
        Example:
            >>> loader = MessageTypeLoader()
            >>> StringConverter = loader.load_converter("StringConverter")
            >>> rix_msg = StringConverter.ros_to_rix(ros_msg)
        """
        if not converter_name:
            raise ValueError("Converter name cannot be empty")
        
        # Use the get_converter function from converters/__init__.py
        # It already has good error handling
        return get_converter(converter_name)
    
    @staticmethod
    def validate_converter(converter_class: Type[Any]) -> bool:
        """
        Validate that a converter class has required methods.
        
        Args:
            converter_class: Converter class to validate
        
        Returns:
            True if valid
        
        Raises:
            AttributeError: If required methods are missing
        """
        required_methods = ['ros_to_rix', 'rix_to_ros']
        
        for method in required_methods:
            if not hasattr(converter_class, method):
                raise AttributeError(
                    f"Converter '{converter_class.__name__}' is missing "
                    f"required method '{method}'"
                )
        
        return True
    
    @staticmethod
    def list_available_converters() -> list:
        """
        Get list of all available converter names.
        
        Returns:
            List of converter names (sorted)
        
        Example:
            >>> loader = MessageTypeLoader()
            >>> converters = loader.list_available_converters()
            >>> print(converters)
            ['BoolConverter', 'Float32Converter', ...]
        """
        return sorted(CONVERTER_REGISTRY.keys())


# Convenience functions for common operations
def load_message_types(ros_import: str, rix_import: str, converter_name: str):
    """
    Load all three components needed for a bridge.
    
    Args:
        ros_import: ROS message import path
        rix_import: RIX message import path
        converter_name: Converter class name
    
    Returns:
        Tuple of (ros_class, rix_class, converter_class)
    
    Example:
        >>> ros_cls, rix_cls, conv = load_message_types(
        ...     "std_msgs.msg.String",
        ...     "rix.msg.standard.String",
        ...     "StringConverter"
        ... )
    """
    loader = MessageTypeLoader()
    
    ros_class = loader.load_ros_class(ros_import)
    rix_class = loader.load_rix_class(rix_import)
    converter_class = loader.load_converter(converter_name)
    
    # Validate converter has required methods
    loader.validate_converter(converter_class)
    
    return ros_class, rix_class, converter_class
