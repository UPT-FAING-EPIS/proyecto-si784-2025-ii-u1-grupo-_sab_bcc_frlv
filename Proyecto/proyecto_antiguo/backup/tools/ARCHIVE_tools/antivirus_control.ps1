Param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('enable','disable','status')]
    [string]$action,
    [string]$notes
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $scriptDir 'antivirus_control.exe'

function Show-Compile-Instructions {
    Write-Host "No se encontró el ejecutable 'antivirus_control.exe'." -ForegroundColor Yellow
    Write-Host "Compila el binario desde MSYS2 (MinGW64) o con Visual Studio:" -ForegroundColor Cyan
    Write-Host "  MSYS2 (MinGW64): open 'MSYS2 MinGW 64-bit' shell and run:" -ForegroundColor Gray
    Write-Host "    pacman -Syu" -ForegroundColor Gray
    Write-Host "    pacman -S --needed mingw-w64-x86_64-toolchain" -ForegroundColor Gray
    Write-Host "    cd /c/Users/windows10/Documents/GitHub/Python_ML" -ForegroundColor Gray
    Write-Host "    g++ -std=c++17 -O2 tools/antivirus_control.cpp -o tools/antivirus_control.exe" -ForegroundColor Gray
    Write-Host "  MSVC (Native Tools): open 'x64 Native Tools Command Prompt' and run:" -ForegroundColor Gray
    Write-Host "    cl.exe /EHsc tools\\antivirus_control.cpp /Fe:tools\\antivirus_control.exe" -ForegroundColor Gray
}

if (-not (Test-Path $exe)) {
    Show-Compile-Instructions
    exit 1
}

switch ($action) {
    'enable' { & $exe enable --notes "$notes" }
    'disable' { & $exe disable --notes "$notes" }
    'status' { & $exe status }
}
