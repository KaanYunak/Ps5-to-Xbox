from __future__ import annotations

from dataclasses import dataclass

from .dualsense import DualSenseState


@dataclass(frozen=True)
class XboxState:
    left_x: float
    left_y: float
    right_x: float
    right_y: float
    left_trigger: float
    right_trigger: float
    buttons: frozenset[str]


def to_xbox_state(state: DualSenseState, deadzone: float) -> XboxState:
    buttons = set(_digital_buttons(state))

    for direction in state.dpad_directions():
        buttons.add(f"dpad_{direction}")

    return XboxState(
        left_x=_axis_to_float(state.left_x, deadzone=deadzone),
        left_y=_axis_to_float(state.left_y, deadzone=deadzone, invert=True),
        right_x=_axis_to_float(state.right_x, deadzone=deadzone),
        right_y=_axis_to_float(state.right_y, deadzone=deadzone, invert=True),
        left_trigger=state.left_trigger / 255.0,
        right_trigger=state.right_trigger / 255.0,
        buttons=frozenset(buttons),
    )


def _axis_to_float(value: int, deadzone: float, invert: bool = False) -> float:
    value = max(0, min(255, value))
    if value == 128:
        normalized = 0.0
    elif value > 128:
        normalized = (value - 128) / 127.0
    else:
        normalized = (value - 128) / 128.0

    if abs(normalized) < deadzone:
        normalized = 0.0

    if invert:
        normalized = -normalized

    return max(-1.0, min(1.0, normalized))


def _digital_buttons(state: DualSenseState) -> tuple[str, ...]:
    from .dualsense import DualSenseButton as B

    mapping = (
        (B.CROSS, "a"),
        (B.CIRCLE, "b"),
        (B.SQUARE, "x"),
        (B.TRIANGLE, "y"),
        (B.L1, "left_shoulder"),
        (B.R1, "right_shoulder"),
        (B.CREATE, "back"),
        (B.OPTIONS, "start"),
        (B.L3, "left_thumb"),
        (B.R3, "right_thumb"),
        (B.PS, "guide"),
    )

    return tuple(name for button, name in mapping if state.buttons & button)
