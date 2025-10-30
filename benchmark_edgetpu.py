#!/usr/bin/env python3
"""Benchmark EdgeTPU inference speed"""
import time
import numpy as np
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate

print("=" * 60)
print("EdgeTPU Benchmark Test")
print("=" * 60)

# Load EdgeTPU delegate
delegate = load_delegate('libedgetpu.so.1')

# Create interpreter with EdgeTPU
interpreter = Interpreter(
    model_path='mobilenet_v2_1.0_224_quant_edgetpu.tflite',
    experimental_delegates=[delegate]
)
interpreter.allocate_tensors()

# Get input details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']

print(f"\nModel: MobileNet V2 (EdgeTPU optimized)")
print(f"Input shape: {input_shape}")
print(f"Input type: {input_details[0]['dtype']}")

# Prepare random input (simulating an image)
input_data = np.random.randint(0, 255, size=input_shape, dtype=np.uint8)

# Warmup
print("\nWarming up...")
for _ in range(5):
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

# Benchmark
print("\nRunning benchmark (100 iterations)...")
times = []
for i in range(100):
    start = time.perf_counter()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    times.append(time.perf_counter() - start)

# Calculate statistics
avg_time = np.mean(times) * 1000  # Convert to ms
std_time = np.std(times) * 1000
min_time = np.min(times) * 1000
max_time = np.max(times) * 1000
fps = 1000 / avg_time

print("\n" + "=" * 60)
print("RESULTS:")
print("-" * 60)
print(f"Average inference: {avg_time:.2f} ms")
print(f"Std deviation: {std_time:.2f} ms")
print(f"Min inference: {min_time:.2f} ms")
print(f"Max inference: {max_time:.2f} ms")
print(f"FPS: {fps:.1f}")
print("=" * 60)

print("\n✅ EdgeTPU is working perfectly!")
print(f"   Achieving {fps:.1f} FPS with MobileNet V2")
print("\nNext steps:")
print("1. Convert YOLOv8 model to TFLite")
print("2. Compile for EdgeTPU")
print("3. Test on goldfish detection")