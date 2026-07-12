# 实验报告

本报告总结光伏缺陷检测项目的实验设计、评估口径和部署解释方式。项目使用公开数据集复现光伏视觉检测中常见的工程流程：数据审计、按任务选择模型、训练、评估、导出和部署检查。

## 范围

项目按标注类型拆分数据集，而不是把所有数据硬塞进同一种模型。

| 数据集 | 标注类型 | 实验路线 | 模型族 |
|---|---|---|---|
| PVEL-AD | EL 电池片缺陷框 | 制造缺陷检测 | YOLO11 和 YOLOv8 |
| PV-Multi-Defect | 可见面板缺陷框 | 表面缺陷检测 | YOLO11 和 YOLOv8 |
| ELPV | 每张电池片一个概率标签 | 图像级分类或回归 | ResNet-18 和 Swin-T |

这样拆分是必要的，因为模型输出必须和标注形式一致。检测模型需要目标框，分类模型需要图像级标签，回归模型需要连续目标值。如果把这些任务混在一起，指标会变得难解释，也容易掩盖真正的失败模式。

## 数据审计

训练前，数据流水线先检查数据形态和标签质量：

| 检查项 | 检查内容 | 为什么重要 |
|---|---|---|
| 图片数量 | `datasets/raw/` 下的本地文件 | 确认本地数据树足够完整。 |
| 标签解析 | ELPV CSV 行和 Pascal VOC XML | 确认标签能被读取，不会静默丢样本。 |
| 类别分布 | 每类目标框数量 | 暴露长尾类别，避免只看平均指标。 |
| 视觉核对 | 真实框样例拼图 | 确认标注框落在合理缺陷区域。 |

生成数据报告的命令：

```bash
python3 data_tools/stats/build_dataset_report.py
```

正常的数据审计结果应该包含可读类别名、非空检测标注数量、明显的长尾分布，以及红框和可见缺陷区域基本一致的样例图。

## 检测实验

PVEL-AD 和 PV-Multi-Defect 转换成 YOLO 格式后，复用同一套检测流水线。

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

正式检测矩阵使用 YOLO11 和 YOLOv8，覆盖两个检测数据集：

| 数据集 | YOLO11 | YOLOv8 |
|---|---|---|
| PVEL-AD | `configs/detection/pvel_ad_yolo11l.yaml` | `configs/detection/pvel_ad_yolov8l.yaml` |
| PV-Multi-Defect | `configs/detection/pv_multi_defect_yolo11l.yaml` | `configs/detection/pv_multi_defect_yolov8l.yaml` |

`l` 尺寸作为正式默认配置，因为它是更强的大模型 baseline。`n` 尺寸用于本机资源有限时做链路验证。检测配置都使用 `patience: 3` early stopping，验证指标不再改善时停止训练。

Ultralytics YOLO 的 early stopping 监控验证集 fitness 分数，这个分数主要由验证集 mAP 驱动。也就是说，早停看的是验证集检测质量是否还在改善，而不是只看训练 loss 是否继续下降。最终报告仍然应该拆开看各项指标，因为单个 fitness 分数可能掩盖 Recall、mAP50、mAP50-95 和稀有类 AP 的差异。

### 检测指标

检测结果应该同时看整体指标和每类指标：

| 指标 | 含义 | 怎么理解 |
|---|---|---|
| mAP50 | IoU 0.50 下的平均精度 | 检查定位和分类是否基本可用。 |
| mAP50-95 | 多个更严格 IoU 阈值下的平均精度 | 更能反映框质量和定位稳定性。 |
| Recall | 真实缺陷中被找到的比例 | 缺陷筛查中漏检成本高，所以很重要。 |
| Per-class AP | 每个缺陷类别的 AP | PVEL-AD 这种长尾数据集必须单独看。 |
| Confusion matrix | 类别级错误模式 | 判断相似缺陷是否互相混淆。 |

早停指标和报告指标的作用不同。早停用来决定什么时候停止训练；报告指标用来解释模型强在哪里、弱在哪里。例如整体 validation fitness 已经平台期时，训练会停止，但报告仍然要检查稀有类别是否明显落后于高频类别。

PVEL-AD 不能只看整体 mAP。划痕、碎片、掉角、印刷错误等稀有类需要单独看 AP 和 Recall。整体 mAP 好但稀有类召回弱，不是一个均衡的检测模型。

PV-Multi-Defect 需要关注大区域缺陷和细小缺陷两类情况：`no_electricity` 这类大区域是否定位稳定，`scratch` 这类细缺陷是否保持足够召回。可视化框可以辅助判断，但不能替代指标。

## ELPV 图像级实验

ELPV 只有图像级概率标签，所以项目使用 torchvision 图像级模型：

| 配置 | 模型 | 任务 | 输出 |
|---|---|---|---|
| `configs/elpv/resnet18_binary.yaml` | ResNet-18 | 二分类 | 正常或缺陷 |
| `configs/elpv/swin_t_binary.yaml` | Swin-T | 二分类 | 正常或缺陷 |
| `configs/elpv/resnet18_regression.yaml` | ResNet-18 | 回归 | 缺陷概率 |
| `configs/elpv/swin_t_regression.yaml` | Swin-T | 回归 | 缺陷概率 |

二分类任务把概率 `0.0` 映射为正常，把大于 `0.0` 的概率映射为缺陷。回归任务保留原始概率标签。

### ELPV 指标

| 指标 | 适用任务 | 怎么理解 |
|---|---|---|
| Accuracy | 二分类 | 可以快速检查整体正确率，但不能单独使用。 |
| F1 | 二分类 | 在类别不完全均衡时同时考虑 precision 和 recall。 |
| AUC | 二分类 | 衡量不同阈值下的排序能力。 |
| MAE | 回归 | 越低表示预测概率越接近标签。 |

ELPV 结果应该理解为图像级筛查能力。它不能和检测 mAP 直接比较，因为 ELPV 没有框标注。好的 ELPV 模型应该给出稳定的整图分数；如果要解释具体位置，还需要额外的定位或异常检测方法。

## 部署评估

部署评估发生在 checkpoint 导出之后。项目包含两条导出路径：

| 模型类型 | 导出脚本 | 预期产物 |
|---|---|---|
| YOLO 检测器 | `deployment/export_yolo.py` | ONNX、TensorRT engine 或 TorchScript |
| ELPV 分类/回归模型 | `deployment/export_elpv.py` | ONNX 模型和 manifest |

部署检查应包含：

| 检查项 | 解释方式 |
|---|---|
| PyTorch 和导出模型输出差异 | 差异应足够小，预测含义保持一致。 |
| 平均延迟 | 表示典型推理速度。 |
| P95 延迟 | 表示重复推理下的尾部延迟。 |
| FPS | 把延迟转换成吞吐量，便于横向比较。 |
| 导出后指标 | 确认速度变化没有掩盖质量下降。 |

部署结果适合整理成 tradeoff 表：模型版本、输入尺寸、推理后端、精度模式、延迟、FPS 和任务质量指标。速度更快只有在 Recall、mAP、F1 或 MAE 仍然满足任务要求时才有意义。

## 工程解释

这个项目更适合理解成一套完整检测流程，而不是单个模型 benchmark：

- PVEL-AD 验证 EL 制造缺陷定位和长尾检测处理。
- PV-Multi-Defect 验证可见表面缺陷定位。
- ELPV 验证图像级筛查和概率预测。
- 部署导出验证训练后的模型能进入推理产物形态。
- 文档和生成图让数据假设可见、可复现。

最重要的工程判断是保持一致性：数据集标注类型、模型输出、评估指标和部署产物必须描述同一个任务。只要这几部分对齐，后续继续扩展更大模型、前处理对比、ONNX Runtime 检查和 TensorRT benchmark，都不需要改变项目结构。
