"""Tests for spacemouse message encoding/decoding in the rover_protocol codec."""

from rover_protocol import CONSTANTS, MessageEncoder


def _make_payload(x=0, y=0, z=0, rx=0, ry=0, rz=0, buttons=0):
    return {"x": x, "y": y, "z": z, "rx": rx, "ry": ry, "rz": rz, "buttons": buttons}


def test_spacemouse_roundtrip_positive_values():
    encoder = MessageEncoder()
    payload = _make_payload(x=100, y=200, z=300, rx=400, ry=500, rz=600, buttons=1)
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    encoded = encoder.encode_data(payload, msg_id)
    decoded, decoded_id = encoder.decode_data(encoded)

    assert decoded_id == msg_id
    assert decoded["x"] == 100
    assert decoded["y"] == 200
    assert decoded["z"] == 300
    assert decoded["rx"] == 400
    assert decoded["ry"] == 500
    assert decoded["rz"] == 600
    assert decoded["buttons"] == 1


def test_spacemouse_roundtrip_negative_values():
    encoder = MessageEncoder()
    payload = _make_payload(x=-350, y=-100, z=-1, rx=-500, ry=-32000, rz=-1)
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    encoded = encoder.encode_data(payload, msg_id)
    decoded, decoded_id = encoder.decode_data(encoded)

    assert decoded_id == msg_id
    assert decoded["x"] == -350
    assert decoded["y"] == -100
    assert decoded["z"] == -1
    assert decoded["rx"] == -500
    assert decoded["ry"] == -32000
    assert decoded["rz"] == -1


def test_spacemouse_roundtrip_zero_values():
    encoder = MessageEncoder()
    payload = _make_payload()
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    encoded = encoder.encode_data(payload, msg_id)
    decoded, decoded_id = encoder.decode_data(encoded)

    assert decoded_id == msg_id
    for key in ("x", "y", "z", "rx", "ry", "rz", "buttons"):
        assert decoded[key] == 0


def test_spacemouse_roundtrip_boundary_values():
    encoder = MessageEncoder()
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    # INT_16 min for axes
    payload_min = _make_payload(
        x=-32768, y=-32768, z=-32768, rx=-32768, ry=-32768, rz=-32768, buttons=0
    )
    encoded = encoder.encode_data(payload_min, msg_id)
    decoded, decoded_id = encoder.decode_data(encoded)

    assert decoded_id == msg_id
    for key in ("x", "y", "z", "rx", "ry", "rz"):
        assert decoded[key] == -32768

    # INT_16 max for axes
    payload_max = _make_payload(
        x=32767, y=32767, z=32767, rx=32767, ry=32767, rz=32767, buttons=65535
    )
    encoded = encoder.encode_data(payload_max, msg_id)
    decoded, decoded_id = encoder.decode_data(encoded)

    assert decoded_id == msg_id
    for key in ("x", "y", "z", "rx", "ry", "rz"):
        assert decoded[key] == 32767
    assert decoded["buttons"] == 65535


def test_spacemouse_buttons_uint16():
    encoder = MessageEncoder()
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    payload = _make_payload(buttons=0xFFFF)
    encoded = encoder.encode_data(payload, msg_id)
    decoded, _ = encoder.decode_data(encoded)

    assert decoded["buttons"] == 0xFFFF

    payload_zero = _make_payload(buttons=0)
    encoded_zero = encoder.encode_data(payload_zero, msg_id)
    decoded_zero, _ = encoder.decode_data(encoded_zero)

    assert decoded_zero["buttons"] == 0


def test_spacemouse_direction_is_to_rover():
    encoder = MessageEncoder()
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    assert encoder.is_to_rover(msg_id)


def test_spacemouse_message_name():
    encoder = MessageEncoder()
    msg_id = CONSTANTS.COMPACT_MESSAGES.SPACEMOUSE_ID

    assert encoder.get_message_name(msg_id) == "spacemouse"
