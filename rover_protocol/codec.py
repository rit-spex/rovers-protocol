"""Shared message encoder/decoder for rover protocol."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple, Union

from .constants import CONSTANTS, DataType

BYTES_LIKE = (bytes, bytearray, memoryview)


@dataclass
class Signal:
    """A single signal in a compact protocol message."""

    _type: DataType
    _default_value: Any = 0

    def __post_init__(self) -> None:
        self._value = self._default_value

    @property
    def type(self) -> DataType:
        return self._type

    @property
    def value(self) -> Any:
        return self._value

    @property
    def default_value(self) -> Any:
        return self._default_value

    def to_string(self) -> str:
        return (
            f"Signal(type={self._type}, value={self._value}, "
            f"default={self._default_value})"
        )

class MessageEncoder:
    """Bidirectional compact message encoder/decoder."""

    def __init__(self):
        self._messages = self._build_message_definitions()
        self._id_to_name = {
            msg_id: message["name"] for msg_id, message in self._messages.items()
        }
        self._name_to_id = {
            message["name"]: msg_id for msg_id, message in self._messages.items()
        }
        self._directions = {
            msg_id: message["direction"] for msg_id, message in self._messages.items()
        }
        self._alias_to_numeric = self._build_alias_maps()

    def _build_message_definitions(self) -> dict[int, dict[str, Any]]:
        proto_messages = CONSTANTS.PROTOCOL_DEFINITION["messages"]
        compact_defs = {}

        dt_lookup = {
            "BOOLEAN": CONSTANTS.COMPACT_MESSAGES.BOOLEAN,
            "UINT_2_BOOL": CONSTANTS.COMPACT_MESSAGES.UINT_2_BOOL,
            "UINT_8": CONSTANTS.COMPACT_MESSAGES.UINT_8,
            "UINT_8_JOYSTICK": CONSTANTS.COMPACT_MESSAGES.UINT_8_JOYSTICK,
            "UINT_16": CONSTANTS.COMPACT_MESSAGES.UINT_16,
        }

        for message_name, message_def in proto_messages.items():
            msg_id = int(message_def["id"])
            signal_defs = message_def.get("signals", {})
            values: Dict[str, Signal] = {}
            for signal_name, signal_def in signal_defs.items():
                type_name = str(signal_def["type"])
                values[signal_name] = Signal(
                    dt_lookup[type_name],
                    signal_def.get("default", 0),
                )

            compact_defs[msg_id] = {
                "name": message_name,
                "direction": str(message_def.get("direction", "")),
                "values": values,
            }

        return compact_defs

    def _build_alias_maps(self) -> dict:
        def extract(obj):
            out = {}
            for attr in dir(obj):
                if attr.endswith("_STR") and hasattr(obj, attr[:-4]):
                    out[getattr(obj, attr)] = getattr(obj, attr[:-4])
            return out

        xbox = CONSTANTS.XBOX
        n64 = CONSTANTS.N64

        xbox_map = {}
        xbox_map.update(extract(xbox.JOYSTICK))
        xbox_map.update(extract(xbox.TRIGGER))
        for alias, num in extract(xbox.BUTTON).items():
            xbox_map[alias] = num + xbox.BUTTON_INDEX_OFFSET

        n64_map = {}
        n64_map.update(extract(n64.JOYSTICK))
        n64_map.update(extract(n64.BUTTON))

        return {xbox.NAME: xbox_map, n64.NAME: n64_map}

    def get_messages(self) -> dict[int, dict[str, Any]]:
        return self._messages

    def get_message_name(self, message_id: int) -> str:
        return self._id_to_name[int(message_id)]

    def get_message_id(self, message_name: str) -> int:
        return self._name_to_id[message_name]

    def get_message_direction(self, message_id: int) -> str:
        return self._directions[int(message_id)]

    def is_to_rover(self, message_id: int) -> bool:
        return self.get_message_direction(message_id) == "to_rover"

    def is_from_rover(self, message_id: int) -> bool:
        return self.get_message_direction(message_id) == "from_rover"

    def encode_data(
        self,
        data: dict[str, Any],
        id_: Union[int, bytes, bytearray, memoryview],
    ) -> bytes:
        message_id = self._normalize_message_id(id_)
        if message_id not in self._messages:
            raise KeyError(
                f"Unknown message_id during encode: {message_id}. "
                f"Known: {list(self._messages.keys())}"
            )
        return message_id.to_bytes(1, byteorder="big") + self._encode_signals(
            message_id, data
        )

    def decode_data(self, data: bytes) -> tuple[dict[str, Any], int]:
        message_id = int.from_bytes(data[0:1], byteorder="big")
        if message_id not in self._messages:
            raise KeyError(
                f"Unknown message_id during decode: {message_id}. "
                f"Known: {list(self._messages.keys())}"
            )

        decoded = {}
        byte_idx = 1
        bits_left = 8

        for key, signal in self._messages[message_id]["values"].items():
            bits_needed = signal.type.num_bits
            value = 0

            while bits_needed > 0:
                if bits_left - bits_needed < 0:
                    bits_needed -= bits_left
                    value <<= bits_left
                    value |= self._read_byte(data, byte_idx) & ((1 << bits_left) - 1)
                    byte_idx += 1
                    bits_left = 8
                else:
                    value <<= bits_needed
                    value |= (self._read_byte(data, byte_idx) >> (bits_left - bits_needed)) & (
                        (1 << bits_needed) - 1
                    )
                    bits_left -= bits_needed
                    bits_needed = 0
                    if bits_left == 0:
                        bits_left = 8
                        byte_idx += 1

            decoded[key] = self._int_to_native(signal.type, value)

        return decoded, message_id

    def decode_with_metadata(self, data: bytes) -> Tuple[dict[str, Any], int, str, str]:
        decoded, message_id = self.decode_data(data)
        message_name = self.get_message_name(message_id)
        direction = self.get_message_direction(message_id)
        return decoded, message_id, message_name, direction

    def _normalize_message_id(self, id_) -> int:
        if isinstance(id_, BYTES_LIKE):
            if len(id_) == 0:
                raise ValueError("message_id bytes cannot be empty")
            id_ = int.from_bytes(bytes(id_), byteorder="big")
        try:
            message_id = int(id_)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"message_id must be an int or bytes-like object; got {type(id_)!r}"
            ) from exc

        if message_id < 0 or message_id > 0xFF:
            raise ValueError(
                f"message_id must be in the range 0..255; got {message_id}"
            )

        return message_id

    @staticmethod
    def _to_int_if_bytes_like(value: Any) -> Any:
        if isinstance(value, BYTES_LIKE):
            return int.from_bytes(bytes(value), byteorder="big")
        return value

    @staticmethod
    def _read_byte(data: bytes, byte_idx: int) -> int:
        return int.from_bytes(data[byte_idx : byte_idx + 1], byteorder="big")

    def _encode_signals(self, message_id: int, data: dict[str, Any]) -> bytes:
        result = bytearray()
        current_byte = 0
        bits_left = 8

        for key, signal in self._messages[message_id]["values"].items():
            raw = self._get_value_for_key(message_id, key, data, signal)
            int_val = self._native_to_int(signal, raw)
            bits_needed = signal.type.num_bits

            while bits_needed > 0:
                if bits_left - bits_needed < 0:
                    bits_needed -= bits_left
                    current_byte |= (int_val >> bits_needed) & ((1 << bits_left) - 1)
                    result.append(current_byte)
                    bits_left = 8
                    current_byte = 0
                else:
                    current_byte |= (int_val & ((1 << bits_needed) - 1)) << (
                        bits_left - bits_needed
                    )
                    bits_left -= bits_needed
                    bits_needed = 0
                    if bits_left == 0:
                        result.append(current_byte)
                        bits_left = 8
                        current_byte = 0

        if bits_left < 8:
            result.append(current_byte)

        return bytes(result)

    def _get_value_for_key(
        self,
        message_id: int,
        key: str,
        data: dict[str, Any],
        signal: Signal,
    ):
        if key in data:
            return self._to_int_if_bytes_like(data[key])

        msg_name = self._messages[message_id]["name"]
        alias_map = self._alias_to_numeric.get(msg_name, {})
        numeric_key = alias_map.get(key)

        if numeric_key is not None and numeric_key in data:
            return self._to_int_if_bytes_like(data[numeric_key])

        return signal.default_value

    def _native_to_int(self, signal: Signal, value: Any) -> int:
        value = self._to_int_if_bytes_like(value)
        cm = CONSTANTS.COMPACT_MESSAGES

        if signal.type == cm.UINT_8_JOYSTICK:
            return self._convert_uint8_joystick(value)
        if signal.type == cm.UINT_2_BOOL:
            return self._convert_uint2_bool(value)
        if signal.type == cm.BOOLEAN:
            return self._convert_boolean(value)
        return int(value)

    def _convert_uint8_joystick(self, value: Any) -> int:
        if isinstance(value, float):
            value = max(-1.0, min(1.0, value))
            return int(value * 100 + 100)
        if isinstance(value, int):
            if value < 0 or value > 255:
                raise ValueError(f"Joystick value out of range: {value}")
            return value
        raise TypeError(f"Unsupported joystick type: {type(value)!r}")

    def _convert_uint2_bool(self, value: Any) -> int:
        if isinstance(value, bool):
            return value + 1
        if isinstance(value, int):
            if value not in (1, 2):
                raise ValueError(
                    f"UINT_2_BOOL must be 1 (OFF) or 2 (ON); got: {value}"
                )
            return value
        if isinstance(value, float):
            return bool(value) + 1
        raise TypeError(f"Unsupported 2-bit boolean type: {type(value)!r}")

    def _convert_boolean(self, value: Any) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            if value < 0 or value > 1:
                raise ValueError(f"BOOLEAN out of range: {value}")
            return value
        raise TypeError(f"Unsupported boolean type: {type(value)!r}")

    def _int_to_native(self, dt: DataType, value: int):
        cm = CONSTANTS.COMPACT_MESSAGES
        if dt == cm.BOOLEAN:
            return bool(value)
        if dt == cm.UINT_2_BOOL:
            return value == 2
        if dt == cm.UINT_8_JOYSTICK:
            return (float(value) - 100.0) / 100.0
        return value


