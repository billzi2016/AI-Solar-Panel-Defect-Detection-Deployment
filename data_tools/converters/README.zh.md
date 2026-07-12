# 数据集格式转换工具

本目录包含数据格式转换脚本。转换脚本不实现模型逻辑，只负责把已下载的公开数据集整理成成熟训练库需要的标准目录。

## 当前转换器

`build_yolo_detection_dataset.py` 会把 PVEL-AD 或 PV-Multi-Defect 的 Pascal VOC 标注转换成 Ultralytics YOLO 数据集结构：

```text
datasets/processed/yolo/<dataset_name>/
  dataset.yaml
  images/
  labels/
```

系统允许时，图片会使用 symlink 链接到原始数据，而不是复制一份。这样可以减少磁盘占用，同时满足 Ultralytics 期望的目录模式。

## 命令

生成 PVEL-AD：

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pvel_ad
```

生成 PV-Multi-Defect：

```bash
python3 data_tools/converters/build_yolo_detection_dataset.py --dataset pv_multi_defect
```

输出目录是 `datasets/processed/`，该目录由 `.gitignore` 忽略。
