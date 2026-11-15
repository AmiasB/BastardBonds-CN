$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$work = Split-Path $here
$managed = "E:\T File\Bastard Bonds\BB_Data\Managed"
$csc = "C:\Program Files\dotnet\sdk\10.0.202\Roslyn\bincore\csc.dll"

Set-Location $here
dotnet $csc -nologo -noconfig -nostdlib -target:library -langversion:7.3 -optimize "-out:BB_CN.dll" `
    "-r:$managed\mscorlib.dll" "-r:$managed\System.dll" "-r:$managed\System.Core.dll" "-r:$managed\UnityEngine.dll" `
    "-r:$work\backup\Assembly-CSharp.dll" BB_CN.cs
if ($LASTEXITCODE) { throw "csc failed" }
dotnet run --project patcher -- "$work\backup\Assembly-CSharp.dll" "$here\BB_CN.dll" "$here\literals.tsv" "$here\Assembly-CSharp.dll" $managed
if ($LASTEXITCODE) { throw "patcher failed" }
