$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$bundle = Split-Path $here -Parent

function Find-Game([string]$start) {
	foreach ($dir in @($start, (Split-Path $start -Parent))) {
		if ($dir -and (Test-Path (Join-Path $dir "BB.exe"))) {
			return $dir
		}
	}
	return $null
}

$game = Find-Game $bundle
if (-not $game) {
	throw "找不到游戏。请在放进游戏根目录的 BastardBonds_CN 文件夹里运行还原.bat。"
}
if (Get-Process -Name "BB" -ErrorAction SilentlyContinue) {
	throw "请先退出 Bastard Bonds，再还原。"
}

$backup = Join-Path $game "BB_Data\BB_CN_backup"
$backupDll = Join-Path $backup "Assembly-CSharp.dll"
$backupAssets = Join-Path $backup "sharedassets0.assets"
if (-not (Test-Path $backupDll) -or -not (Test-Path $backupAssets)) {
	throw "没有找到原版备份（BB_Data\BB_CN_backup），无法还原。"
}

Copy-Item $backupDll (Join-Path $game "BB_Data\Managed\Assembly-CSharp.dll") -Force
Copy-Item $backupAssets (Join-Path $game "BB_Data\sharedassets0.assets") -Force
foreach ($name in @("sharedassets4.assets", "sharedassets5.assets")) {
	$kept = Join-Path $backup $name
	if (Test-Path $kept) {
		Copy-Item $kept (Join-Path $game "BB_Data\$name") -Force
	}
}
$helper = Join-Path $game "BB_Data\Managed\BB_CN.dll"
if (Test-Path $helper) { Remove-Item $helper -Force }
Write-Output "已还原原版程序和字体。词典目录 BB_Data\BB_CN 还留着，不进游戏也不会被读取。"
