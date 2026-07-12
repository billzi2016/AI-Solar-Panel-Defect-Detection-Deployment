# 部署流程

部署流程说明训练后的模型怎样进入推理环境。它关注的不只是能不能运行，还包括输出是否一致、延迟是否稳定、速度提升是否值得。

## ONNX 导出

ONNX 是一种模型交换格式。它把 PyTorch 中的模型计算图导出成通用格式，让其他推理后端可以加载。

输入是 PyTorch 权重、模型结构、输入尺寸和 opset 版本。输出是 `.onnx` 文件。

导出后必须做一致性检查。做法是给 PyTorch 模型和 ONNX 模型输入同一张图，比较输出差异。如果差异过大，后续 TensorRT benchmark 没有意义。

## ONNX Runtime

ONNX Runtime 是执行 ONNX 模型的推理后端。它可以作为 PyTorch 和 TensorRT 之间的中间检查点。

输入是 `.onnx` 文件和测试图片。输出是预测结果和推理延迟。

结果正常时，ONNX Runtime 的预测应该接近 PyTorch，速度通常也会更稳定。如果预测结果明显不同，应先检查输入归一化、通道顺序、动态尺寸和后处理代码。

## TensorRT

TensorRT 是 NVIDIA GPU 上常用的推理优化工具。它会根据模型结构、输入尺寸和硬件生成优化后的 engine。

输入是 ONNX 模型。输出是 `.engine` 文件。FP16 模式会用半精度计算降低延迟。INT8 模式还需要校准数据，用来估计量化范围。

结果正常时，TensorRT 应该在精度基本不变的前提下降低延迟。如果速度变快但 Recall 明显下降，这个部署版本不能直接作为默认方案。

## benchmark

benchmark 必须固定测试条件。至少要记录硬件、输入尺寸、batch size、warmup 次数、测试图片数量、平均延迟、P95 延迟和 FPS。

同一个表格里比较 PyTorch、ONNX Runtime 和 TensorRT，读者才能判断加速是否真实。只写“速度提升明显”没有可验证价值。
