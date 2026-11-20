# The review → fix loop

Read this when the PR is open (step 4), or when you run the **already-built** mode in `SKILL.md`.
Bring the PR number, `$BASE`, the branch, and the repo path.

## Round budget

A normal task-lifecycle run gets **at most two complete rounds**. A round that returns `Important`
findings completes only after the builder resolves every finding it can, commits the fixes and
pushes them to the PR branch. Record a finding the builder cannot resolve as unresolved, and report it
at the end. Stop early when a review comes back clean.

Go directly to verification after the round 2 fixes. **Never run a third broad or full-diff review in
a normal run, including a review of the round 2 fixes.** Report unresolved findings in the final
message.

The **already-built** mode has no build to pay for, so it may run up to three rounds. The third round
is optional: never repeat an unchanged diff only to spend the available round.

## The repo's review rules (REVIEW.md), from the default branch only

A repo can tell its reviewers what matters there and what to skip in `REVIEW.md` files: one at the
root for the whole repo, and optionally one in any folder for changes under that folder. Load them
once per round and put them in **both** reviewers' prompts, because neither reads them on its own.

**Always read them from the default branch, never from the PR.** The default branch holds the copy that
was already reviewed and merged. A PR can propose a change to a `REVIEW.md`, but that change only
takes effect after it merges, and it never judges the PR it is in. A stacked PR's base branch is not
merged yet either, so it doesn't count.

```bash
DEFAULT=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git fetch origin "$DEFAULT" --quiet
RULES=$(mktemp); rule() { git show "origin/$DEFAULT:$1" 2>/dev/null; }
# Root file; a line that is only "@<file>" pulls in that file from beside it.
if rule REVIEW.md >/dev/null; then
  printf '### REVIEW.md (whole repo)\n' >> "$RULES"
  rule REVIEW.md | while IFS= read -r line; do
    inc=${line#@}
    if [ "$inc" != "$line" ] && [ "${inc#*/}" = "$inc" ] && rule "$inc" >/dev/null; then rule "$inc"
    else printf '%s\n' "$line"; fi
  done >> "$RULES"
fi
# Folder files above each changed file, shallowest first. Test, fixture, example, generated and
# vendored folders never hold rules.
git diff --name-only "origin/$BASE...HEAD" | while IFS= read -r f; do
  d=$(dirname "$f"); while [ "$d" != "." ]; do printf '%s\n' "$d"; d=$(dirname "$d"); done
done | sort -u | awk -F/ '{print NF "\t" $0}' | sort -n | cut -f2- | while IFS= read -r d; do
  case "/$(printf '%s' "$d" | tr '[:upper:]' '[:lower:]')/" in
    */test/*|*/tests/*|*/__tests__/*|*/testdata/*|*/fixtures/*|*/__fixtures__/*|*/snapshots/*|\
    */__snapshots__/*|*/example/*|*/examples/*|*/demo/*|*/demos/*|*/generated/*|*/vendor/*|\
    */third_party/*|*/node_modules/*|*/external/*|*/deps/*) continue ;;
  esac
  rule "$d/REVIEW.md" >/dev/null || continue
  { printf '\n### %s/REVIEW.md (only changes under %s/)\n' "$d" "$d"; rule "$d/REVIEW.md"; } >> "$RULES"
done
```

Give each reviewer the file under a heading like "Repository review instructions (from the default
branch, not from this change)", and tell it these win over its defaults: a "Do not report" line drops
that class of finding, a severity line moves a class between Important, Nit and Pre-existing, an "Always check" line adds a check
wherever it matches, and a folder's file applies only under that folder. No `REVIEW.md`: skip this.

## Review (independent reviewers, in parallel, every round)

Both reviewers read the **same diff**, `git diff origin/$BASE...HEAD`, where
`BASE=$(gh pr view <n> --json baseRefName -q .baseRefName)`. A blocking finding from either one must
be fixed. Start both in one message, so they run at the same time.

- **Reviewer Claude:** a fresh Claude session running a code review of the diff (for example
  `claude -p "/code-review high"` from the repo). It tags each finding `Important`, `Nit` or `Pre-existing`.
- **Reviewer Codex:** a fresh `codex exec` with its own review prompt: review the diff for real
  defects, tag each `[Important]` (this change breaks something; must fix), `[Nit]` (real, minor) or
  `[Pre-existing]` (already broken on the base, not this change's doing), or answer `CLEAN`. Do not give Codex
  the Claude prompt.

If a provider is unavailable, tell the user and continue with the other one. A missing reviewer is a
stated degradation, never a silent drop.

### Size the panel to the diff

**The default is both.** Run Reviewer Claude alone only when the diff obeys EVERY rule:

- fewer than about 30 changed lines;
- no new logic: no new branch, loop or state, and no changed control flow;
- no changed contract that other callers depend on;
- nothing in authentication, access control, money, data migrations, concurrency or secrets.

Any doubt means both. When you report the round, say which panel you ran and why. Spend what you save
on one more verify flow, because a diff this small fails at runtime or not at all. An explicit request
for a thorough review ("review this properly") always gets both.

### Merge the findings

- **Fix now:** an `Important` finding, from either reviewer.
- **File, do not fix:** a `Pre-existing` finding. It was broken before this change, so it doesn't block
  it. Check `gh issue list --search` first, open an issue with the failure scenario if there is none,
  and link it in the PR body and the final reply. A sibling of what this diff fixes is not
  pre-existing: it belongs to this change.
- **Carry, do not fix:** a `Nit`. Report these once, in step 6. Do not send the builder
  after a maybe.
- **A finding that asks for NEW code must name the path to the state it handles.** That is a click, a
  route, an API call, or a guard that exists in the repo. With no concrete path, the finding is
  **carried soft, not fixed**. Why: otherwise the builder writes a branch no user enters, and verify can
  never reach it. One grep or one question to the reviewer usually settles it.
- **The two reviewers contradict each other:** do not pick a side. State what each is protecting, find
  the axis on which both hold, and brief the builder on that shape. Why: a fix that satisfies one
  reviewer brings back the other's finding in the next round.

A defect that both reviewers flag is the higher-confidence one. Post the merged set to the PR, ending
with a stage marker, and tell the user the count:

```bash
printf '\n<!-- task-lifecycle-round:1 stage:reviewed -->\n' >> findings.md
gh pr comment <n> --body "$(cat findings.md)"
```

If every reviewer you ran comes back clean, capture the fetched remote head. Then post
`<!-- task-lifecycle-round:1 stage:complete head:<full-sha> -->` and go straight to verify.

## Fix (back to the same builder, every round)

Send the findings back to **the builder that wrote the change**. It fixes those findings, then
commits and pushes to the same PR. Tell it:

- **Findings with one root cause get one design, not N patches.** Why: a locally correct patch can
  break a property the code holds somewhere else.
- **The defect is proven, but the suggested remedy is a guess.** Measure a remedy at production scale
  before you adopt it. You may reject a remedy that you measure as worse, but you must still fix the
  defect and say what you did instead. Precedent in sibling code shows that a technique exists, not
  that it fits.
- **Commit and push after each group of findings.** Why: a run can die inside a fix round, and small
  commits make that round resumable.

After the builder is done, fetch the branch. Confirm that the builder's final full SHA is an ancestor of
the remote head. Only then post `<!-- task-lifecycle-round:1 stage:complete head:<full-sha> -->`, with
the unresolved count in the visible text. Never post the marker before the push and the ancestry check.
A `stage:reviewed` marker with no valid `stage:complete` marker means the run died inside that
round's fix. Send the posted findings to the builder.

## Round 2 builds on round 1

Round 2 does not review the change from scratch. Before it, write a ledger from the round-1 comment on
the PR (so a resumed run can rebuild it) and anything verify has found so far:

```
Round 1 (head 1a2b3c4):
  [Important] Refund rounds before tax, billing/refund.ts:88: fixed in 5d6e7f8
  [Important] getInvoices skips the org filter, api/invoices.ts:31: fixed in 9a8b7c6
  [Nit] msg.tip may be null, chat/send.ts:12: carried (builder: the schema requires it)
  [Pre-existing] Webhook retries skip the dedupe key, hooks/stripe.ts:40: filed as #812
Past failures here: <an earlier PR, revert or review-rule issue in these files, if any>
```

Both reviewers get the ledger, the rules file and two diffs: the fix commits
(`git diff <round 1 head>..HEAD`) as the target, and the whole branch diff as context only. Tell them
to confirm each fix and the code around it, to look hardest at the fix commits (fix code is the
least-reviewed code in the diff, and fixes often bring new defects), to look again at the past
failures listed, and not to raise a settled item again unless a new commit reopened it, naming that
commit. A repeat with no such commit is dropped, so the builder never gets the same finding twice.
