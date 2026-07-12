# Experiment Report

This report summarizes the experiment design, evaluation protocol, and deployment interpretation for the solar-defect detection project. The project uses public datasets to reproduce the same engineering workflow that is normally used for photovoltaic visual inspection: data audit, task-specific model selection, training, evaluation, export, and deployment checks.

## Scope

The project separates datasets by label type instead of forcing all data into one model family.

| Dataset | Label type | Experiment track | Model family |
|---|---|---|---|
| PVEL-AD | EL cell defect boxes | Manufacturing-defect detection | YOLO11 and YOLOv8 |
| PV-Multi-Defect | Visible panel defect boxes | Surface-defect detection | YOLO11 and YOLOv8 |
| ELPV | One probability label per cell image | Image-level classification or regression | ResNet-18 and Swin-T |

This separation matters because model outputs must match the label contract. A detector needs boxes. An image classifier needs one label per image. A regression model needs a continuous target. Mixing those tasks would make metrics hard to interpret and would hide real failure modes.

## Data Audit

Before training, the data pipeline checks the dataset shape and label quality:

| Check | What is inspected | Why it matters |
|---|---|---|
| Image count | Local files under `datasets/raw/` | Confirms the local dataset tree is complete enough for experiments. |
| Label parsing | ELPV CSV rows and Pascal VOC XML files | Confirms labels can be read without silently dropping samples. |
| Class balance | Per-class object counts | Reveals long-tail classes that need per-class evaluation. |
| Visual sanity | Generated sample grids with real boxes | Confirms that labels are attached to the expected image regions. |

The generated report is produced by:

```bash
python3 data_tools/stats/build_dataset_report.py
```

Normal data-audit output should include readable class names, non-empty annotation counts for the detection datasets, visible long-tail distributions, and sample grids where red boxes align with plausible defect regions.

## Detection Experiments

PVEL-AD and PV-Multi-Defect use the same detection pipeline after conversion to YOLO format.

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

The formal detection matrix uses YOLO11 and YOLOv8 on both detection datasets:

| Dataset | YOLO11 | YOLOv8 |
|---|---|---|
| PVEL-AD | `configs/detection/pvel_ad_yolo11l.yaml` | `configs/detection/pvel_ad_yolov8l.yaml` |
| PV-Multi-Defect | `configs/detection/pv_multi_defect_yolo11l.yaml` | `configs/detection/pv_multi_defect_yolov8l.yaml` |

The `l` size is the formal default because it is a stronger large-model baseline. The `n` size is used for local validation when compute resources are limited. All configured detection runs use early stopping with `patience: 3`, so training stops when validation quality no longer improves.

Ultralytics YOLO early stopping monitors the validation fitness score, which is primarily driven by validation mAP. In practice, this means early stopping follows whether detection quality is still improving on the validation set rather than whether training loss is still decreasing. The final report should still present the individual metrics, because a single fitness value can hide different behavior across recall, mAP50, mAP50-95, and rare-class AP.

### Detection Metrics

Detection should be evaluated with both aggregate and per-class metrics:

| Metric | What it means | How to read it |
|---|---|---|
| mAP50 | Average precision at IoU 0.50 | A broad localization and classification check. |
| mAP50-95 | Average precision across stricter IoU thresholds | Better for judging box quality and robust localization. |
| Recall | Fraction of labeled defects found | Important for defect screening because misses carry high cost. |
| Per-class AP | AP for each defect class | Required for long-tail datasets such as PVEL-AD. |
| Confusion matrix | Class-level error pattern | Shows whether visually similar defects are mixed up. |

The early-stopping metric and the reporting metrics have different roles. Early stopping chooses when to stop training. Reporting metrics explain what the trained detector is good or weak at. For example, a run may stop because overall validation fitness has plateaued, but the report should still inspect whether rare classes continue to lag behind common classes.

For PVEL-AD, the result should not be judged only by overall mAP. Long-tail classes such as rare scratches, fragments, corners, and printing errors need their own AP and recall checks. A model with good overall mAP but weak rare-class recall is not a balanced inspection model.

For PV-Multi-Defect, the important checks are whether large regions such as `no_electricity` are localized consistently and whether fine defects such as `scratch` keep acceptable recall. The dataset has visible panel defects, so qualitative review of boxes is useful, but it should support metric interpretation rather than replace it.

## ELPV Image-Level Experiments

ELPV uses image-level probability labels, so the project evaluates it with torchvision image-level models:

| Config | Model | Task | Output |
|---|---|---|---|
| `configs/elpv/resnet18_binary.yaml` | ResNet-18 | Binary classification | Normal or defective |
| `configs/elpv/swin_t_binary.yaml` | Swin-T | Binary classification | Normal or defective |
| `configs/elpv/resnet18_regression.yaml` | ResNet-18 | Regression | Defect probability |
| `configs/elpv/swin_t_regression.yaml` | Swin-T | Regression | Defect probability |

Binary classification maps probability `0.0` to normal and probability greater than `0.0` to defective. Regression keeps the original probability target.

### ELPV Metrics

| Metric | Applies to | How to read it |
|---|---|---|
| Accuracy | Binary classification | Useful as a quick check, but not enough on its own. |
| F1 | Binary classification | Balances precision and recall when class balance is uneven. |
| AUC | Binary classification | Measures ranking quality across thresholds. |
| MAE | Regression | Lower values mean predicted probabilities are closer to labels. |

ELPV results should be interpreted as image-level screening quality. They should not be compared directly with detection mAP because ELPV has no box labels. A good ELPV model gives stable whole-image scores; it does not explain exact defect location unless an additional localization or anomaly method is added.

## Deployment Evaluation

Deployment is evaluated after a trained checkpoint is exported. The project includes two export paths:

| Model type | Export script | Expected artifact |
|---|---|---|
| YOLO detector | `deployment/export_yolo.py` | ONNX, TensorRT engine, or TorchScript export |
| ELPV classifier/regressor | `deployment/export_elpv.py` | ONNX model and manifest |

Deployment checks should include:

| Check | Expected interpretation |
|---|---|
| PyTorch vs exported output | Output difference should be small enough that predictions keep the same meaning. |
| Average latency | Shows typical inference speed. |
| P95 latency | Shows tail latency under repeated inference. |
| FPS | Converts latency into throughput for production-style comparison. |
| Metric after export | Confirms speed changes do not hide quality regression. |

The deployment result should be reported as a tradeoff table: model version, input size, backend, precision mode, latency, FPS, and quality metric. A faster model is useful only when recall, mAP, F1, or MAE remains acceptable for the task.

## Engineering Interpretation

The project result is best understood as a complete inspection workflow rather than a single model benchmark:

- PVEL-AD validates EL manufacturing-defect localization and long-tail detection handling.
- PV-Multi-Defect validates visible surface-defect localization.
- ELPV validates image-level screening and probability prediction.
- Deployment export verifies that trained models can move beyond training code into inference artifacts.
- Documentation and generated galleries make the data assumptions visible and reproducible.

The most important engineering judgement is consistency: the dataset label type, model output, metric, and deployment artifact must all describe the same task. When those parts stay aligned, the project can be extended with larger models, preprocessing comparisons, ONNX Runtime checks, and TensorRT benchmarks without changing the underlying structure.
