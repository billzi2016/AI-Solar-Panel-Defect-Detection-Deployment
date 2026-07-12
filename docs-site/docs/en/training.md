# Training

The training workflow should make each experiment reproducible. Training scripts should not depend on manual code edits. They should read data paths, model type, input size, and training settings from configuration files.

## Detection training

The input for detection training includes images, detection annotations, and a data configuration. Each defect box needs a class and coordinates.

The training script reads the data configuration, loads a YOLO model, and updates weights on the training set. The output includes the best weights, training logs, validation metrics, and prediction visualizations.

A normal training run can be checked with four signals:

1. The loss decreases.
2. Validation mAP rises and stabilizes.
3. Per-class recall is reasonable.
4. Prediction images roughly match the ground truth defect locations.

If total mAP is high but recall for rare classes is close to zero, the model has not solved the long-tail problem.

## Classification training

The input for classification training is a set of images and image-level labels. ELPV can be prepared as a binary classification, four-class classification, or regression task.

Binary classification is useful for quick normal or abnormal screening. Four-class classification is useful for defect severity levels. Regression is useful when the output should be a continuous defect score.

The output includes model weights, a confusion matrix, F1, AUC, and a list of error cases. A normal result should explain which grades the model confuses, not only report one accuracy number.

## Anomaly detection training

Anomaly detection training uses only normal samples. The input is a normal training set and a validation set for threshold selection. The output is an anomaly detection model, anomaly score distributions, and heatmaps.

The result should be checked on normal and defective samples together. If normal samples receive high scores, the model will produce many false positives. If defective samples also receive low scores, the model has not learned a useful normal pattern.

## Experiment records

Each training run should record the model, data version, input size, random seed, main parameters, and metrics. The output can be a Markdown table or a JSON file.

This matters because a better experiment must be explainable. If it cannot be reproduced, it should not be treated as a reliable conclusion.
