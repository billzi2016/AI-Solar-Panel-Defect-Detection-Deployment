# ELPV 实验

ELPV 只有图像级缺陷概率标签，没有目标框。因此它应该使用图像级模型评估，而不是 YOLO 检测器。

本实验的输入是一张 300 x 300 的电致发光电池片裁剪图，以及 `labels.csv` 中对应的标签行。输出可以是二分类缺陷判断，也可以是连续的缺陷概率估计，具体由配置文件决定。这样可以把 ELPV 和 PVEL-AD、PV-Multi-Defect 分开：后两个数据集有目标框，可以训练检测器；ELPV 没有框标注，不能直接做 YOLO 检测训练。

## 已实现模型

当前深度学习实验使用 torchvision 架构：

| 模型 | 配置 | 任务 |
|---|---|---|
| ResNet-18 | `configs/elpv/resnet18_binary.yaml` | 二分类：`probability > 0` |
| Swin-T | `configs/elpv/swin_t_binary.yaml` | 二分类：`probability > 0` |
| ResNet-18 | `configs/elpv/resnet18_regression.yaml` | 缺陷概率回归 |
| Swin-T | `configs/elpv/swin_t_regression.yaml` | 缺陷概率回归 |

## Runner 怎么工作

`run_torchvision.py` 会读取一个扁平 YAML 配置，从 ELPV 的 `labels.csv` 读取样本行，划分 train 和 validation，再训练一个 torchvision 模型。这里使用 torchvision，而不是自己实现 ResNet 或 Swin，是为了复用维护稳定的模型定义和标准预处理方式。

当 `task: binary` 时，原始概率等于 `0.0` 的样本作为 `0`，原始概率大于 `0.0` 的样本作为 `1`。模型头输出两个 logits，验证指标包括 accuracy、F1 和 AUC。早停使用 F1，因为正负样本不是完全均衡的。

当 `task: regression` 时，目标值就是原始缺陷概率。模型头输出一个连续值，验证指标是 MAE。MAE 越低，说明预测出的缺陷概率越接近标签。

ResNet-18 是卷积基线。它足够小，适合本机先跑通，并且能给图像级分类一个稳定参考。Swin-T 是 transformer 基线。它对全局上下文建模更强，适合观察分散在电池片不同位置的缺陷线索，但显存和运行时间成本更高。

## 输入和输出

| 项目 | 路径或取值 | 含义 |
|---|---|---|
| 数据集根目录 | `datasets/raw/elpv-dataset` | 本地 ELPV checkout，除少量文档展示图外不进入 Git。 |
| 标签文件 | 数据集包数据中的 `labels.csv` | 提供图片路径、缺陷概率和组件类型。 |
| 配置文件 | `configs/elpv/*.yaml` | 选择模型、任务、图像尺寸、batch、学习率和 early stopping patience。 |
| 最优权重 | `outputs/elpv/<config-name>/best.pt` | 验证集表现最好 epoch 的模型权重。 |
| 指标文件 | `outputs/elpv/<config-name>/metrics.json` | 保存配置、最优 epoch 和每轮验证指标。 |

正常结果应该包含 `metrics.json`，`best_epoch` 应该大于 0，并且验证指标的方向合理：二分类看 F1/AUC 是否提高，回归看 MAE 是否降低。如果 AUC 是 `NaN`，通常说明 validation 划分里只有一个类别，需要检查划分和标签分布。

## 命令

运行 ResNet-18 的两个 ELPV 任务：

```bash
./experiments/elpv/run_all_elpv_resnet.sh
```

运行 Swin-T 的两个 ELPV 任务：

```bash
./experiments/elpv/run_all_elpv_swin.sh
```

这两个脚本仍然调用同一个 runner 和上面列出的同一批配置文件。它们只减少重复命令；模型、数据划分、优化器、指标和输出路径仍然来自 YAML 配置和 `run_torchvision.py`。

需要指定后端时，可以设置 `DEVICE=mps`、`DEVICE=cpu` 或 `DEVICE=cuda:0`：

```bash
DEVICE=mps ./experiments/elpv/run_all_elpv_resnet.sh
```

直接运行单个配置：

```bash
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_binary.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_binary.yaml --device mps
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_binary.yaml --epochs 1 --name elpv_resnet18_binary_smoke
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/swin_t_binary.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/resnet18_regression.yaml
python3 experiments/elpv/run_torchvision.py train --config configs/elpv/swin_t_regression.yaml
```

输出写入 `outputs/elpv/`，该目录由 `.gitignore` 忽略。
