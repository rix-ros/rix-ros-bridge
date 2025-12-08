#!/bin/bash
# Multi-Type Bidirectional Bridge Test
# Tests that String, Int32, and Pose ALL work bidirectionally

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================================================"
echo "Multi-Type Bidirectional Bridge Test"
echo "Testing String, Int32, and Pose in BOTH directions"
echo "========================================================================"

# Check if rixhub is running
if ! pgrep -x "rixhub" > /dev/null; then
    echo -e "${RED}ERROR: rixhub is not running!${NC}"
    echo "Please start rixhub first: ~/.rix/bin/rixhub"
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
echo "Starting Bridge with 3 Bidirectional Bridges"
echo "========================================================================"
echo "  - String (bidirectional)"
echo "  - Int32 (bidirectional)"
echo "  - Pose (bidirectional)"
echo ""

# Start bridge
ros2 run rix_ros_bridge bridge_node \
    --config "$CONFIG_PATH" \
    --mappings "$MAPPINGS_PATH" \
    > /tmp/multibidir_bridge.log 2>&1 &

BRIDGE_PID=$!
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 3

if ! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}ERROR: Bridge failed to start!${NC}"
    cat /tmp/multibidir_bridge.log
    exit 1
fi

echo "Bridge running with 6 handles (3 bidirectional bridges × 2 handles each)"
echo "Waiting for bridge to fully initialize..."
sleep 3

# Test counters
TESTS_PASSED=0
TESTS_TOTAL=6

##############################################################################
echo ""
echo "========================================================================"
echo "Test 1/6: String ROS→RIX"
echo "========================================================================"

(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('string_ros_to_rix')
def cb(msg):
    print(f'✓ RIX received String: {msg.data}', flush=True)
sub = node.create_subscriber(String, '/bidir_string_rix', cb)
time.sleep(1)
start = time.time()
while time.time() - start < 4 and node.ok():
    node.spin_once()
node.shutdown()
" > /tmp/test1.log 2>&1) &
PID=$!

sleep 3
ros2 topic pub /bidir_string std_msgs/msg/String 'data: "Test String ROS→RIX"' --once
sleep 2
wait $PID 2>/dev/null || true
sleep 1

if grep -q "RIX received String" /tmp/test1.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Test 2/6: String RIX→ROS"
echo "========================================================================"

# Publish from RIX in background to establish topic
(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('string_rix_to_ros')
pub = node.create_publisher(String, '/bidir_string_rix')
time.sleep(2)
msg = String()
msg.data = 'Test String RIX→ROS'
for i in range(5):
    pub.publish(msg)
    time.sleep(0.2)
time.sleep(1)
node.shutdown()
")

sleep 2
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true
sleep 1

if grep -q "Test String RIX" /tmp/test2.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Test 3/6: Int32 ROS→RIX"
echo "========================================================================"

(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import Int32
import time

node = Node('int32_ros_to_rix')
def cb(msg):
    print(f'✓ RIX received Int32: {msg.data}', flush=True)
sub = node.create_subscriber(Int32, '/bidir_int32_rix', cb)
time.sleep(1)
start = time.time()
while time.time() - start < 4 and node.ok():
    node.spin_once()
node.shutdown()
" > /tmp/test3.log 2>&1) &
PID=$!

sleep 3
ros2 topic pub /bidir_int32 std_msgs/msg/Int32 'data: 42' --once
sleep 2
wait $PID 2>/dev/null || true
sleep 1

if grep -q "RIX received Int32: 42" /tmp/test3.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Test 4/6: Int32 RIX→ROS"
echo "========================================================================"

timeout 8 ros2 topic echo /bidir_int32 > /tmp/test4.log 2>&1 &
PID=$!
sleep 3

(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.standard import Int32
import time

node = Node('int32_rix_to_ros')
pub = node.create_publisher(Int32, '/bidir_int32_rix')
time.sleep(2)
msg = Int32()
msg.data = 99
for i in range(5):
    pub.publish(msg)
    time.sleep(0.2)
time.sleep(1)
node.shutdown()
")

sleep 2
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true
sleep 1

if grep -q "data: 99" /tmp/test4.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Test 5/6: Pose ROS→RIX"
echo "========================================================================"

(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -u -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.geometry import Pose
import time

node = Node('pose_ros_to_rix')
def cb(msg):
    print(f'✓ RIX received Pose: pos({msg.position.x}, {msg.position.y}, {msg.position.z})', flush=True)
sub = node.create_subscriber(Pose, '/bidir_pose_rix', cb)
time.sleep(1)
start = time.time()
while time.time() - start < 4 and node.ok():
    node.spin_once()
node.shutdown()
" > /tmp/test5.log 2>&1) &
PID=$!

sleep 3
ros2 topic pub /bidir_pose geometry_msgs/msg/Pose '{position: {x: 1.0, y: 2.0, z: 3.0}, orientation: {w: 1.0}}' --once
sleep 2
wait $PID 2>/dev/null || true
sleep 1

if grep -q "RIX received Pose" /tmp/test5.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Test 6/6: Pose RIX→ROS"
echo "========================================================================"

timeout 8 ros2 topic echo /bidir_pose > /tmp/test6.log 2>&1 &
PID=$!
sleep 3

(cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -c "
import sys
sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node
from rix.msg.geometry import Pose, Point, Quaternion
import time

node = Node('pose_rix_to_ros')
pub = node.create_publisher(Pose, '/bidir_pose_rix')
time.sleep(2)
msg = Pose()
msg.position = Point()
msg.position.x = 5.0
msg.position.y = 6.0
msg.position.z = 7.0
msg.orientation = Quaternion()
msg.orientation.w = 1.0
for i in range(5):
    pub.publish(msg)
    time.sleep(0.2)
time.sleep(1)
node.shutdown()
")

sleep 2
kill $PID 2>/dev/null || true
wait $PID 2>/dev/null || true
sleep 1

if grep -q "x: 5.0" /tmp/test6.log; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}✗ FAILED${NC}"
fi

##############################################################################
echo ""
echo "========================================================================"
echo "Cleanup"
echo "========================================================================"

kill $BRIDGE_PID 2>/dev/null || true
echo -e "${GREEN}✓ Bridge stopped${NC}"

echo ""
echo "========================================================================"
echo "FINAL RESULTS"
echo "========================================================================"
echo "Tests passed: $TESTS_PASSED/$TESTS_TOTAL"
echo ""

if [ $TESTS_PASSED -eq 6 ]; then
    echo -e "${GREEN}========================================================================"
    echo "ALL TESTS PASSED! ✓"
    echo "All 3 message types work bidirectionally:"
    echo "  ✓ String (ROS↔RIX)"
    echo "  ✓ Int32 (ROS↔RIX)"
    echo "  ✓ Pose (ROS↔RIX)"
    echo "========================================================================${NC}"
    exit 0
else
    echo -e "${RED}========================================================================"
    echo "SOME TESTS FAILED"
    echo "========================================================================${NC}"
    exit 1
fi
