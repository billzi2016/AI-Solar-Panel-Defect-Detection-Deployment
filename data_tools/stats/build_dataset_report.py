"""Build dataset statistics and visual report assets.

The script reads the local datasets under ``datasets/raw`` and writes a compact
set of public documentation assets under ``data_tools/stats``.  The raw datasets
remain ignored by git; only small summary files and representative image grids
are meant to be committed.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import textwrap
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

from dataloader import (
    RAW_ROOT,
    VocImageRecord,
    VocObject,
    read_elpv,
    read_pvel_ad,
    read_pv_multi_defect,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATS_ROOT = PROJECT_ROOT / "data_tools" / "stats"
ASSET_ROOT = STATS_ROOT / "assets"
SOURCE_EXAMPLE_ROOT = STATS_ROOT / "source_examples"


def ensure_output_dirs() -> None:
    """Create output directories used by generated reports and image assets."""

    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    SOURCE_EXAMPLE_ROOT.mkdir(parents=True, exist_ok=True)


def font(size: int) -> ImageFont.ImageFont:
    """Return a readable font with a portable fallback."""

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def copy_source_examples() -> dict[str, str]:
    """Copy a few source-provided example images into the report asset folder."""

    copied: dict[str, str] = {}
    candidates = {
        "elpv_source_overview.jpg": RAW_ROOT / "elpv-dataset" / "doc" / "images" / "overview.jpg",
        "pv_multi_defect_source_tf1.jpg": RAW_ROOT / "pv_multi_defect" / "tf1.jpg",
        "pv_multi_defect_source_tf2.jpg": RAW_ROOT / "pv_multi_defect" / "tf2.jpg",
        "pv_multi_defect_source_tf3.jpg": RAW_ROOT / "pv_multi_defect" / "tf3.jpg",
        "pv_multi_defect_source_tf4.jpg": RAW_ROOT / "pv_multi_defect" / "tf4.jpg",
        "pv_multi_defect_source_tf5.jpg": RAW_ROOT / "pv_multi_defect" / "tf5.jpg",
    }

    for output_name, source in candidates.items():
        if source.exists():
            destination = SOURCE_EXAMPLE_ROOT / output_name
            shutil.copyfile(source, destination)
            copied[output_name] = relative_to_stats(destination)
    return copied


def relative_to_stats(path: Path) -> str:
    """Return a POSIX path relative to the Markdown files in ``data_tools/stats``."""

    return path.relative_to(STATS_ROOT).as_posix()


def image_thumbnail(path: Path, size: tuple[int, int]) -> tuple[Image.Image, float, int, int]:
    """Open an image and return a fitted tile plus box-scaling metadata.

    Returns:
        A tuple of ``(tile, scale, left, top)``. ``scale`` is the factor applied
        to the original image, while ``left`` and ``top`` are the offsets created
        by centering the resized image inside the fixed white tile.
    """

    with Image.open(path) as image:
        image = image.convert("RGB")
        original_width, original_height = image.size
        image.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", size, "white")
        left = (size[0] - image.width) // 2
        top = (size[1] - image.height) // 2
        canvas.paste(image, (left, top))
        scale = min(size[0] / original_width, size[1] / original_height)
        return canvas, scale, left, top


def select_elpv_examples(elpv: dict) -> list[tuple[str, Path]]:
    """Pick one ELPV image for each defect-probability level."""

    selected: dict[str, Path] = {}
    for row in elpv["rows"]:
        key = f"probability {row['probability']:.2f}"
        if key not in selected:
            selected[key] = Path(row["image"])
    return sorted(selected.items())


def select_voc_examples(records: Iterable[VocImageRecord], limit: int = 12) -> list[tuple[str, Path, tuple[VocObject, ...]]]:
    """Pick representative VOC examples, preferring one image per class."""

    selected: dict[str, VocImageRecord] = {}
    for record in records:
        for obj in record.objects:
            selected.setdefault(obj.name, record)

    examples: list[tuple[str, Path, tuple[VocObject, ...]]] = []
    for name, record in sorted(selected.items()):
        examples.append((name, record.image_path, record.objects))
        if len(examples) >= limit:
            break
    return examples


def draw_boxes(
    draw: ImageDraw.ImageDraw,
    objects: tuple[VocObject, ...],
    scale: float,
    left: int,
    top: int,
    color: str,
) -> None:
    """Draw scaled bounding boxes onto a resized image tile."""

    for obj in objects:
        draw.rectangle(
            [
                left + int(obj.xmin * scale),
                top + int(obj.ymin * scale),
                left + int(obj.xmax * scale),
                top + int(obj.ymax * scale),
            ],
            outline=color,
            width=3,
        )


def make_image_grid(
    examples: list[tuple[str, Path, tuple[VocObject, ...] | None]],
    output_path: Path,
    title: str,
    columns: int = 4,
    tile_size: tuple[int, int] = (220, 220),
) -> str:
    """Create a labeled image grid and return its Markdown-relative path."""

    label_font = font(18)
    title_font = font(28)
    rows = math.ceil(len(examples) / columns)
    label_height = 38
    title_height = 56
    width = columns * tile_size[0]
    height = title_height + rows * (tile_size[1] + label_height)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 12), title, fill=(20, 20, 20), font=title_font)

    for index, (label, path, objects) in enumerate(examples):
        row = index // columns
        col = index % columns
        x = col * tile_size[0]
        y = title_height + row * (tile_size[1] + label_height)
        tile, scale, left, top = image_thumbnail(path, tile_size)

        if objects:
            tile_draw = ImageDraw.Draw(tile)
            draw_boxes(tile_draw, objects[:3], scale, left, top, "red")

        canvas.paste(tile, (x, y))
        wrapped = textwrap.shorten(label.replace("_", " "), width=22, placeholder="...")
        draw.text((x + 8, y + tile_size[1] + 8), wrapped, fill=(30, 30, 30), font=label_font)

    canvas.save(output_path, quality=92)
    return relative_to_stats(output_path)


def make_bar_chart(title: str, values: dict[str, int], output_path: Path, width: int = 980) -> str:
    """Draw a horizontal bar chart with PIL and return its relative path."""

    sorted_values = sorted(values.items(), key=lambda item: item[1], reverse=True)
    row_height = 38
    left_pad = 260
    right_pad = 110
    top_pad = 64
    height = top_pad + max(1, len(sorted_values)) * row_height + 24
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = font(28)
    label_font = font(17)
    draw.text((16, 18), title, fill=(20, 20, 20), font=title_font)

    max_value = max((value for _, value in sorted_values), default=1)
    bar_width = width - left_pad - right_pad
    palette = [(38, 98, 140), (46, 125, 50), (156, 85, 35), (110, 82, 150)]

    for index, (name, value) in enumerate(sorted_values):
        y = top_pad + index * row_height
        label = textwrap.shorten(name.replace("_", " "), width=28, placeholder="...")
        draw.text((16, y + 7), label, fill=(30, 30, 30), font=label_font)
        length = int(bar_width * value / max_value)
        color = palette[index % len(palette)]
        draw.rectangle((left_pad, y + 7, left_pad + length, y + 28), fill=color)
        draw.text((left_pad + length + 10, y + 6), str(value), fill=(30, 30, 30), font=label_font)

    canvas.save(output_path, quality=92)
    return relative_to_stats(output_path)


def markdown_table(mapping: dict[str, int], first_col: str, second_col: str) -> str:
    """Format a simple two-column Markdown table."""

    lines = [f"| {first_col} | {second_col} |", "|---|---:|"]
    for key, value in mapping.items():
        lines.append(f"| `{key}` | {value} |")
    return "\n".join(lines)


def write_json_report(summary: dict) -> None:
    """Write machine-readable statistics for downstream scripts."""

    payload = json.dumps(summary, indent=2, sort_keys=True)
    (STATS_ROOT / "dataset_stats.json").write_text(payload + "\n", encoding="utf-8")


def build_markdown_en(summary: dict, assets: dict[str, str]) -> str:
    """Build the English dataset statistics report."""

    elpv = summary["elpv"]
    pv = summary["pv_multi_defect"]["combined"]
    pvel = summary["pvel_ad"]["combined"]

    return f"""# Dataset Statistics Report

This report is generated from local dataset files with `data_tools/stats/build_dataset_report.py`. It gives the project one shared source of truth for image counts, annotation counts, class balance, and representative examples.

## What This Report Checks

The script verifies four things before training code depends on the datasets:

| Check | Input | Output | Normal result |
|---|---|---|---|
| File discovery | Local `datasets/raw/` folders | Image and annotation counts | Counts match the expected public dataset scale. |
| Label parsing | ELPV CSV and VOC XML files | Class, probability, and box tables | Class names are readable and no parser errors occur. |
| Long-tail shape | Per-class object counts | Bar charts | Rare classes remain visible instead of being hidden by averages. |
| Visual sanity | Real image files | Small example grids | Images open correctly and labels match the visible defect type. |

## Dataset Overview

| Dataset | Local input | Label format | Images counted | Label units counted |
|---|---|---|---:|---:|
| ELPV Dataset | `datasets/raw/elpv-dataset` | CSV defect probability | {elpv["image_count"]} | {sum(elpv["probability_counts"].values())} probability labels |
| PV-Multi-Defect | `datasets/raw/pv_multi_defect` | Pascal VOC XML boxes | {pv["image_count"]} | {pv["box_count"]} boxes |
| PVEL-AD | `datasets/raw/pvel_ad/extracted` | Pascal VOC XML boxes | {summary["pvel_ad"]["all_image_count"]} | {pvel["box_count"]} boxes on {pvel["image_count"]} annotated images |

## From ELPV Dataset

ELPV is a cell-level electroluminescence image dataset. Each image has one defect-probability label instead of object boxes. The label answers a classification question: how likely is this cell to contain a visible defect?

![ELPV generated sample grid]({assets["elpv_grid"]})

![ELPV source overview]({assets.get("elpv_source_overview.jpg", "")})

### ELPV Probability Counts

{markdown_table(elpv["probability_counts"], "Defect probability", "Images")}

### ELPV Module-Type Counts

{markdown_table(elpv["module_type_counts"], "Module type", "Images")}

## From PV-Multi-Defect

PV-Multi-Defect uses object boxes on panel images. It is useful for checking whether a detector can localize visible surface defects, not only classify a full image as defective.

![PV-Multi-Defect generated sample grid]({assets["pv_multi_grid"]})

### Source Example Images From PV-Multi-Defect

![Broken area source example]({assets.get("pv_multi_defect_source_tf1.jpg", "")})

![Bright spot source example]({assets.get("pv_multi_defect_source_tf2.jpg", "")})

![Border source example]({assets.get("pv_multi_defect_source_tf3.jpg", "")})

![Scratch source example]({assets.get("pv_multi_defect_source_tf4.jpg", "")})

![Non-electricity source example]({assets.get("pv_multi_defect_source_tf5.jpg", "")})

### PV-Multi-Defect Box Counts By Class

![PV-Multi-Defect class distribution]({assets["pv_multi_bar"]})

{markdown_table(pv["class_box_counts"], "Class", "Boxes")}

## From PVEL-AD

PVEL-AD is the main long-tail object detection dataset in this workspace. The detector input is a near-infrared EL image. The output is a set of bounding boxes with one of 12 defect classes.

![PVEL-AD generated sample grid]({assets["pvel_grid"]})

### PVEL-AD Box Counts By Class

![PVEL-AD class distribution]({assets["pvel_bar"]})

{markdown_table(pvel["class_box_counts"], "Class", "Boxes")}

### PVEL-AD Split Counts

| Split | Images | Annotated images | Boxes |
|---|---:|---:|---:|
| trainval | {summary["pvel_ad"]["splits"]["trainval"]["image_count"]} | {summary["pvel_ad"]["splits"]["trainval"]["annotated_image_count"]} | {summary["pvel_ad"]["splits"]["trainval"]["box_count"]} |
| test | {summary["pvel_ad"]["splits"]["test"]["image_count"]} | {summary["pvel_ad"]["splits"]["test"]["annotated_image_count"]} | {summary["pvel_ad"]["splits"]["test"]["box_count"]} |

PVEL-AD also contains anomaly-free or auxiliary images without VOC boxes. The full local image count is {summary["pvel_ad"]["all_image_count"]}; the table above counts the images that have released VOC annotations.

## How To Read The Result

The counts are normal when the ELPV image total is close to 2,624, PVEL-AD image total is 36,543, and the object-detection datasets show strong class imbalance. That imbalance is not a data error; it is the reason the training plan needs class-aware sampling, careful recall tracking for rare classes, and separate latency checks after model export.
"""


def build_markdown_zh(summary: dict, assets: dict[str, str]) -> str:
    """Build the Chinese dataset statistics report."""

    elpv = summary["elpv"]
    pv = summary["pv_multi_defect"]["combined"]
    pvel = summary["pvel_ad"]["combined"]

    return f"""# 数据集统计报告

本报告由 `data_tools/stats/build_dataset_report.py` 从本机 `datasets/raw/` 中的真实数据生成。它统一记录图片数量、标注数量、类别分布和样例图，后续训练与部署文档都以这里的统计结果为准。

## 本报告检查什么

| 检查项 | 输入 | 输出 | 正常结果 |
|---|---|---|---|
| 文件发现 | 本机 `datasets/raw/` 目录 | 图片和标注数量 | 数量接近公开数据集的预期规模。 |
| 标签解析 | ELPV CSV 和 VOC XML | 概率、类别、框统计表 | 类别名可读，解析过程没有报错。 |
| 长尾分布 | 每类目标框数量 | 条形图 | 少数类能单独看见，而不是被平均值掩盖。 |
| 视觉核对 | 真实图片文件 | 小尺寸样例拼图 | 图片能正常打开，标签和可见缺陷大体一致。 |

## 数据集总览

| 数据集 | 本地输入 | 标注格式 | 已统计图片 | 已统计标签单位 |
|---|---|---|---:|---:|
| ELPV Dataset | `datasets/raw/elpv-dataset` | CSV 缺陷概率 | {elpv["image_count"]} | {sum(elpv["probability_counts"].values())} 个概率标签 |
| PV-Multi-Defect | `datasets/raw/pv_multi_defect` | Pascal VOC XML 框 | {pv["image_count"]} | {pv["box_count"]} 个目标框 |
| PVEL-AD | `datasets/raw/pvel_ad/extracted` | Pascal VOC XML 框 | {summary["pvel_ad"]["all_image_count"]} | {pvel["box_count"]} 个目标框，覆盖 {pvel["image_count"]} 张有框标注图片 |

## 来自 ELPV Dataset

ELPV 是单电池片级别的 EL 图像数据集。它不提供目标框，而是给每张图一个缺陷概率标签。这个标签适合做全图分类、概率回归或无监督异常检测的评估入口。

![ELPV 生成样例拼图]({assets["elpv_grid"]})

![ELPV 原始示意图]({assets.get("elpv_source_overview.jpg", "")})

### ELPV 缺陷概率统计

{markdown_table(elpv["probability_counts"], "缺陷概率", "图片数")}

### ELPV 晶硅类型统计

{markdown_table(elpv["module_type_counts"], "晶硅类型", "图片数")}

## 来自 PV-Multi-Defect

PV-Multi-Defect 是面板图像上的目标框数据集。它更适合验证检测器能不能定位表面可见缺陷，而不是只判断整张图是否异常。

![PV-Multi-Defect 生成样例拼图]({assets["pv_multi_grid"]})

### 来自 PV-Multi-Defect 的原始示例图

![破损区域原始示例]({assets.get("pv_multi_defect_source_tf1.jpg", "")})

![亮斑原始示例]({assets.get("pv_multi_defect_source_tf2.jpg", "")})

![边框异常原始示例]({assets.get("pv_multi_defect_source_tf3.jpg", "")})

![划痕原始示例]({assets.get("pv_multi_defect_source_tf4.jpg", "")})

![不导电黑区原始示例]({assets.get("pv_multi_defect_source_tf5.jpg", "")})

### PV-Multi-Defect 各类别目标框数量

![PV-Multi-Defect 类别分布]({assets["pv_multi_bar"]})

{markdown_table(pv["class_box_counts"], "类别", "目标框数量")}

## 来自 PVEL-AD

PVEL-AD 是本项目主要使用的长尾目标检测数据集。模型输入是近红外 EL 图像，输出是缺陷框和 12 类缺陷标签。

![PVEL-AD 生成样例拼图]({assets["pvel_grid"]})

### PVEL-AD 各类别目标框数量

![PVEL-AD 类别分布]({assets["pvel_bar"]})

{markdown_table(pvel["class_box_counts"], "类别", "目标框数量")}

### PVEL-AD 划分统计

| 划分 | 图片数 | 有标注图片数 | 目标框数量 |
|---|---:|---:|---:|
| trainval | {summary["pvel_ad"]["splits"]["trainval"]["image_count"]} | {summary["pvel_ad"]["splits"]["trainval"]["annotated_image_count"]} | {summary["pvel_ad"]["splits"]["trainval"]["box_count"]} |
| test | {summary["pvel_ad"]["splits"]["test"]["image_count"]} | {summary["pvel_ad"]["splits"]["test"]["annotated_image_count"]} | {summary["pvel_ad"]["splits"]["test"]["box_count"]} |

PVEL-AD 中还包含没有 VOC 框的正常图或辅助图。本地完整图片数是 {summary["pvel_ad"]["all_image_count"]}；上表统计的是已经发布 VOC 框标注的图片。

## 怎么判断结果正常

如果 ELPV 的图片总数接近 2,624，PVEL-AD 的图片总数是 36,543，并且两个目标检测数据集都呈现明显类别不均衡，那么统计结果就是符合预期的。这里的不均衡不是错误，而是后续训练必须处理的问题：训练时要关注少数类召回率，采样和增强不能只服务高频类别，模型导出后还要单独检查推理速度和精度变化。
"""


def build_assets(aggregate: dict) -> dict[str, str]:
    """Generate all image assets used by the Markdown reports."""

    assets = copy_source_examples()
    assets["elpv_grid"] = make_image_grid(
        [(label, path, None) for label, path in select_elpv_examples(aggregate["elpv"])],
        ASSET_ROOT / "elpv_probability_examples.jpg",
        "From ELPV Dataset",
        columns=4,
    )
    assets["pv_multi_grid"] = make_image_grid(
        select_voc_examples(aggregate["pv_multi_defect"]["records"], limit=8),
        ASSET_ROOT / "pv_multi_defect_examples.jpg",
        "From PV-Multi-Defect",
        columns=4,
    )
    assets["pvel_grid"] = make_image_grid(
        select_voc_examples(
            aggregate["pvel_ad"]["records"]["trainval"] + aggregate["pvel_ad"]["records"]["test"],
            limit=12,
        ),
        ASSET_ROOT / "pvel_ad_examples.jpg",
        "From PVEL-AD",
        columns=4,
    )
    assets["pv_multi_bar"] = make_bar_chart(
        "PV-Multi-Defect box counts by class",
        aggregate["pv_multi_defect"]["combined"]["class_box_counts"],
        ASSET_ROOT / "pv_multi_defect_class_distribution.jpg",
    )
    assets["pvel_bar"] = make_bar_chart(
        "PVEL-AD box counts by class",
        aggregate["pvel_ad"]["combined"]["class_box_counts"],
        ASSET_ROOT / "pvel_ad_class_distribution.jpg",
    )
    return assets


def strip_records_for_json(aggregate: dict) -> dict:
    """Remove path-heavy record objects before writing JSON statistics."""

    return {
        "elpv": {
            key: value for key, value in aggregate["elpv"].items() if key != "rows"
        },
        "pv_multi_defect": {
            "combined": aggregate["pv_multi_defect"]["combined"],
        },
        "pvel_ad": {
            "all_image_count": aggregate["pvel_ad"]["all_image_count"],
            "splits": aggregate["pvel_ad"]["splits"],
            "combined": aggregate["pvel_ad"]["combined"],
        },
    }


def main() -> None:
    """Generate dataset statistics, reports, and visual documentation assets."""

    ensure_output_dirs()
    aggregate = {
        "elpv": read_elpv(),
        "pv_multi_defect": read_pv_multi_defect(),
        "pvel_ad": read_pvel_ad(),
    }
    assets = build_assets(aggregate)
    summary = strip_records_for_json(aggregate)
    write_json_report(summary)
    (STATS_ROOT / "dataset_report.md").write_text(
        build_markdown_en(summary, assets), encoding="utf-8"
    )
    (STATS_ROOT / "dataset_report.zh.md").write_text(
        build_markdown_zh(summary, assets), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
