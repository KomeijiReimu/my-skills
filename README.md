[English](README.en.md) | [中文](README.md)

# my-skills

一套可安装到编码 Agent 的通用 skills，帮助 Agent 完成 README 写作、最终文档整理、Git 提交、论文阅读、项目上下文维护和系统级技术文档生成。

## 安装

使用 `npx`：

```bash
npx skills add KomeijiReimu/my-skills
```

使用 `bunx`：

```bash
bunx skills add KomeijiReimu/my-skills
```

安装单个 skill，例如 `create-readme`：

```bash
npx skills add KomeijiReimu/my-skills --skill create-readme
bunx skills add KomeijiReimu/my-skills --skill create-readme
```

安装来源：[`KomeijiReimu/my-skills`](https://github.com/KomeijiReimu/my-skills)

## Skills

| Skill | 用途 |
| --- | --- |
| [`create-readme`](create-readme/SKILL.md) | 创建、重写和审校面向最终用户的 README。 |
| [`deliverable-document-writer`](deliverable-document-writer/SKILL.md) | 将笔记、草稿或审阅材料整理成可提交的最终文档。 |
| [`git-commit`](git-commit/SKILL.md) | 按 Conventional Commits 规范创建 Git 提交。 |
| [`paper-reader`](paper-reader/SKILL.md) | 对论文进行逐句中文翻译与解析。 |
| [`project-context`](project-context/SKILL.md) | 维护项目的 `.agent-context/` 上下文信息。 |
| [`project-documentation-generator`](project-documentation-generator/SKILL.md) | 通读仓库并生成系统级技术文档。 |

## 目录结构

每个 skill 位于仓库根目录下的独立目录中，入口文件统一为 `SKILL.md`：

```text
create-readme/SKILL.md
deliverable-document-writer/SKILL.md
git-commit/SKILL.md
paper-reader/SKILL.md
project-context/SKILL.md
project-documentation-generator/SKILL.md
```

## 适用 Agent

这些 skills 可安装到支持 skills 工作流的编码 Agent，例如 OpenCode、Claude Code 和 Cursor。
