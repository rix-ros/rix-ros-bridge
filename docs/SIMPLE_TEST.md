# Simple Manual Integration Test

## Test Results

Run these commands to verify the bridge works:

---

## Terminal 1: Start Bridge
```bash
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
source install/setup.bash

ros2 run rix_ros_bridge bridge_node \
  --config /home/rob422student/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/bridge_config.json \
  --mappings /home/rob422student/Desktop/ROB490/bridge_ws/src/rix_ros_bridge/config/message_mappings.json
```

**Expected:** You should see:
- "Factory supports 18 message types"
- "Bridge 'string_bridge' created successfully"
- "Bridge 'string_echo_bridge' created successfully"
- "All bridges created successfully. Total handles: 2"

---

## Test 1: ROS → RIX

**Terminal 2: Start RIX Subscriber**
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 examples/test_bridge_subscriber.py
```

**Terminal 3: Publish ROS Message**
```bash
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic pub /chatter std_msgs/msg/String 'data: "Hello from ROS"' --once
```

**✓ PASS if Terminal 2 shows:** `✓ Received from ROS bridge: 'Hello from ROS'`

---

## Test 2: RIX → ROS

**Terminal 2: Start ROS Subscriber** (Stop RIX subscriber with Ctrl+C first)
```bash
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 topic echo /chatter_from_rix
```

**Terminal 3: Publish RIX Message** 
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH python3 -c "
from rix.core import Node
from rix.msg.standard import String
import time

node = Node('test_pub')
pub = node.create_publisher(String, '/chatter')
time.sleep(1)

msg = String()
msg.data = 'Hello from RIX'
pub.publish(msg)
print('Published:', msg.data)

time.sleep(1)
node.shutdown()
"
```

**✓ PASS if Terminal 2 shows:** `data: Hello from RIX`

---

## Quick Verification Commands

**Check ROS topics:**
```bash
ros2 topic list
# Should show: /chatter, /chatter_from_rix
```

**Check bridge is running:**
```bash
ps aux | grep rix_ros_bridge | grep -v grep
```

---

## Summary

- ✅ ROS → RIX: Messages published to `/chatter` appear on `/chatter_from_ros`
- ✅ RIX → ROS: Messages published to RIX `/chatter` appear on ROS `/chatter_from_rix`
- ✅ Bridge handles 2 configured bridges simultaneously
- ✅ Multi-threaded executor allows parallel processing
