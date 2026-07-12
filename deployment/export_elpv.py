"""ELPV torchvision model deployment export entry point.

本文件的意图：把 `experiments/elpv/run_torchvision.py` 训练出的 ResNet-18
或 Swin-T checkpoint 导出为 ONNX。ELPV 是图像级任务，因此导出脚本只处理
分类/回归模型，不混入 YOLO 的检测后处理。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "deployment" / "elpv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.elpv.run_torchvision import build_model, load_flat_yaml  # noqa: E402


def configure_runtime_cache() -> None:
    """配置运行时缓存目录，保证导出过程产生的临时文件位置可控。"""

    cache_root = PROJECT_ROOT / ".cache" / "runtime"
    cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TMPDIR", str(cache_root))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_root / "matplotlib"))
    os.environ.setdefault("TORCH_HOME", str(cache_root / "torch"))


def parse_args() -> argparse.Namespace:
    """解析 ELPV ONNX 导出命令行参数。"""

    parser = argparse.ArgumentParser(description="Export an ELPV torchvision checkpoint to ONNX.")
    parser.add_argument("--config", required=True, type=Path, help="ELPV config used to build the model.")
    parser.add_argument("--checkpoint", required=True, type=Path, help="Path to outputs/elpv/<name>/best.pt.")
    parser.add_argument("--output", type=Path, default=None, help="Optional ONNX output path.")
    parser.add_argument("--opset", default=17, type=int, help="ONNX opset version.")
    parser.add_argument("--device", default="cpu", help="Export device. CPU is the most portable default.")
    return parser.parse_args()


def resolve_output_path(config: dict[str, Any], explicit_output: Path | None) -> Path:
    """根据配置名生成默认 ONNX 输出路径。"""

    if explicit_output is not None:
        return explicit_output
    output_dir = OUTPUT_ROOT / str(config["name"])
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "model.onnx"


def load_checkpoint(model: torch.nn.Module, checkpoint_path: Path, device: torch.device) -> None:
    """加载训练得到的 state_dict，并兼容只保存权重的 checkpoint 格式。"""

    state_dict = torch.load(checkpoint_path, map_location=device)
    if not isinstance(state_dict, dict):
        raise TypeError(f"Checkpoint must contain a state_dict dictionary: {checkpoint_path}")
    model.load_state_dict(state_dict)


def export_onnx(args: argparse.Namespace) -> Path:
    """构建 ELPV 模型、加载 checkpoint，并导出 ONNX 文件。"""

    config = load_flat_yaml(args.config)
    device = torch.device(args.device)
    model = build_model(
        model_name=str(config["model"]),
        task=str(config["task"]),
        pretrained=False,
    ).to(device)
    load_checkpoint(model=model, checkpoint_path=args.checkpoint, device=device)
    model.eval()

    output_path = resolve_output_path(config=config, explicit_output=args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dummy_input = torch.randn(1, 3, int(config["imgsz"]), int(config["imgsz"]), device=device)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=args.opset,
        do_constant_folding=True,
        input_names=["image"],
        output_names=["logits" if str(config["task"]) == "binary" else "probability"],
        dynamic_axes={
            "image": {0: "batch"},
            "logits" if str(config["task"]) == "binary" else "probability": {0: "batch"},
        },
    )

    manifest = {
        "config": str(args.config),
        "checkpoint": str(args.checkpoint),
        "onnx": str(output_path),
        "model": config["model"],
        "task": config["task"],
        "imgsz": config["imgsz"],
        "opset": args.opset,
        "expected_input": "RGB tensor normalized with mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)",
        "expected_output": "Two logits for binary classification, or one value for regression.",
    }
    (output_path.parent / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    """命令行入口：配置缓存、导出 ONNX、打印产物路径。"""

    configure_runtime_cache()
    output_path = export_onnx(parse_args())
    print(json.dumps({"onnx": str(output_path)}, indent=2))


if __name__ == "__main__":
    main()
