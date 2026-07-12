# ELPV Experiments

ELPV has image-level defect probability labels, not bounding boxes. It should be evaluated with image-level models rather than YOLO detectors.

The input to this experiment is one 300 x 300 electroluminescence cell crop and its metadata row from `labels.csv`. The output is either a binary defect decision or a continuous defect-probability estimate, depending on the config. This keeps ELPV separate from PVEL-AD and PV-Multi-Defect, because those two datasets can train object detectors while ELPV cannot provide box supervision.

## Implemented Models

The current deep learning experiments use torchvision architectures:

| Model | Config | Task |
|---|---|---|
| ResNet-18 | `configs/elpv/resnet18_binary.yaml` | Binary classification: `probability > 0` |
| Swin-T | `configs/elpv/swin_t_binary.yaml` | Binary classification: `probability > 0` |
| ResNet-18 | `configs/elpv/resnet18_regression.yaml` | Defect-probability regression |
| Swin-T | `configs/elpv/swin_t_regression.yaml` | Defect-probability regression |

## How The Runner Works

`run_torchvision.py` reads a flat YAML config, loads ELPV rows through `labels.csv`, splits the rows into train and validation partitions, and trains one torchvision model. It uses torchvision instead of a custom implementation so the experiment depends on maintained model definitions and standard preprocessing behavior.

For `task: binary`, the target is `0` when the original probability is `0.0` and `1` when the probability is greater than zero. The model head has two output logits, and validation reports accuracy, F1, and AUC. F1 is the early-stopping score because the positive class is not perfectly balanced.

For `task: regression`, the target is the original probability value. The model head has one output value, and validation reports mean absolute error. Lower MAE means the predicted defect probability is closer to the label.

ResNet-18 is the convolutional baseline. It is small enough to run locally and gives a stable reference for image-level classification. Swin-T is the transformer baseline. It has stronger global context modeling, which can help when defect evidence is distributed across the cell image, but it costs more memory and runtime.

## Inputs And Outputs

| Item | Path or value | Meaning |
|---|---|---|
| Dataset root | `datasets/raw/elpv-dataset` | Local ELPV checkout, ignored by git except selected documentation images. |
| Label file | `labels.csv` inside the dataset package data | Provides image path, defect probability, and module type. |
| Configs | `configs/elpv/*.yaml` | Choose model, task, image size, batch size, learning rate, and early stopping patience. |
| Best checkpoint | `outputs/elpv/<config-name>/best.pt` | Model weights from the best validation epoch. |
| Metrics | `outputs/elpv/<config-name>/metrics.json` | Config, best epoch, and per-epoch validation metrics. |

The run is normal when `metrics.json` is created, `best_epoch` is greater than zero, and the validation metric moves in the expected direction: higher F1/AUC for binary classification or lower MAE for regression. If AUC is `NaN`, the validation split likely has only one class and the split configuration should be checked.

## Commands

```bash
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_binary.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/swin_t_binary.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_regression.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/swin_t_regression.yaml
```

Outputs are written to `outputs/elpv/`, which is ignored by git.
