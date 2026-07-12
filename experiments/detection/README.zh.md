# 检测实验

本目录包含目标检测实验入口。项目使用 Ultralytics YOLO 做模型训练、验证、预测和导出。仓库里的代码负责准备数据并调用成熟库，不实现自定义检测器。

## 流程

1. 把已下载的 VOC 格式数据集转换成 YOLO 目录。
2. 先跑短训练，验证数据路径、标签、batch 和输出目录是否正常。
3. 短训练成功后再运行更长训练。
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

## 短训练

短训练只用于检查链路。它会验证 Ultralytics 能否读取图片、解析标签、创建 batch 并写出结果。

```bash
python3 experiments/detection/run_yolo.py train --data datasets/processed/yolo/pvel_ad/dataset.yaml --epochs 1 --imgsz 640 --model yolov8n.pt --name pvel_ad_smoke
```

## 验证

```bash
python3 experiments/detection/run_yolo.py val --data datasets/processed/yolo/pvel_ad/dataset.yaml --model outputs/detection/pvel_ad_smoke/weights/best.pt
```

## 导出

```bash
python3 experiments/detection/run_yolo.py export --model outputs/detection/pvel_ad_smoke/weights/best.pt --format onnx
```

输出写入 `outputs/detection/`，该目录由 `.gitignore` 忽略。
