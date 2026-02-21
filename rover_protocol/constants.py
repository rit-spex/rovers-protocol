"""Constants and controller mappings loaded from protocol.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

from .schema import load_protocol_definition


@dataclass(frozen=True)
class DataType:
    num_bits: int
    id: int


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


def _as_int(value) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 0)
    raise TypeError(f"Unsupported numeric value type: {type(value)!r}")


def _upper_keys(mapping: dict):
    return {str(k).upper(): v for k, v in mapping.items()}


_PROTO = load_protocol_definition()
_DT_DEFS = _PROTO["data_types"]

_DATA_TYPES = {
    name: DataType(num_bits=_as_int(defn["num_bits"]), id=_as_int(defn["id"]))
    for name, defn in _DT_DEFS.items()
}

_MESSAGES = _PROTO["messages"]
_MESSAGE_IDS = {name: _as_int(defn["id"]) for name, defn in _MESSAGES.items()}
_CAN_MESSAGES = _PROTO.get("can_messages", {})
_OPEN_CAN_MESSAGES = _PROTO.get("open_can_messages", {})
_CAN_MESSAGE_IDS = {name: _as_int(defn["id"]) for name, defn in _CAN_MESSAGES.items()}
_OPEN_CAN_MESSAGE_IDS = {
    name: _as_int(defn["id"]) for name, defn in _OPEN_CAN_MESSAGES.items()
}
_UPDATE_FREQUENCY_NS = _as_int(_PROTO["timing"]["update_frequency_ms"]) * 1_000_000
_HEARTBEAT_NS = _as_int(_PROTO["timing"]["heartbeat_interval_ms"]) * 1_000_000

INPUT_TYPE = _ns(IS_BUTTON=0, IS_AXIS=1, IS_TRIGGER=2)


class _XboxJoystick:
    MIN_VALUE = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["min_value"])
    NEUTRAL_INT = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["neutral_int"])
    NEUTRAL_HEX = NEUTRAL_INT.to_bytes(1, byteorder="big")
    NEUTRAL_FLOAT = float(_PROTO["controllers"]["xbox"]["joystick"]["neutral_float"])
    MAX_VALUE = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["max_value"])

    AXIS_LX = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["axis_lx"])
    AXIS_LX_STR = "AXIS_LX"
    AXIS_LY = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["axis_ly"])
    AXIS_LY_STR = "AXIS_LY"
    AXIS_RX = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["axis_rx"])
    AXIS_RX_STR = "AXIS_RX"
    AXIS_RY = _as_int(_PROTO["controllers"]["xbox"]["joystick"]["axis_ry"])
    AXIS_RY_STR = "AXIS_RY"


class _XboxTrigger:
    AXIS_LT = _as_int(_PROTO["controllers"]["xbox"]["trigger"]["axis_lt"])
    AXIS_LT_STR = "AXIS_LT"
    AXIS_RT = _as_int(_PROTO["controllers"]["xbox"]["trigger"]["axis_rt"])
    AXIS_RT_STR = "AXIS_RT"


class _XboxButton:
    SIZE_BUTTON_IN_BITS = 2
    NUM_BUTTONS_PER_BYTE = 8 // SIZE_BUTTON_IN_BITS

    ON = _as_int(_PROTO["controllers"]["xbox"]["button"]["on"])
    OFF = _as_int(_PROTO["controllers"]["xbox"]["button"]["off"])

    A = _as_int(_PROTO["controllers"]["xbox"]["button"]["a"])
    A_STR = "A"
    B = _as_int(_PROTO["controllers"]["xbox"]["button"]["b"])
    B_STR = "B"
    X = _as_int(_PROTO["controllers"]["xbox"]["button"]["x"])
    X_STR = "X"
    Y = _as_int(_PROTO["controllers"]["xbox"]["button"]["y"])
    Y_STR = "Y"
    LEFT_BUMPER = _as_int(_PROTO["controllers"]["xbox"]["button"]["left_bumper"])
    LEFT_BUMPER_STR = "LEFT_BUMPER"
    RIGHT_BUMPER = _as_int(_PROTO["controllers"]["xbox"]["button"]["right_bumper"])
    RIGHT_BUMPER_STR = "RIGHT_BUMPER"
    SELECT = _as_int(_PROTO["controllers"]["xbox"]["button"]["select"])
    SELECT_STR = "SELECT"
    START = _as_int(_PROTO["controllers"]["xbox"]["button"]["start"])
    START_STR = "START"
    HOME = _as_int(_PROTO["controllers"]["xbox"]["button"]["home"])
    HOME_STR = "HOME"
    LEFT_STICK = _as_int(_PROTO["controllers"]["xbox"]["button"]["left_stick"])
    LEFT_STICK_STR = "LEFT_STICK"
    RIGHT_STICK = _as_int(_PROTO["controllers"]["xbox"]["button"]["right_stick"])
    RIGHT_STICK_STR = "RIGHT_STICK"


class _XboxJoypad:
    UP = tuple(_PROTO["controllers"]["xbox"]["joypad"]["up"])
    DOWN = tuple(_PROTO["controllers"]["xbox"]["joypad"]["down"])
    LEFT = tuple(_PROTO["controllers"]["xbox"]["joypad"]["left"])
    RIGHT = tuple(_PROTO["controllers"]["xbox"]["joypad"]["right"])


class _Xbox:
    NAME = str(_PROTO["controllers"]["xbox"]["name"])
    NUM_AXES = _as_int(_PROTO["controllers"]["xbox"]["num_axes"])
    NUM_USED_AXES = _as_int(_PROTO["controllers"]["xbox"]["num_used_axes"])
    NUM_TRIGGER = _as_int(_PROTO["controllers"]["xbox"]["num_trigger"])
    NUM_BUTTONS = _as_int(_PROTO["controllers"]["xbox"]["num_buttons"])
    BUTTON_INDEX_OFFSET = _as_int(_PROTO["controllers"]["xbox"]["button_index_offset"])

    INPUT_TYPE = INPUT_TYPE
    JOYSTICK = _XboxJoystick
    TRIGGER = _XboxTrigger
    BUTTON = _XboxButton
    JOYPAD = _XboxJoypad


class _N64Joystick:
    MIN_VALUE = _as_int(_PROTO["controllers"]["n64"]["joystick"]["min_value"])
    NEUTRAL_INT = _as_int(_PROTO["controllers"]["n64"]["joystick"]["neutral_int"])
    NEUTRAL_HEX = NEUTRAL_INT.to_bytes(1, byteorder="big")
    MAX_VALUE = _as_int(_PROTO["controllers"]["n64"]["joystick"]["max_value"])

    AXIS_X = _as_int(_PROTO["controllers"]["n64"]["joystick"]["axis_x"])
    AXIS_X_STR = "AXIS_X"
    AXIS_Y = _as_int(_PROTO["controllers"]["n64"]["joystick"]["axis_y"])
    AXIS_Y_STR = "AXIS_Y"


class _N64Button:
    SIZE_BUTTON_IN_BITS = 2
    NUM_BUTTONS_PER_BYTE = 8 // SIZE_BUTTON_IN_BITS

    ON = _as_int(_PROTO["controllers"]["n64"]["button"]["on"])
    OFF = _as_int(_PROTO["controllers"]["n64"]["button"]["off"])

    A = _as_int(_PROTO["controllers"]["n64"]["button"]["a"])
    A_STR = "A"
    B = _as_int(_PROTO["controllers"]["n64"]["button"]["b"])
    B_STR = "B"
    C_UP = _as_int(_PROTO["controllers"]["n64"]["button"]["c_up"])
    C_UP_STR = "C_UP"
    C_DOWN = _as_int(_PROTO["controllers"]["n64"]["button"]["c_down"])
    C_DOWN_STR = "C_DOWN"
    C_LEFT = _as_int(_PROTO["controllers"]["n64"]["button"]["c_left"])
    C_LEFT_STR = "C_LEFT"
    C_RIGHT = _as_int(_PROTO["controllers"]["n64"]["button"]["c_right"])
    C_RIGHT_STR = "C_RIGHT"
    L = _as_int(_PROTO["controllers"]["n64"]["button"]["l"])
    L_STR = "L"
    R = _as_int(_PROTO["controllers"]["n64"]["button"]["r"])
    R_STR = "R"
    Z = _as_int(_PROTO["controllers"]["n64"]["button"]["z"])
    Z_STR = "Z"
    START = _as_int(_PROTO["controllers"]["n64"]["button"]["start"])
    START_STR = "START"
    DP_UP = _as_int(_PROTO["controllers"]["n64"]["button"]["dp_up"])
    DP_UP_STR = "DP_UP"
    DP_DOWN = _as_int(_PROTO["controllers"]["n64"]["button"]["dp_down"])
    DP_DOWN_STR = "DP_DOWN"
    DP_LEFT = _as_int(_PROTO["controllers"]["n64"]["button"]["dp_left"])
    DP_LEFT_STR = "DP_LEFT"
    DP_RIGHT = _as_int(_PROTO["controllers"]["n64"]["button"]["dp_right"])
    DP_RIGHT_STR = "DP_RIGHT"


class _N64Joypad:
    UP = tuple(_PROTO["controllers"]["n64"]["joypad"]["up"])
    DOWN = tuple(_PROTO["controllers"]["n64"]["joypad"]["down"])
    LEFT = tuple(_PROTO["controllers"]["n64"]["joypad"]["left"])
    RIGHT = tuple(_PROTO["controllers"]["n64"]["joypad"]["right"])


class _N64:
    NAME = str(_PROTO["controllers"]["n64"]["name"])
    NUM_AXES = _as_int(_PROTO["controllers"]["n64"]["num_axes"])
    NUM_USED_AXES = _as_int(_PROTO["controllers"]["n64"]["num_used_axes"])
    NUM_TRIGGER = _as_int(_PROTO["controllers"]["n64"]["num_trigger"])
    NUM_BUTTONS = _as_int(_PROTO["controllers"]["n64"]["num_buttons"])

    INPUT_TYPE = INPUT_TYPE
    JOYSTICK = _N64Joystick
    BUTTON = _N64Button
    JOYPAD = _N64Joypad


def _build_message_namespace(message_ids: dict[str, int], definitions: dict):
    id_entries = {f"{name.upper()}_ID": message_id for name, message_id in message_ids.items()}
    return _ns(
        **id_entries,
        MESSAGE_ID_BY_NAME=_upper_keys(message_ids),
        DEFINITIONS=definitions,
    )


class CONSTANTS:
    SIMULATION_MODE = False
    # Framing marker prepended to combined controller messages so the receiver
    # can recognise the start of an integrated data frame.
    START_MESSAGE = b"\xde"

    class CONVERSION:
        NS_PER_MS = 1_000_000
        NS_PER_S = 1_000_000_000
        ONE_HUNDRED_MS_TO_NS = 100_000_000
        FIVE_HUNDRED_MS_TO_NS = 500_000_000

    class HEARTBEAT:
        NAME = "heartbeat"
        MESSAGE = bytes([_MESSAGE_IDS["heartbeat"]])
        MESSAGE_LENGTH = 3
        TIMESTAMP_MESSAGE = "timestamp"
        INTERVAL = _HEARTBEAT_NS

    COMPACT_MESSAGES = _ns(
        N64_ID=_MESSAGE_IDS["n64"],
        XBOX_ID=_MESSAGE_IDS["xbox"],
        QUIT_ID=_MESSAGE_IDS["quit"],
        HEARTBEAT_ID=_MESSAGE_IDS["heartbeat"],
        AUTO_STATE_ID=_MESSAGE_IDS["auto_state"],
        LIFE_DETECTION_ID=_MESSAGE_IDS["life_detection"],
        ARM_ENCODERS_ID=_MESSAGE_IDS["arm_encoders"],
        DRIVE_IMU_ID=_MESSAGE_IDS["drive_imu"],
        ROVER_ESTOP_ID=_MESSAGE_IDS["rover_estop"],
        SUBSYSTEM_ENABLED_ID=_MESSAGE_IDS["subsystem_enabled"],
        CONTROL_MODE_ID=_MESSAGE_IDS["control_mode"],
        DATA_TYPE=DataType,
        UINT_2_BOOL=_DATA_TYPES["UINT_2_BOOL"],
        UINT_8=_DATA_TYPES["UINT_8"],
        UINT_16=_DATA_TYPES["UINT_16"],
        UINT_8_JOYSTICK=_DATA_TYPES["UINT_8_JOYSTICK"],
        BOOLEAN=_DATA_TYPES["BOOLEAN"],
        MESSAGE_ID_BY_NAME=_upper_keys(_MESSAGE_IDS),
    )

    CAN_MESSAGES = _build_message_namespace(_CAN_MESSAGE_IDS, _CAN_MESSAGES)
    OPEN_CAN_MESSAGES = _build_message_namespace(
        _OPEN_CAN_MESSAGE_IDS, _OPEN_CAN_MESSAGES
    )

    class TIMING:
        UPDATE_FREQUENCY = _UPDATE_FREQUENCY_NS
        DEADBAND_THRESHOLD = float(_PROTO["timing"]["deadband_threshold"])

    class COMMUNICATION:
        DEFAULT_PORT = str(_PROTO["communication"]["serial"]["default_port_linux"])
        DEFAULT_PORT_WINDOWS = str(_PROTO["communication"]["serial"]["default_port_windows"])
        DEFAULT_BAUD_RATE = _as_int(_PROTO["communication"]["serial"]["baud_rate"])
        REMOTE_XBEE_ADDRESS = str(_PROTO["communication"]["serial"]["remote_xbee_address"])
        UDP_HOST = str(_PROTO["communication"]["udp"]["host"])
        UDP_BASESTATION_PORT = _as_int(_PROTO["communication"]["udp"]["basestation_port"])
        UDP_ROVER_PORT = _as_int(_PROTO["communication"]["udp"]["rover_port"])
        UDP_TELEMETRY_PORT = _as_int(_PROTO["communication"]["udp"]["telemetry_port"])

    CONTROLLER_MODES = _ns(
        NORMAL_MULTIPLIER=float(_PROTO["controller_modes"]["normal_multiplier"]),
        CREEP_MULTIPLIER=float(_PROTO["controller_modes"]["creep_multiplier"]),
        REVERSE_MULTIPLIER=float(_PROTO["controller_modes"]["reverse_multiplier"]),
    )

    class QUIT:
        NAME = "quit"
        QUIT_MESSAGE = "QUIT"
        VALUE = 1

    class AutoState:
        NAME = "auto_state"
        MIN = _as_int(_PROTO["auto_states"]["min"])
        MAX = _as_int(_PROTO["auto_states"]["max"])

    AUTO_STATE = AutoState

    XBOX = _Xbox
    N64 = _N64
    PROTOCOL_DEFINITION = _PROTO
