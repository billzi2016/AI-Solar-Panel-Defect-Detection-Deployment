"""YOLO deployment export entry point.

本文件的意图：把已经训练好的 Ultralytics YOLO checkpoint 导出成部署格式。
这里不重新实现 YOLO，也不改写后处理逻辑，只把项目路径、输出 manifest
和 Ultralytics 官方 export API 统一起来，方便后续复现实验。
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "deployment" / "yolo"


def configure_runtime_cache() -> None:
    """配置运行时缓存目录，避免导出过程把缓存写到不可控位置。"""

    cache_root = PROJECT_ROOT / ".cache" / "runtime"
    cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TMPDIR", str(cache_root))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_root / "matplotlib"))
    os.environ.setdefault("YOLO_CONFIG_DIR", str(cache_root / "ultralytics"))


def parse_args() -> argparse.Namespace:
    """解析 YOLO 导出命令行参数。"""

    parser = argparse.ArgumentParser(description="Export a trained Ultralytics YOLO checkpoint.")
    parser.add_argument("--model", required=True, type=Path, help="Path to a trained .pt checkpoint.")
    parser.add_argument("--format", default="onnx", choices=["onnx", "engine", "torchscript"], help="Export format.")
    parser.add_argument("--imgsz", default=640, type=int, help="Export input image size.")
    parser.add_argument("--device", default=None, help="Ultralytics device value, for example cpu, 0, cuda:0, or mps.")
    parser.add_argument("--half", action="store_true", help="Use FP16 export when the backend supports it.")
    parser.add_argument("--dynamic", action="store_true", help="Enable dynamic shape export when supported.")
    parser.add_argument("--name", default=None, help="Optional output manifest name.")
    return parser.parse_args()


def write_manifest(args: argparse.Namespace, exported_path: str | Path | None) -> Path:
    """写出导出 manifest，记录输入 checkpoint、导出参数和产物路径。"""

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_name = args.name or f"{args.model.stem}_{args.format}"
    manifest_path = OUTPUT_ROOT / f"{manifest_name}.json"
    manifest: dict[str, Any] = {
        "model": str(args.model),
        "format": args.format,
        "imgsz": args.imgsz,
        "device": args.device,
        "half": args.half,
        "dynamic": args.dynamic,
        "exported_path": str(exported_path) if exported_path is not None else None,
        "expected_input": "RGB image after Ultralytics preprocessing",
        "expected_output": "Ultralytics detection tensors and postprocessed boxes when loaded through YOLO APIs",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def export_model(args: argparse.Namespace) -> Path:
    """调用 Ultralytics export，并返回 manifest 路径。"""

    from ultralytics import YOLO

    model = YOLO(str(args.model))
    exported_path = model.export(
        format=args.format,
        imgsz=args.imgsz,
        device=args.device,
        half=args.half,
        dynamic=args.dynamic,
    )
    return write_manifest(args=args, exported_path=exported_path)


def main() -> None:
    """命令行入口：配置缓存、导出模型、打印 manifest 路径。"""

    configure_runtime_cache()
    manifest_path = export_model(parse_args())
    print(json.dumps({"manifest": str(manifest_path)}, indent=2))


if __name__ == "__main__":
    main()
