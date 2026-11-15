$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$bundle = Split-Path $here -Parent

function Find-Game([string]$start) {
	foreach ($dir in @($start, (Split-Path $start -Parent))) {
		if ($dir -and (Test-Path (Join-Path $dir "BB.exe")) -and (Test-Path (Join-Path $dir "BB_Data\Managed\Assembly-CSharp.dll"))) {
			return $dir
		}
	}
	return $null
}

$game = Find-Game $bundle
if (-not $game) {
	throw "找不到游戏。请把 BastardBonds_CN 文件夹放进游戏根目录，和 BB.exe 放在同一层，再运行打补丁.bat。"
}
if (Get-Process -Name "BB" -ErrorAction SilentlyContinue) {
	throw "请先退出 Bastard Bonds，再运行打补丁。"
}

$managed = Join-Path $game "BB_Data\Managed"
$backup = Join-Path $game "BB_Data\BB_CN_backup"
$dll = Join-Path $managed "Assembly-CSharp.dll"
$assets = Join-Path $game "BB_Data\sharedassets0.assets"
New-Item -ItemType Directory -Force -Path $backup | Out-Null

$backupDll = Join-Path $backup "Assembly-CSharp.dll"
$backupAssets = Join-Path $backup "sharedassets0.assets"
if ((Test-Path (Join-Path $managed "BB_CN.dll")) -and -not (Test-Path $backupDll)) {
	throw "游戏里已经有汉化文件，但没有原版备份（BB_Data\BB_CN_backup）。这次没有改动任何东西。"
}
if (-not (Test-Path $backupDll)) {
	Copy-Item $dll $backupDll
}
if (-not (Test-Path $backupAssets)) {
	Copy-Item $assets $backupAssets
}

$dllTmp = Join-Path $backup "Assembly-CSharp.patched.dll"
$assetTmp = Join-Path $backup "sharedassets0.patched.assets"
if (Test-Path $dllTmp) { Remove-Item $dllTmp -Force }
if (Test-Path $assetTmp) { Remove-Item $assetTmp -Force }

& (Join-Path $here "patcher.exe") $backupDll (Join-Path $here "BB_CN.dll") (Join-Path $here "literals.tsv") $dllTmp $managed
if ($LASTEXITCODE -ne 0) { throw "程序补丁失败。" }

& (Join-Path $here "xdelta3.exe") -f -d -s $backupAssets (Join-Path $here "font.vcdiff") $assetTmp
if ($LASTEXITCODE -ne 0) {
	Remove-Item $dllTmp, $assetTmp -Force -ErrorAction SilentlyContinue
	throw "字体补丁失败。这个补丁只对应 Steam 1.2.9 的原版 sharedassets0.assets。"
}

Copy-Item $dllTmp $dll -Force
Copy-Item $assetTmp $assets -Force
Copy-Item (Join-Path $here "BB_CN.dll") (Join-Path $managed "BB_CN.dll") -Force
$dict = Join-Path $game "BB_Data\BB_CN"
New-Item -ItemType Directory -Force -Path $dict | Out-Null
Copy-Item (Join-Path $here "dict\*.tsv") $dict -Force
Remove-Item $dllTmp, $assetTmp -Force
Write-Output "补丁已装好。原版文件在 BB_Data\BB_CN_backup。启动游戏即可。"
