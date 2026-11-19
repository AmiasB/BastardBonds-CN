$ErrorActionPreference = "Stop"
$work = Split-Path $PSScriptRoot -Parent
$out = Join-Path $PSScriptRoot "BastardBonds_CN"
$cn = Join-Path $out "cn_patch"
New-Item -ItemType Directory -Force -Path $cn | Out-Null

dotnet publish (Join-Path $work "patch\patcher\patcher.csproj") -c Release -o $cn
if ($LASTEXITCODE) { throw "publish failed" }
Remove-Item (Join-Path $cn "patcher.pdb") -Force -ErrorAction SilentlyContinue

Copy-Item (Join-Path $work "patch\BB_CN.dll") (Join-Path $cn "BB_CN.dll") -Force
Copy-Item (Join-Path $work "patch\literals.tsv") (Join-Path $cn "literals.tsv") -Force
$dict = Join-Path $cn "dict"
New-Item -ItemType Directory -Force -Path $dict | Out-Null
Remove-Item (Join-Path $dict "*.tsv") -Force -ErrorAction SilentlyContinue
Copy-Item (Join-Path $work "build\BB_CN\*.tsv") $dict -Force

$xd = Join-Path $PSScriptRoot "_tools\xdelta3-3.2.2-windows-x86_64\xdelta3.exe"
if (-not (Test-Path $xd)) { throw "missing $xd" }
Copy-Item $xd (Join-Path $cn "xdelta3.exe") -Force
& $xd -f -e -9 -s (Join-Path $work "backup\sharedassets0.assets") (Join-Path $work "build\sharedassets0.assets") (Join-Path $cn "font.vcdiff")
if ($LASTEXITCODE) { throw "xdelta encode failed" }
& $xd -f -e -9 -s (Join-Path $work "backup\sharedassets4.assets") (Join-Path $work "build\sharedassets4.assets") (Join-Path $cn "help4.vcdiff")
if ($LASTEXITCODE) { throw "help4 xdelta encode failed" }
& $xd -f -e -9 -s (Join-Path $work "backup\sharedassets5.assets") (Join-Path $work "build\sharedassets5.assets") (Join-Path $cn "help5.vcdiff")
if ($LASTEXITCODE) { throw "help5 xdelta encode failed" }

function Copy-Utf8Bom($src, $dst) {
	$text = [System.IO.File]::ReadAllText($src)
	$enc = New-Object System.Text.UTF8Encoding $true
	[System.IO.File]::WriteAllText($dst, $text, $enc)
}
Copy-Utf8Bom (Join-Path $PSScriptRoot "apply.ps1") (Join-Path $cn "apply.ps1")
Copy-Utf8Bom (Join-Path $PSScriptRoot "restore.ps1") (Join-Path $cn "restore.ps1")
Copy-Item (Join-Path $PSScriptRoot "打补丁.bat") $out -Force
Copy-Item (Join-Path $PSScriptRoot "还原.bat") $out -Force
Copy-Utf8Bom (Join-Path $PSScriptRoot "使用说明.txt") (Join-Path $out "使用说明.txt")
Copy-Utf8Bom (Join-Path $PSScriptRoot "README中文版.txt") (Join-Path $cn "README中文版.txt")

$zip = Join-Path $PSScriptRoot "BastardBonds_CN.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
tar -a -cf $zip -C $PSScriptRoot "BastardBonds_CN"
if ($LASTEXITCODE) { throw "zip failed" }
Get-Item $zip | Select-Object FullName, Length
