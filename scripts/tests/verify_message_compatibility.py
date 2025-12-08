#!/usr/bin/env python3
"""
Message Compatibility Verification Script

Checks if RIX and ROS message types have compatible field structures.
This helps verify which types can be bridged in Phase 2.
"""

import sys
import os

# Add RIX to path
sys.path.insert(0, '/home/rob422student/.rix/python/rix')


def get_rix_fields(msg_obj):
    """Extract field names from RIX message object."""
    skip = ['deserialize', 'serialize', 'hash', 'size', 'Offset']
    return [attr for attr in dir(msg_obj) if not attr.startswith('_') and attr not in skip]


def get_ros_fields(msg_class):
    """Extract field names from ROS message class."""
    # ROS2 stores fields in __slots__ with leading underscore
    return [slot[1:] if slot.startswith('_') else slot 
            for slot in msg_class.__slots__ if slot != '_check_fields']


def verify_type(rix_module, rix_type, ros_module, ros_type):
    """
    Verify if RIX and ROS message types are compatible.
    
    Returns: (compatible: bool, rix_fields: list, ros_fields: list, notes: str)
    """
    try:
        # Import RIX type
        rix_pkg = __import__(f'rix.msg.{rix_module}', fromlist=[rix_type])
        rix_class = getattr(rix_pkg, rix_type)
        rix_fields = get_rix_fields(rix_class())
        
        # Import ROS type
        ros_pkg = __import__(ros_module, fromlist=[ros_type])
        ros_class = getattr(ros_pkg, ros_type)
        ros_fields = get_ros_fields(ros_class)
        
        # Check if fields match
        rix_set = set(rix_fields)
        ros_set = set(ros_fields)
        
        if rix_set == ros_set:
            return True, rix_fields, ros_fields, "✓ Fields match exactly"
        elif rix_set.issubset(ros_set):
            missing = ros_set - rix_set
            return True, rix_fields, ros_fields, f"⚠ RIX subset of ROS (missing: {missing})"
        elif ros_set.issubset(rix_set):
            extra = rix_set - ros_set
            return True, rix_fields, ros_fields, f"⚠ ROS subset of RIX (extra: {extra})"
        else:
            diff = rix_set.symmetric_difference(ros_set)
            return False, rix_fields, ros_fields, f"✗ Fields differ: {diff}"
            
    except Exception as e:
        return False, [], [], f"✗ Error: {str(e)}"


def main():
    """Run verification for all priority types."""
    
    print("=" * 80)
    print("RIX-ROS MESSAGE COMPATIBILITY VERIFICATION")
    print("=" * 80)
    print()
    
    # Define types to verify (P1 priority)
    verifications = [
        # (rix_module, rix_type, ros_module, ros_type, description)
        ('standard', 'String', 'std_msgs.msg', 'String', 'String message'),
        ('standard', 'Int32', 'std_msgs.msg', 'Int32', 'Int32 message'),
        ('standard', 'Int64', 'std_msgs.msg', 'Int64', 'Int64 message'),
        ('standard', 'Float', 'std_msgs.msg', 'Float32', 'Float32 message'),
        ('standard', 'Double', 'std_msgs.msg', 'Float64', 'Float64 message'),
        ('standard', 'Bool', 'std_msgs.msg', 'Bool', 'Bool message'),
        ('standard', 'UInt8', 'std_msgs.msg', 'UInt8', 'UInt8 message'),
        ('standard', 'UInt16', 'std_msgs.msg', 'UInt16', 'UInt16 message'),
        ('standard', 'UInt32', 'std_msgs.msg', 'UInt32', 'UInt32 message'),
        ('standard', 'UInt64', 'std_msgs.msg', 'UInt64', 'UInt64 message'),
        ('standard', 'Int8', 'std_msgs.msg', 'Int8', 'Int8 message'),
        ('standard', 'Int16', 'std_msgs.msg', 'Int16', 'Int16 message'),
        ('geometry', 'Point', 'geometry_msgs.msg', 'Point', 'Point message'),
        ('geometry', 'Pose', 'geometry_msgs.msg', 'Pose', 'Pose message'),
        ('geometry', 'Quaternion', 'geometry_msgs.msg', 'Quaternion', 'Quaternion message'),
        ('geometry', 'Vector3', 'geometry_msgs.msg', 'Vector3', 'Vector3 message'),
        ('geometry', 'Twist', 'geometry_msgs.msg', 'Twist', 'Twist message'),
        ('geometry', 'Transform', 'geometry_msgs.msg', 'Transform', 'Transform message'),
    ]
    
    compatible_count = 0
    total_count = len(verifications)
    
    print("P1 PRIORITY TYPES (Week 1 Implementation):")
    print("-" * 80)
    
    for rix_mod, rix_type, ros_mod, ros_type, desc in verifications:
        compat, rix_fields, ros_fields, notes = verify_type(rix_mod, rix_type, ros_mod, ros_type)
        
        status = "✓ COMPATIBLE" if compat else "✗ INCOMPATIBLE"
        if compat:
            compatible_count += 1
        
        print(f"\n{desc}:")
        print(f"  RIX: {rix_mod}/{rix_type}")
        print(f"  ROS: {ros_mod}.{ros_type}")
        print(f"  Status: {status}")
        print(f"  RIX fields: {rix_fields}")
        print(f"  ROS fields: {ros_fields}")
        print(f"  Notes: {notes}")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: {compatible_count}/{total_count} types verified as compatible")
    print("=" * 80)
    
    if compatible_count == total_count:
        print("\n✓ All P1 types are compatible! Ready to implement converters.")
        return 0
    else:
        print(f"\n⚠ {total_count - compatible_count} types need investigation before implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
