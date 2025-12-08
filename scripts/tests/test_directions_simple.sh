#!/bin/bash
# Simplified Directional Bridge Test Script
# Tests correct direction only (no reverse blocking tests)

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================================================"
echo "Directional Bridge Integration Test (Simplified)"
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
echo "Setting up environment..."
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash 2>/dev/null
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
source install/setup.bash 2>/dev/null
echo "Environment ready"

CONFIG_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/directional_test_config.json"
MAPPINGS_PATH="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json"

echo ""
echo "========================================================================"
echo "Step 1: Starting Bridge"
echo "========================================================================"
echo "  - Bidirectional: String"
echo "  - ROS→RIX only: Int32"
echo "  - RIX→ROS only: Pose"
echo ""

# Start bridge in background
ros2 run rix_ros_bridge bridge_node \
    --config "$CONFIG_PATH" \
    --mappings "$MAPPINGS_PATH" \
    > /tmp/directional_bridge.log 2>&1 &

BRIDGE_PID=$!
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 3

# Check if bridge is still running
if ! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}ERROR: Bridge failed to start!${NC}"
    cat /tmp/directional_bridge.log
    exit 1
fi

echo "Bridge running with 4 handles (2 bidirectional + 1 + 1 unidirectional)"

echo ""
echo "========================================================================"
echo "Test 1: Bidirectional String (ROS → RIX)"
echo "========================================================================"

# Start RIX subscriber
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('bidir_test1')

def callback(msg):
    print(f'✓ RIX received String: {msg.data}', flush=True)

sub = node.create_subscriber(String, '/bidir_string_rix', callback)
time.sleep(1)

start = time.time()
while time.time() - start < 4 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/bidir_rix_sub.log 2>&1) &
STRING_SUB_PID=$!

sleep 3

# Publish from ROS
echo "Publishing String from ROS..."
ros2 topic pub /bidir_string std_msgs/msg/String 'data: "Bidirectional test ROS→RIX"' --once
sleep 2

# Let subscriber finish naturally, then wait
sleep 2
wait $STRING_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "RIX received String" /tmp/bidir_rix_sub.log; then
    echo -e "${GREEN}✓ Bidirectional ROS→RIX: PASSED${NC}"
    cat /tmp/bidir_rix_sub.log
else
    echo -e "${RED}✗ Bidirectional ROS→RIX: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 2: Bidirectional String (RIX → ROS)"
echo "========================================================================"

# Start ROS subscriber first in background
echo "Starting ROS subscriber..."
timeout 8 ros2 topic echo /bidir_string > /tmp/bidir_ros_sub.log 2>&1 &
ROS_SUB_PID=$!
sleep 3

# Now publish from RIX
echo "Publishing String from RIX..."
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('bidir_test2')
pub = node.create_publisher(String, '/bidir_string_rix')
time.sleep(2)

msg = String()
msg.data = 'Bidirectional test RIX→ROS'

# Publish multiple times
for i in range(5):
    pub.publish(msg)
    time.sleep(0.2)

print(f'Published: {msg.data}', flush=True)
time.sleep(1)
node.shutdown()
")

sleep 2
kill $ROS_SUB_PID 2>/dev/null || true
wait $ROS_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "Bidirectional test RIX" /tmp/bidir_ros_sub.log; then
    echo -e "${GREEN}✓ Bidirectional RIX→ROS: PASSED${NC}"
    grep "data:" /tmp/bidir_ros_sub.log | head -3
else
    echo -e "${RED}✗ Bidirectional RIX→ROS: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 3: Unidirectional ROS→RIX (Int32)"
echo "========================================================================"

# Start RIX subscriber
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import Int32
import time

node = Node('ros_to_rix_test')

def callback(msg):
    print(f'✓ RIX received Int32: {msg.data}', flush=True)

sub = node.create_subscriber(Int32, '/ros_only_int32_rix', callback)
time.sleep(1)

start = time.time()
while time.time() - start < 4 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/ros_to_rix_int32.log 2>&1) &
INT32_SUB_PID=$!

sleep 3

# Publish from ROS
echo "Publishing Int32 from ROS..."
ros2 topic pub /ros_only_int32 std_msgs/msg/Int32 'data: 99' --once
sleep 2

# Let subscriber finish naturally, then wait
sleep 2
wait $INT32_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "RIX received Int32" /tmp/ros_to_rix_int32.log; then
    echo -e "${GREEN}✓ ROS→RIX Int32: PASSED${NC}"
    cat /tmp/ros_to_rix_int32.log
else
    echo -e "${RED}✗ ROS→RIX Int32: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 4: Unidirectional RIX→ROS (Pose)"
echo "========================================================================"

# Start ROS subscriber first in background
echo "Starting ROS subscriber..."
timeout 8 ros2 topic echo /rix_only_pose > /tmp/rix_to_ros_pose.log 2>&1 &
POSE_SUB_PID=$!
sleep 3

# Now publish from RIX
echo "Publishing Pose from RIX..."
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.geometry import Pose, Point, Quaternion
import time

node = Node('rix_to_ros_test')
pub = node.create_publisher(Pose, '/rix_only_pose_rix')
time.sleep(2)

msg = Pose()
msg.position = Point()
msg.position.x = 5.0
msg.position.y = 6.0
msg.position.z = 7.0
msg.orientation = Quaternion()
msg.orientation.w = 1.0

# Publish multiple times
for i in range(5):
    pub.publish(msg)
    time.sleep(0.2)

print(f'Published Pose from RIX: pos({msg.position.x}, {msg.position.y}, {msg.position.z})', flush=True)
time.sleep(1)
node.shutdown()
")

sleep 2
kill $POSE_SUB_PID 2>/dev/null || true
wait $POSE_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "x: 5.0" /tmp/rix_to_ros_pose.log; then
    echo -e "${GREEN}✓ RIX→ROS Pose: PASSED${NC}"
    grep -A 10 "position:" /tmp/rix_to_ros_pose.log | head -8
else
    echo -e "${RED}✗ RIX→ROS Pose: FAILED${NC}"
fi

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

BIDIR_ROS_TO_RIX=0
BIDIR_RIX_TO_ROS=0
ROS_TO_RIX=0
RIX_TO_ROS=0

if grep -q "RIX received String" /tmp/bidir_rix_sub.log; then
    BIDIR_ROS_TO_RIX=1
    echo -e "${GREEN}✓ Bidirectional ROS→RIX: PASSED${NC}"
else
    echo -e "${RED}✗ Bidirectional ROS→RIX: FAILED${NC}"
fi

if grep -q "Bidirectional test RIX" /tmp/bidir_ros_sub.log; then
    BIDIR_RIX_TO_ROS=1
    echo -e "${GREEN}✓ Bidirectional RIX→ROS: PASSED${NC}"
else
    echo -e "${RED}✗ Bidirectional RIX→ROS: FAILED${NC}"
fi

if grep -q "RIX received Int32" /tmp/ros_to_rix_int32.log; then
    ROS_TO_RIX=1
    echo -e "${GREEN}✓ ROS→RIX Int32: PASSED${NC}"
else
    echo -e "${RED}✗ ROS→RIX Int32: FAILED${NC}"
fi

if grep -q "x: 5.0" /tmp/rix_to_ros_pose.log; then
    RIX_TO_ROS=1
    echo -e "${GREEN}✓ RIX→ROS Pose: PASSED${NC}"
else
    echo -e "${RED}✗ RIX→ROS Pose: FAILED${NC}"
fi

echo ""
TOTAL=$((BIDIR_ROS_TO_RIX + BIDIR_RIX_TO_ROS + ROS_TO_RIX + RIX_TO_ROS))

if [ $TOTAL -eq 4 ]; then
    echo -e "${GREEN}========================================================================"
    echo "ALL DIRECTIONAL TESTS PASSED! ✓"
    echo "4/4 tests passed"
    echo "- Bidirectional bridges work both ways"
    echo "- Unidirectional ROS→RIX works"
    echo "- Unidirectional RIX→ROS works"
    echo "========================================================================${NC}"
    exit 0
else
    echo -e "${RED}========================================================================"
    echo "SOME TESTS FAILED"
    echo "$TOTAL/4 tests passed"
    echo "========================================================================${NC}"
    exit 1
fi
