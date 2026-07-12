"""ELPV dataset loader."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from data_tools.utils.paths import RAW_ROOT


def read_elpv(raw_root: Path = RAW_ROOT) -> dict:
    """Read ELPV labels and return image, probability, and module-type counts."""

    data_dir = raw_root / "elpv-dataset" / "src" / "elpv_dataset" / "data"
    labels_path = data_dir / "labels.csv"
    rows: list[dict] = []
    probability_counter: Counter[str] = Counter()
    module_counter: Counter[str] = Counter()

    with labels_path.open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter=" ")
        for raw_row in reader:
            row = [cell for cell in raw_row if cell]
            if len(row) != 3:
                continue
            image_rel, probability, module_type = row
            image_path = data_dir / image_rel
            rows.append(
                {
                    "image": str(image_path),
                    "probability": float(probability),
                    "module_type": module_type,
                }
            )
            probability_counter[probability] += 1
            module_counter[module_type] += 1

    return {
        "image_count": len(rows),
        "probability_counts": dict(sorted(probability_counter.items())),
        "module_type_counts": dict(sorted(module_counter.items())),
        "rows": rows,
    }
