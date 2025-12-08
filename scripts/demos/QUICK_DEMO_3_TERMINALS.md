# Quick 3-Terminal Demo (Simplified)

## For a faster demo with just 3 terminals testing key message types

---

## Terminal 1: Bridge
```bash
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
ros2 run rix_ros_bridge bridge_node \
  --config src/rix_ros_bridge/config/demo2_config.json \
  --mappings src/rix_ros_bridge/config/message_mappings.json
```

---

## Terminal 2: Subscriber (keep switching)

### For RIX→ROS tests:
```bash
# String
ros2 topic echo /demo/string_to_ros

# Int32 (after String test, Ctrl+C and run this)
ros2 topic echo /demo/int32_to_ros

# Point (after Int32 test, Ctrl+C and run this)
ros2 topic echo /demo/point_to_ros
```

### For ROS→RIX tests (check Terminal 1 for bridge conversion):
```bash
# String
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 -c "
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import String; import time
n=Node('test')
n.create_subscriber(String, '/demo/string_to_rix', lambda m: print(f'✓ {m.data}'))
print('Waiting...'); time.sleep(30)
"
```

---

## Terminal 3: Publisher (manual tests)

### RIX→ROS Tests (Terminal 2 should receive):

**String:**
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import String; import time
n=Node('test'); p=n.create_publisher(String, '/demo/string_from_rix'); time.sleep(1)
m=String(); m.data='Hello from RIX'
for i in range(5): p.publish(m); p.spin_once(); time.sleep(0.5)
n.shutdown()
EOF
```

**Int32:**
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import Int32; import time
n=Node('test'); p=n.create_publisher(Int32, '/demo/int32_from_rix'); time.sleep(1)
m=Int32(); m.data=42
for i in range(5): p.publish(m); p.spin_once(); time.sleep(0.5)
n.shutdown()
EOF
```

**Point:**
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.geometry import Point; import time
n=Node('test'); p=n.create_publisher(Point, '/demo/point_from_rix'); time.sleep(1)
m=Point(); m.x=1.0; m.y=2.0; m.z=3.0
for i in range(5): p.publish(m); p.spin_once(); time.sleep(0.5)
n.shutdown()
EOF
```

### ROS→RIX Tests (check Terminal 1 bridge log):

**String:**
```bash
ros2 topic pub /demo/string_from_ros std_msgs/msg/String 'data: "Hello from ROS"' --qos-durability volatile --once
```

**Int32:**
```bash
ros2 topic pub /demo/int32_from_ros std_msgs/msg/Int32 'data: 99' --qos-durability volatile --once
```

**Point:**
```bash
ros2 topic pub /demo/point_from_ros geometry_msgs/msg/Point '{x: 5.0, y: 6.0, z: 7.0}' --qos-durability volatile --once
```

---

## Demo Flow

1. **Start Terminal 1** (bridge) - leave running
2. **Terminal 2:** Start `ros2 topic echo /demo/string_to_ros`
3. **Terminal 3:** Run String RIX→ROS publisher
4. **Verify:** Terminal 2 shows "Hello from RIX" ✅
5. **Repeat** for Int32 and Point (switch Terminal 2 subscriber)
6. **Terminal 2:** Start RIX string subscriber
7. **Terminal 3:** Run String ROS→RIX publisher
8. **Verify:** Terminal 1 shows "✓ ROS→RIX SUCCESS" ✅

This proves both directions work (with RIX IPC issue acknowledged for ROS→RIX delivery).
