# Documentation

This documentation site uses MkDocs. MkDocs reads `docs-site/mkdocs.yml` and builds Markdown pages under `docs-site/docs/` into a static website.

## What MkDocs is

MkDocs is a static documentation site generator. The input is Markdown files and YAML configuration. The output is HTML, CSS, and JavaScript files.

This project uses MkDocs because documentation can live in the same repository as the code. GitHub Actions can build the site after a push and publish it to GitHub Pages.

## How i18n is used

i18n means multi-language support. This project keeps Chinese and English pages. Chinese pages live under `docs-site/docs/zh/`, and English pages live under `docs-site/docs/en/`.

Chinese filenames use `.zh.md`. English filenames do not use a language suffix. This makes the language version visible while keeping English filenames suitable for default display.

## Navigation rules

Every document under `docs-site/docs/` must be listed in the `nav` section of `docs-site/mkdocs.yml`. If a page is not in navigation, readers cannot reliably find it from the site entry point.

The navigation also includes a GitHub link. It points back to the project repository, so readers can move from the documentation site to the source.

## Build check

The local check command is:

```bash
mkdocs build -f docs-site/mkdocs.yml --strict
```

The input is the MkDocs configuration and Markdown pages. The output is `docs-site/site/`. This directory is a build artifact and is not committed to git.

When strict mode succeeds, navigation and page references have no obvious errors. When it fails, check the file path and line number in the error first.
