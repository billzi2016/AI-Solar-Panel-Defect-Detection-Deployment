"""Build the README overview gallery from real local samples.

本文件的意图：生成 README 顶部使用的总览 JPG。它读取 `datasets/raw/`
中的真实样本和真实标签，只做抽样、拼图、重绘真实 VOC 框和排版，
保证 README 总览图可以由本地数据复现。
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = PROJECT_ROOT / "assets" / "diagrams" / "readme_dataset_gallery.jpg"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_tools.utils import VocImageRecord, VocObject, read_elpv, read_pv_multi_defect, read_pvel_ad  # noqa: E402


@dataclass(frozen=True)
class GalleryTile:
    """README 总览图中的一个真实样本格子。"""

    title: str
    subtitle: str
    image_path: Path
    objects: tuple[VocObject, ...] = ()


@dataclass(frozen=True)
class GalleryRow:
    """README 总览图中的一整行维度。"""

    title: str
    description: str
    tiles: tuple[GalleryTile, ...]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """返回可读字体；系统字体不可用时退回 PIL 默认字体。"""

    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def fit_image(path: Path, size: tuple[int, int]) -> tuple[Image.Image, float, int, int]:
    """把真实图片缩放到固定格子中，并返回缩放比例和偏移。"""

    with Image.open(path) as image:
        image = image.convert("RGB")
        original_width, original_height = image.size
        image.thumbnail(size, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", size, (247, 248, 248))
        left = (size[0] - image.width) // 2
        top = (size[1] - image.height) // 2
        canvas.paste(image, (left, top))
        scale = min(size[0] / original_width, size[1] / original_height)
        return canvas, scale, left, top


def draw_scaled_boxes(
    draw: ImageDraw.ImageDraw,
    objects: tuple[VocObject, ...],
    scale: float,
    left: int,
    top: int,
) -> None:
    """按真实 VOC 坐标把标注框画到缩放后的图片上。"""

    for obj in objects[:4]:
        draw.rectangle(
            (
                left + int(obj.xmin * scale),
                top + int(obj.ymin * scale),
                left + int(obj.xmax * scale),
                top + int(obj.ymax * scale),
            ),
            outline=(225, 24, 31),
            width=4,
        )


def select_elpv_tiles() -> tuple[GalleryTile, ...]:
    """从 ELPV 中按缺陷概率等级各选一个真实样本。"""

    selected: dict[float, Path] = {}
    for row in read_elpv()["rows"]:
        selected.setdefault(float(row["probability"]), Path(row["image"]))

    labels = {
        0.0: ("Normal cell", "ELPV probability 0.00"),
        1.0 / 3.0: ("Low-confidence defect", "ELPV probability 0.33"),
        2.0 / 3.0: ("Likely defect", "ELPV probability 0.67"),
        1.0: ("Defective cell", "ELPV probability 1.00"),
    }
    return tuple(
        GalleryTile(title=title, subtitle=subtitle, image_path=selected[probability])
        for probability, (title, subtitle) in labels.items()
        if probability in selected
    )


def first_record_by_class(records: list[VocImageRecord], class_names: list[str]) -> tuple[GalleryTile, ...]:
    """按类别顺序选取第一张包含该类别的真实 VOC 样本。"""

    tiles: list[GalleryTile] = []
    for class_name in class_names:
        for record in records:
            objects = tuple(obj for obj in record.objects if obj.name == class_name)
            if objects:
                tiles.append(
                    GalleryTile(
                        title=class_name.replace("_", " "),
                        subtitle=f"{len(objects)} box(es) in this sample",
                        image_path=record.image_path,
                        objects=objects,
                    )
                )
                break
    return tuple(tiles)


def build_rows() -> tuple[GalleryRow, ...]:
    """读取三个数据集，并组装 README 总览图的多维度行。"""

    pv_records = read_pv_multi_defect()["records"]
    pvel_data = read_pvel_ad()
    pvel_records = pvel_data["records"]["trainval"] + pvel_data["records"]["test"]

    return (
        GalleryRow(
            title="ELPV image-level severity labels",
            description="One cell image has one probability label. There are no boxes, so this row supports classification, regression, and anomaly scoring.",
            tiles=select_elpv_tiles(),
        ),
        GalleryRow(
            title="PV-Multi-Defect visible surface classes",
            description="Each tile is a real panel image with Pascal VOC boxes. This row shows the surface-defect detection track.",
            tiles=first_record_by_class(pv_records, ["black_border", "broken", "hot_spot", "no_electricity", "scratch"]),
        ),
        GalleryRow(
            title="PVEL-AD common manufacturing defects",
            description="PVEL-AD uses near-infrared EL images and 12 manufacturing-defect classes. This row shows frequent classes used by the YOLO detection track.",
            tiles=first_record_by_class(pvel_records, ["finger", "crack", "black_core", "thick_line", "horizontal_dislocation", "short_circuit"]),
        ),
        GalleryRow(
            title="PVEL-AD rare and fine-grained classes",
            description="Rare classes are important because average metrics can hide misses on low-count defects. These samples keep the long-tail issue visible.",
            tiles=first_record_by_class(pvel_records, ["vertical_dislocation", "star_crack", "printing_error", "corner", "fragment", "scratch"]),
        ),
        GalleryRow(
            title="Task output differences",
            description="The same project handles image-level labels, panel-level boxes, and EL-cell manufacturing boxes. The model output changes with the label type.",
            tiles=(
                GalleryTile("ELPV", "image-level score", select_elpv_tiles()[0].image_path),
                first_record_by_class(pv_records, ["hot_spot"])[0],
                first_record_by_class(pvel_records, ["crack"])[0],
            ),
        ),
    )


def draw_text_block(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    text_font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    line_gap: int = 4,
) -> int:
    """绘制自动换行文字块，并返回文字块底部 y 坐标。"""

    x, y = position
    for line in textwrap.wrap(text, width=width):
        draw.text((x, y), line, fill=fill, font=text_font)
        bbox = draw.textbbox((x, y), line, font=text_font)
        y += bbox[3] - bbox[1] + line_gap
    return y


def draw_gallery(rows: tuple[GalleryRow, ...]) -> None:
    """绘制完整 README 总览 JPG。"""

    title_font = font(42, bold=True)
    row_title_font = font(25, bold=True)
    body_font = font(18)
    tile_title_font = font(17, bold=True)
    tile_subtitle_font = font(14)

    page_width = 1680
    margin = 36
    row_gap = 30
    tile_gap = 18
    tile_size = (240, 168)
    label_height = 66
    row_header_height = 86
    title_height = 118
    max_tiles = max(len(row.tiles) for row in rows)
    row_height = row_header_height + tile_size[1] + label_height
    page_height = title_height + len(rows) * row_height + (len(rows) - 1) * row_gap + margin

    canvas = Image.new("RGB", (page_width, page_height), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, page_width, title_height - 8), fill=(245, 247, 248))
    draw.text((margin, 28), "Solar Defect Data Gallery", fill=(18, 25, 33), font=title_font)
    draw.text((margin, 78), "Generated from local datasets/raw samples and labels; boxes are redrawn from Pascal VOC annotations.", fill=(72, 82, 94), font=body_font)

    y = title_height
    for row in rows:
        draw.rounded_rectangle((margin, y, page_width - margin, y + row_height), radius=10, fill=(250, 251, 251), outline=(218, 224, 230), width=1)
        draw.text((margin + 18, y + 16), row.title, fill=(25, 33, 42), font=row_title_font)
        draw_text_block(draw, (margin + 18, y + 48), row.description, body_font, (79, 89, 101), width=145)

        tile_count = len(row.tiles)
        tile_total_width = tile_count * tile_size[0] + (tile_count - 1) * tile_gap
        start_x = margin + 18
        if tile_count < max_tiles:
            start_x += (max_tiles * tile_size[0] + (max_tiles - 1) * tile_gap - tile_total_width) // 2

        tile_y = y + row_header_height
        for index, tile in enumerate(row.tiles):
            tile_x = start_x + index * (tile_size[0] + tile_gap)
            image, scale, left, top = fit_image(tile.image_path, tile_size)
            tile_draw = ImageDraw.Draw(image)
            if tile.objects:
                draw_scaled_boxes(tile_draw, tile.objects, scale, left, top)
            canvas.paste(image, (tile_x, tile_y))
            draw.rectangle((tile_x, tile_y, tile_x + tile_size[0], tile_y + tile_size[1]), outline=(210, 216, 222), width=1)
            draw_text_block(draw, (tile_x, tile_y + tile_size[1] + 8), tile.title, tile_title_font, (25, 33, 42), width=24)
            draw_text_block(draw, (tile_x, tile_y + tile_size[1] + 32), tile.subtitle, tile_subtitle_font, (82, 92, 105), width=28)

        y += row_height + row_gap

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT_PATH, quality=92)


def main() -> None:
    """命令行入口：生成根 README 使用的真实数据总览图。"""

    draw_gallery(build_rows())
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
