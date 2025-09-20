cmake_minimum_required(VERSION 3.15)
project(antivirus_cpp_project VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(antivirus_cli
    src_cpp/main.cpp
    src_cpp/antivirus_controller.cpp
    src_cpp/model_runner.cpp
)

target_include_directories(antivirus_cli PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src_cpp)
