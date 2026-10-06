---
name: agent-ready
description: Audit a repository against the proven patterns for making codebases legible to coding agents (context cascade, repo map, noise filters, just-in-time skills, deterministic hooks), then apply the fixes the user approves — generating AGENTS.md/CLAUDE.md hierarchies, a REPOSITORY-MAP.md, committed permission deny rules, extracted skills, and verified hooks. Use this skill whenever the user wants a repo made "agent-ready", asks to audit, improve, or set up CLAUDE.md or AGENTS.md files, says their CLAUDE.md is bloated or being ignored, wants Claude Code to work better in a monorepo or large codebase, mentions the "harness", "repo map", or "context files", or complains that Claude keeps getting lost, reading generated files, or running the wrong commands in their repo — even if they never say "audit" or "harness".
---

# Agent-Ready

Fit a repository with the harness that makes coding agents effective in it: the right context files in the right places, a map when the tree is opaque, noise excluded before it wastes context, reusable workflows packaged as skills, and quality checks moved into hooks.

The flow is always: **measure → audit → report → approval checklist → apply**. The report is a teaching artifact as much as a diagnostic — every finding names the pattern it comes from and gives a one-line why, so a reader learns the vocabulary while fixing their repo.

## Ground rules

- **Never write to the repo before the user approves specific findings.** If the user asked only for an audit or review, stop after the report and offer the checklist — do not present it as pending work.
- **Evidence-only content.** Every line you generate for a context file must trace to something you verified in the repo: a command that exists in package.json/Makefile/CI config, a directory that exists, a convention visible in the code. If nothing verifiable exists for a section, omit the section. Never write filler like "This project uses TypeScript best practices."
- **Thresholds below are defaults to reason from, not rules.** A repo map for a 5-folder project is noise; a 400-line CLAUDE.md for a genuinely gnarly monorepo might be right. State your reasoning when you deviate.
- **Re-runs are drift checks.** On a repo that already has a harness, distinguish `missing` (never set up) from `drifted` (map entries pointing at renamed dirs, hooks invoking commands that no longer exist, context claims contradicted by the current code, workarounds for model limitations that no longer exist).

## Phase 1 — Measure

Size the repo with cheap deterministic commands before reading any file contents. This determines which patterns are even worth recommending.

```bash
# scale and shape
ls -d */ 2>/dev/null | wc -l                                  # top-level dirs
git ls-files | wc -l                                          # tracked files
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head  # language mix
# existing harness
find . -maxdepth 4 \( -name "CLAUDE.md" -o -name "AGENTS.md" \) -not -path "*/node_modules/*"
ls .claude/settings.json .claude/settings.local.json 2>/dev/null
find . -maxdepth 4 -path "*/.claude/skills/*" -name "SKILL.md" -not -path "*/node_modules/*"
ls REPOSITORY-MAP.md 2>/dev/null
# noise candidates
ls -d node_modules vendor dist build out .next target coverage 2>/dev/null
git ls-files | grep -cE '\.(generated|gen)\.|_pb2\.py|\.pb\.go' 2>/dev/null
# command surface (evidence for context files and hooks)
cat package.json 2>/dev/null | head -60   # or Makefile, pyproject.toml, etc.
```

Also check `git log --oneline -5 -- CLAUDE.md AGENTS.md` on existing context files — a file untouched for a year in an active repo is a drift suspect.

Classify the repo: **small** (one team-sized codebase, shallow tree), **large** (many top-level dirs or mixed domains), **monorepo** (multiple services/packages with their own build/test commands). Say which class you landed on and why; it gates everything below.

## Phase 2 — Audit checks

Run every check, but only raise a finding where the measured scale says the pattern would pay for itself.

### 1. Context Cascade — layered AGENTS.md files

Guidance should get more specific as you approach the code being edited: a lean root file with global pointers and critical gotchas, subdirectory files holding local commands and conventions. Only files on the walk-up route from the working directory load, so sibling teams' rules never pollute a session.

Check: does a root context file exist? In a large repo/monorepo, do the subtrees with their own build/test/deploy reality have their own context file? Is universal guidance buried in a leaf, or subtree detail crammed into the root?

Heuristic: a subtree earns its own file when it has its own test or build command, its own deploy story, or its own domain vocabulary. Root file target is pointers + gotchas, roughly a screenful.

### 2. Repo Map — REPOSITORY-MAP.md

When directory names don't reveal what lives inside (codenames, legacy partitions, many top-level folders), the agent starts every session with blind search. A boring, factual map — folder, purpose, main entry points, owner if useful — lets it scan before opening anything.

Check: are the top-level names self-explanatory? Heuristic: worth it from roughly 15+ top-level dirs, or fewer if the names are opaque (`alpha/`, `core2/`, `legacy-v3/`). Stale entries are worse than no map — on re-runs, verify every listed folder still exists and does what the map claims.

### 3. Noise Filter — committed deny rules

Generated files, build artifacts, and vendor code pollute every search and read. Exclusions belong in version control so the whole team inherits them: `permissions.deny` rules for `Read()` in `.claude/settings.json`.

Check: do noise directories exist (from Phase 1) without corresponding committed deny rules? Is `.gitignore` handling build output but `.claude/settings.json` absent or silent? Flag over-aggressive exclusions too — hiding files that source code imports from.

### 5/6. Just-in-Time and Scoped Skills

Specialized workflows (deploy runbooks, migration recipes, release checklists) living inside a context file cost every session what only some sessions need. As skills they load on demand, and placing the skill file inside the subtree it serves (`services/payments/.claude/skills/`) scopes it for free — the same walk-up that loads context files discovers skills.

Check: does any context file contain multi-step workflow prose? Heuristic: a section with 3+ sequential steps, or that reads as "how to do X" rather than "what is true here", belongs in a skill. Also check existing `.claude/skills/`: are repo-wide skills actually subtree-specific (move them down), or subtree skills actually universal (move them up)?

### 9. Deterministic Checks — hooks

"Always run the linter before committing" written as an instruction competes with every other instruction and gets forgotten. As a hook it runs on the matching event whether the model remembers or not.

Check: does the context file contain instructions of the form "always/never run X on Y" that a hook could enforce? Do lint/format/typecheck commands exist in the repo's tooling with no hook wired?

**Only propose hooks for commands you verified.** Before including a hook in the report, run the command once yourself: it must exist, exit clean on the current tree, and finish fast (a few seconds — a slow hook drags every future session). If it fails or crawls, report that instead of the hook.

### Quality audit of existing context files

Existing CLAUDE.md/AGENTS.md content gets audited against the same principles the generated ones follow:

- **Bloat**: beyond ~200 lines, ask what each section is paying for. Session-scoped notes, changelogs, and one-time migration state don't belong.
- **Misplaced content**: workflow prose → skill (check 5/6); "always run X" rules → hook (check 9); style rules a linter/formatter already enforces → delete; code snippets → replace with file path references (snippets go stale).
- **Vague instructions**: "follow best practices", "leverage the X agent" — delete; they spend attention and change nothing.
- **Discoverable facts**: anything the agent learns from reading the code in two searches (naming conventions used consistently everywhere) doesn't need saying.
- **Missing relevance signals**: flat walls of unconditional rules get partially ignored, because the harness tells the model the file "may or may not be relevant". See the `<important if>` technique in Phase 5.
- **Model-era workarounds**: rules that read like babysitting ("make only single-file changes", "don't attempt multi-step refactors") were written for weaker models and now constrain stronger ones. Flag as drifted.

### Advisory (report one line each, never act)

- **Symbol Lookup (LSP)**: if the repo is multi-language or uses C/C++/Java/C#, note that a code-intelligence plugin turns thousand-match greps into three resolved references.
- **Scout Subagent**: for big refactors in this repo, exploration belongs in a read-only subagent that writes findings to a file the editing session reads.
- **Search-as-a-Tool**: if answers routinely live outside the repo (design docs, runbooks), an MCP bridge to existing internal search is the pattern.

## Phase 3 — Report

Deliver the report in the conversation (no report file). Rank findings by impact on day-to-day sessions — context correctness first, then noise, then workflow packaging, then hooks. For each finding:

```
N. [Pattern name] — missing | drifted | ok
   Evidence: what you measured/read (paths, line counts, commands)
   Proposed fix: the exact artifact you would create or change
   Why: one sentence tying it to the pattern's payoff
```

Include the `ok` findings briefly — telling a student what the repo already does right is half the teaching value. End with the advisory trio and the repo classification.

## Phase 4 — Approval

Present every proposed fix as one multi-select checklist (AskUserQuestion with `multiSelect: true` if available, otherwise a numbered list to reply to). One entry per artifact, phrased as the concrete change ("Create REPOSITORY-MAP.md covering 23 top-level dirs", "Extract deploy runbook from CLAUDE.md into services/api/.claude/skills/deploy/"). Apply exactly the approved set, nothing more.

## Phase 5 — Apply

### File convention: AGENTS.md canonical, CLAUDE.md symlink

Every context file you create is an `AGENTS.md` with a relative symlink `CLAUDE.md -> AGENTS.md` beside it, so the same content serves every agent. When editing an existing plain CLAUDE.md, convert it to this pair unless the repo has already standardized otherwise. If symlinks are impractical (e.g. the repo must support Windows checkouts without symlink support), write identical copies and say so.

### Writing context files

Structure every generated or rewritten file as:

1. One-line project identity, bare.
2. Project map (or pointer to REPOSITORY-MAP.md), bare.
3. Commands table wrapped in one `<important if="you need to run commands to build, test, lint, or generate code">` block — keep every command you found evidence for.
4. Each remaining rule or domain section in its own `<important if="...">` block with a **narrow, specific** condition ("you are adding or modifying API routes", not "you are writing code").

The `<important if>` blocks exist because the harness injects every context file with a note that it "may or may not be relevant" — unconditioned content gets skimmed. Foundational context (identity, map, stack) stays bare because it's relevant to ~every task; everything conditional gets a targeted trigger. Never group unrelated rules under one broad condition.

Apply the evidence-only rule ruthlessly: commands verified in tooling files, paths verified with `ls`, conventions verified in at least two places in the code. Tribal knowledge you can't verify gets left out — mention in the summary that the owner can add gotchas the code can't show.

### REPOSITORY-MAP.md

Standalone file at the repo root; the root AGENTS.md points to it. One line per top-level folder: name, factual purpose, main entry point if non-obvious. No architecture prose, no aspirations — stale narrative misleads with confidence. Verify every line against `ls` output.

### Noise filter

Merge deny rules into `.claude/settings.json` — read the existing file first and preserve everything in it; never clobber. Rules look like `"deny": ["Read(./dist/**)", "Read(./vendor/**)"]` under `permissions`. Only deny paths you confirmed exist and confirmed are generated/vendored (check `.gitignore`, build configs, or file headers). Mention that individual devs can override locally in `.claude/settings.local.json` — that's the escape hatch for whoever owns the generator.

### Skill extraction

For each workflow section approved for extraction: create `<subtree>/.claude/skills/<name>/SKILL.md` in the subtree the workflow belongs to (repo root `.claude/skills/` only if genuinely repo-wide). Frontmatter `name` + a description stating what it does **and** when to reach for it. Body keeps every concrete step, command, and failure note from the original — this is a move, not a summary. Then delete the section from the context file, leaving a one-line pointer only if discoverability would otherwise suffer.

### Hooks

Wire only the hooks whose commands you verified in Phase 2 (exists, exits clean, fast). Add to `.claude/settings.json` hooks config, scoped to the narrowest matching event (e.g. PostToolUse on file edits for a formatter). Show the user the exact command and timing you measured. Then delete the now-redundant instruction from the context file — the whole point is moving enforcement out of prose.

### After applying

Summarize: artifacts created/changed with paths, what was deliberately left out and why (unverifiable tribal knowledge, patterns below the repo's scale), and the one-line advisory trio if relevant. Suggest committing the harness files so the team inherits them.
