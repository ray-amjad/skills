---
name: plan-phases
description: Plan a non-trivial change as a phase split (2–5 phases) using one planner subagent that fans out its own explorers and sub-planners, then check the split with a different model before any code is written. Use as the first stage of task-lifecycle, or standalone whenever a change is big enough that "where do we cut this" is a real question — "plan this feature", "break this down", "how should we phase this migration".
---

# Plan in phases

Finding *where* a change goes is a different job from making it, and the map it produces is bulky and single-use. So planning runs as **one planner subagent that owns the whole fan-out below it**: the map is built and consumed in one context, and what reaches you is a short phase list rather than a description of the codebase you're about to stop needing.

## Dispatch one planner

Brief it with: the ask in your own words; the repo path; the path to any spec, plan, issue, or design doc the user pointed at, with an instruction to **read it first and treat it as the source of truth for scope**; and these constraints:

- It **owns the fan-out below it** — it may nest explorers, sub-planners, or neither. How many and at what angles is its call; it's the one that will know what this codebase makes hard. A small change in a familiar repo needs no fan-out at all.
- An **explorer** (read-only, told explicitly *do not edit any files*, on a fast/cheap model — the phase split is a judgement, but finding files is not) answers *where the change goes* and makes no judgement.
- A **sub-planner** (read-only, default model) owns **one area of the change** and plans it — and may nest its own explorers, or its own sub-planners if its area still holds separate areas inside it. **Planning is recursive on purpose.** The schema, the API, and the UI of one feature are three areas, and each is planned better by an agent holding only that one. A change that spans four areas planned in one context gets the fourth area reasoned about through everything the first three left behind.
- **The recursion has to narrow, and it stops at three levels of planner.** If the honest structure runs deeper than planner → sub-planner → sub-planner, that's a change too big for one run: come back and say so.
- **A sub-planner returns a plan slice for its area, not a phase split of the whole change** — what its area delivers, the files, the precedent, the gotchas, and the contract it needs from the other areas. The top planner **merges** the slices and owns the final split. Four sub-planners returning three phases each is not twelve phases; a planner that concatenates them has skipped the one judgement only it can make.
- Explorers and sub-planners return **paths, symbols and patterns, not file contents** — an agent that pastes 400 lines of source has moved the context problem rather than solved it.

## What the planner returns

A **phase split: 2–5 phases**, each one a slice that leaves the repo *coherent* — it compiles, and that phase's piece is finished — even though the feature isn't usable until the last phase lands. Each phase carries what a builder needs: what it delivers, the files it's expected to touch, the precedent in this codebase to match, and the gotchas.

- **If the spec is already phased, its boundaries are the split.** Re-cutting a plan the user already wrote just introduces disagreement.
- **A change that fits one focused diff is one phase, and that's a normal answer.** Don't manufacture phases for a two-file feature.
- **If the honest count runs past five, come back and say why** rather than split further — that's a change too big for one run, and the user should decide before it starts.

The planner writes the split to **`.git/lifecycle/phases.md`** — under `.git/` so it can never land in a PR diff — and returns the list. The file is what a resumed run reads; the return value is what builders get briefed from.

## Check the plan — a different model, one pass, before any code

Without this check, a bad cut is found at the most expensive moment there is: after the builders have already spent hours on it. A plan is the one artefact where a second opinion is nearly free — it's one short file, not a diff — and a different model is the right one to ask.

If the Codex CLI is available, use the **codex-consult** skill (or run it directly):

```bash
codex exec "Read .git/lifecycle/phases.md, and <the spec path, if there is one>. Do not write any code. Answer only these: does any phase depend on something a LATER phase builds? does any phase leave the repo broken rather than coherent? is work the ask needs missing from every phase? List only problems, with the phase number. Say 'no problems' if there are none." < /dev/null
```

No Codex? Use a fresh subagent that has seen none of the planning, with the same prompt. Neither available cleanly — say so and build the plan as it stands. A missing check is a stated degradation, never a silent drop.

Three rules keep this a check and not a second planning round:

- **Only ordering, dependency, and missing-work problems count.** Where to cut a plan is a judgement the planner made with the codebase in front of it. A different opinion on taste is not a finding.
- **One pass.** If there are real problems, dispatch one subagent with `phases.md` and the critique, told to **amend** the split — not re-cut it from scratch. Do not check the amended plan again.
- **Show the user the checked split before building starts**, so a wrong reading costs one message instead of the whole run.
