# Bridge Workspace File Index

## Quick Access

### Documentation (`docs/`)
- `BRIDGE_NODE_DESIGN.md` - Core bridge architecture
- `DYNAMIC_LOADING_DESIGN.md` - Dynamic converter loading system
- `P2_EXPANSION_PLAN.md` - Phase 2 expansion roadmap
- `ROS_RIX_MESSAGE_MAPPINGS.txt` - Complete message type mappings (26 types)
- `SECTION_3-6_IMPLEMENTATION_GUIDE.txt` - Step-by-step implementation guides
- `SIMPLE_TEST.md` - Quick testing guide

### Demo Scripts (`scripts/demos/`)
- `demo2.sh` - **Main demo script** - Tests all 26 message types bidirectionally
- `demo2_clean.sh` - Clean implementation with Python helper files
- `demo2_tests/` - Python test utilities (rix_subscriber.py, rix_publisher.py)

### Test Scripts (`scripts/tests/`)
- `run_integration_test.sh` - Integration test suite
- `test_directions.sh` - Bidirectional communication tests
- `test_multi_type.sh` - Multi-type message tests
- `verify_message_compatibility.py` - Message compatibility verification

## Running Demos

```bash
# Main demo (all 26 types, both directions)
cd ~/Desktop/ROB490/bridge_ws
./scripts/demos/demo2.sh

# Clean demo (external Python files)
./scripts/demos/demo2_clean.sh
```

## Running Tests

```bash
# Integration tests
cd ~/Desktop/ROB490/bridge_ws
./scripts/tests/run_integration_test.sh

# Directional tests
./scripts/tests/test_directions.sh
```
