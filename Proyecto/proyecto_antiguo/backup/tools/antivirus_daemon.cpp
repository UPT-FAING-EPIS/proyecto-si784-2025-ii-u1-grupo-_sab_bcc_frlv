#include <chrono>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <atomic>
#include <cstdlib>

namespace fs = std::filesystem;

static std::atomic<bool> keep_running(true);

void sigint_handler(int) {
    keep_running = false;
}

static fs::path config_path() {
    return fs::current_path() / "config" / "antivirus_config.json";
}

static std::string read_file(const fs::path &p) {
    std::ifstream ifs(p);
    if (!ifs) return std::string();
    std::ostringstream ss;
    ss << ifs.rdbuf();
    return ss.str();
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

int main(int argc, char **argv) {
    signal(SIGINT, sigint_handler);
    signal(SIGTERM, sigint_handler);

    // Defaults
    std::string model = "backup/modelo/modelo_keylogger_from_datos.onnx";
    std::string input = "DATOS/Keylogger_Detection_Dataset.csv";
    int interval = 10; // seconds between inference runs when enabled
    std::string log_file = "logs/antivirus_daemon.log";
    fs::path logp = log_file;

    // Simple args: --model <path> --input <path> --interval <sec>
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--model" && i + 1 < argc) model = argv[++i];
        else if (a == "--input" && i + 1 < argc) input = argv[++i];
        else if (a == "--interval" && i + 1 < argc) interval = std::stoi(argv[++i]);
        else if (a == "--log" && i + 1 < argc) log_file = argv[++i];
    }

    if (!fs::exists(logp.parent_path())) fs::create_directories(logp.parent_path());

    std::ofstream log(logp.string(), std::ios::app);
    if (!log) {
        std::cerr << "No se pudo abrir el archivo de log: " << logp.string() << std::endl;
        return 1;
    }

    log << "[daemon] start\n";
    log.flush();

    bool last_enabled = false;

    while (keep_running) {
        bool enabled = false;
        fs::path cfg = config_path();
        if (fs::exists(cfg)) {
            std::string content = read_file(cfg);
            parse_enabled(content, enabled);
        }

        if (enabled) {
            log << "[daemon] enabled -> running inference\n";
            log.flush();

            // Build command to run existing script
            // Prefer Python in PATH; user can set full path to python if needed.
            std::ostringstream cmd;
            cmd << "python scripts/predecir_keylogger.py --onnx \"" << model << "\" --input \"" << input << "\" >> \"" << logp.string() << "\" 2>&1";

            int ret = std::system(cmd.str().c_str());
            log << "[daemon] inference exit code: " << ret << "\n";
            log.flush();

            // Wait interval seconds or until signalled
            for (int i = 0; i < interval && keep_running; ++i) std::this_thread::sleep_for(std::chrono::seconds(1));
        } else {
            if (last_enabled != enabled) {
                log << "[daemon] disabled -> idle\n";
                log.flush();
            }
            // Sleep a short time and re-check
            for (int i = 0; i < 2 && keep_running; ++i) std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        last_enabled = enabled;
    }

    log << "[daemon] stopping\n";
    log.close();
    return 0;
}
