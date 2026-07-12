"""Run Ultralytics YOLO detection experiments.

This wrapper keeps project paths and output directories consistent while leaving
training, validation, prediction, and export behavior to Ultralytics.  It is a
thin operational entry point, not a custom model implementation.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT = PROJECT_ROOT / "outputs" / "detection"


def configure_runtime_cache() -> None:
    """Set writable cache locations before importing PyTorch or Ultralytics."""

    cache_root = PROJECT_ROOT / ".cache" / "runtime"
    cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TMPDIR", str(cache_root))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_root / "matplotlib"))
    os.environ.setdefault("YOLO_CONFIG_DIR", str(cache_root / "ultralytics"))


def parse_args() -> argparse.Namespace:
    """Parse YOLO experiment arguments."""

    parser = argparse.ArgumentParser(description="Run Ultralytics YOLO workflows for solar-defect detection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train = subparsers.add_parser("train", help="Train a YOLO detector.")
    train.add_argument("--config", type=Path, help="Path to a flat YAML training config.")
    train.add_argument("--data", type=Path)
    train.add_argument("--model")
    train.add_argument("--epochs", type=int)
    train.add_argument("--imgsz", type=int)
    train.add_argument("--batch", type=int)
    train.add_argument("--patience", type=int)
    train.add_argument("--device", default=None)
    train.add_argument("--name")

    val = subparsers.add_parser("val", help="Validate a YOLO detector.")
    val.add_argument("--data", required=True, type=Path)
    val.add_argument("--model", required=True, type=Path)
    val.add_argument("--imgsz", default=640, type=int)
    val.add_argument("--device", default=None)
    val.add_argument("--name", default="yolo_val")

    export = subparsers.add_parser("export", help="Export a YOLO checkpoint.")
    export.add_argument("--model", required=True, type=Path)
    export.add_argument("--format", default="onnx", choices=["onnx", "engine", "torchscript"])
    export.add_argument("--imgsz", default=640, type=int)
    export.add_argument("--half", action="store_true")

    return parser.parse_args()


def parse_scalar(value: str) -> Any:
    """Parse the scalar value subset used by project YAML configs."""

    value = value.strip()
    if value in {"", "null", "None"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value.strip("\"'")


def load_flat_yaml(path: Path) -> dict[str, Any]:
    """Load a simple key-value YAML file without adding a runtime dependency."""

    values: dict[str, Any] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(f"Invalid config line {line_number} in {path}: {raw_line}")
        key, value = line.split(":", 1)
        values[key.strip()] = parse_scalar(value)
    return values


def merge_train_config(args: argparse.Namespace) -> argparse.Namespace:
    """Merge YAML training config with explicit command-line overrides."""

    config = load_flat_yaml(args.config) if args.config else {}
    required_defaults = {
        "model": "yolo11l.pt",
        "epochs": 100,
        "imgsz": 640,
        "batch": 4,
        "patience": 3,
        "device": None,
        "name": "yolo_train",
    }

    for key, default in required_defaults.items():
        cli_value = getattr(args, key)
        setattr(args, key, cli_value if cli_value is not None else config.get(key, default))

    data_value = args.data if args.data is not None else config.get("data")
    if data_value is None:
        raise ValueError("Training requires --data or a config file with a data field.")
    args.data = Path(data_value)
    return args


def run_train(args: argparse.Namespace) -> None:
    """Call Ultralytics training with project-standard output paths."""

    from ultralytics import YOLO

    args = merge_train_config(args)
    model = YOLO(str(args.model))
    model.train(
        data=str(args.data),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        patience=args.patience,
        device=args.device,
        project=str(DEFAULT_PROJECT),
        name=args.name,
        exist_ok=True,
    )


def run_val(args: argparse.Namespace) -> None:
    """Call Ultralytics validation for a trained checkpoint."""

    from ultralytics import YOLO

    model = YOLO(str(args.model))
    model.val(
        data=str(args.data),
        imgsz=args.imgsz,
        device=args.device,
        project=str(DEFAULT_PROJECT),
        name=args.name,
        exist_ok=True,
    )


def run_export(args: argparse.Namespace) -> None:
    """Call Ultralytics export for deployment artifact generation."""

    from ultralytics import YOLO

    model = YOLO(str(args.model))
    model.export(format=args.format, imgsz=args.imgsz, half=args.half)


def main() -> None:
    """Dispatch the requested YOLO workflow."""

    configure_runtime_cache()
    args = parse_args()
    if args.command == "train":
        run_train(args)
    elif args.command == "val":
        run_val(args)
    elif args.command == "export":
        run_export(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
