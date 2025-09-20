#include "antivirus_controller.h"
#include "model_runner.h"
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <chrono>

int main(int argc, char **argv) {
    std::string cfg = "config/antivirus_config.json";
    AntivirusController ctrl(cfg);

    if (argc < 2) {
        std::cout << "Usage: antivirus_cli <enable|disable|status|run> [options]\n";
        return 1;
    }

    std::string cmd = argv[1];
    if (cmd == "enable") {
        std::string notes = (argc >= 3) ? argv[2] : "";
        ctrl.enable(notes);
        std::cout << "enabled\n";
        return 0;
    }
    if (cmd == "disable") {
        std::string notes = (argc >= 3) ? argv[2] : "";
        ctrl.disable(notes);
        std::cout << "disabled\n";
        return 0;
    }
    if (cmd == "status") {
        std::cout << (ctrl.is_enabled() ? "enabled" : "disabled") << std::endl;
        return 0;
    }
    if (cmd == "run") {
        std::string model = (argc >= 3) ? argv[2] : "backup/modelo/modelo_keylogger_from_datos.onnx";
        std::string input = (argc >= 4) ? argv[3] : "DATOS/Keylogger_Detection_Dataset.csv";
        ModelRunner mr(model, input);
        int rc = mr.run();
        std::cout << "model exit: " << rc << std::endl;
        return rc;
    }

    if (cmd == "interactive") {
        std::cout << "Entering interactive mode. Type 'help' for commands.\n";
        while (true) {
            std::cout << "> ";
            std::string line;
            if (!std::getline(std::cin, line)) break;
            if (line == "quit" || line == "exit") break;
            if (line == "help") {
                std::cout << "Commands:\n  run [model] [input]  - run one inference\n  status - show enabled/disabled\n  enable [notes] - enable\n  disable [notes] - disable\n  exit - quit\n";
                continue;
            }
            if (line.rfind("run", 0) == 0) {
                std::istringstream iss(line);
                std::string cmd2, model, input;
                iss >> cmd2 >> model >> input;
                if (model.empty()) model = "backup/modelo/modelo_keylogger_from_datos.onnx";
                if (input.empty()) input = "DATOS/Keylogger_Detection_Dataset.csv";
                ModelRunner mr(model, input);
                mr.run();
                continue;
            }
            if (line == "status") { std::cout << (ctrl.is_enabled() ? "enabled" : "disabled") << std::endl; continue; }
            if (line.rfind("enable", 0) == 0) { std::string notes = line.substr(7); ctrl.enable(notes); std::cout << "enabled\n"; continue; }
            if (line.rfind("disable", 0) == 0) { std::string notes = line.substr(8); ctrl.disable(notes); std::cout << "disabled\n"; continue; }
            std::cout << "Unknown command (type 'help').\n";
        }
        return 0;
    }

    std::cerr << "Unknown command\n";
    return 1;
}
