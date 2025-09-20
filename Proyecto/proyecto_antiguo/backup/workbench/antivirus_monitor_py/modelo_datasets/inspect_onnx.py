#!/usr/bin/env python3
"""Inspeccionar un modelo ONNX: listar inputs, outputs y tipos."""
import sys
from pathlib import Path

model_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'modelos' / 'modelo_keylogger_from_datos.onnx'
print('Model path:', model_path)

try:
    import onnxruntime as ort
except Exception as e:
    print('onnxruntime no disponible:', e)
    sys.exit(1)

print('Available providers:', ort.get_available_providers())
try:
    sess = ort.InferenceSession(str(model_path), providers=ort.get_available_providers())
except Exception as e:
    print('Error creando InferenceSession:', e)
    sys.exit(1)

print('\nInputs:')
for i in sess.get_inputs():
    print('-', i.name, 'shape=', i.shape, 'type=', i.type)

print('\nOutputs:')
for o in sess.get_outputs():
    print('-', o.name, 'shape=', o.shape, 'type=', o.type)

try:
    import onnx
    m = onnx.load_model(str(model_path))
    print('\nONNX graph info:')
    print('nodes:', len(m.graph.node))
    for n in m.graph.node[-5:]:
        print(' node:', n.op_type, 'name:', n.name)
except Exception as e:
    print('\nonnx package not available or failed to parse:', e)

print('\nDone')