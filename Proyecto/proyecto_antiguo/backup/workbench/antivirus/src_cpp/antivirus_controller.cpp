#include "antivirus_controller.h"
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <chrono>

namespace fs = std::filesystem;

static std::string now_iso_z() {
    using namespace std::chrono;
    auto now = system_clock::now();
    std::time_t t = system_clock::to_time_t(now);
    std::tm tm;
#ifdef _WIN32
    gmtime_s(&tm, &t);
#else
    gmtime_r(&t, &tm);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return oss.str();
}

AntivirusController::AntivirusController(const std::string &config_path) : config_path_(config_path) {}

bool AntivirusController::is_enabled() {
    if (!fs::exists(config_path_)) return false;
    std::ifstream ifs(config_path_);
    if (!ifs) return false;
    std::string content((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
    auto pos = content.find("\"enabled\"");
    if (pos == std::string::npos) return false;
    auto colon = content.find(':', pos);
    if (colon == std::string::npos) return false;
    auto sub = content.substr(colon + 1);
    auto tpos = sub.find("true");
    auto fpos = sub.find("false");
    if (tpos != std::string::npos && (fpos == std::string::npos || tpos < fpos)) return true;
    return false;
}

void AntivirusController::enable(const std::string &notes) {
    if (!fs::exists(fs::path(config_path_).parent_path())) fs::create_directories(fs::path(config_path_).parent_path());
    std::ofstream ofs(config_path_, std::ios::trunc);
    ofs << "{\n";
    ofs << "  \"enabled\": true,\n";
    ofs << "  \"last_changed\": \"" << now_iso_z() << "\",\n";
    ofs << "  \"notes\": \"" << notes << "\"\n";
    ofs << "}\n";
}

void AntivirusController::disable(const std::string &notes) {
    if (!fs::exists(fs::path(config_path_).parent_path())) fs::create_directories(fs::path(config_path_).parent_path());
    std::ofstream ofs(config_path_, std::ios::trunc);
    ofs << "{\n";
    ofs << "  \"enabled\": false,\n";
    ofs << "  \"last_changed\": \"" << now_iso_z() << "\",\n";
    ofs << "  \"notes\": \"" << notes << "\"\n";
    ofs << "}\n";
}
