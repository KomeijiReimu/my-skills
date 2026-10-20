[English](README.en.md) | [中文](README.md)

# my-skills

一套面向 AI Agent 的通用 skills，提供可按需安装、独立使用的任务流程与执行约束。

## 安装

使用 `npx`：

```bash
npx skills add KomeijiReimu/my-skills
```

使用 `bunx`：

```bash
bunx skills add KomeijiReimu/my-skills
```

安装单个 skill：

```bash
npx skills add KomeijiReimu/my-skills --skill create-readme
npx skills add KomeijiReimu/my-skills --skill fkgpt-output-quality
```

安装来源：[`KomeijiReimu/my-skills`](https://github.com/KomeijiReimu/my-skills)

安装后，在支持 skills 的 Agent 中点名使用，例如：

> 用 create-readme 为这个项目重写 README，覆盖全部用户可见功能、安装步骤和典型用法。

## 按任务选择

### 输出管控

| Skill | 用途与执行方式 |
| --- | --- |
| [`fkgpt-output-quality`](fkgpt-output-quality/SKILL.md) | 管控聊天回复、进度消息和文件文档的表达。通过生成前约束与模拟发送前 hook，清除虚构反驳、无关免责、黑话和流程膨胀；违规候选稿须修改后再交付。 |

该 skill 由 Agent 加载后执行，hook 通过指令模拟发送前自检。

#### 文档写作的专门优化

下列 4 个文档类 skill 都内置了文风约束，让面向人类读者的成稿保持清楚、完整：

- **表达具体。** 用清楚的对象、动作和事实替代“证据门禁”“语义闭环”等自造黑话，按读者需要解释专业术语。
- **去掉多余防御。** 清除无源否定、假想反驳、无关免责和空泛自评，保留影响理解与使用的限制和风险。
- **成稿独立可读。** 正文围绕读者问题组织，清除聊天回应、修订备忘和写作过程叙述。
- **保留完整内容。** README 覆盖功能与使用要点，技术文档解释实现细节，论文译文保留原文信息与含义。
- **修改落实到正文。** 交付修正后的成稿，问题直接在文件中处理。
- **公式可渲染。** Markdown 中的数学表达使用 LaTeX：行内 `$...$`，独立公式用单独成段的 `$$...$$`。

### 面向人类读者的文档创作与整理

| Skill | 适合什么任务 | 交付内容 |
| --- | --- | --- |
| [`create-readme`](create-readme/SKILL.md) | 创建或重写项目首页，覆盖全部已核实的用户可见功能与使用要点。 | `README.md`：用途、功能、安装、快速上手、典型用法、配置和重要限制。 |
| [`deliverable-document-writer`](deliverable-document-writer/SKILL.md) | 将笔记、草稿或审阅材料整理成可直接提交、分享的成稿。 | 独立可读的报告、方案或完整章节，连接事实、证据与结论。 |
| [`project-documentation-generator`](project-documentation-generator/SKILL.md) | 通读仓库，解释功能实现、模块协作与核心代码路径。 | 系统级技术文档，包含实现详解、运行配置和 Mermaid 图，默认文件名如 `PROJECT_FULL_DOCUMENTATION.md`。 |
| [`paper-reader`](paper-reader/SKILL.md) | 批量精读论文，持续完成整批可读论文的逐句中文翻译、详尽解析或两者。 | 每篇独立生成译文与／或解析；译文忠于原文，覆盖章节、图表、公式和附录。 |

### 长期工作与上下文管理

| Skill | 适合什么任务 | 产出与使用边界 |
| --- | --- | --- |
| [`project-context`](project-context/SKILL.md) | 为后续 Agent 维护长期项目的中文工作上下文，支持创建、更新、接手、重建与审计。 | `.agent-context/` 中的 10 份核心上下文资料，支持跨会话接续工作；维护须由用户在当前请求明确授权。 |

### 开发协作

| Skill | 用途 |
| --- | --- |
| [`git-commit`](git-commit/SKILL.md) | 分析真实 diff，按逻辑变更组织暂存，生成 Conventional Commits 格式的标题与正文并提交。 |

## 结构与内容示例

以下示例使用虚构的文件校验工具、数据导入服务和论文片段，展示各 skill 对应的内容结构与写作风格。

### create-readme：功能与使用说明完整的项目首页

围绕用户的采用与使用过程组织 README，逐项展示真实功能。例如一个命令行工具：

```text
项目名称与一句话用途
├── 主要功能：输入、输出、支持的操作
├── 环境与安装
├── 快速上手：最短命令与预期结果
├── 典型用法：按真实使用场景展开
├── 配置与参数
├── 重要限制与数据处理方式
└── 深入文档入口
```

**正文片段：**

> **Hashdir** 为目录中的文件生成 SHA-256 校验清单，用于备份后的完整性核对。
>
> **主要功能**
> - 递归扫描目录，为每个文件计算校验值。
> - 将结果保存为清单，供后续复查。
> - 对比两次清单，列出新增、删除和内容变化的文件。
>
> **快速上手**
> 在 Python 3.10+ 环境中运行 `python hashdir.py ./photos --output checksums.json`，将相对路径与校验值写入清单。
>
> **复查备份**
> 运行 `python hashdir.py ./restored --compare checksums.json`，定位与原清单不一致的文件。

### deliverable-document-writer：从零散材料到可直接提交的成稿

按报告、方案或论文的读者任务安排章节；已有草稿则保持其结构、语体和论证密度。例如一份版本范围决策稿：

```text
交付目标与结论
├── 背景与问题
├── 事实和证据
├── 方案比较与选择依据
├── 实施安排与责任
└── 风险、待决事项与验收条件
```

**正文片段：**

> **版本范围**
>
> 本次发布交付批量导出与失败重试。批量导出覆盖现有的手工逐条下载流程；失败重试复用已记录的任务状态，用户可从失败位置继续。
>
> **验收条件**
>
> 导出文件应包含用户选中的全部记录。网络中断后，已完成的记录保持完成状态，重试仅处理剩余记录。

### project-documentation-generator：系统级实现说明

默认生成一份覆盖全仓库的技术文档，串联功能入口、核心模块、数据结构、处理流程和输出。

```text
项目概览
├── 仓库结构与模块地图
├── 整体架构
├── 各项功能的实现详解
├── 核心代码路径与异常处理
├── 数据模型、状态与外部依赖
├── 配置、构建、测试与部署
├── Mermaid 架构图与流程图
└── 关键约束与维护建议
```

**正文片段：**

> **CSV 导入路径**
>
> `ImportController` 接收文件并创建导入任务。`CsvParser` 逐行解析字段，`RowValidator` 检查列数与必填项，合法记录交给 `RecordRepository` 批量写入。校验失败的记录保留行号与原因，供导入结果页展示。

```mermaid
flowchart LR
    A[上传 CSV] --> B[创建导入任务]
    B --> C[解析与字段校验]
    C --> D[批量写入合法记录]
    C --> E[记录失败行与原因]
    D --> F[汇总导入结果]
    E --> F
```

### paper-reader：批量读完，逐句保真

- **整批覆盖**：清单记录每篇论文的所选模式、输出文件与处理状态，逐篇完成对应任务。
- **持续处理**：持续完成全部可读论文，不因篇数多、篇幅长或部分完成而提前收尾。单篇损坏时记录原因，继续其余论文。
- **忠于原文**：全文逐句翻译，保留原文论点、限定、数值、术语、公式和附录，不以摘要代替全文，不擅自增删或润色。
- **翻译与解析分开**：译文对应原文，解释与评价放在独立解析文件中。

按所选模式生成两类独立文件：

```text
paper.translation.zh.md          paper.analysis.zh.md
├── 来源、标题与翻译模式         ├── 文献信息与研究问题
├── 原文章节与逐句译文           ├── 前提、符号与问题形式化
├── 图表标题、算法与公式         ├── 方法、目标函数与算法步骤
├── 附录                         ├── 实验设置、结果与消融
└── 原始参考文献条目             └── 图表解读、局限与复现线索
```

**解析片段：**

> **目标函数**
>
> 模型通过最小化均方误差拟合预测值与观测值：

$$
\mathcal{L}(\theta) = \frac{1}{n}\sum_{i=1}^{n}\bigl(f_{\theta}(x_i)-y_i\bigr)^2
$$

> 其中，$n$ 为样本数，$f_{\theta}(x_i)$ 为模型预测，$y_i$ 为观测值。每个样本的误差先平方再求平均，误差较大的样本对损失的贡献更大。

### project-context：面向 Agent 的长期上下文与工作接续

为后续 Agent 维护固定的中文项目上下文体系，将当前事实、历史变化与后续行动分别存放，支持跨会话读取、核验和接续工作：

```text
.agent-context/
├── README.md             # 阅读入口与维护规则
├── current-state.md      # 当前状态与阻塞
├── project-map.md        # 目录、模块与入口
├── architecture.md       # 架构与运行方式
├── timeline.md           # 变更时间线
├── decisions.md          # 决策、原因与取舍
├── task-history.md       # 任务及其结果
├── user-preferences.md   # 用户偏好与项目约定
├── risks.md              # 风险、证据与状态
└── agent-handoff.md      # 接手顺序与后续行动
```

**接手指南片段：**

> **先读什么**：先读 `current-state.md` 确认当前阶段，再读 `project-map.md` 定位导入模块。
>
> **当前进展**：CSV 解析与字段校验已实现，失败行展示仍待完成。
>
> **继续工作**：从 `src/import/result-view.ts` 接入行号与失败原因，补充缺列和空字段场景的测试。

### 输出管控与 Git 协作示例

`fkgpt-output-quality` 按任务与证据判断一句话是否有用。例如已确认发布时间为周五：

| 候选答复 | 修正后 |
| --- | --- |
| 周五，但这不能证明未来所有版本也都周五发布。 | 周五。 |

`git-commit` 根据真实变更生成提交，例如针对 CSV 缺列处理的修改：

```text
fix(import): reject CSV rows with missing columns

Report the row number and missing fields in the import result.
```

## 目录结构

每个 skill 位于仓库根目录下的独立目录中，入口文件统一为 `SKILL.md`：

```text
fkgpt-output-quality/SKILL.md
create-readme/SKILL.md
deliverable-document-writer/SKILL.md
git-commit/SKILL.md
paper-reader/SKILL.md
project-context/SKILL.md
project-documentation-generator/SKILL.md
```

## 适用 Agent

这些 skills 可安装到支持 skills 工作流的编码 Agent，例如 OpenCode、Claude Code 和 Cursor。
