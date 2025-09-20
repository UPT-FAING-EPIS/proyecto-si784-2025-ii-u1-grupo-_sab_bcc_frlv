antivirus_cpp_project

This small C++ project provides a CLI `antivirus_cli` with commands:
- enable [notes]
- disable [notes]
- status
- run [model_path] [input_path]

It uses the existing Python inference script for now. Build with CMake (MSYS2 MinGW64 or MSVC).

Build example (MSYS2 MinGW64):

pacman -S --needed mingw-w64-x86_64-toolchain cmake
mkdir build && cd build
cmake -G "MinGW Makefiles" ..
cmake --build .

Run:

# enable
./antivirus_cli enable "Testing"
# status
./antivirus_cli status
# run inference
./antivirus_cli run backup/modelo/modelo_keylogger_from_datos.onnx DATOS/Keylogger_Detection_Dataset.csv
