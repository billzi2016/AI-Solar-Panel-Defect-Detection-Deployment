# YOLO 检测训练矩阵

本页是所有 YOLO 检测实验的训练地图。本机 validation 脚本使用最小的 `n` 模型。正式结果脚本默认使用 `l` 配置，因为 `l` 是 large，也是 Ultralytics 常见尺寸中的倒数第二大模型。完整尺寸顺序是：

```text
n < s < m < l < x
```

`m` 是 medium，中型模型。`l` 比中型更大。`x` 是最大模型，只适合在显存和训练时间足够时使用。

## 模型变大时参数怎么变

| 尺寸 | YOLO11 参数量 | YOLOv8 参数量 | 作用 | 默认 batch | 为什么这样变 |
|---|---:|---:|---|---:|---|
| `n` | 约 2.6M | 约 3.2M | 本机 validation 和快速对比 | 16 | 最小模型，显存占用最低，最快检查数据和标签。 |
| `s` | 约 9.4M | 约 11.2M | 轻量实验 | 12 | 比 `n` 容量更大，但资源压力还比较可控。 |
| `m` | 约 20.1M | 约 25.9M | 中型实验 | 8 | 表达能力更强，显存占用和训练时间都会增加。 |
| `l` | 约 25.3M | 约 43.7M | 正式默认结果 | 4 | large 模型，更适合做正式对比，但训练成本更高。 |
| `x` | 约 56.9M | 约 68.2M | 最大尺寸压力实验 | 2 | 容量和显存占用最高，只在资源足够时使用。 |

参数量是 Ultralytics 对应模型族的大致数值，主要用于估算显存和训练时间。需要精确数值时，应在当前安装环境里通过 Ultralytics 模型对象的 `model.info()` 打印确认。所有配置默认使用 `epochs: 100`、`imgsz: 640` 和 `patience: 3`。`patience: 3` 表示验证指标连续 3 轮没有继续改善时提前停止，避免模型已经平台期后还长时间训练。如果小缺陷漏检，后续可以提高 `imgsz`，但图像尺寸提高后通常也要降低 batch。

# PVEL-AD

PVEL-AD 是主要的 EL 电池片缺陷检测数据集。它包含 12 类缺陷，并且类别分布明显长尾。

## YOLO11

### 尺寸：n，约 2.6M 参数

配置：`configs/detection/pvel_ad_yolo11n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11n.yaml
```

### 尺寸：s，约 9.4M 参数

配置：`configs/detection/pvel_ad_yolo11s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11s.yaml
```

### 尺寸：m，约 20.1M 参数

配置：`configs/detection/pvel_ad_yolo11m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11m.yaml
```

### 尺寸：l，约 25.3M 参数

配置：`configs/detection/pvel_ad_yolo11l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11l.yaml
```

### 尺寸：x，约 56.9M 参数

配置：`configs/detection/pvel_ad_yolo11x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11x.yaml
```

## YOLOv8

### 尺寸：n，约 3.2M 参数

配置：`configs/detection/pvel_ad_yolov8n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8n.yaml
```

### 尺寸：s，约 11.2M 参数

配置：`configs/detection/pvel_ad_yolov8s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8s.yaml
```

### 尺寸：m，约 25.9M 参数

配置：`configs/detection/pvel_ad_yolov8m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8m.yaml
```

### 尺寸：l，约 43.7M 参数

配置：`configs/detection/pvel_ad_yolov8l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8l.yaml
```

### 尺寸：x，约 68.2M 参数

配置：`configs/detection/pvel_ad_yolov8x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8x.yaml
```

# PV-Multi-Defect

PV-Multi-Defect 是可见面板缺陷检测数据集。它包含 5 类缺陷，转换后复用同一个 YOLO 训练 wrapper。

## YOLO11

### 尺寸：n，约 2.6M 参数

配置：`configs/detection/pv_multi_defect_yolo11n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11n.yaml
```

### 尺寸：s，约 9.4M 参数

配置：`configs/detection/pv_multi_defect_yolo11s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11s.yaml
```

### 尺寸：m，约 20.1M 参数

配置：`configs/detection/pv_multi_defect_yolo11m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11m.yaml
```

### 尺寸：l，约 25.3M 参数

配置：`configs/detection/pv_multi_defect_yolo11l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11l.yaml
```

### 尺寸：x，约 56.9M 参数

配置：`configs/detection/pv_multi_defect_yolo11x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11x.yaml
```

## YOLOv8

### 尺寸：n，约 3.2M 参数

配置：`configs/detection/pv_multi_defect_yolov8n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8n.yaml
```

### 尺寸：s，约 11.2M 参数

配置：`configs/detection/pv_multi_defect_yolov8s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8s.yaml
```

### 尺寸：m，约 25.9M 参数

配置：`configs/detection/pv_multi_defect_yolov8m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8m.yaml
```

### 尺寸：l，约 43.7M 参数

配置：`configs/detection/pv_multi_defect_yolov8l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8l.yaml
```

### 尺寸：x，约 68.2M 参数

配置：`configs/detection/pv_multi_defect_yolov8x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8x.yaml
```
