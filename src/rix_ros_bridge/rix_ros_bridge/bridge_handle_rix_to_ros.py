"""
Bridge Handle: RIX to ROS

Handles message flow from RIX subscriber to ROS2 publisher.
"""


class BridgeHandleRixToRos:
    """Bridge from RIX subscriber to ROS publisher."""
    
    def __init__(self, ros_node, rix_node, rix_topic, ros_topic, ros_msg_class, rix_msg_class, converter):
        """
        Initialize RIX to ROS bridge handle.
        
        Args:
            ros_node: ROS2 node instance
            rix_node: RIX node instance
            rix_topic: RIX topic to subscribe to
            ros_topic: ROS topic to publish to
            ros_msg_class: ROS message class
            rix_msg_class: RIX message class
            converter: Message converter class
        """
        self.ros_node = ros_node
        self.rix_node = rix_node
        self.rix_topic = rix_topic
        self.ros_topic = ros_topic
        self.ros_msg_class = ros_msg_class
        self.rix_msg_class = rix_msg_class
        self.converter = converter
        
        self.ros_publisher = None
        self.rix_subscriber = None
        self.active = False
    
    def start(self):
        """Initialize publishers and subscribers."""
        # Create ROS publisher
        self.ros_publisher = self.ros_node.create_publisher(
            self.ros_msg_class,
            self.ros_topic,
            10  # QoS depth
        )
        
        # Create RIX subscriber
        self.rix_subscriber = self.rix_node.create_subscriber(
            self.rix_msg_class,
            self.rix_topic,
            self.rix_callback
        )
        
        self.active = True
        self.ros_node.get_logger().info(
            f'RIX→ROS bridge started: {self.rix_topic} → {self.ros_topic}'
        )
    
    def rix_callback(self, rix_msg):
        """
        Callback for RIX subscriber.
        
        Receives RIX message, converts it to ROS format, and publishes to ROS.
        
        Args:
            rix_msg: Incoming RIX message
        """
        if not self.active:
            return
        
        try:
            print(f" RIX→ROS CALLBACK TRIGGERED: {self.rix_topic}", flush=True)
            # Convert RIX message to ROS message
            ros_msg = self.converter.rix_to_ros(rix_msg)
            
            # Publish to ROS
            self.ros_publisher.publish(ros_msg)
            print(f" RIX→ROS SUCCESS: {self.rix_topic} → {self.ros_topic}", flush=True)
            
            # Log the bridged message
            self.ros_node.get_logger().debug(
                f'Bridged RIX→ROS: {self.rix_topic} → {self.ros_topic}'
            )
        except Exception as e:
            print(f" RIX→ROS ERROR: {e}", flush=True)
            self.ros_node.get_logger().error(
                f'Error bridging RIX→ROS message: {e}'
            )
    
    def stop(self):
        """Cleanup resources."""
        self.active = False
        
        # Destroy ROS publisher
        if self.ros_publisher is not None:
            self.ros_node.destroy_publisher(self.ros_publisher)
            self.ros_publisher = None
        
        # Note: RIX subscriber cleanup is handled by RIX node
        self.rix_subscriber = None
        
        self.ros_node.get_logger().info(
            f'RIX→ROS bridge stopped: {self.rix_topic} → {self.ros_topic}'
        )
