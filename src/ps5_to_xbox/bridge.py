from __future__ import annotations

import signal
import time
from dataclasses import dataclass

from .dualsense import DualSenseReportError, parse_input_report
from .hid_reader import DualSenseHidReader, list_dualsense_devices
from .mapping import to_xbox_state
from .xbox import VirtualXboxController


@dataclass(frozen=True)
class BridgeConfig:
    device_index: int = 0
    deadzone: float = 0.04
    read_size: int = 78
    timeout_ms: int = 50
    reconnect_delay: float = 1.0
    reconnect: bool = True
    verbose: bool = False
    dump_raw: bool = False


class Bridge:
    def __init__(self, config: BridgeConfig) -> None:
        self.config = config
        self._running = True
        self._controller: VirtualXboxController | None = None

    def run(self) -> int:
        self._install_signal_handlers()
        self._controller = VirtualXboxController()
        print("Virtual Xbox 360 controller ready.")

        try:
            while self._running:
                devices = list_dualsense_devices()
                if not devices:
                    print("DualSense not found. Waiting...")
                    if not self.config.reconnect:
                        return 2
                    time.sleep(self.config.reconnect_delay)
                    continue

                if self.config.device_index >= len(devices):
                    print(
                        f"Device index {self.config.device_index} is not available; "
                        f"{len(devices)} DualSense device(s) found."
                    )
                    return 2

                info = devices[self.config.device_index]
                print(f"Using {info.display_name}")
                try:
                    self._read_device(info)
                except OSError as exc:
                    print(f"Device disconnected or HID read failed: {exc}")
                except RuntimeError as exc:
                    print(str(exc))
                    return 2

                if not self.config.reconnect:
                    break
                time.sleep(self.config.reconnect_delay)
        finally:
            if self._controller is not None:
                self._controller.reset()

        return 0

    def _read_device(self, info) -> None:
        last_report_at = time.perf_counter()
        frames = 0
        with DualSenseHidReader(
            info,
            read_size=self.config.read_size,
            timeout_ms=self.config.timeout_ms,
        ) as reader:
            for report in reader.reports():
                if not self._running:
                    return

                if self.config.dump_raw:
                    print(report.hex(" "))

                try:
                    dualsense_state = parse_input_report(report)
                except DualSenseReportError as exc:
                    if self.config.verbose:
                        print(f"Skipping report: {exc}")
                    continue

                xbox_state = to_xbox_state(dualsense_state, self.config.deadzone)
                assert self._controller is not None
                self._controller.apply(xbox_state)

                frames += 1
                now = time.perf_counter()
                elapsed = now - last_report_at
                if self.config.verbose and elapsed >= 1.0:
                    print(f"{frames / elapsed:.0f} reports/s")
                    frames = 0
                    last_report_at = now

    def _install_signal_handlers(self) -> None:
        def stop(_signum, _frame) -> None:
            self._running = False

        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)
