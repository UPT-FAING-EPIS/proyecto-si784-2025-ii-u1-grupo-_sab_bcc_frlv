#include "model_runner.h"
#include <cstdlib>
#include <sstream>
#include <filesystem>
#include <fstream>
#include <iostream>

ModelRunner::ModelRunner(const std::string &model_path, const std::string &input_path)
    : model_path_(model_path), input_path_(input_path) {}

int ModelRunner::run() {
    namespace fs = std::filesystem;
    // Find repository root by searching upward for the scripts folder
    fs::path cwd = fs::current_path();
    fs::path repo = cwd;
    bool found = false;
    while (true) {
        if (fs::exists(repo / "scripts" / "predecir_keylogger.py")) { found = true; break; }
        if (!repo.has_parent_path()) break;
        repo = repo.parent_path();
    }
    if (!found) {
        // fallback to cwd (best-effort)
        repo = cwd;
    }

    fs::path script = repo / "scripts" / "predecir_keylogger.py";

    // place logs in repo/logs so they are easy to find
    fs::path logdir = repo / "logs";
    if (!fs::exists(logdir)) fs::create_directories(logdir);
    fs::path out = logdir / "last_inference_output.txt";

    // Resolve model and input paths relative to repo if they are relative
    fs::path modelp = fs::path(model_path_);
    if (modelp.is_relative()) modelp = repo / modelp;
    fs::path inputp = fs::path(input_path_);
    if (inputp.is_relative()) inputp = repo / inputp;

    // Prefer a specific python executable to ensure installed packages are available.
    // Adjust this path if your Python is installed elsewhere.
    std::string python_exec = "C:\\Program Files\\Python313\\python.exe";

    std::ostringstream cmd;
    cmd << "\"" << python_exec << "\" \"" << script.string() << "\" --onnx \"" << modelp.string() << "\" --input \"" << inputp.string() << "\" > \"" << out.string() << "\" 2>&1";

    // write the command to the log before executing for debugging
    {
        std::ofstream dbg(out.string(), std::ios::trunc);
        dbg << "CMD: " << cmd.str() << "\n";
        dbg.close();
    }

    int rc = std::system(cmd.str().c_str());

    // print captured output
    std::ifstream ifs(out.string());
    if (ifs) {
        std::cout << ifs.rdbuf() << std::endl;
    } else {
        std::cout << "(no output captured)\n";
    }
    return rc;
}
