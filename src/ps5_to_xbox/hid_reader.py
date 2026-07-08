from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .dualsense import DUALSENSE_PRODUCT_IDS, SONY_VENDOR_ID


@dataclass(frozen=True)
class HidDeviceInfo:
    path: bytes | str
    vendor_id: int
    product_id: int
    product_string: str
    serial_number: str
    manufacturer_string: str

    @property
    def display_name(self) -> str:
        product = self.product_string or DUALSENSE_PRODUCT_IDS.get(
            self.product_id, "Sony HID device"
        )
        serial = f" serial={self.serial_number}" if self.serial_number else ""
        return f"{product} vid={self.vendor_id:04x} pid={self.product_id:04x}{serial}"


def list_dualsense_devices() -> list[HidDeviceInfo]:
    hid = _import_hid()
    devices = []
    for item in hid.enumerate(SONY_VENDOR_ID, 0):
        product_id = int(item.get("product_id") or 0)
        product = str(item.get("product_string") or "")
        if product_id not in DUALSENSE_PRODUCT_IDS and "DualSense" not in product:
            continue

        devices.append(
            HidDeviceInfo(
                path=item["path"],
                vendor_id=int(item.get("vendor_id") or SONY_VENDOR_ID),
                product_id=product_id,
                product_string=product,
                serial_number=str(item.get("serial_number") or ""),
                manufacturer_string=str(item.get("manufacturer_string") or ""),
            )
        )

    return devices


class DualSenseHidReader:
    def __init__(self, info: HidDeviceInfo, read_size: int, timeout_ms: int) -> None:
        self.info = info
        self.read_size = read_size
        self.timeout_ms = timeout_ms
        self._device = None

    def __enter__(self) -> "DualSenseHidReader":
        hid = _import_hid()
        device = hid.device()
        device.open_path(self.info.path)
        device.set_nonblocking(False)
        self._device = device
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._device is not None:
            self._device.close()
            self._device = None

    def reports(self) -> Iterable[bytes]:
        if self._device is None:
            raise RuntimeError("DualSenseHidReader must be used as a context manager")

        while True:
            data = self._device.read(self.read_size, self.timeout_ms)
            if data:
                yield bytes(data)


def _import_hid():
    try:
        import hid
    except ImportError as exc:
        raise RuntimeError(
            "hidapi is not installed. Run: python -m pip install -e ."
        ) from exc
    return hid
