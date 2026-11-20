import hashlib
import importlib.util
import struct
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path

spec = importlib.util.spec_from_file_location("web_package", Path(__file__).resolve().parents[3] / "tools/ota_web_package.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class WebPackageTests(unittest.TestCase):
    def test_header_and_digest(self):
        data = b"x" * 4097
        h = m.make_header(data, 5, "g1-test-ota5-trial")
        self.assertEqual(len(h), 128)
        self.assertEqual(struct.unpack_from("<8s4I", h), (b"CLOCKOT1", 0x23500002, len(data), 5, 1))
        self.assertEqual(h[24:56], hashlib.sha256(data).digest())
        self.assertEqual(h[56:75], b"g1-test-ota5-trial\0")
        self.assertEqual(h[120:], bytes(8))

    def test_generation_identity_and_legacy_wire_compatibility(self):
        for build in ["g2-test-ota11-trial", "test-ota11-trial"]:
            with self.assertRaises(ValueError):
                m.make_header(b"x" * 4096, 11, build)
        h = m.make_header(b"x" * 4096, 11, "g1-test-ota11-trial")
        # The existing ota10 receiver requires this target/flags/reserved layout.
        self.assertEqual(struct.unpack_from("<I", h, 8)[0], 0x23500002)
        self.assertEqual(struct.unpack_from("<I", h, 20)[0], 1)
        self.assertEqual(h[120:], bytes(8))

    def test_invalid_inputs(self):
        for size, seq, build in [(4095, 1, "g1-test"), (0x180001, 1, "g1-test"), (4096, 0, "g1-test"),
                                 (4096, 65536, "g1-test"), (4096, 1, "g1-" + "x" * 64), (4096, 1, ""),
                                 (4096, 1, "g1-bad\nidentity")]:
            with self.assertRaises(ValueError):
                m.make_header(b"x" * size, seq, build)

    def test_package_identity_and_default_name(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "firmware_version.h").write_text(
                '#define CLOCK_BUILD_ID "g1-test-ota11-trial"\n'
                '#define CLOCK_FIRMWARE_VERSION "1.0.0+61.gabcdef0"\n')
            (directory / "device_identity.h").write_text(m.IDENTITY_PATH.read_text())
            (directory / "speaking_clock_c.bin").write_bytes(b"x" * 4096)
            with patch.object(m.subprocess, "check_output", return_value="hash: verified ARM Secure tbyb: not bought version: 1.11\n"):
                review = m.package(directory, "unused-picotool")
                self.assertEqual(review["model"], "Pi2Clock G1")
                self.assertEqual(review["generation"], "G1")
                self.assertEqual(review["file"], "Pi2Clock-G1-v1.0.0+61.gabcdef0-ota11.clockota")
                self.assertTrue((directory / review["file"]).exists())
                with self.assertRaises(ValueError):
                    m.package(directory, "unused-picotool") # No replacement of a reviewed package.
                identity = m.IDENTITY_PATH.read_text().replace('"G1"', '"G2"')
                (directory / "device_identity.h").write_text(identity)
                with self.assertRaises(ValueError):
                    m.package(directory, "unused-picotool", directory / "wrong.clockota")


if __name__ == "__main__":
    unittest.main()
