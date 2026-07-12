# Data Loading Utilities

This directory is the shared dataloader layer for the whole `data_tools` package. Other modules should import from the package entry point:

```python
from data_tools.utils import read_elpv, read_pv_multi_defect, read_pvel_ad
```

Do not import from `data_tools.stats` to load data. The statistics report is only one consumer of this layer.

## Module Layout

| Module | Responsibility |
|---|---|
| `__init__.py` | Public import surface for loaders, paths, and VOC records. |
| `paths.py` | Shared project and raw-dataset paths. |
| `voc.py` | Pascal VOC XML parsing and summary helpers. |
| `elpv.py` | ELPV CSV and image-label loader. |
| `pv_multi_defect.py` | PV-Multi-Defect VOC loader. |
| `pvel_ad.py` | PVEL-AD VOC loader, including the separate released test-annotation path. |

## Expected Use

The input is the ignored local dataset tree under `datasets/raw/`. The output is Python dictionaries and `VocImageRecord` objects that downstream scripts can use for reporting, conversion, sampling, or training-data preparation.
