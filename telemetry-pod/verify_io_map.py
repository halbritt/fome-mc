#!/usr/bin/env python3
"""Retired revision-2 proposal traceability checker; see IO_MAP.md and IO_MAP_HISTORY.md.

The original implementation remains at 13c0bfb:telemetry-pod/verify_io_map.py.
Current requirements and the MCU_Path CSV are outside that historical capture.
"""
import sys


if __name__ == "__main__":
    print("RETIRED: revision-2 proposal traceability check; see telemetry-pod/IO_MAP.md. "
          "Use make verify-io PROJECT=telemetry-pod for current connectivity; "
          "current specification traceability has not been recaptured.", file=sys.stderr)
    raise SystemExit(2)
