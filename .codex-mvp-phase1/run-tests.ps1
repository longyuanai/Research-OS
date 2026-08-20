<#
  Research-OS MVP —— 测试与覆盖率运行脚本

  用法：
      .\run-tests.ps1              # 只跑测试
      .\run-tests.ps1 -Coverage    # 跑测试 + 行覆盖率（stdlib trace，无需安装）
      .\run-tests.ps1 -Verbose2    # 逐条显示测试名

  背景：系统 PATH 上的 python.exe 是 Windows Store 占位 stub（退出码 49），
  无法运行。本脚本按优先级自动定位可用解释器，无需手工填路径。
#>
[CmdletBinding()]
param(
    [switch]$Coverage,
    [switch]$Verbose2
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

# ---- 1. 定位可用解释器 -------------------------------------------------------
$candidates = @(
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
    "$env:APPDATA\uv\python\cpython-3.12.13-windows-x86_64-none\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
)

$MvpPython = $null
foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) { $MvpPython = $c; break }
}

# py launcher 兜底（排除 WindowsApps stub）
if (-not $MvpPython) {
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        $line = (& py -0p 2>&1 | Where-Object { $_ -match 'python\.exe' } | Select-Object -First 1)
        if ($line -match '([A-Za-z]:\\[^\s].*python\.exe)') {
            $found = $Matches[1]
            if ($found -notmatch 'WindowsApps') { $MvpPython = $found }
        }
    }
}

if (-not $MvpPython) {
    Write-Error "未找到可用的 Python 解释器。PATH 上的 python.exe 是 Store stub，不可用。`n请安装 Python 3.12+ 或把真实解释器路径加入本脚本的 `$candidates。"
    exit 1
}

$ver = (& $MvpPython -V 2>&1)
Write-Host "解释器 : $MvpPython" -ForegroundColor Cyan
Write-Host "版本   : $ver" -ForegroundColor Cyan
Write-Host ""

# ---- 2. 运行 ----------------------------------------------------------------
# unittest 把进度和摘要写到 stderr。Windows PowerShell 5.1 会把原生命令的 stderr
# 包装成 ErrorRecord 并置 $? = $false，即使退出码为 0。此处放宽以 $LASTEXITCODE 为准。
$ErrorActionPreference = 'Continue'
$sw = [Diagnostics.Stopwatch]::StartNew()

if ($Coverage) {
    $covScript = Join-Path $PSScriptRoot 'tools\measure_coverage.py'
    if (-not (Test-Path -LiteralPath $covScript)) {
        Write-Error "缺少 $covScript"
        exit 1
    }
    $env:MVP_DIR = $PSScriptRoot
    & $MvpPython $covScript
    $code = $LASTEXITCODE
}
else {
    $verbosity = if ($Verbose2) { '-v' } else { '' }
    if ($verbosity) {
        & $MvpPython -m unittest discover -s tests $verbosity
    } else {
        & $MvpPython -m unittest discover -s tests
    }
    $code = $LASTEXITCODE
}

$sw.Stop()
Write-Host ""
Write-Host ("耗时 : {0:N1}s" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Cyan
if ($code -eq 0) {
    Write-Host "结果 : PASS" -ForegroundColor Green
} else {
    Write-Host "结果 : FAIL (exit $code)" -ForegroundColor Red
}
exit $code
