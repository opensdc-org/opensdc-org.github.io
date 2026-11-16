# OpenSDC · 数据压缩文献整理

收录 HPC、计算机系统与体系结构领域的数据压缩论文，按发表场所整理研究问题、方法、实验结果和来源，并总结相关研究趋势。另有两份配套目录：论文对应的开源压缩器与代码仓库，以及论文常用的数据集。

- 网站：<https://opensdc-org.github.io/survey/>
- 文献核验截至：2026-11-16；当前记录为 153 篇主清单、13 篇附录。

## 目录

```text
survey/
├── index.html           # 生成的页面：论文图谱
├── compressors.html     # 生成的页面：压缩器与代码目录
├── datasets.html        # 生成的页面：数据集目录
├── assets/
│   ├── styles.css       # 页面样式
│   ├── app.js           # 论文页的搜索、筛选、跳转和打印
│   └── catalog.js       # 两个目录页的搜索与筛选
├── data/
│   ├── papers.json      # 论文记录
│   ├── software.json    # 代码仓库记录
│   └── datasets.json    # 数据集记录
├── content/
│   ├── scope.html       # 时间范围、收录标准与核验说明
│   └── trends.json      # 趋势分析与论文引用
├── scripts/
│   ├── build.py         # 页面生成脚本
│   └── refresh_repos.py # 从 GitHub 刷新仓库信息
└── README.md
```

## 生成与预览

需要 Python 3.9 或以上版本，无第三方依赖。在本目录运行：

```sh
python3 scripts/build.py
```

脚本一次生成 `index.html`、`compressors.html` 和 `datasets.html`，用浏览器直接打开即可预览。页面使用相对路径互相链接并加载样式和脚本，移动时需保留整个目录。

## 更新文献

在 `data/papers.json` 中修改论文记录，在 `content/` 中修改收录标准和趋势分析，然后重新生成页面。统计数字、目录和筛选选项由脚本生成，无需手工修改 `index.html`。

提交时一并提交源文件和生成的三个页面。站点沿用仓库的 GitHub Pages 配置，从 `main` 分支发布到 `/survey/`。

## 内容约定

- `id` 为稳定的唯一标识，供目录与趋势引用使用。
- `status` 为 `main`（主清单）或 `appendix`（待核验或边缘相关）。
- 记录题名、发表场所、年份、稳定链接、问题、方法、结果、场景、来源及核验限制。
- `select_reason` 用于解释专题补充的相关性；界面中的范围分类由该字段生成。主要检索范围之外的场所（SIGCOMM、DAC、期刊等）进入主清单时必须填写，否则生成脚本报错。
- `tags` 使用已有标签；常见同义写法由 `scripts/build.py` 的 `aliases` 归并。筛选下拉列表只列出现两次及以上的标签。
- `evidence` 为自由文本；“核验深度”筛选按其中是否含“正文/全文”“摘要/报告”自动分为三档。
- 保留最大值/平均值、基线、硬件、误差设置等实验口径；无法核验的数值明确留作待核验。
- `code` 列出该论文对应的代码仓库（`data/software.json` 中的 `id`），`data` 列出论文用过的数据集（`data/datasets.json` 中的 `id`）；生成脚本会检查引用是否存在。没有 `code` 的条目在页面上显示“未检索到公开代码”，需要另作说明时写 `code_note`。
- 会议年份、在线优先年份、录用记录与正式出版信息分别注明；核验日期按实际文献检索进度更新，需同时修改 `scripts/build.py` 的 `ASOF`、`content/scope.html` 和本文件。

## 代码与数据集目录

`data/software.json` 的 `items` 每条对应一个代码仓库，`groups` 决定目录页的分组顺序。

- 只收录核实过的仓库：仓库存在，并且 README 引用了对应论文、论文正文给出了该链接，或有其他明确依据。依据写在 `basis` 字段。
- `summary`、`platform`、`modes`（误差模式）、`example`（示例命令）、`note` 由人工填写；`example` 必须原样摘自仓库 README。
- `license`、`lang`、`build`、`pushed`、`archived`、`release` 来自 GitHub，不要手改，运行 `python3 scripts/refresh_repos.py` 刷新（加 `--check` 只报告差异）。脚本读取 `GITHUB_TOKEN`，没有时尝试 `gh auth token`。
- `bench: true` 表示该压缩器已有 OpenSDC-Bench 结果；`host` 标记 OpenSDC 托管的项目。
- 没有对应论文的条目（常用基线、评测工具、托管项目）用 `paper_note` 说明收录原因。

`data/datasets.json` 每条对应一个数据集或基准负载。

- SDRBench 条目的布局、大小和提供方取自 <https://sdrbench.github.io/datasets.html>；`bench` 字段写 OpenSDC-Bench 实际使用的子集，与 OpenSDC-Bench 的 `datasets/README.md` 保持一致。
- `links` 只放核实可访问的下载入口；找不到公开入口时留空，并在 `terms` 里说明。
- 论文与数据集的对应关系写在论文记录的 `data` 字段，依据是论文正文或摘要中出现的数据集名称（`data_basis` 记录是哪一种）。它只表示论文用过该数据集，不代表字段、版本或误差设置相同。
