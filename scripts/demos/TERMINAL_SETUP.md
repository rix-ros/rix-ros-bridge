# Multi-Terminal Demo Setup

## Overview
This demo uses **12 terminals** to show bidirectional message passing:
- **Terminal 1:** Bridge (always running)
- **Terminals 2-6:** ROS subscribers (for RIX→ROS tests)
- **Terminals 7-11:** RIX subscribers (for ROS→RIX tests)
- **Terminal 12:** Demo script (publishes messages)

---

## Step 1: Start Bridge (Terminal 1)

```bash
cd ~/Desktop/ROB490/bridge_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
export PYTHONPATH=/home/rob422student/.rix/python/rix:$PYTHONPATH
ros2 run rix_ros_bridge bridge_node \
  --config src/rix_ros_bridge/config/demo2_config.json \
  --mappings src/rix_ros_bridge/config/message_mappings.json
```

**Wait for:** `All bridges created successfully. Total handles: 52`

---

## Step 2: Start ROS Subscribers (Terminals 2-6)

### Terminal 2: String Subscriber
```bash
ros2 topic echo /demo/string_to_ros
```

### Terminal 3: Int32 Subscriber
```bash
ros2 topic echo /demo/int32_to_ros
```

### Terminal 4: Float32 Subscriber
```bash
ros2 topic echo /demo/float32_to_ros
```

### Terminal 5: Point Subscriber
```bash
ros2 topic echo /demo/point_to_ros
```

### Terminal 6: Pose Subscriber
```bash
ros2 topic echo /demo/pose_to_ros
```

---

## Step 3: Start RIX Subscribers (Terminals 7-11)

**Note:** These will show bridge conversion in Terminal 1, but may not receive due to RIX IPC issue.

### Terminal 7: String Subscriber
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import String; import time
n=Node('sub_string')
n.create_subscriber(String, '/demo/string_to_rix', lambda m: print(f'✓ RECEIVED: {m.data}'))
print('String subscriber ready, waiting...')
while True: time.sleep(1)
EOF
```

### Terminal 8: Int32 Subscriber
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import Int32; import time
n=Node('sub_int32')
n.create_subscriber(Int32, '/demo/int32_to_rix', lambda m: print(f'✓ RECEIVED: {m.data}'))
print('Int32 subscriber ready, waiting...')
while True: time.sleep(1)
EOF
```

### Terminal 9: Float32 Subscriber
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.standard import Float; import time
n=Node('sub_float')
n.create_subscriber(Float, '/demo/float32_to_rix', lambda m: print(f'✓ RECEIVED: {m.data}'))
print('Float32 subscriber ready, waiting...')
while True: time.sleep(1)
EOF
```

### Terminal 10: Point Subscriber
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.geometry import Point; import time
n=Node('sub_point')
n.create_subscriber(Point, '/demo/point_to_rix', lambda m: print(f'✓ RECEIVED: ({m.x}, {m.y}, {m.z})'))
print('Point subscriber ready, waiting...')
while True: time.sleep(1)
EOF
```

### Terminal 11: Pose Subscriber
```bash
cd ~/Desktop/ROB490/rix-py
PYTHONPATH=/home/rob422student/.rix/python/rix python3 << 'EOF'
import sys; sys.path.insert(0, '/home/rob422student/.rix/python/rix')
from rix.core import Node; from rix.msg.geometry import Pose; import time
n=Node('sub_pose')
def cb(m): print(f'✓ RECEIVED: pos=({m.position.x},{m.position.y},{m.position.z}), quat.w={m.orientation.w}')
n.create_subscriber(Pose, '/demo/pose_to_rix', cb)
print('Pose subscriber ready, waiting...')
while True: time.sleep(1)
EOF
```

---

## Step 4: Run Demo Script (Terminal 12)

Once all subscribers are running:

```bash
cd ~/Desktop/ROB490/bridge_ws
chmod +x scripts/demos/demo2_coordinated.sh
./scripts/demos/demo2_coordinated.sh
```

---

## What to Expect

### RIX→ROS Tests (Tests 1-5)
- **Terminals 2-6** will display received messages ✅
- Example Terminal 2 output: `data: Hello from RIX`

### ROS→RIX Tests (Tests 6-10)
- **Terminal 1 (bridge)** will show: `✓ ROS→RIX SUCCESS: /demo/xxx_from_ros → /demo/xxx_to_rix`
- **Terminals 7-11** may not receive due to RIX IPC issue ⚠️
- This proves bridge converts correctly, delivery issue is RIX-side

---

## Quick Reference

| Terminal | Role | Command Type |
|----------|------|--------------|
| 1 | Bridge | ROS2 node |
| 2-6 | ROS Subscribers | `ros2 topic echo` |
| 7-11 | RIX Subscribers | Python scripts |
| 12 | Demo Script | Bash script |

---

## Troubleshooting

**If nothing appears in terminals:**
1. Verify bridge is running (Terminal 1)
2. Check rixhub is running: `pgrep rixhub`
3. Restart all terminals and try again

**To stop RIX subscribers (Terminals 7-11):**
- Press `Ctrl+C` in each terminal

**To restart demo:**
- Keep Terminals 1-11 running
- Just re-run Terminal 12 script
