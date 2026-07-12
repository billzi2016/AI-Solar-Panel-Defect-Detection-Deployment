# 数据集统计工具

本目录包含数据集统计脚本和它生成的报告文件。脚本、JSON 汇总、Markdown 报告和小尺寸图片资产放在同一个目录里，方便后续重新统计、检查和维护。

数据解析逻辑统一放在 `data_tools/utils/`。统计工具从这个公共包导入 ELPV、PV-Multi-Defect、PVEL-AD 和 Pascal VOC 工具，而不是在统计报告目录里维护一套私有 loader。

## 数据集范围

本项目使用三个公开光伏缺陷数据集，因为它们对应的问题不一样。

| 数据集 | 图像类型 | 标注类型 | 主要任务 | 模型应该输出什么 |
|---|---|---|---|---|
| ELPV Dataset | 单电池片 EL 图像 | 每张图一个缺陷概率 | 图像分类或异常打分 | 整张电池片图像的概率、类别或异常分数。 |
| PV-Multi-Defect | 带可见表面缺陷的面板图像 | Pascal VOC 目标框 | 面板级可见缺陷检测 | 缺陷区域的框坐标和类别名。 |
| PVEL-AD | 近红外 EL 电池片图像 | Pascal VOC 目标框，加正常图或辅助图 | 长尾缺陷检测和异常分析 | 缺陷框坐标和 12 类制造缺陷之一。 |

### ELPV Dataset

ELPV 用来回答“单张电池片是否看起来有缺陷”。输入是标准化后的灰度 EL 图像。它的标签不是目标框，而是缺陷概率，例如 `0.0`、`0.3333333333333333`、`0.6666666666666666` 或 `1.0`。正常的统计结果应该包含完整图片数量、可读的概率分布，以及能够正常打开的 300 x 300 电池片样例图。

### PV-Multi-Defect

PV-Multi-Defect 用来回答“可见的面板缺陷出现在什么位置”。输入是面板图像。标签是一个或多个 Pascal VOC 目标框，类别包括 `broken`、`hot_spot`、`black_border`、`scratch` 和 `no_electricity`。正常的统计结果应该能成功解析 XML，类别数量呈现真实不均衡，并且抽样图片中的缺陷类别和肉眼看到的区域基本一致。

### PVEL-AD

PVEL-AD 是本项目主要使用的长尾检测数据集。输入是光伏电池片近红外 EL 图像。已发布的框标注覆盖 12 类缺陷：`finger`、`crack`、`black_core`、`thick_line`、`horizontal_dislocation`、`short_circuit`、`vertical_dislocation`、`star_crack`、`printing_error`、`corner`、`fragment` 和 `scratch`。正常的统计结果应该显示完整图片数 36,543，trainval 和 test 子集都有已发布 VOC 标注，并且类别表里高频类和稀有类都能被单独看见。

## 它做什么

`build_dataset_report.py` 会读取本机 `datasets/raw/` 下的数据集，并生成：

| 输出 | 路径 | 作用 |
|---|---|---|
| 机器可读统计 | `dataset_stats.json` | 让后续训练或校验脚本复用同一份统计结果。 |
| 英文报告 | `dataset_report.md` | 说明数据规模、标注格式、类别分布和检查方法。 |
| 中文报告 | `dataset_report.zh.md` | 中文文档使用的同一份报告。 |
| 生成图表 | `assets/` | 从本地真实文件生成的条形图和样例拼图。 |
| 来源示例图 | `datasets/raw/...` | 少量被 allowlist 放开的原始项目图片，用于文档展示；完整数据集仍然被忽略。 |

## 原始项目图片

它们保留在 `datasets/raw/` 中，目的是让读者先看到源数据长什么样，再去看统计脚本生成的分布图和抽样拼图。

### 来自 ELPV Dataset

ELPV 项目说明中把该数据集定义为从光伏组件高分辨率电致发光图像中截取出来的太阳能电池片图像。数据集包含 2,624 张标准化后的 300 x 300 灰度样本，来源于 44 个组件。每张图都有一个 0 到 1 之间的缺陷概率标签，并标注该电池片来自单晶或多晶组件。

![ELPV 原始总览图](../../datasets/raw/elpv-dataset/doc/images/overview.jpg)

源项目说明：ELPV 的 overview 图用颜色覆盖层表示缺陷概率。红色越深，表示对应太阳能电池片存在缺陷的可能性越高。

### 来自 PV-Multi-Defect

PV-Multi-Defect 项目把面板图片放在 `JPEGImages/`，把 Pascal VOC 标注放在 `Annotations/`。源 README 中给出的五类可见缺陷示例分别是：破损区域、明显亮斑、黑色或灰色边框区域、划痕区域，以及不导电导致的黑色区域。

![PV-Multi-Defect 原始破损区域示例](../../datasets/raw/pv_multi_defect/tf1.jpg)

源项目说明：带有破损区域的光伏面板。

![PV-Multi-Defect 原始亮斑示例](../../datasets/raw/pv_multi_defect/tf2.jpg)

源项目说明：带有明显亮斑区域的光伏面板。

![PV-Multi-Defect 原始边框区域示例](../../datasets/raw/pv_multi_defect/tf3.jpg)

源项目说明：带有黑色或灰色边框区域的光伏面板。

![PV-Multi-Defect 原始划痕示例](../../datasets/raw/pv_multi_defect/tf4.jpg)

源项目说明：带有划痕区域的光伏面板。

![PV-Multi-Defect 原始不导电黑区示例](../../datasets/raw/pv_multi_defect/tf5.jpg)

源项目说明：存在不导电区域、并呈现黑色区域的光伏面板。

### 来自 PVEL-AD

PVEL-AD 项目说明中把该数据集定义为面向光伏电池片异常检测的大规模近红外 EL 数据集。它包含 36,543 张图，既有无异常样本，也有 12 类缺陷样本；已发布的框标注让它成为一个长尾目标检测任务，因为断栅等高频类远多于划痕、碎片等稀有类。

![PVEL-AD 原始项目总览图](../../datasets/raw/pvel_ad/EL2021.png)

源项目说明：PVEL-AD 将该数据集定义为光伏电池片电致发光异常检测数据集，包含无异常电池片和 12 类缺陷样本，缺陷类型包括裂纹、星状裂纹、断栅、黑芯、粗线、划痕、碎片、掉角、印刷错误、水平错位、垂直错位和短路。

![PVEL-AD 原始示例图](../../datasets/raw/pvel_ad/pvel.jpg)

源项目说明：该图用于展示 PVEL-AD 近红外 EL 图像中的光伏电池片缺陷视觉形态。本项目只把它作为源数据参考图保留；由 `build_dataset_report.py` 生成的样例拼图和类别分布图会单独放在统计报告中。

## 怎么运行

在项目根目录运行：

```bash
python3 data_tools/stats/build_dataset_report.py
```

输入是本地 ignored 的数据集目录：

```text
datasets/raw/
```

输出是当前目录：

```text
data_tools/stats/
```

如果脚本没有解析报错，`dataset_stats.json` 被更新，并且 Markdown 报告中的图片能正常显示，就说明这次统计是正常的。
