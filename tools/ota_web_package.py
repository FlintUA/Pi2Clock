"""Prepare a slot-independent browser update. No device access or installation."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HEADER_SIZE = 128
MAX_SIZE = 0x180000


def make_header(data, sequence, build):
    encoded = build.encode("ascii")
    if not 4096 <= len(data) <= MAX_SIZE or not 1 <= sequence <= 65535:
        raise ValueError("Invalid payload size or ordered sequence")
    if not 1 <= len(encoded) < 64 or any(c < 32 or c > 126 for c in encoded):
        raise ValueError("Build identity must fit 63 printable ASCII bytes")
    header = bytearray(HEADER_SIZE)
    struct.pack_into("<8s4I", header, 0, b"CLOCKOT1", 0x23500002, len(data), sequence, 1)
    header[24:56] = hashlib.sha256(data).digest()
    header[56:56 + len(encoded)] = encoded
    return bytes(header)


def package(directory, tool, output):
    directory = Path(directory)
    header = (directory / "firmware_version.h").read_text()
    build = re.search(r'CLOCK_BUILD_ID "([^"\n]+)"', header)[1]
    match = re.search(r"-ota([0-9]+)-trial$", build)
    if not match or "dirty" in build or "reject" in build:
        raise ValueError("Only clean, non-reject OTA trial builds may be published")
    sequence = int(match[1])
    data = (directory / "speaking_clock_c.bin").read_bytes()
    info = subprocess.check_output([str(tool), "info", "-m", str(directory / "speaking_clock_c.uf2")],
                                   text=True, encoding="utf-8", errors="replace")
    if not re.search(r"hash:\s+verified", info) or "ARM Secure" not in info or not re.search(r"tbyb:\s+not bought", info):
        raise ValueError("ROM hash/type/trial verification failed")
    if not re.search(r"version:\s+1\." + str(sequence) + r"(?:\s|$)", info):
        raise ValueError("ROM version and build sequence differ")
    output = Path(output)
    if output.exists():
        raise ValueError("Refusing to overwrite an existing update")
    blob = make_header(data, sequence, build) + data
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(blob)
    review = {"build": build, "sequence": sequence, "bytes": len(blob),
              "sha256": hashlib.sha256(blob).hexdigest(), "payload_sha256": hashlib.sha256(data).hexdigest(),
              "format": "CLOCKOT1", "board": "pico2_w", "trial": True, "installed": False}
    output.with_suffix(".review.json").write_text(json.dumps(review, indent=2) + "\n")
    return review


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", required=True)
    parser.add_argument("--picotool", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(package(args.build, args.picotool, args.output), indent=2))
