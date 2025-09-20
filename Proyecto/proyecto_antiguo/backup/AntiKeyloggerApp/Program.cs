using System;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;

class Program
{
	static void Main(string[] args)
	{
		// Ruta al modelo ONNX
		string modelPath = "../modelo_keylogger.onnx";

		// Crear opciones para usar GPU
		SessionOptions options = new SessionOptions();
		options.AppendExecutionProvider_CUDA(); // Usa GPU (CUDA)

		// Crear la sesión ONNX
		using var session = new InferenceSession(modelPath, options);

		// Ejemplo de datos de entrada (reemplaza con tus datos reales)
		float[] inputData = new float[] { /* valores numéricos aquí */ };
		int featureCount = inputData.Length;
		var inputTensor = new DenseTensor<float>(inputData, new int[] { 1, featureCount });

		// Nombre del input (debe coincidir con el modelo, normalmente 'float_input')
		var inputs = new NamedOnnxValue[] { NamedOnnxValue.CreateFromTensor("float_input", inputTensor) };

		// Ejecutar la inferencia
		using IDisposableReadOnlyCollection<DisposableNamedOnnxValue> results = session.Run(inputs);

		// Obtener el resultado
		foreach (var result in results)
		{
			var prediction = result.AsEnumerable<float>();
			foreach (var value in prediction)
			{
				Console.WriteLine($"Predicción: {value}");
			}
		}
	}
}

