from __future__ import annotations

import argparse

from .bridge import Bridge, BridgeConfig
from .hid_reader import list_dualsense_devices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ps5-to-xbox",
        description="Map a DualSense controller to a virtual Xbox 360 controller.",
    )
    parser.add_argument("--list", action="store_true", help="List detected DualSense devices and exit.")
    parser.add_argument("--device-index", type=int, default=0, help="DualSense index from --list.")
    parser.add_argument("--deadzone", type=float, default=0.04, help="Stick deadzone from 0.0 to 0.3.")
    parser.add_argument("--read-size", type=int, default=78, help="HID input report read size.")
    parser.add_argument("--timeout-ms", type=int, default=50, help="HID read timeout in milliseconds.")
    parser.add_argument("--reconnect-delay", type=float, default=1.0, help="Seconds between reconnect attempts.")
    parser.add_argument("--no-reconnect", action="store_true", help="Exit instead of waiting after disconnect.")
    parser.add_argument("--verbose", action="store_true", help="Print report rate and skipped parser errors.")
    parser.add_argument("--dump-raw", action="store_true", help="Print raw HID reports in hex.")
    args = parser.parse_args(argv)

    if args.deadzone < 0.0 or args.deadzone > 0.3:
        parser.error("--deadzone must be between 0.0 and 0.3")

    if args.list:
        devices = list_dualsense_devices()
        if not devices:
            print("No DualSense devices found.")
            return 1
        for index, device in enumerate(devices):
            print(f"[{index}] {device.display_name}")
        return 0

    config = BridgeConfig(
        device_index=args.device_index,
        deadzone=args.deadzone,
        read_size=args.read_size,
        timeout_ms=args.timeout_ms,
        reconnect_delay=args.reconnect_delay,
        reconnect=not args.no_reconnect,
        verbose=args.verbose,
        dump_raw=args.dump_raw,
    )
    return Bridge(config).run()
