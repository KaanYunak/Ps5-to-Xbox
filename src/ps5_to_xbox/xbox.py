from __future__ import annotations

from .mapping import XboxState


class VirtualXboxController:
    def __init__(self) -> None:
        try:
            import vgamepad as vg
        except ImportError as exc:
            raise RuntimeError(
                "vgamepad is not installed. Run: python -m pip install -e ."
            ) from exc

        self._vg = vg
        self._gamepad = vg.VX360Gamepad()
        self._pressed: set[str] = set()
        self._button_map = {
            "a": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
            "b": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
            "x": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
            "y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "left_shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "right_shoulder": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "back": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "start": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
            "left_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "right_thumb": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "guide": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE,
            "dpad_up": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            "dpad_down": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            "dpad_left": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            "dpad_right": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        }

    def apply(self, state: XboxState) -> None:
        self._gamepad.left_joystick_float(
            x_value_float=state.left_x,
            y_value_float=state.left_y,
        )
        self._gamepad.right_joystick_float(
            x_value_float=state.right_x,
            y_value_float=state.right_y,
        )
        self._gamepad.left_trigger_float(value_float=state.left_trigger)
        self._gamepad.right_trigger_float(value_float=state.right_trigger)

        desired = set(state.buttons)
        for button in self._pressed - desired:
            self._gamepad.release_button(button=self._button_map[button])
        for button in desired - self._pressed:
            self._gamepad.press_button(button=self._button_map[button])

        self._pressed = desired
        self._gamepad.update()

    def reset(self) -> None:
        self._gamepad.reset()
        self._gamepad.update()
        self._pressed.clear()
