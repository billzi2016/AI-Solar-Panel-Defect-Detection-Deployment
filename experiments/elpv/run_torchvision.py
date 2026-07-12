"""Train torchvision ResNet and Swin models on ELPV image-level labels.

ELPV has one defect-probability label per cell image, not bounding boxes.  This
runner therefore treats ELPV as an image-level classification or regression
problem and uses mature torchvision architectures instead of a custom detector.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "elpv"


def configure_runtime_cache() -> None:
    """Set writable cache directories before model and plotting libraries run."""

    cache_root = PROJECT_ROOT / ".cache" / "runtime"
    cache_root.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("TMPDIR", str(cache_root))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_root / "matplotlib"))
    os.environ.setdefault("TORCH_HOME", str(cache_root / "torch"))


configure_runtime_cache()

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, roc_auc_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms


@dataclass(frozen=True)
class ElpvRow:
    """One ELPV image path and its probability label."""

    image_path: Path
    probability: float
    module_type: str


class ElpvDataset(Dataset):
    """Torch dataset for ELPV cell images."""

    def __init__(self, rows: list[ElpvRow], task: str, transform: transforms.Compose) -> None:
        self.rows = rows
        self.task = task
        self.transform = transform

    def __len__(self) -> int:
        """Return the number of images in the split."""

        return len(self.rows)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Load one grayscale EL image and return it as a 3-channel tensor."""

        row = self.rows[index]
        with Image.open(row.image_path) as image:
            image = image.convert("RGB")
            tensor = self.transform(image)

        if self.task == "binary":
            target = torch.tensor(1 if row.probability > 0 else 0, dtype=torch.long)
        elif self.task == "regression":
            target = torch.tensor(row.probability, dtype=torch.float32)
        else:
            raise ValueError(f"Unsupported task: {self.task}")
        return tensor, target


def parse_scalar(value: str) -> Any:
    """Parse the scalar subset used by the project YAML configs."""

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
    """Load a simple key-value YAML file without adding another dependency."""

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


def read_elpv_rows(data_root: Path) -> list[ElpvRow]:
    """Read ELPV labels.csv rows and resolve image paths."""

    rows: list[ElpvRow] = []
    with (data_root / "labels.csv").open("r", encoding="utf-8") as handle:
        reader = csv.reader(handle, delimiter=" ")
        for raw_row in reader:
            row = [cell for cell in raw_row if cell]
            if len(row) != 3:
                continue
            image_rel, probability, module_type = row
            rows.append(
                ElpvRow(
                    image_path=data_root / image_rel,
                    probability=float(probability),
                    module_type=module_type,
                )
            )
    return rows


def resolve_device(config_device: str | None) -> torch.device:
    """Resolve the configured device with a conservative auto fallback."""

    if config_device:
        return torch.device(config_device)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model(model_name: str, task: str, pretrained: bool) -> nn.Module:
    """Create a torchvision model and replace its prediction head."""

    output_dim = 2 if task == "binary" else 1
    if model_name == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, output_dim)
        return model
    if model_name == "swin_t":
        weights = models.Swin_T_Weights.DEFAULT if pretrained else None
        model = models.swin_t(weights=weights)
        model.head = nn.Linear(model.head.in_features, output_dim)
        return model
    raise ValueError(f"Unsupported model: {model_name}")


def make_transform(imgsz: int) -> transforms.Compose:
    """Build the deterministic image transform used by train and validation."""

    return transforms.Compose(
        [
            transforms.Resize((imgsz, imgsz)),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
        ]
    )


def build_loaders(rows: list[ElpvRow], task: str, imgsz: int, batch: int, seed: int) -> tuple[DataLoader, DataLoader]:
    """Create deterministic train and validation loaders."""

    labels = [1 if row.probability > 0 else 0 for row in rows]
    train_rows, val_rows = train_test_split(
        rows,
        test_size=0.2,
        random_state=seed,
        stratify=labels,
    )
    transform = make_transform(imgsz)
    train_loader = DataLoader(
        ElpvDataset(train_rows, task=task, transform=transform),
        batch_size=batch,
        shuffle=True,
        num_workers=0,
    )
    val_loader = DataLoader(
        ElpvDataset(val_rows, task=task, transform=transform),
        batch_size=batch,
        shuffle=False,
        num_workers=0,
    )
    return train_loader, val_loader


def evaluate(model: nn.Module, loader: DataLoader, task: str, device: torch.device) -> dict[str, float]:
    """Evaluate the current model on a validation loader."""

    model.eval()
    y_true: list[float] = []
    y_score: list[float] = []
    y_pred: list[int] = []

    with torch.no_grad():
        for images, targets in loader:
            images = images.to(device)
            outputs = model(images)
            if task == "binary":
                probabilities = torch.softmax(outputs, dim=1)[:, 1].cpu().numpy()
                predicted = (probabilities >= 0.5).astype(int)
                y_score.extend(probabilities.tolist())
                y_pred.extend(predicted.tolist())
                y_true.extend(targets.cpu().numpy().astype(int).tolist())
            else:
                predictions = outputs.squeeze(1).cpu().numpy()
                y_score.extend(predictions.tolist())
                y_true.extend(targets.cpu().numpy().tolist())

    if task == "binary":
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "f1": float(f1_score(y_true, y_pred)),
        }
        try:
            metrics["auc"] = float(roc_auc_score(y_true, y_score))
        except ValueError:
            metrics["auc"] = float("nan")
        return metrics

    return {
        "mae": float(mean_absolute_error(y_true, y_score)),
    }


def train(config: dict[str, Any]) -> dict[str, Any]:
    """Train one ELPV image-level model from a config dictionary."""

    seed = int(config["seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    device = resolve_device(config.get("device"))
    task = str(config["task"])
    output_dir = OUTPUT_ROOT / str(config["name"])
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_elpv_rows(PROJECT_ROOT / str(config["data_root"]))
    train_loader, val_loader = build_loaders(
        rows=rows,
        task=task,
        imgsz=int(config["imgsz"]),
        batch=int(config["batch"]),
        seed=seed,
    )
    model = build_model(str(config["model"]), task=task, pretrained=bool(config["pretrained"])).to(device)
    criterion: nn.Module = nn.CrossEntropyLoss() if task == "binary" else nn.MSELoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["learning_rate"]),
        weight_decay=float(config["weight_decay"]),
    )

    best_score: float | None = None
    best_epoch = 0
    stale_epochs = 0
    history: list[dict[str, Any]] = []

    for epoch in range(1, int(config["epochs"]) + 1):
        model.train()
        total_loss = 0.0
        for images, targets in train_loader:
            images = images.to(device)
            targets = targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            if task == "regression":
                outputs = outputs.squeeze(1)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * images.size(0)

        metrics = evaluate(model, val_loader, task=task, device=device)
        train_loss = total_loss / len(train_loader.dataset)
        score = metrics["f1"] if task == "binary" else -metrics["mae"]
        history_row = {"epoch": epoch, "train_loss": train_loss, **metrics}
        history.append(history_row)

        if best_score is None or score > best_score:
            best_score = score
            best_epoch = epoch
            stale_epochs = 0
            torch.save(model.state_dict(), output_dir / "best.pt")
        else:
            stale_epochs += 1

        if stale_epochs >= int(config["patience"]):
            break

    result = {
        "config": config,
        "best_epoch": best_epoch,
        "history": history,
        "output_dir": str(output_dir),
    }
    (output_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def parse_args() -> argparse.Namespace:
    """Parse the ELPV runner command line."""

    parser = argparse.ArgumentParser(description="Train torchvision models on ELPV image-level labels.")
    parser.add_argument("command", choices=["train"])
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--device", default=None, help="Override the config device, for example cpu, cuda, cuda:0, or mps.")
    parser.add_argument("--epochs", default=None, type=int, help="Override the config epoch count for local validation runs.")
    parser.add_argument("--batch", default=None, type=int, help="Override the config batch size.")
    parser.add_argument("--imgsz", default=None, type=int, help="Override the config image size.")
    parser.add_argument("--name", default=None, help="Override the output directory name.")
    return parser.parse_args()


def main() -> None:
    """Load config and dispatch the requested command."""

    configure_runtime_cache()
    args = parse_args()
    config = load_flat_yaml(args.config)
    if args.device is not None:
        config["device"] = args.device
    if args.epochs is not None:
        config["epochs"] = args.epochs
    if args.batch is not None:
        config["batch"] = args.batch
    if args.imgsz is not None:
        config["imgsz"] = args.imgsz
    if args.name is not None:
        config["name"] = args.name
    if args.command == "train":
        result = train(config)
        print(json.dumps({"output_dir": result["output_dir"], "best_epoch": result["best_epoch"]}, indent=2))


if __name__ == "__main__":
    main()
