from typing import Any

from rover_protocol import CONSTANTS, MessageEncoder


def test_auto_state_roundtrip_and_clamp_behavior():
    encoder = MessageEncoder()

    encoded = encoder.encode_data(
        {"auto_state": 5},
        CONSTANTS.COMPACT_MESSAGES.AUTO_STATE_ID,
    )

    decoded, message_id = encoder.decode_data(encoded)

    assert message_id == CONSTANTS.COMPACT_MESSAGES.AUTO_STATE_ID
    assert decoded["auto_state"] == 5


def test_from_rover_life_detection_decode_direction():
    encoder = MessageEncoder()

    payload = {
        "color_sensor": 77,
        "limit_switch_1": True,
        "limit_switch_2": False,
        "auger_depth": 10,
        "pump_output_level": 20,
        "slide_position": 30,
        "selected_tube": 2,
        "spec_slide_position": 40,
        "spec_color_sensor": 41,
    }

    encoded = encoder.encode_data(payload, CONSTANTS.COMPACT_MESSAGES.LIFE_DETECTION_ID)
    decoded, message_id = encoder.decode_data(encoded)

    assert encoder.is_from_rover(message_id)
    assert encoder.get_message_name(message_id) == "life_detection"
    assert decoded["color_sensor"] == 77
    assert decoded["limit_switch_1"] is True


def test_xbox_alias_and_numeric_button_key_encode_same_bytes():
    encoder = MessageEncoder()

    numeric_key = CONSTANTS.XBOX.BUTTON.B + CONSTANTS.XBOX.BUTTON_INDEX_OFFSET
    alias_key = CONSTANTS.XBOX.BUTTON.B_STR

    numeric_payload: dict[Any, Any] = {numeric_key: CONSTANTS.XBOX.BUTTON.ON}

    encoded_numeric = encoder.encode_data(
        numeric_payload,
        CONSTANTS.COMPACT_MESSAGES.XBOX_ID,
    )
    encoded_alias = encoder.encode_data(
        {alias_key: CONSTANTS.XBOX.BUTTON.ON},
        CONSTANTS.COMPACT_MESSAGES.XBOX_ID,
    )

    assert bytes(encoded_numeric) == bytes(encoded_alias)
