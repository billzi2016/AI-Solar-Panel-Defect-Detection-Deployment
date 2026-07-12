# 部署工具

本目录放可执行的部署辅助工具。这些工具不负责训练模型，而是读取已经训练好的 checkpoint，生成部署产物，并写出小型 manifest 记录导出了什么。

## YOLO 导出

`export_yolo.py` 封装 Ultralytics export API。它用于 PVEL-AD 和 PV-Multi-Defect 的检测模型 checkpoint。

输入：

| 输入 | 含义 |
|---|---|
| `--model` | 已训练 YOLO `.pt` checkpoint，通常来自 `outputs/detection/<run>/weights/best.pt`。 |
| `--format` | 导出目标，例如 `onnx`、`engine` 或 `torchscript`。 |
| `--imgsz` | 导出图使用的图像尺寸。除非有明确原因，应该和训练、验证尺寸一致。 |
| `--device` | 传给 Ultralytics 的运行设备。根据机器使用 `cpu`、`mps` 或 CUDA 设备。 |

命令：

```bash
python3 deployment/export_yolo.py \
  --model outputs/detection/pvel_ad_yolo11l/weights/best.pt \
  --format onnx \
  --imgsz 640 \
  --name pvel_ad_yolo11l_onnx
```

输出：

| 输出 | 含义 |
|---|---|
| 导出的模型文件 | 由 Ultralytics 生成，位置以它返回的路径为准。 |
| `outputs/deployment/yolo/<name>.json` | manifest，记录 checkpoint、导出格式、图像尺寸、精度选项和导出路径。 |

正常结果应该包含 Ultralytics 打印出的导出路径，并且 manifest 文件存在。对于 ONNX，下一步应该用 ONNX Runtime 在固定图片集合上做推理一致性检查。

## ELPV ONNX 导出

`export_elpv.py` 用于导出 `experiments/elpv/run_torchvision.py` 训练出的 ResNet-18 或 Swin-T checkpoint。

输入：

| 输入 | 含义 |
|---|---|
| `--config` | ELPV 配置文件，用来确定模型名称、任务类型和图像尺寸。 |
| `--checkpoint` | `outputs/elpv/<name>/best.pt` 中保存的最优权重。 |
| `--output` | 可选的 ONNX 输出路径。 |
| `--opset` | ONNX opset 版本，默认是 `17`。 |

命令：

```bash
python3 deployment/export_elpv.py \
  --config configs/elpv/resnet18_binary.yaml \
  --checkpoint outputs/elpv/elpv_resnet18_binary/best.pt
```

输出：

| 输出 | 含义 |
|---|---|
| `outputs/deployment/elpv/<name>/model.onnx` | 带动态 batch 维度的 ONNX 模型。 |
| `outputs/deployment/elpv/<name>/manifest.json` | 导出元数据，以及输入输出约定。 |

正常结果应该生成 `model.onnx` 和 `manifest.json`。二分类模型输出两个 logits，回归模型输出一个连续值。输入是 RGB tensor，尺寸来自配置文件，并使用每个通道 `0.5` 的 mean 和 std 做归一化。

## 导出后应该比较什么

部署不是只生成一个文件。一个可判断的部署结果至少应该比较：

| 检查项 | 为什么需要 |
|---|---|
| PyTorch 和 ONNX 输出差异 | 确认预处理、图导出和输出解释没有错位。 |
| 平均延迟和 P95 延迟 | 同时观察典型速度和尾部延迟。 |
| FPS | 让不同模型的吞吐量可以横向比较。 |
| 导出后的检测 mAP 或分类 F1/AUC | 确认速度变化没有掩盖质量下降。 |
