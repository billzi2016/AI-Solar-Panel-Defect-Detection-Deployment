"""Shared dataset-loading utilities for the data tools package.

The modules under ``data_tools`` should import dataset readers from here instead
of reaching into a specific report or conversion folder.  This keeps ELPV,
PV-Multi-Defect, and PVEL-AD parsing behavior consistent across statistics,
dataset conversion, and future training-data preparation scripts.
"""

from data_tools.utils.elpv import read_elpv
from data_tools.utils.paths import PROJECT_ROOT, RAW_ROOT
from data_tools.utils.pv_multi_defect import read_pv_multi_defect
from data_tools.utils.pvel_ad import read_pvel_ad
from data_tools.utils.voc import VocImageRecord, VocObject, read_voc_dataset, summarize_voc

__all__ = [
    "PROJECT_ROOT",
    "RAW_ROOT",
    "VocImageRecord",
    "VocObject",
    "read_elpv",
    "read_pv_multi_defect",
    "read_pvel_ad",
    "read_voc_dataset",
    "summarize_voc",
]
