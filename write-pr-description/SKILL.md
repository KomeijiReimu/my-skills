---
name: write-pr-description
description: |-
  Draft or revise pull request bodies from branch changes and repository templates.
  Explain purpose, behavior changes, design decisions, and review focus. Select
  change-level evidence and exclude local work logs. Use proactively when preparing
  a branch for review, filling a PR template, or updating a stale description,
  including requests such as "open a PR" or "put this up for review".

  Examples:
  - user: "Write a PR description for this branch" → draft a reviewer-focused body.
  - user: "Fill in this repository's PR template" → answer its required sections.
  - user: "Refresh the description after these changes" → describe the current branch.
---

# write-pr-description

A pull request description has one job: give the reviewer what the diff cannot.

The diff already states what changed. The description states why it changed, what it
affects, which decisions were made along the way, and where the author wants attention.
Everything below follows from that. When a rule here conflicts with what a specific
reviewer needs, serve the reviewer.

Produce the PR body. Follow the repository's workflow to open or update the PR.

## 1. Collect the facts before drafting

Usually you did the work and already know most of this. When you are describing a branch
you did not write, or a PR you have just been handed, start here.

```bash
# From a checkout of the branch
git --no-pager log <base>..HEAD            # commit bodies first, they carry the why
git --no-pager diff <base>...HEAD --stat

# From a PR number, with no local branch
gh pr view <n> --repo <owner/repo> --json title,commits,files,baseRefName
gh pr diff <n> --repo <owner/repo>
```

Read the commit bodies before the diff. They are usually the richest source of
motivation. Then verify what they claim: a commit message saying "matches the existing
pattern in this file" is an assertion about code, and it is often wrong. Do not forward a
claim you have not checked.

Verify by looking, not by reasoning. The checks worth making are cheap and specific:

- Read what the change deletes. When a change exists to fix something, the defect is
  usually visible in the removed code.
- Ask the system what a thing means, rather than inferring it: `gcloud iam roles
  describe` for a role's permission set, the provider or API schema for a resource's
  fields, the parser for what a marker does.
- Grep a flag across the environment files before claiming it is on or off.
- Open the file a comment or commit message points at, and confirm it says what the
  pointer claims.

One check of this kind usually produces the best sentence in the description.

Gather what the diff cannot tell the reviewer:

- The motivation. What breaks, costs, or stays impossible without this change.
- The linked issue, spec, or design doc, and any spec files committed on the branch.
- Decisions with a real alternative, and why the alternative lost.
- The blast radius: what this can break beyond the files it touches.
- Evidence of the changed behavior: relevant test coverage, CI results, and reproducible
  acceptance checks.
- Open questions about the change's behavior, design, or impact.

## 2. Follow the repository's template

Check the repository for a PR template. Where there are several, pick the one matching
the change. Templates differ per repository, so check every time rather than reusing the
shape from your last PR.

**Follow the template's structure and required fields.** Remove sections when its
instructions say to remove them. Keep required answers factual and concise; a testing
section is not a request for the author's local work log.

- Keep the headings, their wording, and their order. Reviewers and tooling both scan for
  them.
- Answer every section, in your own words, under the heading. Do not reproduce the
  template's question text, its explanatory links, or its examples. A template with four
  gate sections can otherwise cost two hundred words to say "no" four times.
- Where a section does not apply, say so in a clause that shows you considered it ("No
  new tables"), rather than deleting it or leaving it bare.
- Tick a box only when its statement is supported by evidence. Otherwise leave it
  unticked. Add an explanation only when the template requires one, and keep it to the
  check's status or requirement. Do not append workstation details or troubleshooting
  history, and do not restate the box's own text back to the reader.
- Preserve machine-read content: changelog markers, artifact or media markers, issue
  linking keys. Check that the marker is live where the template puts it. Some templates
  show a marker inside an HTML comment that the parser strips, which means a marker left
  in place is silently ignored. Confirm against the parser or a merged PR.
- Instructional HTML comments can go once you have answered them.

When no template exists, use this shape, which is the same shape a template would give
you:

1. The opening paragraph from step 3, with no heading above it. It carries both what and
   why, so there is no separate `Why` section.
2. `## Review guide`, when step 4 calls for one.
3. `## What changed`
4. `## Validation`, when there is relevant evidence or a concrete acceptance check.

This shape collapses on a small change. A heading over a single line is the same ceremony
step 4 warns about, so drop any section that would hold one and let the opening carry it.
Omit an optional validation section when it has nothing useful to add.

## 3. Write the body

Open with one to three sentences covering what the change does and why. A reviewer who
reads only the first paragraph should be able to tell whether they are the right
reviewer.

Where the repository has a template, this paragraph goes inside its first content
section, whatever that section is called. Do not add a lead above the template's first
heading, and do not repeat it once inside.

Then give the substance:

- Explain the mechanism only where it is not obvious from the code. A new abstraction, a
  non-local invariant, or an unusual control flow needs a paragraph. A renamed field does
  not.
- Name behavior changes explicitly, including ones that are side effects of the main
  change. These are what break other people. For a permissions change, state the
  direction: what is now allowed that was not, and what is now refused that was allowed.
- Record decisions with their rejected alternatives. This is the highest-value content in
  most descriptions and it cannot be recovered from the diff. Where there was no real
  alternative, state the decision plainly. Do not manufacture one to fill the slot.
- Include visual evidence for a user-visible change: a screenshot, or before and after
  where the change is a modification. Reference only captures that exist.
- Link the issue, spec, or conversation once. Where there is none, say so only if the
  repository asks for one, through a template section or a contributing guide.
  Announcing "no linked issue" in a repository that does not use them is lint compliance
  rather than information. Never invent a plausible ticket ID to fill the gap; a wrong
  link costs more than no link.

### Validation

Write about the change's behavior and evidence the reviewer can use. Keep the author's
local activity out of the PR body: commands tried, setup problems, interrupted builds,
missing devices or credentials, and lists of platforms tested or not tested locally.

- **Test coverage.** Name the behavior a regression test asserts when that helps explain
  the change. Adding a test establishes coverage, not a successful run.
- **Recorded results.** Cite a relevant CI job, report, or other inspectable artifact
  when its result helps judge the change. State only what that evidence establishes.
- **Acceptance checks.** When the changed behavior needs a specific check, give the
  scenario and expected outcome. Label it as a check, not an observed result. Derive it
  from the change's risks, not from what the author happened to skip locally.
- **Known defects or merge blockers.** State the affected behavior, its impact, and the
  remaining requirement. A reproducible defect belongs in the PR even if it was first
  found locally; describe the defect, not the debugging session.

Do not add status lines such as "Linux packaging incomplete", "not tested on my Windows
11 machine", or "tests not run locally". Do not recast them as generic requests for the
reviewer to finish the author's local checklist. Keep local execution details in the
working conversation or task log when needed for handoff.

An absent result is not evidence of success. Omit unsupported result claims; do not fill
the gap with a local-status disclaimer. Keep required template answers and checkboxes
accurate, as described in step 2.

### Prose

Use ASD-STE100 as the baseline: active voice, one topic per sentence, sentences under
about 25 words, simple tenses, one term per concept for the whole description. Code
identifiers, command lines, and established repository jargon are technical names; leave
them alone. See [references/plain-language.md](references/plain-language.md) for the
rules and the exemptions.

## 4. Add reviewer guidance when it is warranted

Add a review guide when the reading order is not obvious, when you have a specific place
you want attention, or when the change can break things well beyond the files it touches.
Skip it when a competent reviewer will know where to look without being told.

Put it high, directly after the summary. A reviewer should not have to scroll past
compliance checklists to find where to start. `## Review guide` is a reasonable default
heading when the template does not supply one.

On a small PR, guidance is a sentence or two, not a section. Fold it into the opening
rather than raising a heading over it. A heading on two paragraphs is ceremony, and so is
a reading order for six files.

A review guide contains some or all of:

- A recommended reading order, for PRs large enough that the order matters.
- Focus areas: what you are unsure of, security-relevant surfaces, decisions with a
  meaningful alternative, and one-way doors where the ambiguity is genuine.

Write it for a competent engineer. Point at the code and the open question; never explain
how to review code. See [references/review-guide.md](references/review-guide.md), which
opens with a short map of which of its sections you need.

## 5. Cut

Drafts run long, and the excess is almost never in the thinking. It collects in the parts
that feel obligatory: the checklist answers, the inventory of tests, the second statement
of something you already said. Those parts are also the easiest to delete, which makes
this pass cheap and worth doing every time.

Rough anchors for the whole body, before you start cutting:

- A test-only, config, or mechanical change with no behavior change: a short paragraph.
- A small change with a real risk surface: a few hundred words, nearly all of them about
  the risk rather than the diff.
- A focused fix or feature: four or five hundred words.
- A new mechanism with consumers: under a thousand.
- A very large or foundational change: around a thousand, with most of the extra spent on
  the reading order and the focus areas.

These are anchors, not limits. Being over one means look harder at the list below; it
never means cut a decision.

Then take each paragraph and name the decision it helps the reviewer make. If you cannot
name one, delete it. The usual finds:

- Anything the diff shows at a glance. "The hash-scroll logic was generalized", "the
  field was renamed", one bullet per changed line, a restatement of the lockfile. The
  exception is something that looks unintended, such as a name that disagrees with what
  it binds to. The reviewer can see it but cannot tell it is wrong, so it stays.
- Paraphrases of comments this diff adds. The reviewer reads them in place, one scroll
  away.
- Inventories of the tests you added. Keep only coverage facts that affect a review
  decision, such as a changed behavior outside the regression tests. A list of test
  function names reads as padding.
- Explanations of how standard tools behave. Terraform replacing a renamed resource, how
  a test macro polls, when a React effect fires, how a library spawns a child process.
  Explain this change, not the reviewer's tools.
- Local work logs: build attempts, machine-specific setup failures, command histories,
  and lists of checks the author did or did not run.
- The second statement of a fact. State each relevant result or open question once.
- Sentences whose only job is to point at another part of the description. Cross
  references inside one page mean the content is in the wrong place.
- Sentences about the description itself. "A review guide is included because this change
  has a wide blast radius." Write the guide; do not justify it.
- Commit trailers. `Co-Authored-By` belongs in the commit, not in the PR body.

Keep, even when cutting hard: the motivation, the behavior changes, the decisions and
their rejected alternatives, the open questions, and the blast radius. These are the
reason the description exists. When something has to go, cut mechanism before you cut a
decision.

## 6. Self-check

- Does the first paragraph let a reviewer decide whether the PR is theirs?
- Is every claimed result supported by inspectable evidence, with test coverage and
  acceptance criteria clearly distinguished from observed results?
- Have you removed local execution histories and tested/untested platform lists while
  preserving concrete defects and merge requirements?
- Have you verified every factual claim carried over from a commit message?
- Did the cut take a decision, a rejected alternative, or an open question with it? Those
  are the first things to go when you compress, and the last things you should lose. Put
  them back.
- Does the description match the branch as it stands now, rather than the path you took
  to get there?
- If there is reviewer guidance, is it near the top?

## Anti-patterns

**Narrating the branch's own history.** The most common failure. Sentences like "this PR
previously included unit tests, which were removed after review feedback", or "the
description above overstated this and has been corrected", describe a transition that
does not exist in the diff the reviewer is reading. The reviewer sees one state against
the base. Describe that state.

Note what survives the rule: the reasoning usually still matters, only the transition
goes. "The tests were moved after review" becomes "Caller-level tests exercise the
dispatch behavior across match arms" when that is what the current branch contains.

This holds however long the branch is. A branch with thirty commits still reaches the
reviewer as one state against the base.

**Restating the diff.** A file-by-file inventory is the standard way to write something
long that carries no information.

**Reporting the author's workstation.** "Linux packaging incomplete" and "not tested on
my Windows 11 machine" describe a local session, not the change. Remove them rather than
adding an environment-status section. Preserve an actual packaging defect as a specific
failure, its affected target, and its impact on the change.

**Unverified claims, about anything.** Inflated test claims are the familiar case ("fully
tested", "no regressions"), but a confident wrong claim about mechanism is more
dangerous, because a reviewer is less likely to check it. Before asserting what a role
permits, what a flag gates, or what a function guarantees, verify it.

**Grading your own work.** "Comprehensive", "robust", "clean", "properly". Padding that
costs credibility.

**Lecturing the reviewer.** "Please check for edge cases and make sure the error handling
is correct." A competent reviewer already does this, and it displaces the specific
pointers only you can give.

**Leaving a stale description.** After a rework or a force-push, rewrite the body to
describe the current branch. Do not append a revision log to the bottom.
