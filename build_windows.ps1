param(
  # A full path to a Python 3.13 or 3.14 executable can be supplied when needed.
  # Without it, the script finds the standard per-user installation first.
  [string[]]$PythonCommand = @(),
  [string]$InnoSetupCompiler = "",
  [switch]$SkipDependencyInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$AssetsDir = Join-Path $ProjectRoot "assets"
$ReleaseDir = Join-Path $ProjectRoot "Release"
$StagingRoot = Join-Path $ProjectRoot ".build-artifacts"
$PyInstallerDist = Join-Path $StagingRoot "pyinstaller-dist"
$PyInstallerWork = Join-Path $StagingRoot "pyinstaller-work"
$AppIcon = Join-Path $AssetsDir "CodexModelGate.ico"
$SetupIcon = Join-Path $AssetsDir "CodexModelGate-Setup.ico"
$PortableExe = Join-Path $ReleaseDir "CodexModelGate-Pendrive.exe"
$SetupExe = Join-Path $ReleaseDir "CodexModelGate-Setup.exe"
$PortableReadme = Join-Path $ReleaseDir "LEIA-ME-PORTATIL.md"

function Invoke-Python {
  param([Parameter(Mandatory = $true)][string[]]$Arguments)

  $result = & $PythonCommand[0] @PythonPrefix @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "O comando Python falhou: $($Arguments -join ' ')"
  }
  return $result
}

function Resolve-PythonCommand {
  param([string[]]$RequestedCommand)

  if ($RequestedCommand.Count -gt 0) {
    return $RequestedCommand
  }

  if ($env:LOCALAPPDATA) {
    $perUserPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
    if (Test-Path -LiteralPath $perUserPython) {
      return @($perUserPython)
    }
  }

  $launcher = Get-Command "py.exe" -ErrorAction SilentlyContinue
  if (-not $launcher) {
    $launcher = Get-Command "py" -ErrorAction SilentlyContinue
  }
  if ($launcher) {
    return @($launcher.Source, "-3.13")
  }

  $python = Get-Command "python.exe" -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command "python" -ErrorAction SilentlyContinue
  }
  if ($python) {
    return @($python.Source)
  }

  throw "Python 3.13 x64 não foi encontrado. Instale-o ou informe -PythonCommand com o caminho do python.exe."
}

$PythonCommand = @(Resolve-PythonCommand -RequestedCommand $PythonCommand)
if ($PythonCommand.Count -eq 0) {
  throw "Informe o comando do Python 3.13 em -PythonCommand."
}

$PythonPrefix = @()
if ($PythonCommand.Count -gt 1) {
  $PythonPrefix = $PythonCommand[1..($PythonCommand.Count - 1)]
}

function Resolve-InnoSetupCompiler {
  param([string]$RequestedCompiler)

  if ($RequestedCompiler) {
    if (-not (Test-Path -LiteralPath $RequestedCompiler)) {
      throw "O compilador informado do Inno Setup não foi encontrado: $RequestedCompiler"
    }
    return (Resolve-Path -LiteralPath $RequestedCompiler).Path
  }

  $candidates = @()
  $candidates += Join-Path $ProjectRoot ".build-tools\Inno Setup 6\ISCC.exe"
  $programFilesX86 = ${env:ProgramFiles(x86)}
  if ($programFilesX86) {
    $candidates += Join-Path $programFilesX86 "Inno Setup 6\ISCC.exe"
  }
  if ($env:ProgramFiles) {
    $candidates += Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe"
  }
  if ($env:LOCALAPPDATA) {
    $candidates += Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
  }
  foreach ($candidate in $candidates) {
    if (Test-Path -LiteralPath $candidate) {
      return (Resolve-Path -LiteralPath $candidate).Path
    }
  }

  $fromPath = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
  if (-not $fromPath) {
    $fromPath = Get-Command "iscc" -ErrorAction SilentlyContinue
  }
  if ($fromPath) {
    return $fromPath.Source
  }

  throw "Inno Setup 6 não foi encontrado. Instale-o ou informe -InnoSetupCompiler com o caminho de ISCC.exe."
}

$pythonVersion = (Invoke-Python -Arguments @("-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))")).Trim()
if ($pythonVersion -notmatch '^3\.(13|14)\.\d+$') {
  throw "Este empacotamento exige Python 3.13 ou 3.14; foi encontrado $pythonVersion."
}
$pythonBits = (Invoke-Python -Arguments @("-c", "import struct; print(struct.calcsize('P') * 8)")).Trim()
if ($pythonBits -ne "64") {
  throw "Use Python 3.13 ou 3.14 de 64 bits para gerar os executáveis x64; a instalação atual é $pythonBits bits."
}

# The finished EXEs contain Python, Tcl/Tk and document-validation libraries.
# Python is required only on the developer build machine, never on the recipient's computer.
Invoke-Python -Arguments @("-c", "import tkinter as tk; tk.Tcl(); print('Tcl/Tk validado')") | Write-Host
if (-not $SkipDependencyInstall) {
  Invoke-Python -Arguments @("-m", "pip", "install", "--upgrade", "pyinstaller", "-r", (Join-Path $ProjectRoot "requirements.txt")) | Write-Host
}

# Generate both ICO resources locally from the versioned design assets.  No external
# image download or image-editing application is part of the release process.
Invoke-Python -Arguments @((Join-Path $ProjectRoot "tools\generate_icon_assets.py"), "--output-dir", $AssetsDir) | Write-Host
foreach ($icon in @($AppIcon, $SetupIcon)) {
  if (-not (Test-Path -LiteralPath $icon)) {
    throw "O gerador de ícones não criou o recurso esperado: $icon"
  }
}

New-Item -ItemType Directory -Force -Path $ReleaseDir, $StagingRoot, $PyInstallerDist, $PyInstallerWork | Out-Null

# Only the two known release products and the portable readme are replaced.  Files a
# developer may keep in Release are not removed by this script.
foreach ($artifact in @($PortableExe, $SetupExe, $PortableReadme)) {
  if (Test-Path -LiteralPath $artifact) {
    Remove-Item -LiteralPath $artifact -Force
  }
}

Invoke-Python -Arguments @(
  "-m", "PyInstaller",
  "--noconfirm", "--clean", "--log-level", "WARN", "--onefile", "--windowed",
  "--name", "CodexModelGate",
  "--icon", $AppIcon,
  "--collect-all", "pypdf",
  "--collect-all", "pdfplumber",
  "--collect-all", "reportlab",
  "--collect-all", "playwright",
  "--distpath", $PyInstallerDist,
  "--workpath", $PyInstallerWork,
  "--specpath", $StagingRoot,
  (Join-Path $ProjectRoot "codex_model_gate_gui.py")
) | Write-Host

$PayloadExe = Join-Path $PyInstallerDist "CodexModelGate.exe"
if (-not (Test-Path -LiteralPath $PayloadExe)) {
  throw "O PyInstaller terminou sem gerar o executável esperado: $PayloadExe"
}

# This is a direct portable executable.  It is never wrapped by Inno Setup, so it
# creates no shortcuts, uninstaller or registry entry on the computer where it runs.
Copy-Item -LiteralPath $PayloadExe -Destination $PortableExe -Force
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README-PORTATIL.md") -Destination $PortableReadme -Force

$iscc = Resolve-InnoSetupCompiler -RequestedCompiler $InnoSetupCompiler
Push-Location $ProjectRoot
try {
  & $iscc "/Qp" "CodexModelGate.iss"
  if ($LASTEXITCODE -ne 0) {
    throw "O Inno Setup não conseguiu gerar o instalador Windows."
  }
}
finally {
  Pop-Location
}

foreach ($artifact in @($SetupExe, $PortableExe, $PortableReadme)) {
  if (-not (Test-Path -LiteralPath $artifact)) {
    throw "A entrega está incompleta; não foi gerado: $artifact"
  }
}

Write-Host "Entrega criada em ${ReleaseDir}:"
Write-Host " - CodexModelGate-Setup.exe (instalador Windows com atalhos e desinstalador)"
Write-Host " - CodexModelGate-Pendrive.exe (executável portátil direto)"
Write-Host " - LEIA-ME-PORTATIL.md"
