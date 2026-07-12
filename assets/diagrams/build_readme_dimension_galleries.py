"""Build README galleries from real local dataset samples.

本文件的意图：为根目录 README 生成多张 JPG gallery。每张图都读取
`datasets/raw/` 中的真实样本和真实标签；脚本只负责抽样、拼图、重绘真实
VOC 标注框和排版，保证 README 图片可以由本地数据复现。
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "assets" / "diagrams"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_tools.utils import VocImageRecord, VocObject, read_elpv, read_pv_multi_defect, read_pvel_ad  # noqa: E402


@dataclass(frozen=True)
class SampleTile:
    """Gallery 中的一个真实样本。"""

    image_path: Path
    label: str
    objects: tuple[VocObject, ...] = ()


@dataclass(frozen=True)
class SampleRow:
    """Gallery 中的一行，代表一个具体类别或概率等级。"""

    title: str
    description: str
    samples: tuple[SampleTile, ...]


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
    """把真实图片缩放到固定格子，返回画框需要的缩放比例和偏移。"""

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


def draw_boxes(draw: ImageDraw.ImageDraw, objects: tuple[VocObject, ...], scale: float, left: int, top: int) -> None:
    """按真实 VOC 标注坐标绘制红色检测框。"""

    for obj in objects[:6]:
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


def wrap_text(draw: ImageDraw.ImageDraw, text: str, width: int, text_font: ImageFont.ImageFont) -> list[str]:
    """按像素宽度换行，避免标题或说明溢出。"""

    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=text_font) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


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
    for line in wrap_text(draw, text, width, text_font):
        draw.text((x, y), line, fill=fill, font=text_font)
        bbox = draw.textbbox((x, y), line, font=text_font)
        y += bbox[3] - bbox[1] + line_gap
    return y


def select_elpv_rows(samples_per_row: int = 6) -> tuple[SampleRow, ...]:
    """按 ELPV 缺陷概率等级生成行，每行多张真实样本。"""

    rows_by_probability: dict[float, list[Path]] = {}
    for row in read_elpv()["rows"]:
        rows_by_probability.setdefault(float(row["probability"]), []).append(Path(row["image"]))

    labels = [
        (0.0, "ELPV probability 0.00: normal cells", "Image-level label; the model should output a low defect score."),
        (1.0 / 3.0, "ELPV probability 0.33: uncertain or weak defects", "Mild evidence is visible, but the label is not a detection box."),
        (2.0 / 3.0, "ELPV probability 0.67: likely defects", "These samples are closer to defective cells and are useful for severity regression."),
        (1.0, "ELPV probability 1.00: defective cells", "The whole image is labeled defective; the output is still an image-level score."),
    ]
    rows: list[SampleRow] = []
    for probability, title, description in labels:
        paths = rows_by_probability.get(probability, [])[:samples_per_row]
        rows.append(
            SampleRow(
                title=title,
                description=description,
                samples=tuple(SampleTile(image_path=path, label=path.stem) for path in paths),
            )
        )
    return tuple(rows)


def collect_class_samples(records: list[VocImageRecord], class_name: str, limit: int) -> tuple[SampleTile, ...]:
    """为一个 VOC 类别选取多张真实样本，并只绘制该类别的框。"""

    samples: list[SampleTile] = []
    seen: set[Path] = set()
    for record in records:
        objects = tuple(obj for obj in record.objects if obj.name == class_name)
        if not objects or record.image_path in seen:
            continue
        seen.add(record.image_path)
        samples.append(
            SampleTile(
                image_path=record.image_path,
                label=f"{len(objects)} box(es)",
                objects=objects,
            )
        )
        if len(samples) >= limit:
            break
    return tuple(samples)


def select_pv_rows(samples_per_row: int = 6) -> tuple[SampleRow, ...]:
    """按 PV-Multi-Defect 的每个具体缺陷类别生成行。"""

    records = read_pv_multi_defect()["records"]
    class_descriptions = {
        "black_border": "Black or gray border regions on panel images.",
        "broken": "Broken panel areas with localized physical damage.",
        "hot_spot": "Bright spot regions that need box-level localization.",
        "no_electricity": "Dark non-electricity regions that can occupy large panel areas.",
        "scratch": "Thin scratched regions that are easy to miss at low resolution.",
    }
    return tuple(
        SampleRow(
            title=f"PV-Multi-Defect: {class_name.replace('_', ' ')}",
            description=description,
            samples=collect_class_samples(records, class_name, samples_per_row),
        )
        for class_name, description in class_descriptions.items()
    )


def select_pvel_rows(samples_per_row: int = 6) -> tuple[SampleRow, ...]:
    """按 PVEL-AD 的每个具体制造缺陷类别生成行。"""

    data = read_pvel_ad()
    records = data["records"]["trainval"] + data["records"]["test"]
    class_descriptions = {
        "finger": "Finger interruption defects; frequent enough to dominate aggregate metrics.",
        "crack": "Line cracks in EL cell images.",
        "black_core": "Dark core regions that can occupy a large portion of a cell.",
        "thick_line": "Abnormally thick bright or dark line structures.",
        "horizontal_dislocation": "Horizontal dislocation patterns crossing the cell.",
        "short_circuit": "Large dark short-circuit regions.",
        "vertical_dislocation": "Vertical dislocation patterns; visually different from horizontal cases.",
        "star_crack": "Small star-like crack structures.",
        "printing_error": "Repeated printing defects with many fine boxes in some samples.",
        "corner": "Corner damage, usually sparse and easy to hide in averages.",
        "fragment": "Fragment defects with localized broken regions.",
        "scratch": "Rare scratch defects in the PVEL-AD long tail.",
    }
    return tuple(
        SampleRow(
            title=f"PVEL-AD: {class_name.replace('_', ' ')}",
            description=description,
            samples=collect_class_samples(records, class_name, samples_per_row),
        )
        for class_name, description in class_descriptions.items()
    )


def draw_gallery(title: str, subtitle: str, rows: tuple[SampleRow, ...], output_path: Path) -> None:
    """把多行真实样本绘制成一张 README JPG gallery。"""

    page_width = 1260
    margin = 34
    row_gap = 24
    header_height = 120
    tile_size = (182, 136)
    tile_gap = 12
    row_text_height = 88
    label_height = 28
    row_height = row_text_height + tile_size[1] + label_height + 24

    title_font = font(40, bold=True)
    subtitle_font = font(18)
    row_title_font = font(22, bold=True)
    row_desc_font = font(16)
    label_font = font(13)

    page_height = header_height + len(rows) * row_height + (len(rows) - 1) * row_gap + margin
    canvas = Image.new("RGB", (page_width, page_height), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    draw.rectangle((0, 0, page_width, header_height - 10), fill=(244, 247, 249))
    draw.text((margin, 26), title, fill=(20, 27, 36), font=title_font)
    draw.text((margin, 78), subtitle, fill=(75, 85, 97), font=subtitle_font)

    y = header_height
    for row in rows:
        draw.rounded_rectangle((margin, y, page_width - margin, y + row_height), radius=10, fill=(250, 251, 251), outline=(219, 225, 230), width=1)
        text_width = page_width - (margin + 18) * 2
        draw_text_block(draw, (margin + 18, y + 16), row.title, row_title_font, (24, 31, 40), width=text_width)
        draw_text_block(draw, (margin + 18, y + 50), row.description, row_desc_font, (84, 94, 106), width=text_width)

        tile_x = margin + 18
        tile_y = y + row_text_height
        for sample in row.samples:
            image, scale, left, top = fit_image(sample.image_path, tile_size)
            tile_draw = ImageDraw.Draw(image)
            if sample.objects:
                draw_boxes(tile_draw, sample.objects, scale, left, top)
            canvas.paste(image, (tile_x, tile_y))
            draw.rectangle((tile_x, tile_y, tile_x + tile_size[0], tile_y + tile_size[1]), outline=(211, 217, 223), width=1)
            label = textwrap.shorten(sample.label, width=22, placeholder="...")
            draw.text((tile_x, tile_y + tile_size[1] + 8), label, fill=(55, 65, 78), font=label_font)
            tile_x += tile_size[0] + tile_gap

        y += row_height + row_gap

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)


def main() -> None:
    """命令行入口：生成 README 使用的三张真实数据 gallery。"""

    outputs = {
        "readme_gallery_elpv.jpg": (
            "ELPV image-level label gallery",
            "Each row is one real probability label level; samples come from local labels.csv and image files.",
            select_elpv_rows(),
        ),
        "readme_gallery_pv_multi_defect.jpg": (
            "PV-Multi-Defect box-label gallery",
            "Each row is one real surface-defect class; red boxes are redrawn from Pascal VOC annotations.",
            select_pv_rows(),
        ),
        "readme_gallery_pvel_ad.jpg": (
            "PVEL-AD manufacturing-defect gallery",
            "Each row is one real PVEL-AD class; the layout keeps common and rare classes visible.",
            select_pvel_rows(),
        ),
    }
    for filename, (title, subtitle, rows) in outputs.items():
        output_path = OUTPUT_ROOT / filename
        draw_gallery(title=title, subtitle=subtitle, rows=rows, output_path=output_path)
        print(output_path)


if __name__ == "__main__":
    main()
