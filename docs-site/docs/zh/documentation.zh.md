# 文档维护

本文档站使用 MkDocs。MkDocs 会读取 `docs-site/mkdocs.yml`，把 `docs-site/docs/` 下的 Markdown 页面构建成静态网站。

## MkDocs 是什么

MkDocs 是一个静态文档站生成器。输入是 Markdown 文件和 YAML 配置。输出是 HTML、CSS 和 JavaScript 文件。

本项目使用 MkDocs 是因为文档内容可以和代码放在同一个仓库中维护。GitHub Actions 可以在 push 后自动构建并发布到 GitHub Pages。

## i18n 怎么用

i18n 指多语言支持。本项目保留中文和英文两套页面。中文页面放在 `docs-site/docs/zh/`，英文页面放在 `docs-site/docs/en/`。

中文文件名使用 `.zh.md`，英文文件名不加语言后缀。这样做让语言版本一眼可见，同时保持英文文件名适合默认展示。

## 导航规则

所有进入 `docs-site/docs/` 的文档都必须写进 `docs-site/mkdocs.yml` 的 `nav`。如果页面没有出现在导航里，读者就很难从站点入口找到它。

导航中还有一个 GitHub 链接。它指向项目仓库，让读者可以从文档站回到源码。

## 构建检查

本地检查命令是：

```bash
mkdocs build -f docs-site/mkdocs.yml --strict
```

输入是 MkDocs 配置和 Markdown 页面。输出是 `docs-site/site/`。这个目录是构建产物，不进入 git。

严格模式构建成功，说明导航和页面引用没有明显错误。构建失败时，应先看错误信息里的文件路径和行号。
