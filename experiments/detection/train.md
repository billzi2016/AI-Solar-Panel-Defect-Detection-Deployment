# YOLO Detection Training Matrix

This page is the training map for all YOLO detection experiments. The local validation scripts use the smallest `n` models. Formal result scripts use the `l` configs by default because `l` is the large model and the second largest common Ultralytics size. The full size order is:

```text
n < s < m < l < x
```

`m` is the medium model. `l` is larger than medium. `x` is the largest and should only be used when memory and training time are available.

## How Parameters Change With Model Size

| Size | YOLO11 params | YOLOv8 params | Role | Batch default | Why it changes |
|---|---:|---:|---|---:|---|
| `n` | about 2.6M | about 3.2M | Local validation and fast comparison | 16 | Smallest model, lowest memory cost, fastest way to check data and labels. |
| `s` | about 9.4M | about 11.2M | Light experiment | 12 | More capacity than `n`, still manageable on limited hardware. |
| `m` | about 20.1M | about 25.9M | Medium experiment | 8 | Better capacity, higher memory use, slower training. |
| `l` | about 25.3M | about 43.7M | Formal default result | 4 | Large model, stronger baseline for final comparison, but more expensive. |
| `x` | about 56.9M | about 68.2M | Maximum-size stress run | 2 | Highest capacity and memory cost; use only when resources allow it. |

The parameter counts are approximate Ultralytics model-family values. They are meant for planning memory and runtime cost; for an exact count in the installed environment, print `model.info()` from the Ultralytics model object. All configs use `epochs: 100`, `imgsz: 640`, and `patience: 3`. `patience: 3` enables early stopping when validation metrics stop improving, so a model does not keep training for many epochs after it has already plateaued. If small defects are missed, `imgsz` can be increased later, but batch size usually has to decrease when image size increases.

# PVEL-AD

PVEL-AD is the main EL cell defect detection dataset. It has 12 defect classes and a long-tail class distribution.

## YOLO11

### Size: n, about 2.6M parameters

Config: `configs/detection/pvel_ad_yolo11n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11n.yaml
```

### Size: s, about 9.4M parameters

Config: `configs/detection/pvel_ad_yolo11s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11s.yaml
```

### Size: m, about 20.1M parameters

Config: `configs/detection/pvel_ad_yolo11m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11m.yaml
```

### Size: l, about 25.3M parameters

Config: `configs/detection/pvel_ad_yolo11l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11l.yaml
```

### Size: x, about 56.9M parameters

Config: `configs/detection/pvel_ad_yolo11x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolo11x.yaml
```

## YOLOv8

### Size: n, about 3.2M parameters

Config: `configs/detection/pvel_ad_yolov8n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8n.yaml
```

### Size: s, about 11.2M parameters

Config: `configs/detection/pvel_ad_yolov8s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8s.yaml
```

### Size: m, about 25.9M parameters

Config: `configs/detection/pvel_ad_yolov8m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8m.yaml
```

### Size: l, about 43.7M parameters

Config: `configs/detection/pvel_ad_yolov8l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8l.yaml
```

### Size: x, about 68.2M parameters

Config: `configs/detection/pvel_ad_yolov8x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pvel_ad_yolov8x.yaml
```

# PV-Multi-Defect

PV-Multi-Defect is the visible panel defect detection dataset. It has 5 classes and uses the same YOLO training wrapper after conversion.

## YOLO11

### Size: n, about 2.6M parameters

Config: `configs/detection/pv_multi_defect_yolo11n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11n.yaml
```

### Size: s, about 9.4M parameters

Config: `configs/detection/pv_multi_defect_yolo11s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11s.yaml
```

### Size: m, about 20.1M parameters

Config: `configs/detection/pv_multi_defect_yolo11m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11m.yaml
```

### Size: l, about 25.3M parameters

Config: `configs/detection/pv_multi_defect_yolo11l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11l.yaml
```

### Size: x, about 56.9M parameters

Config: `configs/detection/pv_multi_defect_yolo11x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolo11x.yaml
```

## YOLOv8

### Size: n, about 3.2M parameters

Config: `configs/detection/pv_multi_defect_yolov8n.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8n.yaml
```

### Size: s, about 11.2M parameters

Config: `configs/detection/pv_multi_defect_yolov8s.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8s.yaml
```

### Size: m, about 25.9M parameters

Config: `configs/detection/pv_multi_defect_yolov8m.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8m.yaml
```

### Size: l, about 43.7M parameters

Config: `configs/detection/pv_multi_defect_yolov8l.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8l.yaml
```

### Size: x, about 68.2M parameters

Config: `configs/detection/pv_multi_defect_yolov8x.yaml`

```bash
python3 experiments/detection/run_yolo.py train --config configs/detection/pv_multi_defect_yolov8x.yaml
```
