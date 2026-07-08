from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, IntFlag

SONY_VENDOR_ID = 0x054C

DUALSENSE_PRODUCT_IDS = {
    0x0CE6: "DualSense Wireless Controller",
    0x0DF2: "DualSense Edge Wireless Controller",
}


class DualSenseButton(IntFlag):
    SQUARE = 1 << 0
    CROSS = 1 << 1
    CIRCLE = 1 << 2
    TRIANGLE = 1 << 3
    L1 = 1 << 4
    R1 = 1 << 5
    L2_BUTTON = 1 << 6
    R2_BUTTON = 1 << 7
    CREATE = 1 << 8
    OPTIONS = 1 << 9
    L3 = 1 << 10
    R3 = 1 << 11
    PS = 1 << 12
    TOUCHPAD = 1 << 13
    MUTE = 1 << 14


class Dpad(IntEnum):
    UP = 0
    UP_RIGHT = 1
    RIGHT = 2
    DOWN_RIGHT = 3
    DOWN = 4
    DOWN_LEFT = 5
    LEFT = 6
    UP_LEFT = 7
    NONE = 8


@dataclass(frozen=True)
class DualSenseState:
    report_id: int
    left_x: int
    left_y: int
    right_x: int
    right_y: int
    left_trigger: int
    right_trigger: int
    dpad: Dpad
    buttons: DualSenseButton

    def dpad_directions(self) -> tuple[str, ...]:
        return {
            Dpad.UP: ("up",),
            Dpad.UP_RIGHT: ("up", "right"),
            Dpad.RIGHT: ("right",),
            Dpad.DOWN_RIGHT: ("down", "right"),
            Dpad.DOWN: ("down",),
            Dpad.DOWN_LEFT: ("down", "left"),
            Dpad.LEFT: ("left",),
            Dpad.UP_LEFT: ("up", "left"),
            Dpad.NONE: (),
        }[self.dpad]


class DualSenseReportError(ValueError):
    pass


def parse_input_report(report: bytes | bytearray | list[int]) -> DualSenseState:
    data = bytes(report)
    if len(data) < 11:
        raise DualSenseReportError(f"Input report is too short: {len(data)} bytes")

    report_id = data[0]
    common_offset = _common_report_offset(report_id)

    required = common_offset + 10
    if len(data) <= required:
        raise DualSenseReportError(
            f"Input report {report_id:#04x} is too short for DualSense common data"
        )

    x = data[common_offset]
    y = data[common_offset + 1]
    rx = data[common_offset + 2]
    ry = data[common_offset + 3]
    l2 = data[common_offset + 4]
    r2 = data[common_offset + 5]

    button_0 = data[common_offset + 7]
    button_1 = data[common_offset + 8]
    button_2 = data[common_offset + 9]

    dpad_raw = button_0 & 0x0F
    dpad = Dpad(dpad_raw) if dpad_raw <= Dpad.NONE else Dpad.NONE

    buttons = DualSenseButton(0)
    if button_0 & 0x10:
        buttons |= DualSenseButton.SQUARE
    if button_0 & 0x20:
        buttons |= DualSenseButton.CROSS
    if button_0 & 0x40:
        buttons |= DualSenseButton.CIRCLE
    if button_0 & 0x80:
        buttons |= DualSenseButton.TRIANGLE

    if button_1 & 0x01:
        buttons |= DualSenseButton.L1
    if button_1 & 0x02:
        buttons |= DualSenseButton.R1
    if button_1 & 0x04:
        buttons |= DualSenseButton.L2_BUTTON
    if button_1 & 0x08:
        buttons |= DualSenseButton.R2_BUTTON
    if button_1 & 0x10:
        buttons |= DualSenseButton.CREATE
    if button_1 & 0x20:
        buttons |= DualSenseButton.OPTIONS
    if button_1 & 0x40:
        buttons |= DualSenseButton.L3
    if button_1 & 0x80:
        buttons |= DualSenseButton.R3

    if button_2 & 0x01:
        buttons |= DualSenseButton.PS
    if button_2 & 0x02:
        buttons |= DualSenseButton.TOUCHPAD
    if button_2 & 0x04:
        buttons |= DualSenseButton.MUTE

    return DualSenseState(
        report_id=report_id,
        left_x=x,
        left_y=y,
        right_x=rx,
        right_y=ry,
        left_trigger=l2,
        right_trigger=r2,
        dpad=dpad,
        buttons=buttons,
    )


def _common_report_offset(report_id: int) -> int:
    if report_id == 0x01:
        return 1
    if report_id == 0x31:
        return 2

    # Some HID backends can return the payload without a report id.
    return 0
