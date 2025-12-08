#!/bin/bash
# Coordinated Demo - Publishes test messages (subscribers must be running in other terminals)

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo "========================================================================="
echo "COORDINATED DEMO: Publishing Test Messages"
echo "========================================================================="
echo ""
echo "⚠️  PREREQUISITE: Subscribers must be running in other terminals!"
echo "   See: TERMINAL_SETUP.md for instructions"
echo ""
read -p "Press Enter when subscribers are ready..."

cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH

PASSED=0
FAILED=0

echo ""
echo "========================================================================="
echo "Testing RIX→ROS Direction (5 types)"
echo "========================================================================="

# Test 1: String
echo -e "${BLUE}[1/10] String (RIX→ROS)${NC}"
cd ~/Desktop/ROB490/rix-py
python3 << 'EOF' 2>/dev/null
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import String; import time
n=Node('demo'); p=n.create_publisher(String, '/demo/string_from_rix'); time.sleep(1)
m=String(); m.data='Hello from RIX'
for i in range(3): p.publish(m); p.spin_once(); time.sleep(0.3)
n.shutdown()
EOF
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 2 for 'Hello from RIX'"
sleep 2

# Test 2: Int32
echo -e "${BLUE}[2/10] Int32 (RIX→ROS)${NC}"
python3 << 'EOF' 2>/dev/null
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import Int32; import time
n=Node('demo'); p=n.create_publisher(Int32, '/demo/int32_from_rix'); time.sleep(1)
m=Int32(); m.data=42
for i in range(3): p.publish(m); p.spin_once(); time.sleep(0.3)
n.shutdown()
EOF
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 3 for data: 42"
sleep 2

# Test 3: Float32
echo -e "${BLUE}[3/10] Float32 (RIX→ROS)${NC}"
python3 << 'EOF' 2>/dev/null
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import Float; import time
n=Node('demo'); p=n.create_publisher(Float, '/demo/float32_from_rix'); time.sleep(1)
m=Float(); m.data=3.14159
for i in range(3): p.publish(m); p.spin_once(); time.sleep(0.3)
n.shutdown()
EOF
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 4 for data: 3.14159"
sleep 2

# Test 4: Point
echo -e "${BLUE}[4/10] Point (RIX→ROS)${NC}"
python3 << 'EOF' 2>/dev/null
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.geometry import Point; import time
n=Node('demo'); p=n.create_publisher(Point, '/demo/point_from_rix'); time.sleep(1)
m=Point(); m.x=1.0; m.y=2.0; m.z=3.0
for i in range(3): p.publish(m); p.spin_once(); time.sleep(0.3)
n.shutdown()
EOF
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 5 for x:1.0, y:2.0, z:3.0"
sleep 2

# Test 5: Pose
echo -e "${BLUE}[5/10] Pose (RIX→ROS)${NC}"
python3 << 'EOF' 2>/dev/null
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.geometry import Pose, Point, Quaternion; import time
n=Node('demo'); p=n.create_publisher(Pose, '/demo/pose_from_rix'); time.sleep(1)
m=Pose(); m.position=Point(); m.position.x=10.0; m.position.y=20.0; m.position.z=30.0
m.orientation=Quaternion(); m.orientation.w=1.0
for i in range(3): p.publish(m); p.spin_once(); time.sleep(0.3)
n.shutdown()
EOF
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 6 for position (10,20,30)"
sleep 2

echo ""
echo "========================================================================="
echo "Testing ROS→RIX Direction (5 types)"
echo "========================================================================="
echo -e "${YELLOW}Note: Bridge will convert, but RIX subscribers may not receive (known IPC issue)${NC}"
echo ""

# Test 6: String
echo -e "${BLUE}[6/10] String (ROS→RIX)${NC}"
cd ~/Desktop/ROB490/bridge_ws
ros2 topic pub /demo/string_from_ros std_msgs/msg/String 'data: "Hello from ROS"' --qos-durability volatile --once 2>/dev/null &
sleep 2
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 7 for 'Hello from ROS' (or check bridge log)"
sleep 1

# Test 7: Int32
echo -e "${BLUE}[7/10] Int32 (ROS→RIX)${NC}"
ros2 topic pub /demo/int32_from_ros std_msgs/msg/Int32 'data: 99' --qos-durability volatile --once 2>/dev/null &
sleep 2
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 8 for data: 99 (or check bridge log)"
sleep 1

# Test 8: Float32
echo -e "${BLUE}[8/10] Float32 (ROS→RIX)${NC}"
ros2 topic pub /demo/float32_from_ros std_msgs/msg/Float32 'data: 2.71828' --qos-durability volatile --once 2>/dev/null &
sleep 2
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 9 for data: 2.71828 (or check bridge log)"
sleep 1

# Test 9: Point
echo -e "${BLUE}[9/10] Point (ROS→RIX)${NC}"
ros2 topic pub /demo/point_from_ros geometry_msgs/msg/Point '{x: 5.0, y: 6.0, z: 7.0}' --qos-durability volatile --once 2>/dev/null &
sleep 2
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 10 for (5,6,7) (or check bridge log)"
sleep 1

# Test 10: Pose
echo -e "${BLUE}[10/10] Pose (ROS→RIX)${NC}"
ros2 topic pub /demo/pose_from_ros geometry_msgs/msg/Pose '{position: {x: 100.0, y: 200.0, z: 300.0}, orientation: {w: 1.0}}' --qos-durability volatile --once 2>/dev/null &
sleep 2
echo -e "  ${GREEN}✓ Published${NC} - Check Terminal 11 for position (100,200,300) (or check bridge log)"
sleep 1

echo ""
echo "========================================================================="
echo "Demo Complete!"
echo "========================================================================="
echo ""
echo "Summary:"
echo "  - RIX→ROS: Check terminals 2-6 for received messages"
echo "  - ROS→RIX: Check terminals 7-11 (or Terminal 1 bridge log for conversion)"
echo ""
