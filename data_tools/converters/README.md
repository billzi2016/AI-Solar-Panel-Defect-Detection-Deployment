# Dataset Converters

This directory contains data-format conversion scripts. The converters do not implement model logic. Their job is to turn downloaded public datasets into standard layouts expected by mature training libraries.

## Current Converter

`build_yolo_detection_dataset.py` converts Pascal VOC annotations from PVEL-AD or PV-Multi-Defect into an Ultralytics YOLO dataset layout:

```text
datasets/processed/yolo/<dataset_name>/
  dataset.yaml
  images/
  labels/
```

Images are linked instead of copied when the operating system allows symlinks. This keeps the processed dataset small while giving Ultralytics the directory pattern it expects.

## Commands

Build PVEL-AD:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
```

Build PV-Multi-Defect:

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

The output stays under `datasets/processed/`, which is ignored by git.
