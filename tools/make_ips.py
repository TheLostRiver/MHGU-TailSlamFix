#!/usr/bin/env python3
"""Generate / verify the MHGU 1.4.0 Hellblade Glavenus tail slam exefs patch.

The patch changes the tail slam hit-data record at file offset 0x17336BC:

    01 00 14 00 ...   ->   02 00 14 00 ...

The first s16 is copied into MhHitAtk + 0x5c as a float.  At 60/120 fps the
original 1.0 only covers one rendered frame (16.7 ms); 2.0 restores the ~33 ms
window that 30 fps gets from tick quantization.

Because 0x17336BC is above the 16 MiB limit of the original IPS format, the
patch is emitted as IPS32.
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

BUILD_ID = "FB08F1D20FD1204FE7070672777F869B"
OFFSET = 0x17336BC
ORIGINAL = b"\x01\x00"
PATCHED = b"\x02\x00"


def make_ips32(offset: int, data: bytes) -> bytes:
    if not 0 <= offset <= 0xFFFFFFFF:
        raise ValueError("offset does not fit in 32 bits")
    if not 1 <= len(data) <= 0xFFFF:
        raise ValueError("data length does not fit in 16 bits")
    return (
        b"IPS32"
        + struct.pack(">I", offset)
        + struct.pack(">H", len(data))
        + data
        + b"EEOF"
    )


def verify(main_bin: Path) -> None:
    blob = main_bin.read_bytes()
    if len(blob) <= OFFSET + len(ORIGINAL):
        raise SystemExit(f"{main_bin} is too small")
    actual = blob[OFFSET : OFFSET + len(ORIGINAL)]
    if actual != ORIGINAL:
        raise SystemExit(
            f"unexpected bytes at 0x{OFFSET:X}: {actual.hex(' ')} "
            f"(expected {ORIGINAL.hex(' ')})"
        )
    print(f"verified original bytes at 0x{OFFSET:X}: {actual.hex(' ')}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--main", type=Path, help="optional main.bin to verify")
    ap.add_argument("--out", type=Path, help="output .ips path")
    args = ap.parse_args()

    if args.main:
        verify(args.main)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes(make_ips32(OFFSET, PATCHED))
        print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    if not args.main and not args.out:
        sys.stdout.buffer.write(make_ips32(OFFSET, PATCHED))


if __name__ == "__main__":
    main()
