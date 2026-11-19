const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const html=fs.readFileSync(path.join(__dirname,'../services/phone_web/index.html'),'utf8');
const script=html.slice(html.indexOf('  let otaView=null'),html.indexOf('  let authorizedLayout=false;'));
const elements=new Map();
const element=id=>{if(!elements.has(id))elements.set(id,{handlers:{},addEventListener(k,f){this.handlers[k]=f;},disabled:false,textContent:'',files:[]});return elements.get(id);};
const state={supported:true,state:'idle',available:true,current_sequence:4,active:'B',received:0,size:0,session:0,mode_restore:true,restart_mode:'direct'};
const calls=[];
let holdBegin=false,releaseBegin;
const context=vm.createContext({document:{getElementById:element},live:{epoch:123,home_trusted:true,firmware:{version:'test'}},
  token:null,checkedEpoch:null,busy:false,pending:null,dirtySettings:new Set(),settingChanges:new Map(),
  updateControls(){},pollStatusSoon(){},confirm:()=>true,crypto:{getRandomValues(a){a[0]=77;return a;}},
  Uint8Array,Uint32Array,DataView,AbortSignal,console,setTimeout,clearTimeout,
  async fetch(url,options={}){
    if(url==='/ota.json')return {ok:true,json:async()=>({...state})};
    assert.equal(url,'/ota');const fields=options.body.split(' ');assert.equal(fields[0],'-');assert.equal(fields[1],'123');
    const action=fields[2];calls.push(action);state.session=Number(fields[3]);
    if(action==='begin' && holdBegin)await new Promise(resolve=>{releaseBegin=resolve;});
    if(action==='begin'){state.state='receiving';state.size=4097;state.received=0;state.available=false;}
    if(action==='chunk'){assert.equal(Number(fields[4]),state.received);state.received+=fields[5].length/2;}
    if(action==='finish'){assert.match(element('firmware-status').textContent,/Verifying/);assert.equal(state.received,state.size);state.state='ready';}
    if(action==='cancel'){state.state='idle';state.available=true;}
    if(action==='apply')state.state='rebooting';
    return {ok:true};
  }});
vm.runInContext(script,context);
vm.runInContext('otaView={supported:true,mode_restore:true,restart_mode:"direct"};renderFirmware(true)',context);
assert.match(element('firmware-network-hint').textContent,/192\.168\.4\.1/);
vm.runInContext('otaView.restart_mode="home";renderFirmware(true)',context);
assert.match(element('firmware-network-hint').textContent,/After this update, use home Wi-Fi/);
vm.runInContext('otaView.mode_restore=false;renderFirmware(true)',context);
assert.match(element('firmware-network-hint').textContent,/including after an update from Direct/);
const header=new Uint8Array(128),view=new DataView(header.buffer);
header.set(Buffer.from('CLOCKOT1'));view.setUint32(8,0x23500002,true);view.setUint32(12,4097,true);view.setUint32(16,5,true);view.setUint32(20,1,true);header.set(Buffer.from('test-ota5-trial'),56);
context.header=header;
assert.equal(vm.runInContext('inspectOtaHeader(header,4225,4).sequence',context),5);
assert.throws(()=>vm.runInContext('inspectOtaHeader(header,4224,4)',context));
assert.throws(()=>vm.runInContext('inspectOtaHeader(header,4225,5)',context));
header[8]^=1;assert.throws(()=>vm.runInContext('inspectOtaHeader(header,4225,4)',context));header[8]^=1;
header[120]=1;assert.throws(()=>vm.runInContext('inspectOtaHeader(header,4225,4)',context));header[120]=0;
async function run(){
  const file=Buffer.concat([header,Buffer.alloc(4097,31)]);
  element('firmware-file').files=[{size:file.length,slice(a,b){const x=file.subarray(a,b);return {arrayBuffer:async()=>x.buffer.slice(x.byteOffset,x.byteOffset+x.length)};}}];
  vm.runInContext('otaView={supported:true,available:true,current_sequence:4,state:"idle"}',context);
  await element('firmware-file').handlers.change();
  vm.runInContext('renderFirmware(true)',context);
  holdBegin=true;
  const transfer=element('firmware-upload').handlers.click();
  assert.match(element('firmware-status').textContent,/Preparing upload/);
  assert.equal(element('firmware-progress').value,0);
  vm.runInContext('renderFirmware(true)',context);
  assert.equal(element('firmware-upload').disabled,true);
  await element('firmware-upload').handlers.click();
  assert.equal(calls.filter(x=>x==='begin').length,1);
  releaseBegin();await transfer;holdBegin=false;
  assert.equal(calls.filter(x=>x==='chunk').length,9);assert.equal(state.state,'ready');
  assert.equal(vm.runInContext('otaLocked()',context),true);
  vm.runInContext('renderFirmware(true)',context);
  assert.match(element('firmware-status').textContent,/No second upload/);
  assert.equal(element('firmware-upload').hidden,true);
  assert.equal(element('firmware-upload').disabled,true);
  vm.runInContext('otaView.available=true;renderFirmware(true)',context);
  await element('firmware-upload').handlers.click();
  assert.equal(calls.filter(x=>x==='begin').length,1); // A stale available flag cannot restart a verified file.
  await element('firmware-install').handlers.click();assert.equal(state.state,'rebooting');
  assert.equal(vm.runInContext('otaRestart.build',context),'test-ota5-trial');
  assert.equal(vm.runInContext('otaRestart.mode',context),'direct');
  assert.match(element('firmware-status').textContent,/SpeakingClock/);
  vm.runInContext('live.epoch=124;live.firmware.build="test-ota5-trial";otaView.state="idle";otaView.current_sequence=5;renderFirmware(true)',context);
  assert.match(element('firmware-status').textContent,/Update installed/);
  assert.equal(element('firmware-upload').disabled,true); // Already-installed selected file is not offered again.
  console.log('OTA browser header checks, bounded upload, progress, verify and explicit install passed');
}
run().catch(error=>{console.error(error);process.exitCode=1;});
