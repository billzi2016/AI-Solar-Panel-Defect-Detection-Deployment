# 检测实验

本目录包含目标检测实验入口。项目使用 Ultralytics YOLO 做模型训练、验证、预测和导出。仓库里的代码负责准备数据并调用成熟库，不实现自定义检测器。

## 流程

1. 把已下载的 VOC 格式数据集转换成 YOLO 目录。
2. 运行 YOLO11 训练入口，作为当前默认实验。
3. 用同一份处理后的数据运行 YOLOv8 baseline。
4. 验证训练得到的 checkpoint。
5. 导出 ONNX，用于后续部署检查。

## 准备数据

PVEL-AD：

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
```

PV-Multi-Defect：

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

## 完整训练

下面两个 shell 脚本用于完整训练。它们使用同一份处理后的数据和同一个 wrapper，因此对比重点是模型版本，而不是项目里有两套训练逻辑。

YOLO11 默认：

```bash
./experiments/detection/train_yolo11.sh
```

YOLOv8 baseline：

```bash
./experiments/detection/train_yolov8.sh
```

两个脚本都支持环境变量覆盖：

```bash
EPOCHS=50 BATCH=8 DEVICE=0 ./experiments/detection/train_yolo11.sh
```

## 短链路检查

短链路检查放在 `tests/smoke/`，因为它是测试工具，不是完整实验。

```bash
./tests/smoke/test_yolo_detection_pipeline.sh
```

## 验证

```bash
python3 experiments/detection/run_yolo.py val --data datasets/processed/yolo/pvel_ad/dataset.yaml --model outputs/detection/pvel_ad_yolo11n/weights/best.pt
```

## 导出

```bash
python3 experiments/detection/run_yolo.py export --model outputs/detection/pvel_ad_yolo11n/weights/best.pt --format onnx
```

输出写入 `outputs/detection/`，该目录由 `.gitignore` 忽略。
