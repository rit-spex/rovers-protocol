from rover_protocol import CONSTANTS, MessageEncoder
from rover_protocol.arm_errors import (
    ARM_ERROR_ACTION_RUNNING,
    ARM_ERROR_FLIP_OCTANT,
    ARM_ERROR_GUIDE_LOCKED,
    ARM_ERROR_NORMAL_OCTANT,
    ARM_ERROR_OCTANT_REQUIRES_PLANAR,
    ARM_ERROR_PLANAR_BASE_RANGE,
    ARM_ERROR_PLANAR_EXIT_LOCKED,
    classify_failure,
    error_text,
)


def test_arm_status_roundtrip():
    encoder = MessageEncoder()
    payload = {
        "arm_error_code": ARM_ERROR_OCTANT_REQUIRES_PLANAR,
        "arm_error_arg": 5,
        "arm_error_seq": 9,
        "arm_operation_mode": 4,
        "locked_joints": 0,
        "homing_joints": 0,
        "arm_flags": 1 << 7,
    }
    encoded = encoder.encode_data(
        payload, CONSTANTS.COMPACT_MESSAGES.ARM_STATUS_ID)
    decoded, message_id = encoder.decode_data(encoded)

    assert message_id == CONSTANTS.COMPACT_MESSAGES.ARM_STATUS_ID
    assert encoder.is_from_rover(message_id)
    assert encoder.get_message_name(message_id) == "arm_status"
    assert decoded == payload


def test_octant_failure_is_classified_with_its_number():
    code, arg = classify_failure("Normal blocked: octant 5 requires Planar")
    assert code == ARM_ERROR_OCTANT_REQUIRES_PLANAR
    assert arg == 5
    assert "5" in error_text(code, arg)
    assert "Planar" in error_text(code, arg)


def test_flip_octant_is_distinct_from_normal_octant():
    assert classify_failure("Flip blocked: octant 3 requires planar")[0] == (
        ARM_ERROR_FLIP_OCTANT)


def test_specific_messages_win_over_the_shared_requires_planar_suffix():
    assert classify_failure(
        "Planar locked: restricted octant requires planar")[0] == (
            ARM_ERROR_PLANAR_EXIT_LOCKED)
    assert classify_failure(
        "Normal unavailable: restricted octant requires planar")[0] == (
            ARM_ERROR_NORMAL_OCTANT)


def test_simple_failures_are_classified():
    assert classify_failure("Planar needs base within +/-5 deg")[0] == (
        ARM_ERROR_PLANAR_BASE_RANGE)
    assert classify_failure("Command blocked: action is running")[0] == (
        ARM_ERROR_ACTION_RUNNING)
    assert classify_failure("Guide blocked: orientation is locked")[0] == (
        ARM_ERROR_GUIDE_LOCKED)
