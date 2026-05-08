from __future__ import annotations

import time
from typing import Optional

VALID_DIGITS = set(range(1, 6))

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None


def list_serial_ports() -> list[str]:
    if list_ports is None:
        raise ImportError(
            "Khong tim thay package 'pyserial'. Hay cai dat bang 'pip install -r requirements.txt'."
        )

    ports = []
    for port in list_ports.comports():
        ports.append(f"{port.device} - {port.description}")

    return ports


class SerialDigitSender:
    def __init__(self, port: Optional[str], baudrate: int = 115200, stable_frames: int = 4):
        if stable_frames < 1:
            raise ValueError("stable_frames must be at least 1")

        self._port = port
        self._baudrate = baudrate
        self._stable_frames = stable_frames
        self._candidate_digit: Optional[int] = None
        self._candidate_frames = 0
        self._last_sent_digit: Optional[int] = None
        self._serial = None

        if self._port is None:
            return

        if serial is None:
            raise ImportError(
                "Khong tim thay package 'pyserial'. Hay cai dat bang 'pip install -r requirements.txt'."
            )

        self._serial = serial.Serial(
            port=self._port,
            baudrate=self._baudrate,
            timeout=0,
            write_timeout=0.2,
        )
        time.sleep(0.2)
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()

    @property
    def enabled(self) -> bool:
        return self._serial is not None

    @property
    def port_label(self) -> str:
        return self._port if self._port is not None else "disabled"

    @property
    def last_sent_digit(self) -> Optional[int]:
        return self._last_sent_digit

    def send_digit(self, digit: int) -> None:
        if digit not in VALID_DIGITS:
            raise ValueError("digit must be in range 1..5")

        self._write_digit(digit)
        self._last_sent_digit = digit

    def update(self, detected_digit: int) -> Optional[int]:
        candidate_digit = detected_digit if detected_digit in VALID_DIGITS else None

        if candidate_digit != self._candidate_digit:
            self._candidate_digit = candidate_digit
            self._candidate_frames = 0

        if candidate_digit is None:
            return None

        self._candidate_frames += 1

        if self._candidate_frames < self._stable_frames:
            return None

        if candidate_digit == self._last_sent_digit:
            return None

        self.send_digit(candidate_digit)
        return candidate_digit

    def _write_digit(self, digit: int) -> None:
        if self._serial is None:
            return

        self._serial.write(f"{digit}\n".encode("ascii"))
        self._serial.flush()

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None


def send_digit_sequence(
    port: str,
    digits: str = "12345",
    baudrate: int = 115200,
    delay_seconds: float = 0.25,
) -> list[int]:
    sequence = []
    for char in digits:
        if char.isspace() or char in ",;":
            continue
        if char < "1" or char > "5":
            raise ValueError("test digits must contain only 1..5")
        sequence.append(int(char))

    if not sequence:
        raise ValueError("test digits must contain at least one digit in range 1..5")

    sender = SerialDigitSender(port=port, baudrate=baudrate, stable_frames=1)
    try:
        for digit in sequence:
            sender.send_digit(digit)
            time.sleep(delay_seconds)
    finally:
        sender.close()

    return sequence
