"""PV-Multi-Defect dataset loader."""

from __future__ import annotations

from pathlib import Path

from data_tools.utils.paths import RAW_ROOT
from data_tools.utils.voc import read_voc_dataset, summarize_voc


def read_pv_multi_defect(raw_root: Path = RAW_ROOT) -> dict:
    """Read PV-Multi-Defect VOC labels and summarize its classes."""

    base = raw_root / "pv_multi_defect"
    records = read_voc_dataset(base / "Annotations", base / "JPEGImages")
    return {
        "combined": summarize_voc(records),
        "records": records,
    }
