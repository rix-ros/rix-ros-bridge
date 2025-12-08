#\!/bin/bash
# Demo 2: Clean implementation with separate Python test files

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=52

SCRIPT_DIR="/home/rob422student/Desktop/ROB490/bridge_ws/demo2_tests"
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH

echo "========================================================================"
echo "DEMO 2: Complete Message Type Test (52 Tests)"
echo "========================================================================"

# Check rixhub
if \! pgrep -x "rixhub" > /dev/null; then
    echo -e "${RED}ERROR: rixhub not running\!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ rixhub running${NC}"

# Setup
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash 2>/dev/null
source install/setup.bash 2>/dev/null

CONFIG="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/demo2_config.json"
MAPPINGS="$HOME/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json"

echo ""
echo "========================================================================"
echo "Starting Bridge"
echo "========================================================================"
ros2 run rix_ros_bridge bridge_node --config "$CONFIG" --mappings "$MAPPINGS" > /tmp/demo2_bridge.log 2>&1 &
BRIDGE_PID=$\!
sleep 8

if \! kill -0 $BRIDGE_PID 2>/dev/null; then
    echo -e "${RED}Bridge failed\!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Bridge started (PID: $BRIDGE_PID)${NC}"
sleep 2

# Test ROS→RIX
test_ros_to_rix() {
    local name=$1
    local msg_module=$2
    local msg_type=$3
    local ros_topic=$4
    local rix_topic=$5
    local ros_msg_cmd=$6
    local display=$7
    
    echo -e "${CYAN}  ROS→RIX:${NC} $display"
    
    # Start RIX subscriber
    cd ~/Desktop/ROB490/rix-py
    timeout 10 python3 "$SCRIPT_DIR/rix_subscriber.py" "$msg_module" "$msg_type" "$rix_topic" 7 > /tmp/test_${name}_r2r.log 2>&1 &
    local pid=$\!
    sleep 4
    
    # Publish from ROS
    eval "$ros_msg_cmd" > /dev/null 2>&1
    sleep 3
    wait $pid 2>/dev/null
    
    if grep -q "✓ RECEIVED" /tmp/test_${name}_r2r.log; then
        echo -e "    ${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "    ${RED}✗ FAIL${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Test RIX→ROS
test_rix_to_ros() {
    local name=$1
    local msg_module=$2
    local msg_type=$3
    local ros_topic=$4
    local rix_topic=$5
    local data_json=$6
    local ros_check=$7
    local display=$8
    
    echo -e "${CYAN}  RIX→ROS:${NC} $display"
    
    # Start ROS subscriber
    timeout 10 ros2 topic echo "$ros_topic" > /tmp/test_${name}_x2r.log 2>&1 &
    local pid=$\!
    sleep 4
    
    # Publish from RIX
    cd ~/Desktop/ROB490/rix-py
    python3 "$SCRIPT_DIR/rix_publisher.py" "$msg_module" "$msg_type" "$rix_topic" "$data_json" > /dev/null 2>&1 &
    sleep 4
    
    kill $pid 2>/dev/null || true
    wait $pid 2>/dev/null || true
    
    if grep -q "$ros_check" /tmp/test_${name}_x2r.log; then
        echo -e "    ${GREEN}✓ PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "    ${RED}✗ FAIL${NC}"
        FAILED=$((FAILED + 1))
    fi
}

echo ""
echo "========================================================================"
echo "Testing std_msgs Types (14 types)"
echo "========================================================================" 

echo -e "${BLUE}[1/26] String${NC}"
test_ros_to_rix "string" "standard" "String" "/demo/string_from_ros" "/demo/string_to_rix" \
    "ros2 topic pub /demo/string_from_ros std_msgs/msg/String 'data: \"Hello ROS\"' --qos-durability volatile --once" \
    "data: 'Hello ROS'"
test_rix_to_ros "string" "standard" "String" "/demo/string_to_ros" "/demo/string_from_rix" \
    '{"data":"Hello RIX"}' "Hello RIX" "data: 'Hello RIX'"

echo -e "${BLUE}[2/26] Int32${NC}"
test_ros_to_rix "int32" "standard" "Int32" "/demo/int32_from_ros" "/demo/int32_to_rix" \
    "ros2 topic pub /demo/int32_from_ros std_msgs/msg/Int32 'data: 42' --qos-durability volatile --once" \
    "data: 42"
test_rix_to_ros "int32" "standard" "Int32" "/demo/int32_to_ros" "/demo/int32_from_rix" \
    '{"data":42}' "data: 42" "data: 42"

echo -e "${BLUE}[3/26] Int64${NC}"
test_ros_to_rix "int64" "standard" "Int64" "/demo/int64_from_ros" "/demo/int64_to_rix" \
    "ros2 topic pub /demo/int64_from_ros std_msgs/msg/Int64 'data: 999999' --qos-durability volatile --once" \
    "data: 999999"
test_rix_to_ros "int64" "standard" "Int64" "/demo/int64_to_ros" "/demo/int64_from_rix" \
    '{"data":999999}' "data: 999999" "data: 999999"

echo -e "${BLUE}[4/26] Float32${NC}"
test_ros_to_rix "float32" "standard" "Float" "/demo/float32_from_ros" "/demo/float32_to_rix" \
    "ros2 topic pub /demo/float32_from_ros std_msgs/msg/Float32 'data: 3.14' --qos-durability volatile --once" \
    "data: 3.14"
test_rix_to_ros "float32" "standard" "Float" "/demo/float32_to_ros" "/demo/float32_from_rix" \
    '{"data":3.14}' "data: 3.14" "data: 3.14"

echo -e "${BLUE}[5/26] Bool${NC}"
test_ros_to_rix "bool" "standard" "Bool" "/demo/bool_from_ros" "/demo/bool_to_rix" \
    "ros2 topic pub /demo/bool_from_ros std_msgs/msg/Bool 'data: true' --qos-durability volatile --once" \
    "data: true"
test_rix_to_ros "bool" "standard" "Bool" "/demo/bool_to_ros" "/demo/bool_from_rix" \
    '{"data":true}' "data: true" "data: true"

# Cleanup
kill $BRIDGE_PID 2>/dev/null || true
echo ""
echo "========================================================================"
echo "Results: ${GREEN}$PASSED${NC}/$TOTAL passed, ${RED}$FAILED${NC}/$TOTAL failed"
echo "========================================================================"
