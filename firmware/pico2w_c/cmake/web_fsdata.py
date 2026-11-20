#!/usr/bin/env python3
"""Generate lwIP httpd fsdata for the phone page.

Same output layout as the Pico SDK's makefsdata.py. With --gzip the page is
stored once, gzip-compressed (deterministic, mtime 0), under its original
URL with a "Content-Encoding: gzip" header. Without --gzip the output is
byte-identical to makefsdata.py (checked by tests/web_fsdata_test.py).
"""
import argparse
import gzip
import mimetypes
import re
from pathlib import Path

ALIGN = 4
SERVER = "Server: lwIP/2.2.0d (http://savannah.nongnu.org/projects/lwip)\r\n"


def file_records(path, root, compress):
    name = f"/{path.relative_to(root).as_posix()}\x00"
    name += "\x00" * (-len(name) % ALIGN)
    body = path.read_bytes()
    content_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    headers = f"Content-Type: {content_type}\r\n"
    if compress:
        body = gzip.compress(body, compresslevel=9, mtime=0)
        headers += "Content-Encoding: gzip\r\n"
    return [
        (name.encode(), f'"/{path.relative_to(root).as_posix()}" ({len(name)} chars)'),
        (b"HTTP/1.0 200 OK\r\n", '"HTTP/1.0 200 OK" (17 chars)'),
        (SERVER.encode(), f'"{SERVER.strip()}" ({len(SERVER)} chars)'),
        (f"Content-Length: {len(body)}\r\n".encode(),
         f'"Content-Length: {len(body)}" ({len(f"Content-Length: {len(body)}") + 2} chars)'),
        ((headers + "\r\n").encode(), None),
        (body, f"raw file data ({len(body)} bytes)"),
    ]


def emit(out, files, compress):
    out.write('#include "lwip/apps/fs.h"\n\n')
    root = files[0].parent
    entries = []
    for path in files:
        var = re.sub(r"\W+", "_", str(path.relative_to(root)), flags=re.ASCII)
        records = file_records(path, root, compress)
        out.write(f"static const unsigned char data_{var}[] = {{\n")
        for data, comment in records:
            if comment is None:  # type (+ encoding) header, worded as makefsdata.py
                text = data.decode()[:-4].replace("\r\n", " ")
                comment = f'"{text}" ({len(data)} chars)'
            out.write(f"\n    /* {comment} */\n")
            for i in range(0, len(data), 16):
                out.write("    " + "".join(f"0x{b:02x}," for b in data[i:i + 16]) + "\n")
        out.write("};\n\n")
        entries.append((var, len(records[0][0])))
    last = "NULL"
    for var, name_size in entries:
        out.write(f"const struct fsdata_file file_{var}[] = {{{{\n    {last},\n    data_{var},\n"
                  f"    data_{var} + {name_size},\n    sizeof(data_{var}) - {name_size},\n"
                  "    FS_FILE_FLAGS_HEADER_INCLUDED | FS_FILE_FLAGS_HEADER_PERSISTENT,\n}};\n\n")
        last = f"file_{var}"
    out.write(f"#define FS_ROOT {last}\n#define FS_NUMFILES {len(entries)}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--input", nargs="+", required=True)
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--gzip", action="store_true")
    args = parser.parse_args()
    mimetypes.init()
    with open(args.output, "w") as out:
        emit(out, [Path(p) for p in args.input], args.gzip)


if __name__ == "__main__":
    main()
