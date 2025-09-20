Antivirus control - build & usage

Quick build instructions

MSYS2 (recommended)
1. Open "MSYS2 MinGW 64-bit" shell from Start.
2. Update packages:
   pacman -Syu
   # if shell closes, re-open "MSYS2 MinGW 64-bit"
3. Install toolchain:
   pacman -S --needed mingw-w64-x86_64-toolchain
4. Build (from MSYS2 MinGW64 shell):
   cd /c/Users/windows10/Documents/GitHub/Python_ML
   g++ -std=c++17 -O2 tools/antivirus_control.cpp -o tools/antivirus_control.exe

MSVC (Visual Studio)
1. Open "x64 Native Tools Command Prompt for VS 2022".
2. Run:
   cl.exe /EHsc tools\antivirus_control.cpp /Fe:tools\antivirus_control.exe

Usage (PowerShell)
From repository root:

# enable
.\tools\antivirus_control.ps1 -action enable -notes "Activado para pruebas"

# status
.\tools\antivirus_control.ps1 -action status

# disable
.\tools\antivirus_control.ps1 -action disable -notes "Desactivado"

Notes
- The executable writes/reads `config/antivirus_config.json` in the repository root.
- The C++ binary is intentionally dependency-free to ease distribution.
