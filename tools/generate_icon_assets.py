"""Generate the two Windows ICO files from versioned, local artwork.

The SVG files in ``assets`` are human-editable design references.  This renderer
uses only the Python standard library so a release build is independent of a
browser, image editor, or downloaded image asset.
"""

from __future__ import annotations

import argparse
import math
import struct
import zlib
from pathlib import Path
from typing import Callable


RGBA = tuple[int, int, int, int]
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)


def _clamp(value: int) -> int:
    return max(0, min(255, value))


class Canvas:
    def __init__(self, size: int) -> None:
        self.size = size
        self.pixels = bytearray(size * size * 4)

    def set_pixel(self, x: int, y: int, color: RGBA) -> None:
        if not (0 <= x < self.size and 0 <= y < self.size):
            return
        index = (y * self.size + x) * 4
        self.pixels[index : index + 4] = bytes(color)

    def rounded_rect(
        self, left: float, top: float, right: float, bottom: float, radius: float, color: RGBA
    ) -> None:
        for y in range(max(0, int(top)), min(self.size, int(bottom) + 1)):
            for x in range(max(0, int(left)), min(self.size, int(right) + 1)):
                nearest_x = min(max(x, left + radius), right - radius)
                nearest_y = min(max(y, top + radius), bottom - radius)
                if (x - nearest_x) ** 2 + (y - nearest_y) ** 2 <= radius**2:
                    self.set_pixel(x, y, color)

    def circle(self, center_x: float, center_y: float, radius: float, color: RGBA) -> None:
        radius_squared = radius * radius
        for y in range(max(0, int(center_y - radius)), min(self.size, int(center_y + radius) + 1)):
            for x in range(max(0, int(center_x - radius)), min(self.size, int(center_x + radius) + 1)):
                if (x - center_x) ** 2 + (y - center_y) ** 2 <= radius_squared:
                    self.set_pixel(x, y, color)

    def line(self, start_x: float, start_y: float, end_x: float, end_y: float, width: float, color: RGBA) -> None:
        length = max(abs(end_x - start_x), abs(end_y - start_y), 1)
        steps = int(length) + 1
        for step in range(steps):
            progress = step / (steps - 1) if steps > 1 else 0
            self.circle(
                start_x + (end_x - start_x) * progress,
                start_y + (end_y - start_y) * progress,
                width / 2,
                color,
            )

    def downsample(self, target_size: int) -> bytes:
        factor = self.size // target_size
        pixels = bytearray(target_size * target_size * 4)
        area = factor * factor
        for y in range(target_size):
            for x in range(target_size):
                totals = [0, 0, 0, 0]
                for sub_y in range(factor):
                    for sub_x in range(factor):
                        source = ((y * factor + sub_y) * self.size + (x * factor + sub_x)) * 4
                        for channel in range(4):
                            totals[channel] += self.pixels[source + channel]
                target = (y * target_size + x) * 4
                for channel in range(4):
                    pixels[target + channel] = totals[channel] // area
        return bytes(pixels)


def _gradient(top_left: RGBA, bottom_right: RGBA, progress: float) -> RGBA:
    return tuple(
        _clamp(round(top_left[channel] + (bottom_right[channel] - top_left[channel]) * progress))
        for channel in range(4)
    )  # type: ignore[return-value]


def _background(canvas: Canvas, top_left: RGBA, bottom_right: RGBA) -> None:
    margin = canvas.size * 0.035
    radius = canvas.size * 0.22
    for y in range(canvas.size):
        for x in range(canvas.size):
            nearest_x = min(max(x, margin + radius), canvas.size - margin - radius)
            nearest_y = min(max(y, margin + radius), canvas.size - margin - radius)
            if (x - nearest_x) ** 2 + (y - nearest_y) ** 2 <= radius**2:
                canvas.set_pixel(x, y, _gradient(top_left, bottom_right, (x + y) / (2 * canvas.size)))


def _app_icon(canvas: Canvas) -> None:
    s = canvas.size
    _background(canvas, (23, 37, 84, 255), (7, 17, 31, 255))
    cyan = (103, 232, 249, 255)
    green = (34, 197, 94, 255)
    pale = (224, 242, 254, 255)
    dark = (15, 23, 42, 255)
    width = s * 0.07
    left, right, base = s * 0.25, s * 0.75, s * 0.76
    canvas.line(left, base, left, s * 0.43, width, cyan)
    canvas.line(right, base, right, s * 0.43, width, green)
    previous_x, previous_y = left, s * 0.43
    for point in range(1, 25):
        angle = 3.14159265 - (3.14159265 * point / 24)
        current_x = s * 0.5 + s * 0.25 * math.cos(angle)
        current_y = s * 0.43 - s * 0.26 * math.sin(angle)
        canvas.line(previous_x, previous_y, current_x, current_y, width, cyan if point < 12 else green)
        previous_x, previous_y = current_x, current_y
    canvas.line(left, base, right, base, width * 0.82, (187, 247, 208, 255))
    nodes = ((s * 0.33, s * 0.32), (s * 0.50, s * 0.22), (s * 0.67, s * 0.32))
    canvas.line(nodes[0][0], nodes[0][1], nodes[1][0], nodes[1][1], s * 0.025, (125, 211, 252, 255))
    canvas.line(nodes[1][0], nodes[1][1], nodes[2][0], nodes[2][1], s * 0.025, (125, 211, 252, 255))
    for x, y in nodes:
        canvas.circle(x, y, s * 0.043, pale)
    canvas.circle(s * 0.50, s * 0.54, s * 0.090, dark)
    canvas.circle(s * 0.50, s * 0.54, s * 0.075, (10, 34, 47, 255))
    canvas.line(s * 0.46, s * 0.54, s * 0.54, s * 0.54, s * 0.026, cyan)
    canvas.line(s * 0.50, s * 0.50, s * 0.50, s * 0.58, s * 0.026, (94, 234, 212, 255))


def _setup_icon(canvas: Canvas) -> None:
    s = canvas.size
    _background(canvas, (59, 23, 108, 255), (22, 10, 50, 255))
    amber = (251, 191, 36, 255)
    orange = (249, 115, 22, 255)
    pale = (254, 215, 170, 255)
    line = s * 0.045
    top = s * 0.33
    left, center, right = s * 0.22, s * 0.50, s * 0.78
    bottom = s * 0.75
    canvas.line(left, top, center, s * 0.49, line, amber)
    canvas.line(center, s * 0.49, right, top, line, orange)
    canvas.line(left, top, left, s * 0.65, line, amber)
    canvas.line(right, top, right, s * 0.65, line, orange)
    canvas.line(left, s * 0.65, center, bottom, line, amber)
    canvas.line(right, s * 0.65, center, bottom, line, orange)
    canvas.line(center, s * 0.49, center, bottom, line, pale)
    canvas.line(center, s * 0.17, center, s * 0.39, s * 0.052, (233, 213, 255, 255))
    canvas.line(center, s * 0.17, s * 0.42, s * 0.25, s * 0.052, (233, 213, 255, 255))
    canvas.line(center, s * 0.17, s * 0.58, s * 0.25, s * 0.052, (233, 213, 255, 255))
    canvas.circle(center, s * 0.62, s * 0.067, (46, 16, 101, 255))
    canvas.line(s * 0.47, s * 0.62, s * 0.53, s * 0.62, s * 0.024, (254, 243, 199, 255))
    canvas.line(center, s * 0.59, center, s * 0.65, s * 0.024, (254, 243, 199, 255))


def _png(width: int, height: int, rgba: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + rgba[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


def _ico(renderer: Callable[[Canvas], None]) -> bytes:
    images: list[tuple[int, bytes]] = []
    for size in ICON_SIZES:
        # Two-times supersampling keeps the small Windows shell sizes smooth while
        # keeping this standard-library generator fast enough for every build.
        canvas = Canvas(size * 2)
        renderer(canvas)
        images.append((size, _png(size, size, canvas.downsample(size))))
    directory_size = 6 + len(images) * 16
    offset = directory_size
    entries: list[bytes] = []
    payloads: list[bytes] = []
    for size, image in images:
        encoded_size = 0 if size == 256 else size
        entries.append(struct.pack("<BBBBHHII", encoded_size, encoded_size, 0, 0, 1, 32, len(image), offset))
        payloads.append(image)
        offset += len(image)
    return struct.pack("<HHH", 0, 1, len(images)) + b"".join(entries) + b"".join(payloads)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera ícones ICO do Codex Model Gate.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets",
        help="Pasta que receberá os arquivos .ico.",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "CodexModelGate.ico").write_bytes(_ico(_app_icon))
    (args.output_dir / "CodexModelGate-Setup.ico").write_bytes(_ico(_setup_icon))


if __name__ == "__main__":
    main()
