#!/bin/bash
# Demo 2: Complete Test of All 26 Message Types (Unidirectional Bridges)
# Tests ROS→RIX and RIX→ROS for every supported message type with full message display

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=52  # 26 types × 2 directions

echo "========================================================================"
echo "DEMO 2: Complete Message Type Test (52 Unidirectional Bridges)"
echo "Testing all 26 message types in both directions with message display"
echo "========================================================================"

# Check rixhub
if ! pgrep -x "rixhub" > /dev/null; then
    echo -e "${RED}ERROR: rixhub not running!${NC}"
    echo "Start rixhub first: ~/.rix/bin/rixhub"
    exit 1
fi
echo -e "${GREEN}✓ rixhub running${NC}"

# Setup
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash 2>/dev/null
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
source install/setup.bash 2>/dev/null

CONFIG="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/demo2_config.json"
MAPPINGS="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json"

echo ""
echo "========================================================================"
echo "Starting Bridge with 52 Unidirectional Bridges"
echo "========================================================================"

ros2 run rix_ros_bridge bridge_node --config "$CONFIG" --mappings "$MAPPINGS" > /tmp/demo2_bridge.log 2>&1 &
BRIDGE_PID=$!
sleep 8

if ! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}Bridge failed to start!${NC}"
    cat /tmp/demo2_bridge.log
    exit 1
fi
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 3

# Test function for ROS→RIX
test_ros_to_rix() {
    local name=$1
    local ros_topic=$2
    local rix_topic=$3
    local ros_msg=$4
    local rix_check_script=$5
    local display_msg=$6
    local logfile="/tmp/demo2_${name}_ros_to_rix.log"
    
    echo -e "${CYAN}  ROS→RIX:${NC}"
    echo -e "    ${YELLOW}Sending to $ros_topic:${NC}"
    echo "    $display_msg"
    
    # Start RIX subscriber
    (cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -u -c "$rix_check_script" > "$logfile" 2>&1) &
    local pid=$!
    sleep 4
    
    # Publish from ROS
    eval "$ros_msg" > /dev/null 2>&1
    sleep 3
    
    # Let subscriber finish
    sleep 1
    wait $pid 2>/dev/null || true
    
    # Check result
    if [ -s "$logfile" ] && grep -q "✓" "$logfile"; then
        echo -e "    ${GREEN}✓ PASS${NC} - Message received on RIX side"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "    ${RED}✗ FAIL${NC} - No message received"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Test function for RIX→ROS  
test_rix_to_ros() {
    local name=$1
    local ros_topic=$2
    local rix_topic=$3
    local rix_pub_script=$4
    local ros_check=$5
    local display_msg=$6
    local logfile="/tmp/demo2_${name}_rix_to_ros.log"
    
    echo -e "${CYAN}  RIX→ROS:${NC}"
    echo -e "    ${YELLOW}Sending to $rix_topic:${NC}"
    echo "    $display_msg"
    
    # Start ROS subscriber
    timeout 10 ros2 topic echo "$ros_topic" > "$logfile" 2>&1 &
    local pid=$!
    sleep 4
    
    # Publish from RIX
    (cd ~/Desktop/ROB490/rix-py && PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -c "$rix_pub_script") &
    sleep 4
    
    # Kill subscriber
    kill $pid 2>/dev/null || true
    wait $pid 2>/dev/null || true
    
    # Check result
    if grep -q "$ros_check" "$logfile"; then
        echo -e "    ${GREEN}✓ PASS${NC} - Message received on ROS side"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "    ${RED}✗ FAIL${NC} - No message received"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo ""
echo "========================================================================"
echo "Testing std_msgs Types (14 types)"
echo "========================================================================"

# 1. String
echo -e "${BLUE}[1/26] String${NC}"
test_ros_to_rix "string" "/demo/string_from_ros" "/demo/string_to_rix" \
    "ros2 topic pub /demo/string_from_ros std_msgs/msg/String 'data: \"Hello ROS\"' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import String; import time; n=Node('t'); n.create_subscriber(String, '/demo/string_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 'Hello ROS'"

test_rix_to_ros "string" "/demo/string_to_ros" "/demo/string_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import String; import time; n=Node('t'); p=n.create_publisher(String, '/demo/string_from_rix'); time.sleep(1); m=String(); m.data='Hello RIX'; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "Hello RIX" \
    "data: 'Hello RIX'"

# 2. Int32
echo -e "${BLUE}[2/26] Int32${NC}"
test_ros_to_rix "int32" "/demo/int32_from_ros" "/demo/int32_to_rix" \
    "ros2 topic pub /demo/int32_from_ros std_msgs/msg/Int32 'data: 42' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int32; import time; n=Node('t'); n.create_subscriber(Int32, '/demo/int32_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 42"

test_rix_to_ros "int32" "/demo/int32_to_ros" "/demo/int32_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int32; import time; n=Node('t'); p=n.create_publisher(Int32, '/demo/int32_from_rix'); time.sleep(1); m=Int32(); m.data=42; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 42" \
    "data: 42"

# 3. Int64
echo -e "${BLUE}[3/26] Int64${NC}"
test_ros_to_rix "int64" "/demo/int64_from_ros" "/demo/int64_to_rix" \
    "ros2 topic pub /demo/int64_from_ros std_msgs/msg/Int64 'data: 999999' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int64; import time; n=Node('t'); n.create_subscriber(Int64, '/demo/int64_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 999999"

test_rix_to_ros "int64" "/demo/int64_to_ros" "/demo/int64_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int64; import time; n=Node('t'); p=n.create_publisher(Int64, '/demo/int64_from_rix'); time.sleep(1); m=Int64(); m.data=999999; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 999999" \
    "data: 999999"

# 4. Int8
echo -e "${BLUE}[4/26] Int8${NC}"
test_ros_to_rix "int8" "/demo/int8_from_ros" "/demo/int8_to_rix" \
    "ros2 topic pub /demo/int8_from_ros std_msgs/msg/Int8 'data: 127' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int8; import time; n=Node('t'); n.create_subscriber(Int8, '/demo/int8_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 127"

test_rix_to_ros "int8" "/demo/int8_to_ros" "/demo/int8_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int8; import time; n=Node('t'); p=n.create_publisher(Int8, '/demo/int8_from_rix'); time.sleep(1); m=Int8(); m.data=127; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 127" \
    "data: 127"

# 5. Int16
echo -e "${BLUE}[5/26] Int16${NC}"
test_ros_to_rix "int16" "/demo/int16_from_ros" "/demo/int16_to_rix" \
    "ros2 topic pub /demo/int16_from_ros std_msgs/msg/Int16 'data: 32000' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int16; import time; n=Node('t'); n.create_subscriber(Int16, '/demo/int16_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 32000"

test_rix_to_ros "int16" "/demo/int16_to_ros" "/demo/int16_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Int16; import time; n=Node('t'); p=n.create_publisher(Int16, '/demo/int16_from_rix'); time.sleep(1); m=Int16(); m.data=32000; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 32000" \
    "data: 32000"

# 6. Float32
echo -e "${BLUE}[6/26] Float32${NC}"
test_ros_to_rix "float32" "/demo/float32_from_ros" "/demo/float32_to_rix" \
    "ros2 topic pub /demo/float32_from_ros std_msgs/msg/Float32 'data: 3.14159' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Float; import time; n=Node('t'); n.create_subscriber(Float, '/demo/float32_to_rix', lambda m: print(f'✓ Received: {m.data:.5f}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 3.14159"

test_rix_to_ros "float32" "/demo/float32_to_ros" "/demo/float32_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Float; import time; n=Node('t'); p=n.create_publisher(Float, '/demo/float32_from_rix'); time.sleep(1); m=Float(); m.data=3.14159; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 3.14" \
    "data: 3.14159"

# 7. Float64
echo -e "${BLUE}[7/26] Float64${NC}"
test_ros_to_rix "float64" "/demo/float64_from_ros" "/demo/float64_to_rix" \
    "ros2 topic pub /demo/float64_from_ros std_msgs/msg/Float64 'data: 2.71828' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Double; import time; n=Node('t'); n.create_subscriber(Double, '/demo/float64_to_rix', lambda m: print(f'✓ Received: {m.data:.5f}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 2.71828"

test_rix_to_ros "float64" "/demo/float64_to_ros" "/demo/float64_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Double; import time; n=Node('t'); p=n.create_publisher(Double, '/demo/float64_from_rix'); time.sleep(1); m=Double(); m.data=2.71828; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 2.71" \
    "data: 2.71828"

# 8. Bool
echo -e "${BLUE}[8/26] Bool${NC}"
test_ros_to_rix "bool" "/demo/bool_from_ros" "/demo/bool_to_rix" \
    "ros2 topic pub /demo/bool_from_ros std_msgs/msg/Bool 'data: true' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Bool; import time; n=Node('t'); n.create_subscriber(Bool, '/demo/bool_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: true"

test_rix_to_ros "bool" "/demo/bool_to_ros" "/demo/bool_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Bool; import time; n=Node('t'); p=n.create_publisher(Bool, '/demo/bool_from_rix'); time.sleep(1); m=Bool(); m.data=True; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: true" \
    "data: true"

# 9. UInt8
echo -e "${BLUE}[9/26] UInt8${NC}"
test_ros_to_rix "uint8" "/demo/uint8_from_ros" "/demo/uint8_to_rix" \
    "ros2 topic pub /demo/uint8_from_ros std_msgs/msg/UInt8 'data: 255' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt8; import time; n=Node('t'); n.create_subscriber(UInt8, '/demo/uint8_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 255"

test_rix_to_ros "uint8" "/demo/uint8_to_ros" "/demo/uint8_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt8; import time; n=Node('t'); p=n.create_publisher(UInt8, '/demo/uint8_from_rix'); time.sleep(1); m=UInt8(); m.data=255; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 255" \
    "data: 255"

# 10. UInt16
echo -e "${BLUE}[10/26] UInt16${NC}"
test_ros_to_rix "uint16" "/demo/uint16_from_ros" "/demo/uint16_to_rix" \
    "ros2 topic pub /demo/uint16_from_ros std_msgs/msg/UInt16 'data: 65000' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt16; import time; n=Node('t'); n.create_subscriber(UInt16, '/demo/uint16_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 65000"

test_rix_to_ros "uint16" "/demo/uint16_to_ros" "/demo/uint16_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt16; import time; n=Node('t'); p=n.create_publisher(UInt16, '/demo/uint16_from_rix'); time.sleep(1); m=UInt16(); m.data=65000; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 65000" \
    "data: 65000"

# 11. UInt32
echo -e "${BLUE}[11/26] UInt32${NC}"
test_ros_to_rix "uint32" "/demo/uint32_from_ros" "/demo/uint32_to_rix" \
    "ros2 topic pub /demo/uint32_from_ros std_msgs/msg/UInt32 'data: 4000000' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt32; import time; n=Node('t'); n.create_subscriber(UInt32, '/demo/uint32_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 4000000"

test_rix_to_ros "uint32" "/demo/uint32_to_ros" "/demo/uint32_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt32; import time; n=Node('t'); p=n.create_publisher(UInt32, '/demo/uint32_from_rix'); time.sleep(1); m=UInt32(); m.data=4000000; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 4000000" \
    "data: 4000000"

# 12. UInt64
echo -e "${BLUE}[12/26] UInt64${NC}"
test_ros_to_rix "uint64" "/demo/uint64_from_ros" "/demo/uint64_to_rix" \
    "ros2 topic pub /demo/uint64_from_ros std_msgs/msg/UInt64 'data: 18446744073' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt64; import time; n=Node('t'); n.create_subscriber(UInt64, '/demo/uint64_to_rix', lambda m: print(f'✓ Received: {m.data}', flush=True)); time.sleep(5); n.shutdown()" \
    "data: 18446744073"

test_rix_to_ros "uint64" "/demo/uint64_to_ros" "/demo/uint64_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import UInt64; import time; n=Node('t'); p=n.create_publisher(UInt64, '/demo/uint64_from_rix'); time.sleep(1); m=UInt64(); m.data=18446744073; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "data: 18446744073" \
    "data: 18446744073"

# 13. Header
echo -e "${BLUE}[13/26] Header${NC}"
test_ros_to_rix "header" "/demo/header_from_ros" "/demo/header_to_rix" \
    "ros2 topic pub /demo/header_from_ros std_msgs/msg/Header '{stamp: {sec: 100, nanosec: 500000000}, frame_id: \"map\"}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Header; import time; n=Node('t'); n.create_subscriber(Header, '/demo/header_to_rix', lambda m: print(f'✓ Received: stamp={m.stamp:.1f}, frame_id=\"{m.frame_id}\"', flush=True)); time.sleep(5); n.shutdown()" \
    "{stamp: {sec: 100, nanosec: 500000000}, frame_id: 'map'}"

test_rix_to_ros "header" "/demo/header_to_ros" "/demo/header_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(Header, '/demo/header_from_rix'); time.sleep(1); m=Header(); m.stamp=100.5; m.frame_id='map'; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: map" \
    "{stamp: {sec: 100, nanosec: 500000000}, frame_id: 'map'}"

# 14. ColorRGBA
echo -e "${BLUE}[14/26] ColorRGBA${NC}"
test_ros_to_rix "color" "/demo/color_from_ros" "/demo/color_to_rix" \
    "ros2 topic pub /demo/color_from_ros std_msgs/msg/ColorRGBA '{r: 1.0, g: 0.5, b: 0.25, a: 0.8}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Color; import time; n=Node('t'); n.create_subscriber(Color, '/demo/color_to_rix', lambda m: print(f'✓ Received: r={m.r}, g={m.g}, b={m.b}, a={m.a}', flush=True)); time.sleep(5); n.shutdown()" \
    "{r: 1.0, g: 0.5, b: 0.25, a: 0.8}"

test_rix_to_ros "color" "/demo/color_to_ros" "/demo/color_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.standard import Color; import time; n=Node('t'); p=n.create_publisher(Color, '/demo/color_from_rix'); time.sleep(1); m=Color(); m.r=1.0; m.g=0.5; m.b=0.25; m.a=0.8; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "r: 1.0" \
    "{r: 1.0, g: 0.5, b: 0.25, a: 0.8}"

echo ""
echo "========================================================================"
echo "Testing geometry_msgs Types (12 types)"
echo "========================================================================"

# 15. Point
echo -e "${BLUE}[15/26] Point${NC}"
test_ros_to_rix "point" "/demo/point_from_ros" "/demo/point_to_rix" \
    "ros2 topic pub /demo/point_from_ros geometry_msgs/msg/Point '{x: 1.0, y: 2.0, z: 3.0}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Point; import time; n=Node('t'); n.create_subscriber(Point, '/demo/point_to_rix', lambda m: print(f'✓ Received: x={m.x}, y={m.y}, z={m.z}', flush=True)); time.sleep(5); n.shutdown()" \
    "{x: 1.0, y: 2.0, z: 3.0}"

test_rix_to_ros "point" "/demo/point_to_ros" "/demo/point_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Point; import time; n=Node('t'); p=n.create_publisher(Point, '/demo/point_from_rix'); time.sleep(1); m=Point(); m.x=1.0; m.y=2.0; m.z=3.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "x: 1.0" \
    "{x: 1.0, y: 2.0, z: 3.0}"

# 16. Quaternion
echo -e "${BLUE}[16/26] Quaternion${NC}"
test_ros_to_rix "quaternion" "/demo/quaternion_from_ros" "/demo/quaternion_to_rix" \
    "ros2 topic pub /demo/quaternion_from_ros geometry_msgs/msg/Quaternion '{x: 0.0, y: 0.0, z: 0.0, w: 1.0}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Quaternion; import time; n=Node('t'); n.create_subscriber(Quaternion, '/demo/quaternion_to_rix', lambda m: print(f'✓ Received: x={m.x}, y={m.y}, z={m.z}, w={m.w}', flush=True)); time.sleep(5); n.shutdown()" \
    "{x: 0.0, y: 0.0, z: 0.0, w: 1.0}"

test_rix_to_ros "quaternion" "/demo/quaternion_to_ros" "/demo/quaternion_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Quaternion; import time; n=Node('t'); p=n.create_publisher(Quaternion, '/demo/quaternion_from_rix'); time.sleep(1); m=Quaternion(); m.x=0; m.y=0; m.z=0; m.w=1.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "w: 1.0" \
    "{x: 0.0, y: 0.0, z: 0.0, w: 1.0}"

# 17. Vector3
echo -e "${BLUE}[17/26] Vector3${NC}"
test_ros_to_rix "vector3" "/demo/vector3_from_ros" "/demo/vector3_to_rix" \
    "ros2 topic pub /demo/vector3_from_ros geometry_msgs/msg/Vector3 '{x: 1.5, y: 2.5, z: 3.5}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Vector3; import time; n=Node('t'); n.create_subscriber(Vector3, '/demo/vector3_to_rix', lambda m: print(f'✓ Received: x={m.x}, y={m.y}, z={m.z}', flush=True)); time.sleep(5); n.shutdown()" \
    "{x: 1.5, y: 2.5, z: 3.5}"

test_rix_to_ros "vector3" "/demo/vector3_to_ros" "/demo/vector3_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Vector3; import time; n=Node('t'); p=n.create_publisher(Vector3, '/demo/vector3_from_rix'); time.sleep(1); m=Vector3(); m.x=1.5; m.y=2.5; m.z=3.5; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "x: 1.5" \
    "{x: 1.5, y: 2.5, z: 3.5}"

# 18. Pose
echo -e "${BLUE}[18/26] Pose${NC}"
test_ros_to_rix "pose" "/demo/pose_from_ros" "/demo/pose_to_rix" \
    "ros2 topic pub /demo/pose_from_ros geometry_msgs/msg/Pose '{position: {x: 10.0, y: 20.0, z: 30.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Pose; import time; n=Node('t'); n.create_subscriber(Pose, '/demo/pose_to_rix', lambda m: print(f'✓ Received: pos=({m.position.x}, {m.position.y}, {m.position.z}), quat=({m.orientation.x}, {m.orientation.y}, {m.orientation.z}, {m.orientation.w})', flush=True)); time.sleep(5); n.shutdown()" \
    "{position: {x: 10.0, y: 20.0, z: 30.0}, orientation: {w: 1.0}}"

test_rix_to_ros "pose" "/demo/pose_to_ros" "/demo/pose_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Pose, Point, Quaternion; import time; n=Node('t'); p=n.create_publisher(Pose, '/demo/pose_from_rix'); time.sleep(1); m=Pose(); m.position=Point(); m.position.x=10.0; m.position.y=20.0; m.position.z=30.0; m.orientation=Quaternion(); m.orientation.w=1.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "x: 10.0" \
    "{position: {x: 10.0, y: 20.0, z: 30.0}, orientation: {w: 1.0}}"

# 19. Twist
echo -e "${BLUE}[19/26] Twist${NC}"
test_ros_to_rix "twist" "/demo/twist_from_ros" "/demo/twist_to_rix" \
    "ros2 topic pub /demo/twist_from_ros geometry_msgs/msg/Twist '{linear: {x: 1.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.5}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Twist; import time; n=Node('t'); n.create_subscriber(Twist, '/demo/twist_to_rix', lambda m: print(f'✓ Received: linear=({m.linear.x}, {m.linear.y}, {m.linear.z}), angular=({m.angular.x}, {m.angular.y}, {m.angular.z})', flush=True)); time.sleep(5); n.shutdown()" \
    "{linear: {x: 1.0}, angular: {z: 0.5}}"

test_rix_to_ros "twist" "/demo/twist_to_ros" "/demo/twist_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Twist, Vector3; import time; n=Node('t'); p=n.create_publisher(Twist, '/demo/twist_from_rix'); time.sleep(1); m=Twist(); m.linear=Vector3(); m.linear.x=1.0; m.angular=Vector3(); m.angular.z=0.5; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "x: 1.0" \
    "{linear: {x: 1.0}, angular: {z: 0.5}}"

# 20. Transform
echo -e "${BLUE}[20/26] Transform${NC}"
test_ros_to_rix "transform" "/demo/transform_from_ros" "/demo/transform_to_rix" \
    "ros2 topic pub /demo/transform_from_ros geometry_msgs/msg/Transform '{translation: {x: 5.0, y: 6.0, z: 7.0}, rotation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Transform; import time; n=Node('t'); n.create_subscriber(Transform, '/demo/transform_to_rix', lambda m: print(f'✓ Received: trans=({m.translation.x}, {m.translation.y}, {m.translation.z}), rot=({m.rotation.x}, {m.rotation.y}, {m.rotation.z}, {m.rotation.w})', flush=True)); time.sleep(5); n.shutdown()" \
    "{translation: {x: 5.0, y: 6.0, z: 7.0}, rotation: {w: 1.0}}"

test_rix_to_ros "transform" "/demo/transform_to_ros" "/demo/transform_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Transform, Vector3, Quaternion; import time; n=Node('t'); p=n.create_publisher(Transform, '/demo/transform_from_rix'); time.sleep(1); m=Transform(); m.translation=Vector3(); m.translation.x=5.0; m.translation.y=6.0; m.translation.z=7.0; m.rotation=Quaternion(); m.rotation.w=1.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "x: 5.0" \
    "{translation: {x: 5.0, y: 6.0, z: 7.0}, rotation: {w: 1.0}}"

# 21. PoseStamped
echo -e "${BLUE}[21/26] PoseStamped${NC}"
test_ros_to_rix "pose_stamped" "/demo/pose_stamped_from_ros" "/demo/pose_stamped_to_rix" \
    "ros2 topic pub /demo/pose_stamped_from_ros geometry_msgs/msg/PoseStamped '{header: {frame_id: \"map\"}, pose: {position: {x: 100.0}, orientation: {w: 1.0}}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import PoseStamped; import time; n=Node('t'); n.create_subscriber(PoseStamped, '/demo/pose_stamped_to_rix', lambda m: print(f'✓ Received: frame=\"{m.header.frame_id}\", pos.x={m.pose.position.x}', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'map'}, pose: {position: {x: 100.0}, orientation: {w: 1.0}}}"

test_rix_to_ros "pose_stamped" "/demo/pose_stamped_to_ros" "/demo/pose_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import PoseStamped, Pose, Point, Quaternion; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(PoseStamped, '/demo/pose_stamped_from_rix'); time.sleep(1); m=PoseStamped(); m.header=Header(); m.header.frame_id='map'; m.pose=Pose(); m.pose.position=Point(); m.pose.position.x=100.0; m.pose.orientation=Quaternion(); m.pose.orientation.w=1.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: map" \
    "{header: {frame_id: 'map'}, pose: {position: {x: 100.0}}}"

# 22. PointStamped
echo -e "${BLUE}[22/26] PointStamped${NC}"
test_ros_to_rix "point_stamped" "/demo/point_stamped_from_ros" "/demo/point_stamped_to_rix" \
    "ros2 topic pub /demo/point_stamped_from_ros geometry_msgs/msg/PointStamped '{header: {frame_id: \"base\"}, point: {x: 50.0, y: 60.0, z: 70.0}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import PointStamped; import time; n=Node('t'); n.create_subscriber(PointStamped, '/demo/point_stamped_to_rix', lambda m: print(f'✓ Received: frame=\"{m.header.frame_id}\", point=({m.point.x}, {m.point.y}, {m.point.z})', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'base'}, point: {x: 50.0, y: 60.0, z: 70.0}}"

test_rix_to_ros "point_stamped" "/demo/point_stamped_to_ros" "/demo/point_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import PointStamped, Point; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(PointStamped, '/demo/point_stamped_from_rix'); time.sleep(1); m=PointStamped(); m.header=Header(); m.header.frame_id='base'; m.point=Point(); m.point.x=50.0; m.point.y=60.0; m.point.z=70.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: base" \
    "{header: {frame_id: 'base'}, point: {x: 50.0, y: 60.0, z: 70.0}}"

# 23. QuaternionStamped
echo -e "${BLUE}[23/26] QuaternionStamped${NC}"
test_ros_to_rix "quaternion_stamped" "/demo/quaternion_stamped_from_ros" "/demo/quaternion_stamped_to_rix" \
    "ros2 topic pub /demo/quaternion_stamped_from_ros geometry_msgs/msg/QuaternionStamped '{header: {frame_id: \"odom\"}, quaternion: {x: 0.0, y: 0.0, z: 0.707, w: 0.707}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import QuaternionStamped; import time; n=Node('t'); n.create_subscriber(QuaternionStamped, '/demo/quaternion_stamped_to_rix', lambda m: print(f'✓ Received: frame=\"{m.header.frame_id}\", quat=({m.quaternion.x}, {m.quaternion.y}, {m.quaternion.z:.3f}, {m.quaternion.w:.3f})', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'odom'}, quaternion: {z: 0.707, w: 0.707}}"

test_rix_to_ros "quaternion_stamped" "/demo/quaternion_stamped_to_ros" "/demo/quaternion_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import QuaternionStamped, Quaternion; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(QuaternionStamped, '/demo/quaternion_stamped_from_rix'); time.sleep(1); m=QuaternionStamped(); m.header=Header(); m.header.frame_id='odom'; m.quaternion=Quaternion(); m.quaternion.z=0.707; m.quaternion.w=0.707; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: odom" \
    "{header: {frame_id: 'odom'}, quaternion: {z: 0.707, w: 0.707}}"

# 24. Vector3Stamped
echo -e "${BLUE}[24/26] Vector3Stamped${NC}"
test_ros_to_rix "vector3_stamped" "/demo/vector3_stamped_from_ros" "/demo/vector3_stamped_to_rix" \
    "ros2 topic pub /demo/vector3_stamped_from_ros geometry_msgs/msg/Vector3Stamped '{header: {frame_id: \"sensor\"}, vector: {x: 9.8, y: 0.0, z: 0.0}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Vector3Stamped; import time; n=Node('t'); n.create_subscriber(Vector3Stamped, '/demo/vector3_stamped_to_rix', lambda m: print(f'✓ Received: frame=\"{m.header.frame_id}\", vector=({m.vector.x}, {m.vector.y}, {m.vector.z})', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'sensor'}, vector: {x: 9.8, y: 0.0, z: 0.0}}"

test_rix_to_ros "vector3_stamped" "/demo/vector3_stamped_to_ros" "/demo/vector3_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import Vector3Stamped, Vector3; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(Vector3Stamped, '/demo/vector3_stamped_from_rix'); time.sleep(1); m=Vector3Stamped(); m.header=Header(); m.header.frame_id='sensor'; m.vector=Vector3(); m.vector.x=9.8; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: sensor" \
    "{header: {frame_id: 'sensor'}, vector: {x: 9.8}}"

# 25. TransformStamped
echo -e "${BLUE}[25/26] TransformStamped${NC}"
test_ros_to_rix "transform_stamped" "/demo/transform_stamped_from_ros" "/demo/transform_stamped_to_rix" \
    "ros2 topic pub /demo/transform_stamped_from_ros geometry_msgs/msg/TransformStamped '{header: {frame_id: \"world\"}, child_frame_id: \"robot\", transform: {translation: {x: 1.0, y: 2.0, z: 3.0}, rotation: {w: 1.0}}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import TransformStamped; import time; n=Node('t'); n.create_subscriber(TransformStamped, '/demo/transform_stamped_to_rix', lambda m: print(f'✓ Received: {m.header.frame_id}->{m.child_frame_id}, trans=({m.transform.translation.x}, {m.transform.translation.y}, {m.transform.translation.z})', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'world'}, child_frame_id: 'robot', transform: {translation: {x: 1.0, y: 2.0, z: 3.0}}}"

test_rix_to_ros "transform_stamped" "/demo/transform_stamped_to_ros" "/demo/transform_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import TransformStamped, Transform, Vector3, Quaternion; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(TransformStamped, '/demo/transform_stamped_from_rix'); time.sleep(1); m=TransformStamped(); m.header=Header(); m.header.frame_id='world'; m.child_frame_id='robot'; m.transform=Transform(); m.transform.translation=Vector3(); m.transform.translation.x=1.0; m.transform.translation.y=2.0; m.transform.translation.z=3.0; m.transform.rotation=Quaternion(); m.transform.rotation.w=1.0; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "child_frame_id: robot" \
    "{header: {frame_id: 'world'}, child_frame_id: 'robot', transform: {translation: {x: 1.0, y: 2.0, z: 3.0}}}"

# 26. TwistStamped
echo -e "${BLUE}[26/26] TwistStamped${NC}"
test_ros_to_rix "twist_stamped" "/demo/twist_stamped_from_ros" "/demo/twist_stamped_to_rix" \
    "ros2 topic pub /demo/twist_stamped_from_ros geometry_msgs/msg/TwistStamped '{header: {frame_id: \"base_link\"}, twist: {linear: {x: 1.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}}}' --qos-durability volatile --once" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import TwistStamped; import time; n=Node('t'); n.create_subscriber(TwistStamped, '/demo/twist_stamped_to_rix', lambda m: print(f'✓ Received: frame=\"{m.header.frame_id}\", linear.x={m.twist.linear.x}, angular.z={m.twist.angular.z}', flush=True)); time.sleep(5); n.shutdown()" \
    "{header: {frame_id: 'base_link'}, twist: {linear: {x: 1.5}, angular: {z: 0.3}}}"

test_rix_to_ros "twist_stamped" "/demo/twist_stamped_to_ros" "/demo/twist_stamped_from_rix" \
    "import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix'); from rix.core import Node; from rix.msg.geometry import TwistStamped, Twist, Vector3; from rix.msg.standard import Header; import time; n=Node('t'); p=n.create_publisher(TwistStamped, '/demo/twist_stamped_from_rix'); time.sleep(1); m=TwistStamped(); m.header=Header(); m.header.frame_id='base_link'; m.twist=Twist(); m.twist.linear=Vector3(); m.twist.linear.x=1.5; m.twist.angular=Vector3(); m.twist.angular.z=0.3; [p.publish(m) for _ in range(5)]; time.sleep(1); n.shutdown()" \
    "frame_id: base_link" \
    "{header: {frame_id: 'base_link'}, twist: {linear: {x: 1.5}, angular: {z: 0.3}}}"

# Cleanup
echo ""
echo "========================================================================"
echo "Cleanup"
echo "========================================================================"
kill $BRIDGE_PID 2>/dev/null || true
echo -e "${GREEN}✓ Bridge stopped${NC}"

# Final results
echo ""
echo "========================================================================"
echo "FINAL RESULTS"
echo "========================================================================"
echo -e "Tests passed: ${GREEN}$PASSED${NC}/$TOTAL"
echo -e "Tests failed: ${RED}$FAILED${NC}/$TOTAL"
echo ""

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}========================================================================"
    echo "🎉 ALL 26 MESSAGE TYPES WORK BIDIRECTIONALLY! 🎉"
    echo "Complete Phase 2 implementation verified!"
    echo "========================================================================"
    echo "${NC}"
    exit 0
else
    PCT=$((PASSED * 100 / TOTAL))
    echo -e "${YELLOW}========================================================================"
    echo "Demo completed with $PCT% success rate"
    echo "========================================================================"
    echo "${NC}"
    exit 1
fi
