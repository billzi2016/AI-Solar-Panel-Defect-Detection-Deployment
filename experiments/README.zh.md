# 实验说明

本目录说明实验怎么组织，以及为什么三个数据集不能用同一种实验方式硬套。

## 数据集和实验类型的对应关系

三个数据集的标注回答的问题不同，所以不能互相替代。

| 数据集 | 标注类型 | 正确实验类型 | 原因 |
|---|---|---|---|
| PVEL-AD | 12 类 EL 缺陷目标框 | 目标检测 | 标注说明每个缺陷在哪里，以及属于哪一类。 |
| PV-Multi-Defect | 可见面板缺陷目标框 | 目标检测 | 标注同样提供缺陷位置，所以可以复用 YOLO 检测流程。 |
| ELPV | 每张电池片一个缺陷概率 | 分类、回归或异常检测 | 它没有目标框，检测器无法从这个数据集学习缺陷位置。 |

## 当前检测实验

当前已经实现的是 Ultralytics YOLO 目标检测实验。它适用于带目标框的数据集。

YOLO 实验矩阵包含 4 个完整训练组合：

| 数据集 | YOLO11 脚本 | YOLOv8 脚本 |
|---|---|---|
| PVEL-AD | `./experiments/detection/yolo_train/train_yolo11_pvel_ad.sh` | `./experiments/detection/yolo_train/train_yolov8_pvel_ad.sh` |
| PV-Multi-Defect | `./experiments/detection/yolo_train/train_yolo11_pv_multi_defect.sh` | `./experiments/detection/yolo_train/train_yolov8_pv_multi_defect.sh` |

PVEL-AD 是主要 EL 缺陷检测实验，因为它包含 12 类长尾缺陷。PV-Multi-Defect 是第二个检测实验，因为它同样有目标框，但图像和类别描述的是面板级可见缺陷。

## ELPV 实验路线

ELPV 不应该硬塞进 YOLO 检测器，因为它只有图像级概率标签，没有目标框。ELPV 正确的实验路线是：

- 分类：输入整张电池片图像，预测正常、可疑或异常。
- 回归：直接预测缺陷概率值。
- 异常检测：学习正常电池片纹理，再给偏离正常模式的图像或区域打分。

这条路线后续应该使用成熟库或标准 PyTorch 图像分类流程，不写自定义检测器。

## 短链路检查

短链路检查放在 `tests/smoke/`。它们只验证数据路径和命令串联，不是完整实验：

```bash
./tests/smoke/test_yolo_detection_pipeline.sh
```
