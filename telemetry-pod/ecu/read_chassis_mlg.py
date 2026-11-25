"""Export FOME MLVLG v2 chassis samples from an ECU SD log to CSV."""
import argparse
import csv
import struct
import sys
from pathlib import Path

FIELD_NAMES = {
    "Time": "time_s",
    "Aux linear 1": "front_brake_bar",
    "Aux linear 2": "rear_brake_bar",
    "Aux linear 3": "fork_mm",
    "Aux linear 4": "shock_mm",
    "Lua: Gauge 1": "lean_deg",
    "Lua: Gauge 2": "pitch_deg",
}
FORMATS = ("B", "b", "H", "h", "I", "i", "q", "f")

def samples(f):
    header = f.read(24)
    if len(header) != 24 or header[:8] != b"MLVLG\0\0\2":
        raise ValueError("Expected a FOME MLVLG version 2 header")
    start, length, count = struct.unpack(">IHH", header[16:24])
    if start != 24 + 89 * count:
        raise ValueError("Field table does not end at the data offset")
    fields = {}
    offset = 0
    for _ in range(count):
        field = f.read(89)
        if len(field) != 89 or field[0] >= len(FORMATS):
            raise ValueError("Invalid field descriptor")
        fmt = ">" + FORMATS[field[0]]
        name = field[1:35].split(b"\0", 1)[0].decode("ascii", "replace")
        if name in FIELD_NAMES:
            if name in fields:
                raise ValueError("Ambiguous log field " + name)
            scale, shift = struct.unpack_from(">ff", field, 46)
            fields[name] = (offset, fmt, scale, shift)
        offset += struct.calcsize(fmt)
    if offset != length or set(fields) != FIELD_NAMES.keys():
        raise ValueError("Wrong record size or missing chassis log columns")
    previous = None
    while block := f.read(length + 5):
        if len(block) != length + 5 or block[0] != 0:
            raise ValueError("Truncated or unsupported log block")
        if previous is not None and block[1] != (previous + 1) % 256:
            raise ValueError("Discontinuous block counter")
        previous = block[1]
        payload = block[4:-1]
        if sum(payload) % 256 != block[-1]:
            raise ValueError("Incorrect block checksum")
        row = {}
        for name, (pos, fmt, scale, shift) in fields.items():
            value = struct.unpack_from(fmt, payload, pos)[0]
            row[FIELD_NAMES[name]] = (value + shift) * scale
        yield row

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    args = parser.parse_args()
    writer = csv.DictWriter(sys.stdout, fieldnames=list(FIELD_NAMES.values()))
    writer.writeheader()
    with args.log.open("rb") as f:
        for row in samples(f):
            writer.writerow({k: format(v, ".8g") for k, v in row.items()})
