"""PVEL-AD dataset loader."""

from __future__ import annotations

from pathlib import Path

from data_tools.utils.paths import RAW_ROOT
from data_tools.utils.voc import VocImageRecord, read_voc_dataset, summarize_voc


def read_pvel_ad(raw_root: Path = RAW_ROOT) -> dict:
    """Read PVEL-AD trainval and released test annotations.

    PVEL-AD stores test images under the extracted dataset folder, while the
    released test XML files are extracted into a separate ``test_annotation``
    folder.  This function captures that layout in one place so later scripts do
    not silently miss the test labels.
    """

    base = raw_root / "pvel_ad" / "extracted" / "solar_cell_EL_image" / "PVELAD" / "EL2021"
    test_annotation_dir = raw_root / "pvel_ad" / "extracted" / "test_annotation" / "test"
    split_records: dict[str, list[VocImageRecord]] = {}

    split_records["trainval"] = read_voc_dataset(
        base / "trainval" / "Annotations",
        base / "trainval" / "JPEGImages",
    )
    split_records["test"] = read_voc_dataset(
        test_annotation_dir,
        base / "test" / "JPEGImages",
    )

    all_records = split_records["trainval"] + split_records["test"]
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}
    all_image_count = sum(
        1
        for path in base.rglob("*")
        if path.is_file() and path.suffix.lower() in image_extensions
    )
    return {
        "all_image_count": all_image_count,
        "splits": {
            split: summarize_voc(records) for split, records in split_records.items()
        },
        "combined": summarize_voc(all_records),
        "records": split_records,
    }
