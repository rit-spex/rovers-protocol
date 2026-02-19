# Rover Protocol

Shared compact wire protocol for the RIT SPEX rover. Used as a **git submodule** by both:

- [`rovers-basestation`](https://github.com/rit-spex/rovers-basestation) — Raspberry Pi basestation
- [`rovers-ros`](https://github.com/rit-spex/rovers-ros) — Rover ROS 2 workspace

## What it provides

- **`protocol.yaml`** — Source of truth for all message definitions, signal types, controller mappings, timing, and communication settings
- **`rover_protocol.MessageEncoder`** — Bidirectional encoder/decoder that packs signals into compact byte messages
- **`rover_protocol.CONSTANTS`** — Namespace with all IDs, button mappings, and tuning values (built from `protocol.yaml` at import time)

## Structure

```
rovers-protocol/
├── protocol.yaml         # All message + controller definitions
├── pyproject.toml
├── rover_protocol/       # Python package
│   ├── __init__.py       # Exports MessageEncoder, Signal, CONSTANTS, etc.
│   ├── codec.py          # MessageEncoder + Signal classes
│   ├── constants.py      # CONSTANTS namespace (loads from protocol.yaml)
│   └── schema.py         # YAML loader
└── tests/
    └── test_codec.py     # Encode/decode round-trip tests
```

## Usage

Both consuming repos include this as a submodule at `lib/rovers-protocol/` and add it to `sys.path` via wrapper modules. No pip install needed just gotta remember to clone with `--recurse-submodules`.

```python
from rover_protocol import MessageEncoder, Signal, CONSTANTS

encoder = MessageEncoder()

# Encode controller data
data = {"AXIS_LY": 100, "AXIS_RY": 100, "A": False, "B": False}
encoded = encoder.encode_data(data, CONSTANTS.COMPACT_MESSAGES.XBOX_ID)

# Decode it back
decoded, message_id = encoder.decode_data(encoded)
```

## Adding a new message

1. Add the message to `protocol.yaml` under `messages:`
2. Add the ID to `CONSTANTS.COMPACT_MESSAGES` in `rover_protocol/constants.py`
3. Run `pytest tests/` to verify encoding/decoding

See the [basestation developer guide](https://github.com/rit-spex/rovers-basestation/blob/main/DEVELOPER_GUIDE.md) for better step-by-step instructions that I am too lazy to add here.

## Installation & Development

While mainly used as a submodule, you can install it in editable mode for better IDE support (autocomplete) or when `sys.path` hacks fail:

```bash
cd lib/rovers-protocol
pip install -e .
```

## Running tests

```bash
pip install pytest pyyaml
python -m pytest tests/
```
