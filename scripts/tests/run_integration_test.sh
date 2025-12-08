#!/bin/bash
# Comprehensive Integration Test Script
# This script tests the RIX-ROS bridge in both directions

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "RIX-ROS Bridge Integration Test"
echo "========================================================================"

# Check if rixhub is running
if ! pgrep -x "rixhub" > /dev/null; then
    echo -e "${RED}ERROR: rixhub is not running!${NC}"
    echo "Please start rixhub in another terminal first:"
    echo "  ~/.rix/bin/rixhub"
    exit 1
fi

echo -e "${GREEN}✓ rixhub is running${NC}"

# Setup environment
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
source install/setup.bash

echo ""
echo "========================================================================"
echo "Step 1: Starting Bridge Node"
echo "========================================================================"

# Use explicit paths to config files in source directory
CONFIG_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/bridge_config.json"
MAPPINGS_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json"

# Start bridge in background
ros2 run rix_ros_bridge bridge_node \
    --config "$CONFIG_PATH" \
    --mappings "$MAPPINGS_PATH" \
    > /tmp/bridge_output.log 2>&1 &

BRIDGE_PID=$!
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 3  # Give bridge time to initialize

# Check if bridge is still running
if ! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}ERROR: Bridge failed to start!${NC}"
    cat /tmp/bridge_output.log
    exit 1
fi

echo ""
echo "========================================================================"
echo "Step 2: Testing ROS → RIX Message Flow"
echo "========================================================================"

# Start RIX subscriber in background
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 examples/test_bridge_subscriber.py > /tmp/rix_sub_output.log 2>&1) &
RIX_SUB_PID=$!

sleep 2  # Give subscriber time to connect

echo "Publishing ROS messages..."
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Publish test messages
ros2 topic pub /chatter std_msgs/msg/String 'data: "Test message 1 from ROS"' --once
sleep 1
ros2 topic pub /chatter std_msgs/msg/String 'data: "Test message 2 from ROS"' --once
sleep 1
ros2 topic pub /chatter std_msgs/msg/String 'data: "Test message 3 from ROS"' --once
sleep 2

# Check RIX subscriber output
echo ""
echo "RIX Subscriber Output:"
echo "----------------------------------------"
cat /tmp/rix_sub_output.log
echo "----------------------------------------"

if grep -q "Received from ROS bridge" /tmp/rix_sub_output.log; then
    echo -e "${GREEN}✓ ROS → RIX: Messages received successfully!${NC}"
else
    echo -e "${RED}✗ ROS → RIX: No messages received${NC}"
fi

# Stop RIX subscriber
kill $RIX_SUB_PID 2>/dev/null || true

echo ""
echo "========================================================================"
echo "Step 3: Testing RIX → ROS Message Flow"
echo "========================================================================"

# Start ROS subscriber in background
ros2 topic echo /chatter_from_rix > /tmp/ros_sub_output.log 2>&1 &
ROS_SUB_PID=$!

sleep 2  # Give subscriber time to connect

echo "Publishing RIX messages..."
cd ~/Desktop/ROB490/rix-py
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH

# Publish from RIX (modified to send a few messages and exit)
timeout 5 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('test_publisher')
pub = node.create_publisher(String, '/chatter')
time.sleep(1)

for i in range(3):
    msg = String()
    msg.data = f'Test message {i+1} from RIX'
    pub.publish(msg)
    print(f'Published: {msg.data}')
    time.sleep(1)

node.shutdown()
" || true

sleep 2

# Stop ROS subscriber
kill $ROS_SUB_PID 2>/dev/null || true

# Check ROS subscriber output
echo ""
echo "ROS Subscriber Output:"
echo "----------------------------------------"
cat /tmp/ros_sub_output.log | head -20
echo "----------------------------------------"

if grep -q "Test message.*from RIX" /tmp/ros_sub_output.log; then
    echo -e "${GREEN}✓ RIX → ROS: Messages received successfully!${NC}"
else
    echo -e "${RED}✗ RIX → ROS: No messages received${NC}"
fi

echo ""
echo "========================================================================"
echo "Cleanup"
echo "========================================================================"

# Stop bridge
kill $BRIDGE_PID 2>/dev/null || true
echo -e "${GREEN}✓ Bridge stopped${NC}"

echo ""
echo "========================================================================"
echo "Test Summary"
echo "========================================================================"

# Check both directions
ROS_TO_RIX_OK=0
RIX_TO_ROS_OK=0

if grep -q "Received from ROS bridge" /tmp/rix_sub_output.log; then
    ROS_TO_RIX_OK=1
    echo -e "${GREEN}✓ ROS → RIX: PASSED${NC}"
else
    echo -e "${RED}✗ ROS → RIX: FAILED${NC}"
fi

if grep -q "Test message.*from RIX" /tmp/ros_sub_output.log; then
    RIX_TO_ROS_OK=1
    echo -e "${GREEN}✓ RIX → ROS: PASSED${NC}"
else
    echo -e "${RED}✗ RIX → ROS: FAILED${NC}"
fi

echo ""
if [ $ROS_TO_RIX_OK -eq 1 ] && [ $RIX_TO_ROS_OK -eq 1 ]; then
    echo -e "${GREEN}========================================================================"
    echo "ALL TESTS PASSED! ✓"
    echo "========================================================================${NC}"
    exit 0
else
    echo -e "${RED}========================================================================"
    echo "SOME TESTS FAILED"
    echo "========================================================================${NC}"
    echo ""
    echo "Debug logs available at:"
    echo "  - Bridge: /tmp/bridge_output.log"
    echo "  - RIX subscriber: /tmp/rix_sub_output.log"
    echo "  - ROS subscriber: /tmp/ros_sub_output.log"
    exit 1
fi
