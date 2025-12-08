#!/usr/bin/env python3
"""Generic RIX publisher for testing"""
import sys
import time
import json

sys.path.insert(0, '/home/rob422student/.rix/python/rix')

# Get parameters
if len(sys.argv) < 5:
    print("Usage: rix_publisher.py <msg_module> <msg_type> <topic> <data_json>")
    sys.exit(1)

msg_module = sys.argv[1]  # e.g., "standard" or "geometry"
msg_type = sys.argv[2]     # e.g., "String", "Int32", "Pose"
topic = sys.argv[3]        # e.g., "/demo/string_from_rix"
data_json = sys.argv[4]    # JSON string with message data

# Import message types
if msg_module == "standard":
    from rix.msg import standard as msg_pkg
elif msg_module == "geometry":
    from rix.msg import geometry as msg_pkg
    from rix.msg.standard import Header
else:
    print(f"Unknown module: {msg_module}")
    sys.exit(1)

MsgClass = getattr(msg_pkg, msg_type)

from rix.core import Node

# Parse data
try:
    data = json.loads(data_json)
except:
    print(f"Failed to parse JSON: {data_json}")
    sys.exit(1)

# Helper to set message fields recursively
def set_fields(obj, data_dict):
    for key, value in data_dict.items():
        if isinstance(value, dict):
            # Nested object - need to create it
            if hasattr(obj, key):
                nested_obj = getattr(obj, key)
                if nested_obj is None:
                    # Create the nested object
                    field_type = type(obj).__annotations__.get(key)
                    if field_type:
                        nested_obj = field_type()
                        setattr(obj, key, nested_obj)
                set_fields(nested_obj, value)
        else:
            setattr(obj, key, value)

# Create and publish message
n = Node('demo_publisher')
p = n.create_publisher(MsgClass, topic)
time.sleep(1)

m = MsgClass()
set_fields(m, data)

print(f"Publishing to {topic}...", flush=True)
for i in range(5):
    p.publish(m)
    time.sleep(0.2)

time.sleep(0.5)
n.shutdown()
print("Published successfully", flush=True)
