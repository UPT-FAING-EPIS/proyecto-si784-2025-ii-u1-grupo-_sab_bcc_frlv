#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <chrono>
#include <ctime>
#include <sstream>
#include <iomanip>

namespace fs = std::filesystem;

static fs::path config_path() {
    return fs::current_path() / "config" / "antivirus_config.json";
}

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

static std::string read_file(const fs::path &p) {
    std::ifstream ifs(p);
    if (!ifs) return std::string();
    std::ostringstream ss;
    ss << ifs.rdbuf();
    return ss.str();
}

static void write_config(bool enabled, const std::string &notes) {
    fs::path p = config_path();
    if (!fs::exists(p.parent_path())) fs::create_directories(p.parent_path());
    std::string ts = now_iso_z();
    std::string esc_notes;
    for (char c : notes) {
        if (c == '"') esc_notes += "\\\"";
        else if (c == '\\') esc_notes += "\\\\";
        else esc_notes += c;
    }
    std::ofstream ofs(p, std::ios::trunc);
    ofs << "{\n";
    ofs << "  \"enabled\": " << (enabled ? "true" : "false") << ",\n";
    ofs << "  \"last_changed\": \"" << ts << "\",\n";
    ofs << "  \"notes\": \"" << esc_notes << "\"\n";
    ofs << "}\n";
}

static bool parse_enabled(const std::string &s, bool &out_enabled) {
    auto pos = s.find("\"enabled\"");
    if (pos == std::string::npos) return false;
    auto colon = s.find(':', pos);
    if (colon == std::string::npos) return false;
    auto sub = s.substr(colon + 1);
    auto tpos = sub.find("true");
    auto fpos = sub.find("false");
    if (tpos != std::string::npos && (fpos == std::string::npos || tpos < fpos)) { out_enabled = true; return true; }
    if (fpos != std::string::npos) { out_enabled = false; return true; }
    return false;
}

static bool extract_field(const std::string &s, const std::string &field, std::string &out) {
    auto pos = s.find('"' + field + '"');
    if (pos == std::string::npos) return false;
    auto colon = s.find(':', pos);
    if (colon == std::string::npos) return false;
    auto quote = s.find('"', colon);
    if (quote == std::string::npos) return false;
    auto endq = s.find('"', quote + 1);
    if (endq == std::string::npos) return false;
    out = s.substr(quote + 1, endq - quote - 1);
    return true;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Uso: antivirus_control <enable|disable|status> [notes]\n";
        return 1;
    }
    std::string cmd = argv[1];
    std::string notes;
    if (argc >= 3) notes = argv[2];

    fs::path cfg = config_path();

    if (cmd == "status") {
        if (!fs::exists(cfg)) { std::cout << "enabled: false\n"; return 0; }
        std::string content = read_file(cfg);
        bool enabled = false;
        if (parse_enabled(content, enabled)) std::cout << "enabled: " << (enabled ? "true" : "false") << "\n";
        std::string last_changed, cfg_notes;
        if (extract_field(content, "last_changed", last_changed)) std::cout << "last_changed: " << last_changed << "\n";
        if (extract_field(content, "notes", cfg_notes) && !cfg_notes.empty()) std::cout << "notes: " << cfg_notes << "\n";
        return 0;
    }

    if (cmd == "enable") {
        write_config(true, notes);
        std::cout << "Antivirus habilitado\n";
        return 0;
    }

    if (cmd == "disable") {
        write_config(false, notes);
        std::cout << "Antivirus deshabilitado\n";
        return 0;
    }

    std::cerr << "Comando desconocido: " << cmd << "\n";
    return 1;
}
