# Detection Experiments

This directory contains experiment entry points for object detection. The project uses Ultralytics YOLO for model training, validation, prediction, and export. The local code prepares datasets and calls the library; it does not implement a custom detector.

## Workflow

1. Convert a downloaded VOC-style dataset to YOLO layout.
2. Run a small smoke training job to verify the data path and labels.
3. Run a longer training job only after the smoke job succeeds.
4. Validate the trained checkpoint.
5. Export the checkpoint to ONNX for deployment checks.

## Prepare Data

PVEL-AD:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
```

PV-Multi-Defect:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

## Smoke Training

The smoke run is intentionally short. It checks that Ultralytics can read images, parse labels, create batches, and write outputs.

```bash
python3 experiments/detection/run_yolo.py train --data datasets/processed/yolo/pvel_ad/dataset.yaml --epochs 1 --imgsz 640 --model yolov8n.pt --name pvel_ad_smoke
```

## Validation

```bash
python3 experiments/detection/run_yolo.py val --data datasets/processed/yolo/pvel_ad/dataset.yaml --model outputs/detection/pvel_ad_smoke/weights/best.pt
```

## Export

```bash
python3 experiments/detection/run_yolo.py export --model outputs/detection/pvel_ad_smoke/weights/best.pt --format onnx
```

Outputs are written under `outputs/detection/`, which is ignored by git.
