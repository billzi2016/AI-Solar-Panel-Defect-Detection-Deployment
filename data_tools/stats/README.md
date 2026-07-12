# Dataset Statistics Tool

This directory contains the dataset statistics tool and the report files it generates. Keeping the script, JSON summary, Markdown report, and small visual assets in one place makes the data audit easy to rerun and review.

Dataset parsing is shared through `data_tools/utils/`. The statistics tool imports ELPV, PV-Multi-Defect, PVEL-AD, and Pascal VOC helpers from that package instead of keeping private loader code inside this report folder.

## Dataset Scope

The project uses three public solar-defect datasets because each one answers a different modeling question.

| Dataset | Image type | Label type | Main task | What the model should output |
|---|---|---|---|---|
| ELPV Dataset | Single-cell electroluminescence images | One defect probability per image | Image classification or anomaly scoring | A probability, class, or anomaly score for the whole cell image. |
| PV-Multi-Defect | Panel images with visible surface defects | Pascal VOC bounding boxes | Object detection on panel-level defects | Box coordinates and defect class names for visible damaged regions. |
| PVEL-AD | Near-infrared EL cell images | Pascal VOC bounding boxes plus normal or auxiliary images | Long-tail defect detection and anomaly analysis | Box coordinates and one of 12 manufacturing-defect classes. |

### ELPV Dataset

ELPV is used when the question is whether a single solar cell looks defective. The input is a normalized grayscale EL image. The label is not a box; it is a defect probability such as `0.0`, `0.3333333333333333`, `0.6666666666666666`, or `1.0`. A normal result for this dataset is a clean image count, a readable probability distribution, and sample images that open as 300 by 300 cell crops.

### PV-Multi-Defect

PV-Multi-Defect is used when the question is where a visible panel defect appears. The input is a panel image. The label is one or more Pascal VOC boxes, with classes such as `broken`, `hot_spot`, `black_border`, `scratch`, and `no_electricity`. A normal result is a non-empty XML parse, class counts with visible imbalance, and sampled images where the defect class is visually plausible.

### PVEL-AD

PVEL-AD is used for the main long-tail detection track. The input is a near-infrared EL image of a photovoltaic cell. The released box labels cover 12 defect classes: `finger`, `crack`, `black_core`, `thick_line`, `horizontal_dislocation`, `short_circuit`, `vertical_dislocation`, `star_crack`, `printing_error`, `corner`, `fragment`, and `scratch`. A normal result is a full image count of 36,543, released VOC annotations for the trainval and test subsets, and a class table where frequent classes and rare classes are both visible.

## What It Does

`build_dataset_report.py` reads the local datasets under `datasets/raw/` and produces:

| Output | Path | Purpose |
|---|---|---|
| Machine-readable statistics | `dataset_stats.json` | Lets later training or validation scripts reuse the same counts. |
| English report | `dataset_report.md` | Explains the dataset scale, label formats, class distribution, and sanity checks. |
| Chinese report | `dataset_report.zh.md` | Same report for Chinese documentation. |
| Generated figures | `assets/` | Bar charts and sampled image grids created from local files. |
| Source examples | `source_examples/` | Small representative images copied from source dataset repositories for documentation display. |

## How To Run

Run the script from the project root:

```bash
python3 data_tools/stats/build_dataset_report.py
```

The input is the local ignored dataset tree:

```text
datasets/raw/
```

The output is this directory:

```text
data_tools/stats/
```

The run is normal when it finishes without parser errors, `dataset_stats.json` is updated, and the Markdown reports show real images rather than broken links.
