#include <onnxruntime_cxx_api.h>
#include <vector>
#include <iostream>

int main() {
	Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "AntiKeylogger");
	Ort::SessionOptions session_options;
	// No es necesario (ni existe) AppendExecutionProvider_CPU: la ejecución por CPU es el proveedor por defecto.
	// Para usar GPU/CUDA, llame a session_options.AppendExecutionProvider_CUDA(...) según su build.

	// Construir model path en el tipo ORTCHAR_T que espera la API
#ifdef _WIN32
	std::basic_string<ORTCHAR_T> model_path_t = ORT_TSTR("modelo_keylogger.onnx");
	Ort::Session session(env, model_path_t.c_str(), session_options);
#else
	const char* model_path_c = "modelo_keylogger.onnx";
	Ort::Session session(env, model_path_c, session_options);
#endif

	// Prepara los datos de entrada (reemplaza con tus valores numéricos)
	std::vector<float> input_data = { /* tus valores aquí */ };
	std::vector<int64_t> input_shape = {1, static_cast<int64_t>(input_data.size())};

	const char* input_names[] = {"float_input"};
	const char* output_names[] = {"output_label"}; // Ajusta si tu modelo tiene otro nombre de output

	Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
	Ort::Value input_tensor = Ort::Value::CreateTensor<float>(memory_info, input_data.data(), input_data.size(), input_shape.data(), input_shape.size());

	Ort::RunOptions run_options;
	auto output_tensors = session.Run(run_options, input_names, &input_tensor, 1, output_names, 1);

	float* output = output_tensors.front().GetTensorMutableData<float>();
	std::cout << "Predicción: " << output[0] << std::endl;

	return 0;
}
