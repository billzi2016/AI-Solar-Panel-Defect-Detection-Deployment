"""Dataset loading and annotation-summary utilities.

This module is the shared data-access layer for local solar-defect datasets.
Report generation, training preparation, and future validation scripts should
import these functions instead of parsing ELPV CSV files or Pascal VOC XML files
again.  Keeping one loader prevents quiet count mismatches between documents and
model code.
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "datasets" / "raw"


@dataclass(frozen=True)
class VocObject:
    """Single Pascal VOC bounding-box object.

    Attributes:
        name: Defect class name from the XML ``object/name`` field.
        xmin: Left pixel coordinate of the box.
        ymin: Top pixel coordinate of the box.
        xmax: Right pixel coordinate of the box.
        ymax: Bottom pixel coordinate of the box.
    """

    name: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int


@dataclass(frozen=True)
class VocImageRecord:
    """One image paired with its parsed Pascal VOC objects.

    The record keeps both image and XML paths so later tools can generate visual
    examples, run integrity checks, or convert annotations to detector-specific
    formats without reparsing directory layouts.
    """

    image_path: Path
    xml_path: Path
    width: int
    height: int
    objects: tuple[VocObject, ...]


def read_elpv(raw_root: Path = RAW_ROOT) -> dict:
    """Read ELPV labels and return image, probability, and module-type counts.

    Args:
        raw_root: Root directory that contains the downloaded dataset folders.

    Returns:
        A dictionary with image count, probability counts, module-type counts,
        and per-image rows.  The rows are kept because report generation uses
        them to sample real examples for visual inspection.
    """

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


def parse_voc_annotation(xml_path: Path, image_dir: Path) -> VocImageRecord | None:
    """Parse one Pascal VOC XML file and connect it to its image.

    Args:
        xml_path: Annotation XML file.
        image_dir: Directory where the image named by the XML file should live.

    Returns:
        A ``VocImageRecord`` when both the XML and referenced image are usable.
        ``None`` is returned for incomplete XML or missing image files so callers
        can count only records that are ready for training or inspection.
    """

    root = ET.parse(xml_path).getroot()
    filename = root.findtext("filename")
    size = root.find("size")
    if filename is None or size is None:
        return None

    width = int(size.findtext("width", "0"))
    height = int(size.findtext("height", "0"))
    objects: list[VocObject] = []

    for obj in root.findall("object"):
        name = obj.findtext("name", "unknown").strip()
        box = obj.find("bndbox")
        if box is None:
            continue
        objects.append(
            VocObject(
                name=name,
                xmin=int(float(box.findtext("xmin", "0"))),
                ymin=int(float(box.findtext("ymin", "0"))),
                xmax=int(float(box.findtext("xmax", "0"))),
                ymax=int(float(box.findtext("ymax", "0"))),
            )
        )

    image_path = image_dir / filename
    if not image_path.exists():
        return None

    return VocImageRecord(
        image_path=image_path,
        xml_path=xml_path,
        width=width,
        height=height,
        objects=tuple(objects),
    )


def read_voc_dataset(annotation_dir: Path, image_dir: Path) -> list[VocImageRecord]:
    """Read a Pascal VOC-style image and annotation directory pair.

    Args:
        annotation_dir: Directory containing ``*.xml`` annotation files.
        image_dir: Directory containing images referenced by those XML files.

    Returns:
        Parsed records with existing image files.  The order is stable because
        XML paths are sorted before parsing.
    """

    records: list[VocImageRecord] = []
    for xml_path in sorted(annotation_dir.glob("*.xml")):
        record = parse_voc_annotation(xml_path, image_dir)
        if record is not None:
            records.append(record)
    return records


def summarize_voc(records: list[VocImageRecord]) -> dict:
    """Create object, image, and shape statistics for parsed VOC records."""

    class_boxes: Counter[str] = Counter()
    images_by_class: dict[str, set[str]] = defaultdict(set)
    object_count_per_image: Counter[str] = Counter()
    dimensions: Counter[str] = Counter()

    for record in records:
        dimensions[f"{record.width}x{record.height}"] += 1
        object_count_per_image[str(len(record.objects))] += 1
        for obj in record.objects:
            class_boxes[obj.name] += 1
            images_by_class[obj.name].add(str(record.image_path))

    return {
        "image_count": len(records),
        "annotated_image_count": sum(1 for record in records if record.objects),
        "box_count": sum(class_boxes.values()),
        "class_box_counts": dict(sorted(class_boxes.items())),
        "class_image_counts": {
            name: len(paths) for name, paths in sorted(images_by_class.items())
        },
        "objects_per_image": dict(
            sorted(object_count_per_image.items(), key=lambda item: int(item[0]))
        ),
        "image_dimensions": dict(sorted(dimensions.items())),
    }


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


def read_pv_multi_defect(raw_root: Path = RAW_ROOT) -> dict:
    """Read PV-Multi-Defect VOC labels and summarize its classes."""

    base = raw_root / "pv_multi_defect"
    records = read_voc_dataset(base / "Annotations", base / "JPEGImages")
    return {
        "combined": summarize_voc(records),
        "records": records,
    }
