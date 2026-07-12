"""Shared Pascal VOC parsing and summary helpers."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VocObject:
    """Single Pascal VOC bounding-box object."""

    name: str
    xmin: int
    ymin: int
    xmax: int
    ymax: int


@dataclass(frozen=True)
class VocImageRecord:
    """One image paired with its parsed Pascal VOC objects."""

    image_path: Path
    xml_path: Path
    width: int
    height: int
    objects: tuple[VocObject, ...]


def parse_voc_annotation(xml_path: Path, image_dir: Path) -> VocImageRecord | None:
    """Parse one Pascal VOC XML file and connect it to its image.

    Args:
        xml_path: Annotation XML file.
        image_dir: Directory where the image named by the XML file should live.

    Returns:
        A parsed record when the XML is usable and the referenced image exists.
        ``None`` means the file should not be counted as trainable input.
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
    """Read a Pascal VOC-style image and annotation directory pair."""

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
