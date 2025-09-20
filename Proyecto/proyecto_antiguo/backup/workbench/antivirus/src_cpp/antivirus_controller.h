#pragma once

#include <string>

class AntivirusController {
public:
    AntivirusController(const std::string &config_path);
    bool is_enabled();
    void enable(const std::string &notes = "");
    void disable(const std::string &notes = "");
private:
    std::string config_path_;
};
