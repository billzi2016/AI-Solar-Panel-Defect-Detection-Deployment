# 数据读取工具

本目录是整个 `data_tools` 包共享的 dataloader 层。其他模块应该从统一入口导入：

```python
from data_tools.utils import read_elpv, read_pv_multi_defect, read_pvel_ad
```

不要从 `data_tools.stats` 里读取数据。统计报告只是这个公共层的一个调用方。

## 模块结构

| 模块 | 职责 |
|---|---|
| `__init__.py` | 对外暴露 loader、路径和 VOC 记录类型。 |
| `paths.py` | 共享项目路径和原始数据集路径。 |
| `voc.py` | Pascal VOC XML 解析和统计工具。 |
| `elpv.py` | ELPV CSV 和图像标签读取。 |
| `pv_multi_defect.py` | PV-Multi-Defect VOC 读取。 |
| `pvel_ad.py` | PVEL-AD VOC 读取，包括单独发布的测试集标注路径。 |

## 预期用法

输入是 ignored 的本地数据集目录 `datasets/raw/`。输出是 Python 字典和 `VocImageRecord` 对象，后续报告、格式转换、采样或训练数据准备脚本都可以复用。
