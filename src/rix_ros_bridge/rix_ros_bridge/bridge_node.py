#!/usr/bin/env python3
"""
RIX-ROS Bridge Node

Main bridge node that manages bidirectional message passing between ROS2 and RIX.
"""

import rclpy
from rclpy.node import Node as RosNode
from std_msgs.msg import String as RosString

import rix.core
from rix.msg.standard import String as RixString

from rix_ros_bridge.bridge_handle_ros_to_rix import BridgeHandleRosToRix
from rix_ros_bridge.bridge_handle_rix_to_ros import BridgeHandleRixToRos
from rix_ros_bridge.converters.std_msgs import StringConverter


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


def main(args=None):
    """
    Main entry point for the bridge node.
    
    Initializes ROS and RIX, creates the bridge, and runs the dual spin loop
    to process events from both systems. Handles Ctrl+C gracefully.
    """
    # Initialize rclpy
    rclpy.init(args=args)
    
    bridge = None
    
    try:
        # Create bridge instance
        bridge = RixRosBridge()
        
        bridge.get_logger().info('Starting bridge spin loop...')
        bridge.get_logger().info('Press Ctrl+C to stop')
        
        # Dual spin loop: alternate between ROS and RIX event processing
        while rclpy.ok():
            # Process ROS events
            rclpy.spin_once(bridge, timeout_sec=0.1)
            
            # Process RIX events
            bridge.spin_once()
            
    except KeyboardInterrupt:
        # User pressed Ctrl+C
        if bridge:
            bridge.get_logger().info('Keyboard interrupt received, shutting down...')
    except Exception as e:
        # Unexpected error
        if bridge:
            bridge.get_logger().error(f'Unexpected error: {e}')
        else:
            print(f'Error before bridge initialization: {e}')
    finally:
        # Cleanup
        if bridge:
            bridge.shutdown()
        
        # Shutdown rclpy
        rclpy.shutdown()
        
        print('RIX-ROS Bridge shutdown complete')


if __name__ == '__main__':
    main()
