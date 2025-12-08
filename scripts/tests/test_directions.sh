#!/bin/bash
# Directional Bridge Test Script

# Don't exit on error - we want to see all test results
# set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================================================"
echo "Directional Bridge Integration Test"
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
echo "Step 1: Starting Bridge with Directional Configuration"
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

echo ""
echo "Bridge Log:"
echo "----------------------------------------"
cat /tmp/directional_bridge.log | head -40
echo "----------------------------------------"

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
received = []

def callback(msg):
    print(f'✓ RIX received String: {msg.data}', flush=True)
    received.append(msg.data)

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

# Kill and wait for subscriber to finish
kill $STRING_SUB_PID 2>/dev/null || true
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

# Start ROS subscriber
timeout 5 ros2 topic echo /bidir_string > /tmp/bidir_ros_sub.log 2>&1 &
ROS_SUB_PID=$!
sleep 2

# Publish from RIX
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
time.sleep(1)

msg = String()
msg.data = 'Bidirectional test RIX→ROS'
pub.publish(msg)
print(f'Published: {msg.data}', flush=True)

time.sleep(1)
node.shutdown()
")

sleep 2
kill $ROS_SUB_PID 2>/dev/null || true

if grep -q "Bidirectional test RIX" /tmp/bidir_ros_sub.log; then
    echo -e "${GREEN}✓ Bidirectional RIX→ROS: PASSED${NC}"
    grep "data:" /tmp/bidir_ros_sub.log | head -3
else
    echo -e "${RED}✗ Bidirectional RIX→ROS: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 3: Unidirectional ROS→RIX (Int32) - Should Work"
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
received = []

def callback(msg):
    print(f'✓ RIX received Int32: {msg.data}', flush=True)
    received.append(msg.data)

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
echo "Publishing Int32 from ROS (should reach RIX)..."
ros2 topic pub /ros_only_int32 std_msgs/msg/Int32 'data: 99' --once
sleep 2

# Kill and wait for subscriber to finish
kill $INT32_SUB_PID 2>/dev/null || true
wait $INT32_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "RIX received Int32" /tmp/ros_to_rix_int32.log; then
    echo -e "${GREEN}✓ ROS→RIX Int32: PASSED (correctly forwarded)${NC}"
    cat /tmp/ros_to_rix_int32.log
else
    echo -e "${RED}✗ ROS→RIX Int32: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 4: Unidirectional ROS→RIX (Int32) - Reverse Should NOT Work"
echo "========================================================================"

# Start ROS subscriber (should NOT receive anything)
ros2 topic echo /ros_only_int32 > /tmp/ros_to_rix_reverse.log 2>&1 &
ROS_SUB_PID=$!
sleep 2

# Publish from RIX (should NOT reach ROS)
echo "Publishing Int32 from RIX (should NOT reach ROS)..."
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import Int32
import time

node = Node('ros_to_rix_reverse')
pub = node.create_publisher(Int32, '/ros_only_int32_rix')
time.sleep(1)

msg = Int32()
msg.data = 999
pub.publish(msg)
print(f'Published Int32 from RIX: {msg.data}', flush=True)

time.sleep(1)
node.shutdown()
")

sleep 1
kill $ROS_SUB_PID 2>/dev/null || true
wait $ROS_SUB_PID 2>/dev/null || true

if grep -q "data: 999" /tmp/ros_to_rix_reverse.log; then
    echo -e "${RED}✗ ROS→RIX reverse: FAILED (message leaked through!)${NC}"
else
    echo -e "${GREEN}✓ ROS→RIX reverse: PASSED (correctly blocked)${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 5: Unidirectional RIX→ROS (Pose) - Should Work"
echo "========================================================================"

# Start ROS subscriber
ros2 topic echo /rix_only_pose > /tmp/rix_to_ros_pose.log 2>&1 &
POSE_SUB_PID=$!
sleep 3

# Publish from RIX
echo "Publishing Pose from RIX (should reach ROS)..."
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
time.sleep(1)

msg = Pose()
msg.position = Point()
msg.position.x = 5.0
msg.position.y = 6.0
msg.position.z = 7.0
msg.orientation = Quaternion()
msg.orientation.w = 1.0

pub.publish(msg)
print(f'Published Pose from RIX: pos({msg.position.x}, {msg.position.y}, {msg.position.z})', flush=True)

time.sleep(1)
node.shutdown()
")

sleep 2
kill $POSE_SUB_PID 2>/dev/null || true
wait $POSE_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "x: 5.0" /tmp/rix_to_ros_pose.log; then
    echo -e "${GREEN}✓ RIX→ROS Pose: PASSED (correctly forwarded)${NC}"
    grep -A 10 "position:" /tmp/rix_to_ros_pose.log | head -8
else
    echo -e "${RED}✗ RIX→ROS Pose: FAILED${NC}"
fi

echo ""
echo "========================================================================"
echo "Test 6: Unidirectional RIX→ROS (Pose) - Reverse Should NOT Work"
echo "========================================================================"

# Start RIX subscriber (should NOT receive anything)
(cd ~/Desktop/ROB490/rix-py && \
 PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH \
 python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.geometry import Pose
import time

node = Node('rix_to_ros_reverse')
received = []

def callback(msg):
    print(f'✗ ERROR: RIX received Pose (should not happen!)', flush=True)
    received.append(msg)

sub = node.create_subscriber(Pose, '/rix_only_pose_rix', callback)
time.sleep(1)

start = time.time()
while time.time() - start < 2 and node.ok():
    node.spin_once()

node.shutdown()
" > /tmp/rix_to_ros_reverse.log 2>&1) &
REVERSE_SUB_PID=$!

sleep 2

# Publish from ROS (should NOT reach RIX)
echo "Publishing Pose from ROS (should NOT reach RIX)..."
ros2 topic pub /rix_only_pose geometry_msgs/msg/Pose '{position: {x: 99.0, y: 99.0, z: 99.0}, orientation: {w: 1.0}}' --once
sleep 2

kill $REVERSE_SUB_PID 2>/dev/null || true
wait $REVERSE_SUB_PID 2>/dev/null || true
sleep 1

if grep -q "ERROR: RIX received Pose" /tmp/rix_to_ros_reverse.log; then
    echo -e "${RED}✗ RIX→ROS reverse: FAILED (message leaked through!)${NC}"
else
    echo -e "${GREEN}✓ RIX→ROS reverse: PASSED (correctly blocked)${NC}"
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
ROS_TO_RIX_FORWARD=0
ROS_TO_RIX_BLOCK=0
RIX_TO_ROS_FORWARD=0
RIX_TO_ROS_BLOCK=0

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
    ROS_TO_RIX_FORWARD=1
    echo -e "${GREEN}✓ ROS→RIX Int32 forward: PASSED${NC}"
else
    echo -e "${RED}✗ ROS→RIX Int32 forward: FAILED${NC}"
fi

if ! grep -q "data: 999" /tmp/ros_to_rix_reverse.log; then
    ROS_TO_RIX_BLOCK=1
    echo -e "${GREEN}✓ ROS→RIX Int32 blocked reverse: PASSED${NC}"
else
    echo -e "${RED}✗ ROS→RIX Int32 blocked reverse: FAILED${NC}"
fi

if grep -q "x: 5.0" /tmp/rix_to_ros_pose.log; then
    RIX_TO_ROS_FORWARD=1
    echo -e "${GREEN}✓ RIX→ROS Pose forward: PASSED${NC}"
else
    echo -e "${RED}✗ RIX→ROS Pose forward: FAILED${NC}"
fi

if ! grep -q "ERROR: RIX received Pose" /tmp/rix_to_ros_reverse.log; then
    RIX_TO_ROS_BLOCK=1
    echo -e "${GREEN}✓ RIX→ROS Pose blocked reverse: PASSED${NC}"
else
    echo -e "${RED}✗ RIX→ROS Pose blocked reverse: FAILED${NC}"
fi

echo ""
TOTAL=$((BIDIR_ROS_TO_RIX + BIDIR_RIX_TO_ROS + ROS_TO_RIX_FORWARD + ROS_TO_RIX_BLOCK + RIX_TO_ROS_FORWARD + RIX_TO_ROS_BLOCK))

if [ $TOTAL -eq 6 ]; then
    echo -e "${GREEN}========================================================================"
    echo "ALL DIRECTIONAL TESTS PASSED! ✓"
    echo "6/6 tests passed"
    echo "- Bidirectional bridges work both ways"
    echo "- Unidirectional bridges work in correct direction"
    echo "- Unidirectional bridges correctly block reverse direction"
    echo "========================================================================${NC}"
    exit 0
else
    echo -e "${RED}========================================================================"
    echo "SOME TESTS FAILED"
    echo "$TOTAL/6 tests passed"
    echo "========================================================================${NC}"
    echo ""
    echo "Debug logs:"
    echo "  - Bridge: /tmp/directional_bridge.log"
    echo "  - Bidirectional RIX sub: /tmp/bidir_rix_sub.log"
    echo "  - Bidirectional ROS sub: /tmp/bidir_ros_sub.log"
    echo "  - ROS→RIX forward: /tmp/ros_to_rix_int32.log"
    echo "  - ROS→RIX reverse: /tmp/ros_to_rix_reverse.log"
    echo "  - RIX→ROS forward: /tmp/rix_to_ros_pose.log"
    echo "  - RIX→ROS reverse: /tmp/rix_to_ros_reverse.log"
    exit 1
fi
