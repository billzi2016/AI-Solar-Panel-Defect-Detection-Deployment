# Deployment

The deployment workflow explains how a trained model enters an inference environment. It checks more than whether the model runs. It also checks output consistency, latency stability, and whether the speedup is worth using.

Executable export helpers live in `deployment/`. YOLO checkpoints use `deployment/export_yolo.py`; ELPV ResNet-18 and Swin-T checkpoints use `deployment/export_elpv.py`. Detailed command examples and input/output contracts are documented in the Deployment Tools page.

## ONNX export

ONNX is a model exchange format. It exports the computation graph from PyTorch into a portable format that other inference backends can load.

The input is PyTorch weights, model structure, input size, and opset version. The output is an `.onnx` file.

After export, output consistency must be checked. The PyTorch model and ONNX model should receive the same image, and their outputs should be compared. If the difference is too large, a later TensorRT benchmark is not meaningful.

## ONNX Runtime

ONNX Runtime is an inference backend for ONNX models. It works as a checkpoint between PyTorch and TensorRT.

The input is an `.onnx` file and test images. The output is predictions and inference latency.

When the result is normal, ONNX Runtime predictions should be close to PyTorch predictions, and latency is often more stable. If predictions differ clearly, check input normalization, channel order, dynamic shape settings, and post-processing code first.

## TensorRT

TensorRT is a common inference optimizer for NVIDIA GPUs. It builds an optimized engine based on the model graph, input size, and hardware.

The input is an ONNX model. The output is an `.engine` file. FP16 mode uses half precision to reduce latency. INT8 mode also needs calibration data to estimate quantization ranges.

When the result is normal, TensorRT should reduce latency while keeping accuracy close to the original model. If speed improves but recall drops clearly, that deployment version should not become the default.

## Benchmark

A benchmark must fix the test conditions. It should record hardware, input size, batch size, warmup count, number of test images, average latency, P95 latency, and FPS.

PyTorch, ONNX Runtime, and TensorRT should be compared in the same table. That lets readers judge whether the speedup is real. A sentence like "speed improved a lot" is not verifiable.
