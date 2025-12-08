#!/bin/bash
# Multi-Type Integration Test Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================================================"
echo "Multi-Type Integration Test (String, Int32, Pose)"
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

CONFIG_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/multi_type_test_config.json"
MAPPINGS_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json"

echo ""
echo "========================================================================"
echo "Step 1: Starting Bridge with 3 Message Types"
echo "========================================================================"

# Start bridge in background
ros2 run rix_ros_bridge bridge_node \
    --config "$CONFIG_PATH" \
    --mappings "$MAPPINGS_PATH" \
    > /tmp/multi_bridge_output.log 2>&1 &

BRIDGE_PID=$!
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 3

# Check if bridge is still running
if ! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}ERROR: Bridge failed to start!${NC}"
    cat /tmp/multi_bridge_output.log
    exit 1
fi

echo ""
echo "Bridge Log:"
echo "----------------------------------------"
cat /tmp/multi_bridge_output.log
echo "----------------------------------------"

echo ""
echo "========================================================================"
echo "Step 2: Test String Messages (ROS → RIX)"
echo "========================================================================"

# Start RIX String subscriber
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('string_sub')
received = []

def callback(msg):
    print(f'✓ String RIX received: {msg.data}', flush=True)
    received.append(msg.data)

sub = node.create_subscriber(String, '/test_string_from_ros', callback)
time.sleep(1)

# Spin for 5 seconds
start = time.time()
while time.time() - start < 5 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/string_rix_sub.log 2>&1) &

STRING_SUB_PID=$!
sleep 2

# Publish String from ROS
echo "Publishing String from ROS..."
ros2 topic pub /test_string std_msgs/msg/String 'data: "Hello String"' --once
sleep 2

# Check output
if grep -q "String RIX received" /tmp/string_rix_sub.log; then
    echo -e "${GREEN}✓ String Test PASSED${NC}"
    cat /tmp/string_rix_sub.log
else
    echo -e "${RED}✗ String Test FAILED${NC}"
fi

wait $STRING_SUB_PID 2>/dev/null || true

echo ""
echo "========================================================================"
echo "Step 3: Test Int32 Messages (ROS → RIX)"
echo "========================================================================"

# Start RIX Int32 subscriber
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import Int32
import time

node = Node('int32_sub')
received = []

def callback(msg):
    print(f'✓ Int32 RIX received: {msg.data}', flush=True)
    received.append(msg.data)

sub = node.create_subscriber(Int32, '/test_int32_from_ros', callback)
time.sleep(1)

# Spin for 5 seconds
start = time.time()
while time.time() - start < 5 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/int32_rix_sub.log 2>&1) &

INT32_SUB_PID=$!
sleep 2

# Publish Int32 from ROS
echo "Publishing Int32 from ROS..."
ros2 topic pub /test_int32 std_msgs/msg/Int32 'data: 42' --once
sleep 2

# Check output
if grep -q "Int32 RIX received" /tmp/int32_rix_sub.log; then
    echo -e "${GREEN}✓ Int32 Test PASSED${NC}"
    cat /tmp/int32_rix_sub.log
else
    echo -e "${RED}✗ Int32 Test FAILED${NC}"
fi

wait $INT32_SUB_PID 2>/dev/null || true

echo ""
echo "========================================================================"
echo "Step 4: Test Pose Messages (ROS → RIX)"
echo "========================================================================"

# Start RIX Pose subscriber
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.geometry import Pose
import time

node = Node('pose_sub')
received = []

def callback(msg):
    print(f'✓ Pose RIX received: pos({msg.position.x}, {msg.position.y}, {msg.position.z}) orient({msg.orientation.w})', flush=True)
    received.append(msg)

sub = node.create_subscriber(Pose, '/test_pose_from_ros', callback)
time.sleep(1)

# Spin for 5 seconds
start = time.time()
while time.time() - start < 5 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/pose_rix_sub.log 2>&1) &

POSE_SUB_PID=$!
sleep 2

# Publish Pose from ROS
echo "Publishing Pose from ROS..."
ros2 topic pub /test_pose geometry_msgs/msg/Pose '{position: {x: 1.0, y: 2.0, z: 3.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}' --once
sleep 2

# Check output
if grep -q "Pose RIX received" /tmp/pose_rix_sub.log; then
    echo -e "${GREEN}✓ Pose Test PASSED${NC}"
    cat /tmp/pose_rix_sub.log
else
    echo -e "${RED}✗ Pose Test FAILED${NC}"
fi

wait $POSE_SUB_PID 2>/dev/null || true

echo ""
echo "========================================================================"
echo "Cleanup"
echo "========================================================================"

kill $BRIDGE_PID 2>/dev/null || true
echo -e "${GREEN}✓ Bridge stopped${NC}"

echo ""
echo "========================================================================"
echo "Test Summary"
echo "========================================================================"

STRING_OK=0
INT32_OK=0
POSE_OK=0

if grep -q "String RIX received" /tmp/string_rix_sub.log; then
    STRING_OK=1
    echo -e "${GREEN}✓ String Messages: PASSED${NC}"
else
    echo -e "${RED}✗ String Messages: FAILED${NC}"
fi

if grep -q "Int32 RIX received" /tmp/int32_rix_sub.log; then
    INT32_OK=1
    echo -e "${GREEN}✓ Int32 Messages: PASSED${NC}"
else
    echo -e "${RED}✗ Int32 Messages: FAILED${NC}"
fi

if grep -q "Pose RIX received" /tmp/pose_rix_sub.log; then
    POSE_OK=1
    echo -e "${GREEN}✓ Pose Messages: PASSED${NC}"
else
    echo -e "${RED}✗ Pose Messages: FAILED${NC}"
fi

echo ""
if [ $STRING_OK -eq 1 ] && [ $INT32_OK -eq 1 ] && [ $POSE_OK -eq 1 ]; then
    echo -e "${GREEN}========================================================================"
    echo "ALL MULTI-TYPE TESTS PASSED! ✓"
    echo "3 different message types bridged successfully!"
    echo "========================================================================${NC}"
    exit 0
else
    echo -e "${RED}========================================================================"
    echo "SOME TESTS FAILED"
    echo "========================================================================${NC}"
    echo ""
    echo "Debug logs:"
    echo "  - Bridge: /tmp/multi_bridge_output.log"
    echo "  - String: /tmp/string_rix_sub.log"
    echo "  - Int32: /tmp/int32_rix_sub.log"
    echo "  - Pose: /tmp/pose_rix_sub.log"
    exit 1
fi
