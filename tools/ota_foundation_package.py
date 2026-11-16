"""Build/verify offline A/B bring-up artifacts. Never opens a device or serial port."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
SLOT=0x180000
STARTS={"a":0x1000,"b":0x181000}
PROTECTED=0x3fa000
MAGIC=(0x0a324655,0x9e5d5157,0x0ab16f30)
ABSOLUTE=0xe48bff57

def inspect_uf2(path,start,size,expected=None):
    if start not in STARTS.values():raise ValueError("Unknown application slot")
    data=Path(path).read_bytes()
    if not data or len(data)%512:raise ValueError("Invalid UF2 length")
    count=len(data)//512
    if count!=(size+255)//256:raise ValueError("Unexpected block count")
    for i in range(count):
        block=data[i*512:(i+1)*512]
        a,b,flags,address,length,index,total,family=struct.unpack("<8I",block[:32])
        end=struct.unpack("<I",block[-4:])[0]
        if (a,b,end)!=MAGIC or (flags,length,index,total,family)!=(0x2000,256,i,count,ABSOLUTE):raise ValueError("Unexpected UF2 header/family/order")
        if address!=0x10000000+start+i*256 or address+256>0x10000000+start+SLOT or address+256>0x10000000+PROTECTED:raise ValueError("UF2 write outside selected app slot")
    if expected is not None:
        payload=b"".join(data[i*512+32:i*512+288] for i in range(count))[:size]
        if payload!=expected:raise ValueError("UF2 payload differs from reviewed binary")
    return hashlib.sha256(data).hexdigest().upper()

def identity(directory,role):
    directory=Path(directory);header=(directory/"firmware_version.h").read_text()
    build=re.search(r'CLOCK_BUILD_ID "([^"\n]+)"',header)[1]
    version=re.search(r'CLOCK_FIRMWARE_VERSION "([^"\n]+)"',header)[1]
    seq=re.search(r'-ota([0-9]+)',build)
    if not seq or "dirty" in build or "dirty" in version:raise ValueError("Only clean OTA builds may be packaged")
    trial="-trial" in build;reject="-reject" in build
    if trial!=(role!="initial") or reject!=(role=="rejected"):raise ValueError("Wrong build role")
    data=(directory/"speaking_clock_c.bin").read_bytes()
    if not data or len(data)>SLOT:raise ValueError("Application exceeds slot")
    return directory,data,{"build":build,"version":version,"sequence":int(seq[1]),"trial":trial,"reject_test":reject,"bytes":len(data),"binary_sha256":hashlib.sha256(data).hexdigest().upper()}

def run(tool,*args):
    return subprocess.check_output([str(tool),*map(str,args)],text=True,encoding="utf-8",errors="replace")

def main():
    parser=argparse.ArgumentParser();parser.add_argument("--initial",required=True);parser.add_argument("--accepted",required=True);parser.add_argument("--rejected",required=True);parser.add_argument("--picotool",required=True);parser.add_argument("--output",required=True)
    args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]
    partition=out/"partitions.uf2"
    run(args.picotool,"partition","create",root/"firmware/pico2w_c/ota/partitions.json",partition)
    metadata=run(args.picotool,"info","-m",partition);(out/"partitions-info.txt").write_text(metadata,encoding="utf-8")
    if not re.search(r"hash:\s+verified",metadata):raise ValueError("Partition hash not verified")
    manifest={"kind":"clock-ota-foundation","browser_upload":False,"hardware_accepted":False,"images":{},"partitions_sha256":hashlib.sha256(partition.read_bytes()).hexdigest().upper()}
    commits=set();sequences=[]
    for role in ("initial","accepted","rejected"):
        directory,data,details=identity(getattr(args,role),role);commits.add(details["build"].split("-")[0]);sequences.append(details["sequence"])
        image_meta=run(args.picotool,"info","-m",directory/"speaking_clock_c.uf2")
        (out/(role+"-info.txt")).write_text(image_meta,encoding="utf-8")
        if not re.search(r"hash:\s+verified",image_meta):raise ValueError("Image hash missing/invalid")
        if bool(re.search(r"tbyb:\s+not bought",image_meta))!=details["trial"]:raise ValueError("ROM trial flag differs from build identity")
        if not re.search(r"version:\s+1\."+str(details["sequence"])+r"(?:\s|$)",image_meta):raise ValueError("ROM version differs from requested sequence")
        if "ARM Secure" not in image_meta:raise ValueError("Wrong image type")
        for slot in (("a",) if role=="initial" else ("a","b")):
            target=out/(role+"-"+slot+".uf2")
            run(args.picotool,"uf2","convert",directory/"speaking_clock_c.bin",target,"--offset",hex(0x10000000+STARTS[slot]),"--family","absolute","--platform","rp2350")
            sha=inspect_uf2(target,STARTS[slot],len(data),data)
            manifest["images"][target.name]={**details,"slot":slot.upper(),"start":STARTS[slot],"end_limit":STARTS[slot]+SLOT,"uf2_sha256":sha}
    if len(commits)!=1 or not sequences[0]<sequences[1]<sequences[2]:raise ValueError("Mismatched commits or unordered versions")
    commit=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    if not commit.startswith(next(iter(commits))) or subprocess.check_output(["git","-C",str(root),"status","--porcelain"],text=True).strip():raise ValueError("Source changed during package creation")
    manifest["commit"]=commit
    manifest["commit_prefix"]=next(iter(commits))
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print("Reviewed A/B bring-up package: "+str(out));print("No hardware operation was performed")
if __name__=="__main__":main()
