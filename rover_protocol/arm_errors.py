"""Arm command rejection codes shared by the rover and the basestation.

``RoverArmController`` reports a human-readable rejection in
``last_failure`` (for example ``"Normal blocked: octant 5 requires Planar"``).
The wire format only has room for a small code plus one argument, normally
the octant number, so this module is the single mapping between the two.

Keep this file identical in the rover and basestation protocol copies.
"""

from __future__ import annotations

import re
from typing import Tuple

ARM_ERROR_NONE = 0
ARM_ERROR_OCTANT_REQUIRES_PLANAR = 1
ARM_ERROR_FLIP_OCTANT = 2
ARM_ERROR_PLANAR_BASE_RANGE = 3
ARM_ERROR_PLANAR_EXIT_LOCKED = 4
ARM_ERROR_PLANAR_EXIT_POSE = 5
ARM_ERROR_PLANAR_OCTANTS = 6
ARM_ERROR_PLANAR_OCTANTS_FLIPPED = 7
ARM_ERROR_HEIGHT_LIMIT = 8
ARM_ERROR_ACTION_RUNNING = 9
ARM_ERROR_INVALID_JOINT = 10
ARM_ERROR_INVALID_AXIS = 11
ARM_ERROR_FLIP_RUNNING = 12
ARM_ERROR_FLIP_NO_PATH = 13
ARM_ERROR_GUIDE_LOCKED = 14
ARM_ERROR_GUIDE_NOT_ALIGNED = 15
ARM_ERROR_NORMAL_OCTANT = 16
ARM_ERROR_NORMAL_LIMITS = 17
ARM_ERROR_FLIPPED_OCTANT = 18
ARM_ERROR_FLIPPED_LIMITS = 19
ARM_ERROR_NOT_READY = 20
ARM_ERROR_ESTOP = 21
ARM_ERROR_UNKNOWN_COMMAND = 22
ARM_ERROR_REJECTED = 23

_OCTANT_RE = re.compile(r"octant\s+(\d+)", re.IGNORECASE)


def classify_failure(message: str) -> Tuple[int, int]:
    """Map a ``RoverArmController`` failure string to ``(code, argument)``."""
    text = (message or "").strip()
    if not text:
        return ARM_ERROR_NONE, 0

    lower = text.lower()
    match = _OCTANT_RE.search(text)
    octant = int(match.group(1)) if match else 0

    # Check the specific "unavailable / locked" messages before the
    # generic "requires planar" suffix they all share.
    if "planar locked" in lower:
        return ARM_ERROR_PLANAR_EXIT_LOCKED, 0
    if "planar cannot be exited" in lower:
        return ARM_ERROR_PLANAR_EXIT_POSE, 0
    if "planar needs base" in lower:
        return ARM_ERROR_PLANAR_BASE_RANGE, 0
    if "planar flipped limited" in lower:
        return ARM_ERROR_PLANAR_OCTANTS_FLIPPED, 0
    if "planar limited" in lower:
        return ARM_ERROR_PLANAR_OCTANTS, 0
    if "normal unavailable" in lower:
        if "restricted" in lower:
            return ARM_ERROR_NORMAL_OCTANT, 0
        return ARM_ERROR_NORMAL_LIMITS, 0
    if "flipped unavailable" in lower:
        if "restricted" in lower:
            return ARM_ERROR_FLIPPED_OCTANT, 0
        return ARM_ERROR_FLIPPED_LIMITS, 0
    if "requires planar" in lower:
        if lower.startswith("flip"):
            return ARM_ERROR_FLIP_OCTANT, octant
        return ARM_ERROR_OCTANT_REQUIRES_PLANAR, octant
    if "height limit" in lower:
        return ARM_ERROR_HEIGHT_LIMIT, 0
    if "action is running" in lower:
        return ARM_ERROR_ACTION_RUNNING, 0
    if "invalid joint" in lower:
        return ARM_ERROR_INVALID_JOINT, 0
    if "invalid axis" in lower:
        return ARM_ERROR_INVALID_AXIS, 0
    if "another flip" in lower:
        return ARM_ERROR_FLIP_RUNNING, 0
    if "no safe path" in lower:
        return ARM_ERROR_FLIP_NO_PATH, 0
    if "orientation is locked" in lower:
        return ARM_ERROR_GUIDE_LOCKED, 0
    if "guide unavailable" in lower:
        return ARM_ERROR_GUIDE_NOT_ALIGNED, 0
    return ARM_ERROR_REJECTED, 0


_TEXT = {
    ARM_ERROR_PLANAR_BASE_RANGE:
        "Planar needs base within +/-5 deg",
    ARM_ERROR_PLANAR_EXIT_LOCKED:
        "Planar required in this octant",
    ARM_ERROR_PLANAR_EXIT_POSE:
        "Planar cannot be exited at this pose",
    ARM_ERROR_PLANAR_OCTANTS:
        "Planar limited to octants 1 and 5",
    ARM_ERROR_PLANAR_OCTANTS_FLIPPED:
        "Planar flipped limited to octants 3 and 7",
    ARM_ERROR_HEIGHT_LIMIT:
        "Height limit - end effector too low",
    ARM_ERROR_ACTION_RUNNING:
        "Arm busy - wait for the action to finish",
    ARM_ERROR_INVALID_JOINT:
        "Invalid joint index",
    ARM_ERROR_INVALID_AXIS:
        "Invalid axis",
    ARM_ERROR_FLIP_RUNNING:
        "Flip blocked - another flip is running",
    ARM_ERROR_FLIP_NO_PATH:
        "Flip blocked - no safe path",
    ARM_ERROR_GUIDE_LOCKED:
        "Guide blocked - orientation locked (press O)",
    ARM_ERROR_GUIDE_NOT_ALIGNED:
        "Guide unavailable - orientation not aligned",
    ARM_ERROR_NORMAL_OCTANT:
        "Normal unavailable in this octant - press X",
    ARM_ERROR_NORMAL_LIMITS:
        "Normal unavailable - outside normal limits",
    ARM_ERROR_FLIPPED_OCTANT:
        "Flipped unavailable in this octant - press X",
    ARM_ERROR_FLIPPED_LIMITS:
        "Flipped unavailable - outside flipped limits",
    ARM_ERROR_NOT_READY:
        "Arm not ready - waiting for joint angles",
    ARM_ERROR_ESTOP:
        "E-stop active - arm commands ignored",
    ARM_ERROR_UNKNOWN_COMMAND:
        "Unknown arm command",
    ARM_ERROR_REJECTED:
        "Arm command rejected",
}


def error_text(code: int, argument: int = 0) -> str:
    """Human-readable text for one wire error code."""
    code = int(code)
    argument = int(argument)
    if code == ARM_ERROR_NONE:
        return ""
    if code == ARM_ERROR_OCTANT_REQUIRES_PLANAR:
        return f"Octant {argument} requires Planar - press X"
    if code == ARM_ERROR_FLIP_OCTANT:
        return f"Flip blocked: octant {argument} requires Planar - press X"
    return _TEXT.get(code, f"Arm error {code}")


__all__ = [
    "ARM_ERROR_NONE",
    "ARM_ERROR_OCTANT_REQUIRES_PLANAR",
    "ARM_ERROR_FLIP_OCTANT",
    "ARM_ERROR_PLANAR_BASE_RANGE",
    "ARM_ERROR_PLANAR_EXIT_LOCKED",
    "ARM_ERROR_PLANAR_EXIT_POSE",
    "ARM_ERROR_PLANAR_OCTANTS",
    "ARM_ERROR_PLANAR_OCTANTS_FLIPPED",
    "ARM_ERROR_HEIGHT_LIMIT",
    "ARM_ERROR_ACTION_RUNNING",
    "ARM_ERROR_INVALID_JOINT",
    "ARM_ERROR_INVALID_AXIS",
    "ARM_ERROR_FLIP_RUNNING",
    "ARM_ERROR_FLIP_NO_PATH",
    "ARM_ERROR_GUIDE_LOCKED",
    "ARM_ERROR_GUIDE_NOT_ALIGNED",
    "ARM_ERROR_NORMAL_OCTANT",
    "ARM_ERROR_NORMAL_LIMITS",
    "ARM_ERROR_FLIPPED_OCTANT",
    "ARM_ERROR_FLIPPED_LIMITS",
    "ARM_ERROR_NOT_READY",
    "ARM_ERROR_ESTOP",
    "ARM_ERROR_UNKNOWN_COMMAND",
    "ARM_ERROR_REJECTED",
    "classify_failure",
    "error_text",
]
