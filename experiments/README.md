# Experiments

This directory explains how experiments are organized and why each dataset uses a different task setup.

## Dataset To Experiment Mapping

The three datasets are not interchangeable because their labels answer different questions.

| Dataset | Label type | Correct experiment type | Why |
|---|---|---|---|
| PVEL-AD | Bounding boxes for 12 EL defect classes | Object detection | The label says where each defect is and which class it belongs to. |
| PV-Multi-Defect | Bounding boxes for visible panel defects | Object detection | The label also provides defect locations, so it can use the same YOLO pipeline. |
| ELPV | One defect probability per cell image | Classification, regression, or anomaly detection | There are no boxes, so a detector cannot learn defect locations from this dataset. |

## Current Detection Experiments

The current implemented experiment track is object detection with Ultralytics YOLO. It is used for datasets that have bounding boxes.

The YOLO experiment matrix has four full-training combinations:

| Dataset | YOLO11 script | YOLOv8 script |
|---|---|---|
| PVEL-AD | `./experiments/detection/yolo_train/train_yolo11_pvel_ad.sh` | `./experiments/detection/yolo_train/train_yolov8_pvel_ad.sh` |
| PV-Multi-Defect | `./experiments/detection/yolo_train/train_yolo11_pv_multi_defect.sh` | `./experiments/detection/yolo_train/train_yolov8_pv_multi_defect.sh` |

PVEL-AD is the main EL defect detection experiment because it has 12 long-tail defect classes. PV-Multi-Defect is the second detection experiment because it also has bounding boxes, but its images and defect classes describe visible panel-level defects.

## ELPV Experiment Track

ELPV should not be forced into the YOLO detector because it has image-level probability labels instead of boxes. The correct experiments for ELPV are:

- Classification: predict normal, suspicious, or defective from the full cell image.
- Regression: predict the defect probability value directly.
- Anomaly detection: learn normal cell texture and score images or regions that deviate from normal.

That track should use a mature library or standard PyTorch image-classification pipeline rather than a custom detector.

## Smoke Checks

Smoke checks belong under `tests/smoke/`. They are short checks for data paths and command wiring, not full experiments:

```bash
./tests/smoke/test_yolo_detection_pipeline.sh
```
