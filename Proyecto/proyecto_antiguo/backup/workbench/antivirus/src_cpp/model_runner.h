#pragma once

#include <string>

class ModelRunner {
public:
    ModelRunner(const std::string &model_path, const std::string &input_path);
    int run(); // returns exit code
private:
    std::string model_path_;
    std::string input_path_;
};
