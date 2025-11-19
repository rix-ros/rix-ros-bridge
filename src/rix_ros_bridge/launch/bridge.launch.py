"""
RIX-ROS Bridge Launch File

Launch the bridge node for ROS2-RIX communication.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for bridge node."""
    
    return LaunchDescription([
        Node(
            package='rix_ros_bridge',
            executable='bridge_node',
            name='rix_ros_bridge',
            output='screen',
            parameters=[
                {'log_level': 'info'}
            ]
        ),
    ])
