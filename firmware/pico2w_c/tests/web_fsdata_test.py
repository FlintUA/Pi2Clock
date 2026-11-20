"""Checks cmake/web_fsdata.py: the gzip page decodes to the source page, the headers are
correct, and the uncompressed mode matches the Pico SDK generator when PICO_SDK_PATH is set."""
import gzip, os, re, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "cmake" / "web_fsdata.py"
PAGE = HERE.parent / "services" / "phone_web" / "index.html"


def generate(out, *extra):
    subprocess.run([sys.executable, str(TOOL), "-i", str(PAGE), "-o", str(out), *extra], check=True)
    return Path(out).read_text()


def payload(text):
    """Return (header bytes, body bytes) of the single generated file."""
    array = re.search(r"data_index_html\[\] = \{(.*?)\};", text, re.S).group(1)
    blocks = re.split(r"/\* .*? \*/", array)[1:]
    parts = [bytes(int(x, 16) for x in re.findall(r"0x([0-9a-f]{2})", b)) for b in blocks]
    return b"".join(parts[1:5]), parts[5], parts[0]


with tempfile.TemporaryDirectory() as tmp:
    source = PAGE.read_bytes()
    headers, body, name = payload(generate(Path(tmp) / "gz.inc", "--gzip"))
    assert name.rstrip(b"\0") == b"/index.html"
    assert gzip.decompress(body) == source
    assert len(body) < len(source) // 2
    assert b"Content-Encoding: gzip\r\n" in headers and b"Content-Type: text/html\r\n" in headers
    assert f"Content-Length: {len(body)}\r\n".encode() in headers
    assert headers.startswith(b"HTTP/1.0 200 OK\r\n") and headers.endswith(b"\r\n\r\n")
    assert generate(Path(tmp) / "gz2.inc", "--gzip") == (Path(tmp) / "gz.inc").read_text(), "not deterministic"

    plain = generate(Path(tmp) / "plain.inc")
    headers, body, _ = payload(plain)
    assert body == source and b"Content-Encoding" not in headers

    sdk = os.environ.get("PICO_SDK_PATH")
    if sdk:
        reference = Path(tmp) / "sdk.inc"
        subprocess.run([sys.executable, f"{sdk}/src/rp2_common/pico_lwip/tools/makefsdata.py",
                        "-i", str(PAGE), "-o", str(reference)], check=True, capture_output=True)
        assert reference.read_text() == plain, "uncompressed output differs from makefsdata.py"
        print("matches Pico SDK makefsdata.py")
print("web_fsdata OK")
