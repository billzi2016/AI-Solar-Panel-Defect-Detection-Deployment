# Deployment Tools

This directory contains executable deployment helpers. The tools do not train models. They take trained checkpoints and produce deployment artifacts plus small manifests that record what was exported.

## YOLO Export

`export_yolo.py` wraps the Ultralytics export API. It is used for PVEL-AD and PV-Multi-Defect detection checkpoints.

Input:

| Input | Meaning |
|---|---|
| `--model` | A trained YOLO `.pt` checkpoint, usually from `outputs/detection/<run>/weights/best.pt`. |
| `--format` | Export target, such as `onnx`, `engine`, or `torchscript`. |
| `--imgsz` | The image size used by the exported graph. It should match the training and validation setting unless there is a reason to change it. |
| `--device` | Runtime device passed to Ultralytics. Use `cpu`, `mps`, or a CUDA device depending on the machine. |

Command:

```bash
python3 deployment/export_yolo.py \
  --model outputs/detection/pvel_ad_yolo11l/weights/best.pt \
  --format onnx \
  --imgsz 640 \
  --name pvel_ad_yolo11l_onnx
```

Output:

| Output | Meaning |
|---|---|
| Exported model file | Created by Ultralytics next to the checkpoint or in the backend-specific location it reports. |
| `outputs/deployment/yolo/<name>.json` | Manifest with checkpoint path, export format, image size, precision flags, and exported path. |

The export is normal when Ultralytics prints an exported file path, the manifest exists, and the exported model can be loaded by the target backend. For ONNX, the next check should be ONNX Runtime inference on a fixed image set.

## ELPV ONNX Export

`export_elpv.py` exports the torchvision ResNet-18 or Swin-T checkpoints produced by `experiments/elpv/run_torchvision.py`.

Input:

| Input | Meaning |
|---|---|
| `--config` | The ELPV config used to define model name, task, and image size. |
| `--checkpoint` | The trained `best.pt` state dictionary from `outputs/elpv/<name>/best.pt`. |
| `--output` | Optional explicit ONNX output path. |
| `--opset` | ONNX opset version. The default is `17`. |

Command:

```bash
python3 deployment/export_elpv.py \
  --config configs/elpv/resnet18_binary.yaml \
  --checkpoint outputs/elpv/elpv_resnet18_binary/best.pt
```

Output:

| Output | Meaning |
|---|---|
| `outputs/deployment/elpv/<name>/model.onnx` | ONNX model with dynamic batch dimension. |
| `outputs/deployment/elpv/<name>/manifest.json` | Export metadata and expected input/output contract. |

The export is normal when `model.onnx` and `manifest.json` are created. For binary classification, the ONNX output is two logits. For regression, the ONNX output is one value. The input is an RGB tensor resized to the configured image size and normalized with mean and standard deviation of `0.5` for each channel.

## What Should Be Compared After Export

Deployment is not complete just because a file was created. A useful deployment result should compare:

| Check | Why it matters |
|---|---|
| PyTorch vs ONNX output difference | Confirms preprocessing, graph export, and output interpretation are consistent. |
| Latency average and P95 | Shows both typical speed and tail latency. |
| FPS | Makes throughput comparable across models. |
| Detection mAP or classification F1/AUC after export | Confirms speed did not hide a quality regression. |
