# Build only. This script never opens COM ports, loads firmware or changes OTP.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$OutputDirectory,[Parameter(Mandatory=$true)][string]$HelixPath)
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
if ((git -C $taskRoot status --porcelain)) { throw 'Commit changes before preparing a reviewed migration package.' }
$base=[IO.Path]::GetFullPath($OutputDirectory)
foreach($item in @(@{Name='initial';Sequence=1;Trial=$false;Reject=$false},@{Name='accepted';Sequence=2;Trial=$true;Reject=$false},@{Name='rejected';Sequence=3;Trial=$true;Reject=$true})) {
    & (Join-Path $taskRoot 'build-clock-bt.ps1') -Mp3 -PhoneWeb -OtaAb -OtaSequence $item.Sequence -OtaTrial:$item.Trial -OtaRejectTrial:$item.Reject -HelixPath $HelixPath -BuildDirectory (Join-Path $base $item.Name)
    if(-not $?) { throw "Build failed: $($item.Name)" }
}
$toolRoot=Join-Path $env:USERPROFILE '.pico-sdk\picotool'
$picotool=(Get-ChildItem -LiteralPath $toolRoot -Filter picotool.exe -File -Recurse | Select-Object -First 1).FullName
if(-not $picotool){throw 'picotool not found'}
& python (Join-Path $taskRoot 'tools\ota_foundation_package.py') --initial (Join-Path $base 'initial') --accepted (Join-Path $base 'accepted') --rejected (Join-Path $base 'rejected') --output (Join-Path $base 'package') --picotool $picotool
if($LASTEXITCODE -ne 0){throw 'Package verification failed'}
