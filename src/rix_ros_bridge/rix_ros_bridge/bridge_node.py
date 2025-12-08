#!/usr/bin/env python3
"""
RIX-ROS Bridge Node

Main bridge node that manages bidirectional message passing between ROS2 and RIX.
"""

import argparse
from pathlib import Path

import rclpy
from rclpy.node import Node as RosNode
from std_msgs.msg import String as RosString

import rix.core
from rix.msg.standard import String as RixString

from rix_ros_bridge.bridge_handle_ros_to_rix import BridgeHandleRosToRix
from rix_ros_bridge.bridge_handle_rix_to_ros import BridgeHandleRixToRos
from rix_ros_bridge.converters.std_msgs import StringConverter
from rix_ros_bridge.config_loader import load_bridge_config
from rix_ros_bridge.bridge_factory import BridgeFactory


class RixRosBridge(RosNode):
    """Main bridge node managing ROS2 and RIX communication."""
    
    def __init__(self):
        """
        Initialize the RIX-ROS bridge.
        
        Creates ROS and RIX nodes, then sets up bidirectional bridging
        for the /chatter topic using String messages.
        """
        # Initialize ROS node
        super().__init__('rix_ros_bridge')
        
        self.get_logger().info('Initializing RIX-ROS Bridge...')
        
        # Initialize RIX node
        self.rix_node = rix.core.Node('rix_ros_bridge')
        
        if not self.rix_node.ok():
            self.get_logger().error('Failed to initialize RIX node!')
            raise RuntimeError('RIX node initialization failed')
        
        self.get_logger().info('RIX node initialized successfully')
        
        # Create bridge handles for /chatter topic
        self._create_bridge_handles()
        
        self.get_logger().info('RIX-ROS Bridge initialization complete')
    
    def _create_bridge_handles(self):
        """
        Create and start bridge handles for hard-coded /chatter topic.
        
        Sets up bidirectional bridging with separate topic names to prevent echo-back:
        - ROS→RIX: Subscribe to ROS /chatter, publish to RIX /chatter_from_ros
        - RIX→ROS: Subscribe to RIX /chatter, publish to ROS /chatter_from_rix
        
        This prevents infinite loops where the bridge echoes its own messages.
        """
        self.get_logger().info('Creating bridge handles with separate topic names')
        
        # Create ROS→RIX handle
        # Subscribes to ROS /chatter, publishes to RIX /chatter_from_ros
        self.ros_to_rix_handle = BridgeHandleRosToRix(
            ros_node=self,
            rix_node=self.rix_node,
            ros_topic='/chatter',
            rix_topic='/chatter_from_ros',
            ros_msg_class=RosString,
            rix_msg_class=RixString,
            converter=StringConverter
        )
        
        # Create RIX→ROS handle
        # Subscribes to RIX /chatter, publishes to ROS /chatter_from_rix
        self.rix_to_ros_handle = BridgeHandleRixToRos(
            ros_node=self,
            rix_node=self.rix_node,
            rix_topic='/chatter',
            ros_topic='/chatter_from_rix',
            ros_msg_class=RosString,
            rix_msg_class=RixString,
            converter=StringConverter
        )
        
        # Start both handles
        self.ros_to_rix_handle.start()
        self.rix_to_ros_handle.start()
        
        self.get_logger().info('Bridge handles created and started')
    
    def spin_once(self):
        """
        Process RIX node events.
        
        This method should be called regularly to process incoming RIX messages
        and trigger RIX callbacks. ROS events are handled by rclpy.spin_once().
        """
        if self.rix_node.ok():
            self.rix_node.spin_once()
    
    def shutdown(self):
        """
        Clean shutdown of the bridge.
        
        Stops all bridge handles and cleans up ROS and RIX resources.
        """
        self.get_logger().info('Shutting down RIX-ROS Bridge...')
        
        # Stop bridge handles
        if hasattr(self, 'ros_to_rix_handle'):
            self.ros_to_rix_handle.stop()
        
        if hasattr(self, 'rix_to_ros_handle'):
            self.rix_to_ros_handle.stop()
        
        # Shutdown RIX node
        if hasattr(self, 'rix_node') and self.rix_node.ok():
            self.rix_node.shutdown()
        
        self.get_logger().info('RIX-ROS Bridge shutdown complete')


class ConfigurableBridgeNode(RosNode):
    """
    Configurable bridge node that creates bridges from JSON configuration.
    
    This is the Phase 2 implementation that supports dynamic bridge creation
    for any message type defined in message_mappings.json.
    """
    
    def __init__(self, config_path: str, mappings_path: str):
        """
        Initialize the configurable bridge node.
        
        Args:
            config_path: Path to bridge_config.json file
            mappings_path: Path to message_mappings.json file
        
        Raises:
            FileNotFoundError: If config or mappings file not found
            ValueError: If configuration is invalid
            ImportError: If message types cannot be loaded
        """
        # Initialize ROS node
        super().__init__('rix_ros_bridge_configurable')
        
        self.get_logger().info('Initializing Configurable RIX-ROS Bridge...')
        
        # Store paths
        self.config_path = config_path
        self.mappings_path = mappings_path
        
        # Initialize RIX node
        self.rix_node = rix.core.Node('rix_ros_bridge_configurable')
        
        if not self.rix_node.ok():
            self.get_logger().error('Failed to initialize RIX node!')
            raise RuntimeError('RIX node initialization failed')
        
        self.get_logger().info('RIX node initialized successfully')
        
        # Load configuration and create bridges
        self.bridge_handles = []
        self._load_and_create_bridges()
        
        self.get_logger().info('Configurable Bridge initialization complete')
    
    def _load_and_create_bridges(self):
        """
        Load configuration and create all configured bridges.
        
        Uses BridgeFactory to dynamically create bridge handles based on
        the configuration file.
        """
        # Load bridge configuration
        self.get_logger().info(f'Loading configuration from: {self.config_path}')
        config = load_bridge_config(self.config_path)
        
        bridge_configs = config['bridges']
        self.get_logger().info(f'Found {len(bridge_configs)} bridge(s) in configuration')
        
        # Create bridge factory
        self.get_logger().info(f'Loading message mappings from: {self.mappings_path}')
        factory = BridgeFactory(self.mappings_path)
        
        # Log supported message types
        supported_types = factory.list_supported_types()
        self.get_logger().info(f'Factory supports {len(supported_types)} message types')
        
        # Create bridges
        for bridge_config in bridge_configs:
            bridge_name = bridge_config['name']
            message_type = bridge_config['message_type']
            direction = bridge_config.get('direction', 'bidirectional')
            
            self.get_logger().info(
                f"Creating bridge '{bridge_name}' "
                f"(type: {message_type}, direction: {direction})"
            )
            
            try:
                # Create bridge handle(s) for this configuration
                handles = factory.create_bridge(bridge_config, self, self.rix_node)
                
                # Start all handles
                for handle in handles:
                    handle.start()
                
                # Store handles
                self.bridge_handles.extend(handles)
                
                self.get_logger().info(
                    f"Bridge '{bridge_name}' created successfully "
                    f"({len(handles)} handle(s))"
                )
                
            except Exception as e:
                self.get_logger().error(
                    f"Failed to create bridge '{bridge_name}': {e}"
                )
                raise
        
        self.get_logger().info(
            f'All bridges created successfully. '
            f'Total handles: {len(self.bridge_handles)}'
        )
    
    def spin_once(self):
        """
        Process RIX node events.
        
        This method should be called regularly to process incoming RIX messages
        and trigger RIX callbacks. ROS events are handled by rclpy.spin_once().
        """
        if self.rix_node.ok():
            self.rix_node.spin_once()
    
    def shutdown(self):
        """
        Clean shutdown of the bridge.
        
        Stops all bridge handles and cleans up ROS and RIX resources.
        """
        self.get_logger().info('Shutting down Configurable RIX-ROS Bridge...')
        
        # Stop all bridge handles
        for i, handle in enumerate(self.bridge_handles):
            try:
                handle.stop()
                self.get_logger().info(f'Stopped bridge handle {i+1}/{len(self.bridge_handles)}')
            except Exception as e:
                self.get_logger().error(f'Error stopping handle {i}: {e}')
        
        # Shutdown RIX node
        if hasattr(self, 'rix_node') and self.rix_node.ok():
            self.rix_node.shutdown()
            self.get_logger().info('RIX node shutdown complete')
        
        self.get_logger().info('Configurable RIX-ROS Bridge shutdown complete')


def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='RIX-ROS Bridge: Configurable bidirectional message bridge'
    )
    
    # Get default paths (relative to package installation)
    # These will be overridden if user provides custom paths
    default_config = str(Path(__file__).parent.parent / 'config' / 'bridge_config.json')
    default_mappings = str(Path(__file__).parent.parent / 'config' / 'message_mappings.json')
    
    parser.add_argument(
        '--config',
        type=str,
        default=default_config,
        help='Path to bridge configuration JSON file (default: config/bridge_config.json)'
    )
    
    parser.add_argument(
        '--mappings',
        type=str,
        default=default_mappings,
        help='Path to message mappings JSON file (default: config/message_mappings.json)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=4,
        help='Number of executor threads for parallel processing (default: 4)'
    )
    
    parser.add_argument(
        '--use-legacy',
        action='store_true',
        help='Use legacy single-bridge mode (hardcoded /chatter topic)'
    )
    
    return parser.parse_args()


def main(args=None):
    """
    Main entry point for the configurable bridge node.
    
    Supports command-line arguments for:
    - Custom configuration files
    - Custom message mappings
    - Thread count for parallel execution
    - Legacy mode (hardcoded bridge)
    
    Uses MultiThreadedExecutor for parallel ROS callback processing
    and dual spin loop for ROS + RIX event processing.
    """
    # Parse command-line arguments
    cli_args = parse_arguments()
    
    # Initialize rclpy
    rclpy.init(args=args)
    
    bridge = None
    executor = None
    
    try:
        # Create bridge instance based on mode
        if cli_args.use_legacy:
            # Legacy mode: hardcoded bridge
            print('Starting in LEGACY mode (hardcoded /chatter bridge)')
            bridge = RixRosBridge()
        else:
            # Configurable mode: load from config files
            print(f'Starting in CONFIGURABLE mode')
            print(f'  Config file: {cli_args.config}')
            print(f'  Mappings file: {cli_args.mappings}')
            print(f'  Threads: {cli_args.threads}')
            
            bridge = ConfigurableBridgeNode(
                config_path=cli_args.config,
                mappings_path=cli_args.mappings
            )
        
        # SINGLE-THREADED EXECUTOR
        # Phase 2 uses single-threaded execution for RIX thread-safety
        # Multi-threaded execution with proper thread-safety mechanisms
        # will be implemented in Phase 3's component-based architecture
        bridge.get_logger().info('Starting bridge with single-threaded executor...')
        bridge.get_logger().info('Press Ctrl+C to stop')
        
        # Dual spin loop: Alternate between ROS and RIX event processing
        # Single-threaded ensures all RIX API calls happen on main thread
        while rclpy.ok():
            # Process ROS events (single-threaded, blocking up to timeout)
            rclpy.spin_once(bridge, timeout_sec=0.1)
            
            # Process RIX events (must be called from main thread)
            bridge.spin_once()
        
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        if bridge:
            bridge.get_logger().info('Keyboard interrupt received, shutting down...')
    except FileNotFoundError as e:
        # Configuration file not found
        if bridge:
            bridge.get_logger().error(f'Configuration file not found: {e}')
        else:
            print(f'Error: Configuration file not found: {e}')
            print(f'Make sure the config files exist:')
            print(f'  - {cli_args.config}')
            print(f'  - {cli_args.mappings}')
    except ValueError as e:
        # Invalid configuration
        if bridge:
            bridge.get_logger().error(f'Invalid configuration: {e}')
        else:
            print(f'Error: Invalid configuration: {e}')
    except Exception as e:
        # Unexpected error
        if bridge:
            bridge.get_logger().error(f'Unexpected error: {e}')
            import traceback
            bridge.get_logger().error(traceback.format_exc())
        else:
            print(f'Error before bridge initialization: {e}')
            import traceback
            traceback.print_exc()
    finally:
        # Cleanup
        if bridge:
            bridge.shutdown()
        
        if executor:
            executor.shutdown()
        
        # Shutdown rclpy
        rclpy.shutdown()
        
        print('RIX-ROS Bridge shutdown complete')


if __name__ == '__main__':
    main()
