# Datasets

This page explains how the project handles solar defect data. Downloading data is only the first step. Each step needs clear inputs and outputs that can be checked.

## PVEL-AD

PVEL-AD is an EL image dataset for photovoltaic cell anomaly detection. It works well for object detection because the annotations include defect boxes.

The input is the original images and original annotations. The processed output should be a unified dataset format, such as YOLO labels or COCO JSON. YOLO format is convenient for YOLO-style detectors. COCO format is useful for general detection evaluation tools.

In this project, PVEL-AD is used to train a multi-class defect localization model. The model should output defect boxes, classes, and confidence scores. A normal result should be judged by per-class AP and recall, not only by total mAP. Industrial datasets often have a long-tailed distribution. Frequent defects can make the total metric look good while rare defects are still missed.

## ELPV

ELPV is an EL image dataset of individual solar cells. Each image has a defect probability label, commonly `0.0`, `0.33`, `0.66`, or `1.0`.

The input is a grayscale cell image and a probability label. The output can be represented in three ways:

1. Binary classification label: normal or abnormal.
2. Four-level classification label: one class for each probability value.
3. Regression label: predict the defect probability directly.

In this project, ELPV is also used for anomaly detection. Training uses only normal samples. Inference outputs an anomaly score and an anomaly heatmap. A normal result can be checked with AUC, false positive rate on normal samples, and recall on clearly defective samples.

## PV-Multi-Defect

PV-Multi-Defect provides photovoltaic defect images and detection annotations. Its layout is often close to a VOC dataset.

The input is images and XML annotations. The processed output is a unified detection format. Conversion must check class names, image size, box coordinates, and empty annotations.

In this project, it is used to test whether the detection workflow can move to another photovoltaic defect dataset. If the same conversion, training, and evaluation scripts can handle both PVEL-AD and PV-Multi-Defect, the engineering design is not too tightly bound to one data source.

## Data checks

Every dataset should produce a validation report before training. The report should include image counts, size distribution, class distribution, missing labels, out-of-bound boxes, duplicate images, and corrupted images.

The input is raw data under `datasets/raw/`. The output is a Markdown report and visualization images. A normal report should answer two questions: whether the training scripts can read the data, and whether the data distribution will affect model evaluation.
