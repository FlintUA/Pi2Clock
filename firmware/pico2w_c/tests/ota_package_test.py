import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location("ota_package",ROOT/"tools/ota_foundation_package.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def block(address,index=0,total=1,family=m.ABSOLUTE):
    out=bytearray(512);struct.pack_into("<8I",out,0,0x0a324655,0x9e5d5157,0x2000,address,256,index,total,family);struct.pack_into("<I",out,508,0x0ab16f30);return out
class PackageTests(unittest.TestCase):
 def test_bounds_and_header(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"image.uf2";p.write_bytes(block(0x10001000));self.assertEqual(len(m.inspect_uf2(p,0x1000,1)),64)
   for data in [block(0x10000000),block(0x103fa000),block(0x10181000),block(0x10001000,index=1),block(0x10001000,family=0xe48bff59),b"bad"]:
    p.write_bytes(data)
    with self.assertRaises(ValueError):m.inspect_uf2(p,0x1000,1)
   p.write_bytes(block(0x10001000))
   with self.assertRaises(ValueError):m.inspect_uf2(p,0x1000,1,b"wrong")
   with self.assertRaises(ValueError):m.inspect_uf2(p,0,1)
   p.write_bytes(block(0x10181000));m.inspect_uf2(p,0x181000,256)
 def test_identity_roles(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"speaking_clock_c.bin").write_bytes(b"sample")
   h=root/"firmware_version.h"
   h.write_text('#define CLOCK_BUILD_ID "abcdef012345-bt-mp3-wifi-phone-ota2-trial"\n#define CLOCK_FIRMWARE_VERSION "1.0.0+47.gabcdef0"\n')
   self.assertTrue(m.identity(root,"accepted")[2]["trial"])
   with self.assertRaises(ValueError):m.identity(root,"initial")
   h.write_text(h.read_text().replace('abcdef012345-','abcdef012345-dirty-'))
   with self.assertRaises(ValueError):m.identity(root,"accepted")
if __name__=="__main__":unittest.main()
