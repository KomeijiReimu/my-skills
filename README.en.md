[中文](README.md) | [English](README.en.md)

# my-skills

A collection of reusable skills for coding agents. The skills cover README writing, final-document editing, Git commits, paper reading, project context maintenance, and system-level technical documentation.

## Installation

With `npx`:

```bash
npx skills add KomeijiReimu/my-skills
```

With `bunx`:

```bash
bunx skills add KomeijiReimu/my-skills
```

Install a single skill, for example `create-readme`:

```bash
npx skills add KomeijiReimu/my-skills --skill create-readme
bunx skills add KomeijiReimu/my-skills --skill create-readme
```

Source: [`KomeijiReimu/my-skills`](https://github.com/KomeijiReimu/my-skills)

## Skills

| Skill | Purpose |
| --- | --- |
| [`create-readme`](create-readme/SKILL.md) | Create, rewrite, and review user-facing README files. |
| [`deliverable-document-writer`](deliverable-document-writer/SKILL.md) | Turn notes, drafts, or review material into submission-ready documents. |
| [`git-commit`](git-commit/SKILL.md) | Create Git commits using the Conventional Commits format. |
| [`paper-reader`](paper-reader/SKILL.md) | Translate and analyze academic papers sentence by sentence in Chinese. |
| [`project-context`](project-context/SKILL.md) | Maintain project context in `.agent-context/`. |
| [`project-documentation-generator`](project-documentation-generator/SKILL.md) | Read a repository and generate system-level technical documentation. |

## Repository layout

Each skill has its own directory at the repository root, with `SKILL.md` as its entry file:

```text
create-readme/SKILL.md
deliverable-document-writer/SKILL.md
git-commit/SKILL.md
paper-reader/SKILL.md
project-context/SKILL.md
project-documentation-generator/SKILL.md
```

## Compatible agents

These skills can be installed into coding agents that support skills workflows, including OpenCode, Claude Code, and Cursor.
