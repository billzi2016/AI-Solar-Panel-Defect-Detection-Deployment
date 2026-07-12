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
| 来源示例图 | `source_examples/` | 从原数据集仓库复制的少量代表图，用于文档展示。 |

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
