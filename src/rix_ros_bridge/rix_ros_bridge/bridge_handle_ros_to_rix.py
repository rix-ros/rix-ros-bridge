"""
Bridge Handle: ROS to RIX

Handles message flow from ROS2 subscriber to RIX publisher.
"""


class BridgeHandleRosToRix:
    """Bridge from ROS subscriber to RIX publisher."""
    
    def __init__(self, ros_node, rix_node, ros_topic, rix_topic, ros_msg_class, rix_msg_class, converter):
        """
        Initialize ROS to RIX bridge handle.
        
        Args:
            ros_node: ROS2 node instance
            rix_node: RIX node instance
            ros_topic: ROS topic to subscribe to
            rix_topic: RIX topic to publish to
            ros_msg_class: ROS message class
            rix_msg_class: RIX message class
            converter: Message converter class
        """
        self.ros_node = ros_node
        self.rix_node = rix_node
        self.ros_topic = ros_topic
        self.rix_topic = rix_topic
        self.ros_msg_class = ros_msg_class
        self.rix_msg_class = rix_msg_class
        self.converter = converter
        
        self.ros_subscriber = None
        self.rix_publisher = None
        self.active = False
    
    def start(self):
        """Initialize publishers and subscribers."""
        # Create ROS subscriber
        self.ros_subscriber = self.ros_node.create_subscription(
            self.ros_msg_class,
            self.ros_topic,
            self.ros_callback,
            10  # QoS depth
        )
        
        # Create RIX publisher
        self.rix_publisher = self.rix_node.create_publisher(
            self.rix_msg_class,
            self.rix_topic
        )
        
        self.active = True
        self.ros_node.get_logger().info(
            f'ROS→RIX bridge started: {self.ros_topic} → {self.rix_topic}'
        )
    
    def ros_callback(self, ros_msg):
        """
        Callback for ROS subscriber.
        
        Receives ROS message, converts it to RIX format, and publishes to RIX.
        
        Args:
            ros_msg: Incoming ROS message
        """
        if not self.active:
            return
        
        try:
            # Convert ROS message to RIX message
            rix_msg = self.converter.ros_to_rix(ros_msg)
            
            # Publish to RIX
            self.rix_publisher.publish(rix_msg)
            
            # Log the bridged message
            self.ros_node.get_logger().debug(
                f'Bridged ROS→RIX: {self.ros_topic} → {self.rix_topic}: {ros_msg.data}'
            )
        except Exception as e:
            self.ros_node.get_logger().error(
                f'Error bridging ROS→RIX message: {e}'
            )
    
    def stop(self):
        """Cleanup resources."""
        self.active = False
        
        # Destroy ROS subscriber
        if self.ros_subscriber is not None:
            self.ros_node.destroy_subscription(self.ros_subscriber)
            self.ros_subscriber = None
        
        # Note: RIX publisher cleanup is handled by RIX node
        self.rix_publisher = None
        
        self.ros_node.get_logger().info(
            f'ROS→RIX bridge stopped: {self.ros_topic} → {self.rix_topic}'
        )
