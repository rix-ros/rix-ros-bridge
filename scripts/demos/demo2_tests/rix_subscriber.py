#!/usr/bin/env python3
"""Generic RIX subscriber for testing"""
import sys
import time

sys.path.insert(0, '/home/rob422student/.rix/python/rix')

# Get parameters
if len(sys.argv) < 4:
    print("Usage: rix_subscriber.py <msg_module> <msg_type> <topic> [timeout]")
    sys.exit(1)

msg_module = sys.argv[1]  # e.g., "standard" or "geometry"
msg_type = sys.argv[2]     # e.g., "String", "Int32", "Pose"
topic = sys.argv[3]        # e.g., "/demo/string_to_rix"
timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0

# Import message type dynamically
if msg_module == "standard":
    from rix.msg import standard as msg_pkg
elif msg_module == "geometry":
    from rix.msg import geometry as msg_pkg
else:
    print(f"Unknown module: {msg_module}")
    sys.exit(1)

MsgClass = getattr(msg_pkg, msg_type)

from rix.core import Node

received = []

def callback(m):
    print(f"✓ RECEIVED", flush=True)
    received.append(m)

n = Node('demo_subscriber')
n.create_subscriber(MsgClass, topic, callback)
print(f"Waiting for messages on {topic}...", flush=True)
time.sleep(timeout)
n.shutdown()

if received:
    print(f"Total: {len(received)} messages", flush=True)
    sys.exit(0)
else:
    print("No messages received", flush=True)
    sys.exit(1)
