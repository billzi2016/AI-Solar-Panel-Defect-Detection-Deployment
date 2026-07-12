# Architecture

This page explains the responsibility of each repository layer. It helps readers decide where a new file should go and helps maintainers check whether a later change breaks the project boundaries.

## Top-level directories

`docs-site/` is the documentation site project. It contains the MkDocs configuration, Chinese pages, English pages, and the GitHub Pages build entry point. The site only describes content that is meant to be maintained in the public repository.

`.github/workflows/` stores GitHub Actions workflows. The current workflow only builds and deploys the documentation site. It does not train models, download datasets, or run experiments.

`datasets/` is reserved for local data. This directory is not committed to git. Raw data, converted data, and train or test splits should stay there.

`weights/` is reserved for model weights. Weight files are usually large and change often during training, so they are not committed to git.

`outputs/` is reserved for experiment results. Evaluation reports, prediction images, benchmark tables, and error case images are generated artifacts and are not committed to git.

## Documentation naming

Chinese pages use the `.zh.md` suffix, for example `datasets.zh.md`. English pages do not use a language suffix, for example `datasets.md`.

The input is one topic with two language versions. The output is a pair of files whose language is obvious from the name. This avoids mixed conventions such as `README.en.md` or `README_cn.md`.

## README and DRY

The root `README.zh.md` and `README.md` files are the content source for the project overview. The README pages inside the documentation site are symlinks to those root files.

DRY means the same fact is maintained in one place. In this project, editing the root README updates the README page in the documentation site without copying the same text into another file.

The expected state is simple: `docs-site/docs/zh/README.zh.md` should be a symlink to `README.zh.md`, and `docs-site/docs/en/README.md` should be a symlink to `README.md`.
