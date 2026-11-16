import hashlib
import importlib.util
import struct
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("web_package", Path(__file__).resolve().parents[3] / "tools/ota_web_package.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WebPackageTests(unittest.TestCase):
    def test_header_and_digest(self):
        data = b"x" * 4097
        h = m.make_header(data, 5, "test-ota5-trial")
        self.assertEqual(len(h), 128)
        self.assertEqual(struct.unpack_from("<8s4I", h), (b"CLOCKOT1", 0x23500002, len(data), 5, 1))
        self.assertEqual(h[24:56], hashlib.sha256(data).digest())
        self.assertEqual(h[56:72], b"test-ota5-trial\0")
        self.assertEqual(h[120:], bytes(8))

    def test_invalid_inputs(self):
        for size, seq, build in [(4095, 1, "test"), (0x180001, 1, "test"), (4096, 0, "test"),
                                 (4096, 65536, "test"), (4096, 1, "x" * 64), (4096, 1, ""),
                                 (4096, 1, "bad\nidentity")]:
            with self.assertRaises(ValueError):
                m.make_header(b"x" * size, seq, build)


if __name__ == "__main__":
    unittest.main()
