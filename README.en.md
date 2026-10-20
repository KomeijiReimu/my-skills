[中文](README.md) | [English](README.en.md)

# my-skills

A collection of general-purpose skills for AI agents, providing task workflows and execution rules that can be installed as needed and used independently.

## Installation

With `npx`:

```bash
npx skills add KomeijiReimu/my-skills
```

With `bunx`:

```bash
bunx skills add KomeijiReimu/my-skills
```

Install a single skill:

```bash
npx skills add KomeijiReimu/my-skills --skill create-readme
npx skills add KomeijiReimu/my-skills --skill fkgpt-output-quality
```

Source: [`KomeijiReimu/my-skills`](https://github.com/KomeijiReimu/my-skills)

After installation, name the skill in a supporting agent, for example:

> Use create-readme to rewrite this project's README, covering every user-facing feature, installation, and typical usage.

## Choose by task

### Output control

| Skill | Purpose and workflow |
| --- | --- |
| [`fkgpt-output-quality`](fkgpt-output-quality/SKILL.md) | Apply drafting constraints against invented user positions, irrelevant caveats, evasive judgments, invented jargon, unnecessary process, and promises in place of action. An internal pre-delivery check rejects noncompliant drafts until they are corrected. Covers chat replies, progress updates, and document files. |

This is an instruction-level simulated hook; the agent must actually load the installed skill to use it.

#### Document prose improvements

The following 4 human-facing documentation skills explicitly address awkward agent-generated prose. Their drafting and delivery checks require:

- **Concrete facts and actions.** Explain what happens, how to use it, and why it matters in language readers understand. Remove invented jargon such as “evidence gates” and “semantic closure.” Retain established project and academic terms, explaining them when useful.
- **No baseless negations or straw-man rebuttals.** Do not invent a reader misconception just to correct it with “this is not…” or “but that does not prove…”.
- **Standalone final prose.** Remove chat replies, revision notes, self-praise, irrelevant caveats, and pointless transitions. Preserve real limitations, risks, and evidence gaps.
- **Keep the substance.** READMEs cover features and usage, technical documents explain implementation, and translations preserve the original information. Cleaning the prose must not turn complete documents into summaries or change a paper's meaning.
- **Read back actual files before delivery.** Fix problems in the document and recheck them instead of stopping at a suggested edit.
- **Renderable formulas.** Write Markdown math in LaTeX: `$...$` inline and standalone `$$...$$` blocks for display equations. Check symbols and delimiters rather than leaving formulas as code or bare commands.

Each documentation skill includes these requirements and can be used independently.

### Human-facing document creation and editing

| Skill | When to use it | Deliverable |
| --- | --- | --- |
| [`create-readme`](create-readme/SKILL.md) | Create an excellent, readable project homepage covering every verified user-facing feature and essential usage point. Inspect the repository, then organize around reader tasks. | `README.md`: purpose, a complete feature overview, installation and quick start, typical usage, necessary configuration, and important limitations. |
| [`deliverable-document-writer`](deliverable-document-writer/SKILL.md) | Turn notes, drafts, interviews, or review material into a formal document ready to submit or share. | A standalone report, proposal, or complete chapter, organized around reader questions with facts, evidence, and conclusions connected. |
| [`project-documentation-generator`](project-documentation-generator/SKILL.md) | Read the whole project and explain how features work, modules interact, and code executes. | System-level technical documentation, such as `PROJECT_FULL_DOCUMENTATION.md`, including implementation details, key code paths, configuration and operation, and Mermaid architecture and flow diagrams. |
| [`paper-reader`](paper-reader/SKILL.md) | Process papers in batches, completing sentence-by-sentence Chinese translations, detailed Chinese analyses, or both for every readable paper. Continue through the batch rather than stopping because it is large, lengthy, or partly complete. | Separate `paper.translation.zh.md` and/or `paper.analysis.zh.md` files per paper. Translations remain faithful to the source, without summarizing, omitting, or rewriting it; preserve sections, figures, formulas, and appendices. Analysis stays in its own file. |

### Long-running work and context management

| Skill | When to use it | Output and usage boundaries |
| --- | --- | --- |
| [`project-context`](project-context/SKILL.md) | Maintain Chinese working context for agents continuing long-running projects. Supports creation, updates, takeover, rebuilding, and auditing to preserve continuity across sessions. | 10 core context files in `.agent-context/`, covering the project map, architecture, state, timeline, decisions, risks, and handoff, for agents to read, verify, and continue work. Maintenance requires explicit authorization in the current request. |

### Development collaboration

| Skill | Purpose |
| --- | --- |
| [`git-commit`](git-commit/SKILL.md) | Inspect the actual diff, stage logical changes, generate a Conventional Commits subject and body, and commit. |

## What the output looks like

The following fictional checksum tool, import service, and paper excerpts illustrate structure and prose. Actual sections, commands, and conclusions come from the task's source material.

### create-readme: understand the project and start using it

Organize the README around adoption and usage, with all actual features represented. A CLI project might use:

```text
Project name and one-sentence purpose
├── Features: inputs, outputs, supported operations
├── Requirements and installation
├── Quick start: shortest command and expected result
├── Typical usage by real use case
├── Configuration and options
├── Important limitations and data handling
└── Links to deeper documentation
```

**Example excerpt:**

> **Hashdir** creates SHA-256 manifests for directory contents so you can check backup integrity.
>
> **Features**
> - Scan a directory recursively and hash each file.
> - Save a manifest for later checks.
> - Compare manifests to identify added, removed, and changed files.
>
> **Quick start**
> With Python 3.10+, run `python hashdir.py ./photos --output checksums.json` to save relative paths and hashes.
>
> **Check a backup**
> Run `python hashdir.py ./restored --compare checksums.json` to find files that differ from the original manifest.

### deliverable-document-writer: source material becomes a submission-ready document

Choose sections for the report, proposal, or paper's reader tasks. When a draft exists, preserve its structure, register, and depth of argument. A release-scope decision document might use:

```text
Objective and conclusion
├── Background and problem
├── Facts and evidence
├── Options and selection rationale
├── Implementation and responsibilities
└── Risks, open decisions, and acceptance criteria
```

**Example excerpt:**

> **Release scope**
>
> This release delivers batch export and failed-task retries. Batch export replaces individual downloads. Retries reuse recorded task state so users can resume from the failure point.
>
> **Acceptance criteria**
>
> The exported file must contain every selected record. After a network interruption, completed records remain complete, and a retry processes only the remaining records.

### project-documentation-generator: implementation detail for maintainers

Produce one repository-wide technical document linking each feature to its entry point, core modules, data structures, processing steps, and output.

```text
Project overview
├── Repository structure and module map
├── Overall architecture
├── Feature-by-feature implementation
├── Key code paths and error handling
├── Data models, states, and dependencies
├── Configuration, build, testing, and deployment
├── Mermaid architecture and flow diagrams
└── Constraints and maintenance guidance
```

**Example excerpt:**

> **CSV import path**
>
> `ImportController` receives the file and creates an import job. `CsvParser` reads fields row by row, and `RowValidator` checks column counts and required fields. Valid records go to `RecordRepository` for batch writes. Invalid records retain their row numbers and reasons for the results page.

```mermaid
flowchart LR
    A[Upload CSV] --> B[Create import job]
    B --> C[Parse and validate fields]
    C --> D[Batch write valid records]
    C --> E[Record failed rows and reasons]
    D --> F[Summarize import results]
    E --> F
```

### paper-reader: complete the batch and preserve the source

- **Cover the whole batch:** Inventory every input, read each paper, produce its requested files, and track its completion status.
- **Keep going:** Do not stop because there are many papers, the material is long, or several papers are already complete. Record a damaged paper's specific blocker and continue with the remaining readable papers; report unfinished items accurately.
- **Stay faithful:** Translate sentence by sentence, preserving claims, qualifications, numbers, terminology, formulas, and appendices. Do not replace the full text with a summary, add or omit content, or rewrite the source for style.
- **Separate translation from analysis:** Keep interpretation and evaluation in the analysis file, with the translation corresponding to the original.

Depending on the selected mode, create separate Chinese translation and analysis files:

```text
paper.translation.zh.md          paper.analysis.zh.md
├── Source, title, mode          ├── Bibliographic details and research question
├── Original sections, sentences ├── Assumptions, notation, formalization
├── Captions, algorithms, math   ├── Method, objective, algorithm
├── Appendices                  ├── Experiments, results, ablations
└── Original bibliography       └── Figures, limitations, reproduction clues
```

**Analysis excerpt, shown here in English:**

> **Objective function**
>
> The model minimizes mean squared error between predictions and observations:

$$
\mathcal{L}(\theta) = \frac{1}{n}\sum_{i=1}^{n}\bigl(f_{\theta}(x_i)-y_i\bigr)^2
$$

> Here, $n$ is the sample count, $f_{\theta}(x_i)$ is the prediction, and $y_i$ is the observation. Errors are squared before averaging, so larger errors contribute more to the loss.

### project-context: long-term context and continuity for agents

Maintain a fixed set of Chinese project context files for subsequent agents, separating current facts, historical changes, and next actions so work can be read, verified, and continued across sessions:

```text
.agent-context/
├── README.md             # Entry point and maintenance rules
├── current-state.md      # Current state and blockers
├── project-map.md        # Directories, modules, entry points
├── architecture.md       # Architecture and operation
├── timeline.md           # Change timeline
├── decisions.md          # Decisions and trade-offs
├── task-history.md       # Tasks and their results
├── user-preferences.md   # Preferences and conventions
├── risks.md              # Risks, evidence, status
└── agent-handoff.md      # Reading order and next actions
```

**Handoff excerpt, shown here in English:**

> **Read first:** Open `current-state.md` for the current phase, then `project-map.md` to locate the import module.
>
> **Current progress:** CSV parsing and field validation are implemented. Failed-row display remains unfinished.
>
> **Continue here:** Wire row numbers and failure reasons into `src/import/result-view.ts`, then add tests for missing columns and empty fields.

### Output control and Git collaboration examples

`fkgpt-output-quality` checks whether a sentence helps with the task and is supported by evidence. If a release is confirmed for Friday:

| Candidate reply | Corrected reply |
| --- | --- |
| Friday, but this does not prove every future release will also be on Friday. | Friday. |

`git-commit` writes from the actual diff. A CSV missing-column fix might produce:

```text
fix(import): reject CSV rows with missing columns

Report the row number and missing fields in the import result.
```

## Repository layout

Each skill has its own directory at the repository root, with `SKILL.md` as its entry file:

```text
fkgpt-output-quality/SKILL.md
create-readme/SKILL.md
deliverable-document-writer/SKILL.md
git-commit/SKILL.md
paper-reader/SKILL.md
project-context/SKILL.md
project-documentation-generator/SKILL.md
```

## Compatible agents

These skills can be installed into coding agents that support skills workflows, including OpenCode, Claude Code, and Cursor.
