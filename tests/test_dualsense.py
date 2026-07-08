import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ps5_to_xbox.dualsense import Dpad, DualSenseButton, parse_input_report
from ps5_to_xbox.mapping import _axis_to_float, to_xbox_state


class DualSenseParserTests(unittest.TestCase):
    def test_parses_usb_report_buttons_and_axes(self):
        report = bytearray(64)
        report[0] = 0x01
        report[1] = 128
        report[2] = 0
        report[3] = 255
        report[4] = 128
        report[5] = 10
        report[6] = 240
        report[8] = 0x20 | Dpad.UP_RIGHT
        report[9] = 0x01 | 0x20 | 0x40
        report[10] = 0x01

        state = parse_input_report(report)

        self.assertEqual(state.report_id, 0x01)
        self.assertEqual(state.left_x, 128)
        self.assertEqual(state.left_y, 0)
        self.assertEqual(state.right_x, 255)
        self.assertEqual(state.right_y, 128)
        self.assertEqual(state.left_trigger, 10)
        self.assertEqual(state.right_trigger, 240)
        self.assertEqual(state.dpad, Dpad.UP_RIGHT)
        self.assertTrue(state.buttons & DualSenseButton.CROSS)
        self.assertTrue(state.buttons & DualSenseButton.L1)
        self.assertTrue(state.buttons & DualSenseButton.OPTIONS)
        self.assertTrue(state.buttons & DualSenseButton.L3)
        self.assertTrue(state.buttons & DualSenseButton.PS)

    def test_parses_bluetooth_common_offset(self):
        report = bytearray(78)
        report[0] = 0x31
        report[2] = 1
        report[3] = 2
        report[4] = 3
        report[5] = 4
        report[6] = 5
        report[7] = 6
        report[9] = 0x40 | Dpad.DOWN

        state = parse_input_report(report)

        self.assertEqual(state.left_x, 1)
        self.assertEqual(state.left_y, 2)
        self.assertEqual(state.right_x, 3)
        self.assertEqual(state.right_y, 4)
        self.assertEqual(state.left_trigger, 5)
        self.assertEqual(state.right_trigger, 6)
        self.assertEqual(state.dpad, Dpad.DOWN)
        self.assertTrue(state.buttons & DualSenseButton.CIRCLE)


class MappingTests(unittest.TestCase):
    def test_axis_deadzone_and_inversion(self):
        self.assertEqual(_axis_to_float(128, deadzone=0.04), 0.0)
        self.assertEqual(_axis_to_float(130, deadzone=0.04), 0.0)
        self.assertEqual(_axis_to_float(0, deadzone=0.04), -1.0)
        self.assertEqual(_axis_to_float(255, deadzone=0.04), 1.0)
        self.assertEqual(_axis_to_float(0, deadzone=0.04, invert=True), 1.0)

    def test_maps_dualsense_to_xbox_names(self):
        report = bytearray(64)
        report[0] = 0x01
        report[1:7] = bytes([128, 128, 128, 128, 255, 0])
        report[8] = 0x20 | Dpad.LEFT
        report[9] = 0x02 | 0x10

        xbox = to_xbox_state(parse_input_report(report), deadzone=0.04)

        self.assertEqual(xbox.left_trigger, 1.0)
        self.assertIn("a", xbox.buttons)
        self.assertIn("right_shoulder", xbox.buttons)
        self.assertIn("back", xbox.buttons)
        self.assertIn("dpad_left", xbox.buttons)


if __name__ == "__main__":
    unittest.main()
