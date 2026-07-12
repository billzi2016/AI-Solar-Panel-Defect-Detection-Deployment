# 项目结构

本页说明仓库中每一层目录的职责。读者可以用它判断一个新文件应该放在哪里，也可以用它检查后续改动是否破坏了工程边界。

## 顶层目录

`docs-site/` 是文档站工程。它包含 MkDocs 配置、中文文档、英文文档和 GitHub Pages 构建入口。文档站只描述仓库中准备公开维护的内容。

`.github/workflows/` 放 GitHub Actions 工作流。当前工作流只负责构建和部署文档站，不负责训练模型、下载数据或运行实验。

`datasets/` 计划用于本地数据。这个目录不进入 git。原始数据、转换后的数据和训练划分都应放在这里。

`weights/` 计划用于模型权重。权重文件通常很大，而且会随训练反复变化，所以不进入 git。

`outputs/` 计划用于实验结果。评估报告、预测图、benchmark 表格和错误样本图都属于输出产物，不进入 git。

## 文档命名规则

中文文档使用 `.zh.md` 后缀，例如 `datasets.zh.md`。英文文档不加语言后缀，例如 `datasets.md`。

这样做的输入是同一主题的两份文档，输出是两个语言版本明确对应的页面。维护者可以通过文件名直接看出语言，也能避免 `README.en.md`、`README_cn.md` 这类不统一命名。

## README 的 DRY 规则

根目录 `README.zh.md` 和 `README.md` 是项目介绍的内容源。文档站中对应的 README 页面使用 symlink 指向根目录文件。

DRY 的意思是同一份事实只维护一次。这里的实际效果是：修改根 README 后，文档站中的 README 页面同步变化，不需要再复制一遍。

判断是否正常的方法很简单：`docs-site/docs/zh/README.zh.md` 应该是一个 symlink，指向 `README.zh.md`；`docs-site/docs/en/README.md` 应该是一个 symlink，指向 `README.md`。
