---
name: design-variations
description: Show the user several genuinely different design options for a UI change — rendered in their real app's own design system — before any of it is built. Use whenever the ask is to explore or decide how something should look rather than to ship it — "show me a few variations", "design options for X", "mock up how Y would work", "I don't like how this looks", "make it look better", "what else could this be" — or as the front half of a build when the user clearly hasn't picked a direction yet. They pick a winner; task-lifecycle builds it.
---

# Design variations

The user hasn't decided yet. Your job is to make deciding cheap: put several genuinely different options in front of them, **rendered in their own product**, and let them point at one.

```
scope the screens → capture the REAL page → N variations as edits to that capture → user picks → get specific → states gallery → comments → hand the winner to task-lifecycle
```

## The one rule

**A variation is an edit to the real page, never a drawing of it.** Start from the app's own rendered markup and its own stylesheet, and change the part under discussion. Everything you didn't touch — the nav, the type, the spacing, the buttons — is the product's, byte for byte, because you never retyped it.

This exists because the obvious approach fails: pretty standalone HTML written from scratch looks like *a* settings page, not *theirs*, and the first reply is always "it should be in the design of the actual site". A from-scratch mockup also can't be judged — the user can't tell whether option 3 reads better than option 2, or whether both just look unfamiliar.

So: **the palette, the fonts, the radii, the shadows, and the component shapes are not yours to vary.** They're the design system, they're already decided. Vary the thing under discussion. Nothing else.

## 1. Scope it

Answer two questions from the codebase, not by asking (unless you genuinely can't tell):

**Which screens does this touch?** Usually more than one, and the extra ones are where the design actually gets decided. A "transfer ownership" ask is the settings page *and* the confirm step *and* what the ex-owner sees afterwards. Enumerate them, with routes, before designing anything.

**What's genuinely in question?** A **flow** ask (a new capability, a destructive action) varies where the control lives, how it's confirmed, how much friction — and holds the entire visual language fixed. A **look** ask ("this page is messy") varies layout, density, hierarchy, what's promoted vs demoted — and holds palette, type scale, and component primitives fixed.

**Default to 5 variations** for full pages; up to 10 is fine for a single small component. More than that and options stop being comparable; fewer and the user is choosing between the first two things you thought of.

## 2. Capture the real page — this is the gate

Boot the app, then for each screen capture three things with Playwright: a baseline screenshot, the rendered markup (`document.documentElement.outerHTML`), and every stylesheet the page actually used, inlined. Then make the capture openable on its own:

- **Strip every `<script>`.** Non-negotiable: the hydration bundle 404s from `file://`, the framework finds markup it can't reconcile, and it *empties the body* — blank page, no error. Any interactivity you want (a tab switching, a modal opening) you write yourself in ten lines of vanilla JS.
- **Inline the CSS** as one `<style>` block; drop the `<link rel="stylesheet">` tags.
- **Base64 anything small and local** — logos, avatars, icons carry more "this is our product" than their size suggests. Big or remote assets keep their absolute URLs.

**Do not write a single variation before the capture opens and looks like the app.** Re-open the `base-*.html` in Playwright, screenshot it, compare against the baseline. If they don't match, fix the capture — every variation inherits the fault, five times over.

**If the app won't boot in ~15 minutes, stop trying.** Fall back to reading the design tokens from source — `globals.css` custom properties, the Tailwind config, the component primitives — and hand-build the page chrome from them. It's meaningfully worse, so say so: *"built from the design tokens rather than a live capture — close, not exact."* Keep working files in a scratch directory outside the repo (`/tmp/design/` or similar) — a mockup committed into the repo lands in a later PR diff.

## 3. Build the variations — one subagent per option, in parallel

Each subagent gets: its assigned direction and the reasoning behind it; the captured `base-*.html` for **every** screen its direction touches; the real data and copy already in the capture; and the instruction to **edit the capture, never author a page**. One output file per variation — its screens stacked vertically under plain labels (`1 · Settings`, `2 · Confirm`, `3 · After`), so one file is one complete answer.

Make them actually differ. Five options that are one option with the button in five places has taught the user nothing — push two of them past where you think they'll land, because "definitely not that" is how people discover what they do want.

## 4. Present, and let them explore-then-exploit

Open the variations for the user (or hand them the file paths), each numbered, named, and captioned with the one sentence that says what makes it different. Include the baseline as `0 · today` when the change is a redesign — options are judged against what exists. Close with an explicit ask: *"reply with a number, or a number plus a change."*

The loop from here is **explore, then exploit**: they point at the one or two worth more time ("more in the style of 1 and 2"), you generate a fresh round *inside* that style, and you repeat until one variant is close enough to edit directly. Then loose direction stops paying and the prompt becomes a list of edits you could hand to a person: *use mono plus accent, remove the read receipt, move the suggested replies above the input.*

Once a variant is nearly final, two moves make the last mile cheap:

- **A states gallery, grounded in the codebase.** The happy path hides most of the design. Send an explorer into the code to inventory the real states — closed, unread badge, empty, error, every settings combination — and render the winning variant in all of them. States the agent imagined are states the user reviews and never ships.
- **Comments in the artifact, diff at the top.** Put a comment box on every state so the user reviews the whole gallery in one pass and exports their notes as markdown. When you apply the notes, move everything that changed to the top of the page with a labelled before/after pair for each — that's what makes the next review take one minute instead of ten.

## 5. They pick — hand it to task-lifecycle

A reply of `3`, or `3 but drop the typed confirmation`, or `2's placement with 4's warning` is the decision. **You don't implement it here.** Compact the conversation if it has grown long — safe, because the artifact is a file on disk and it, not the chat, is the spec — then hand the chosen variation's HTML path, the screens it covers, and any last modification to the **task-lifecycle** skill. This skill decides *what to build*; that one builds it properly.

If the answer is "none of these", that's information: ask what's missing in one line and run another round on a different axis. Don't re-render the same five with new colours.

## Traps

- **Scripts left in the capture blank the page** — silently, from `file://`.
- **A mockup inside the repo ends up in a PR.** Scratch directory only.
- **Don't invent colours.** The palette came from the capture. A variation that needs an accent the design system doesn't have is a finding to report, not a licence to pick one.
- **Nothing here is a code change.** Don't commit anything; the output is a decision.
