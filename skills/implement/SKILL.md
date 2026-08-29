---
name: implement
description: Implement a spec, plan, issue, or brief while keeping a running implementation-notes.html of decisions, deviations, tradeoffs, and open questions. Use whenever the user hands over a spec/plan/issue and asks to build it, even if they don't ask for notes.
---

# Implement

Implement the spec. As you work, maintain a running `implementation-notes.html` capturing anything the author should know about how the implementation diverges from or interprets the spec:

- **decision** — the spec was ambiguous and you chose
- **deviation** — the spec was clear and you departed from it, and why
- **tradeoff** — alternatives you considered and why you picked what you did
- **question** — anything they should confirm or revise

## Notes

Use `scripts/notes.py` (in this skill's directory — use its absolute path):

```bash
python3 scripts/notes.py init --file implementation-notes.html --spec docs/spec.md
python3 scripts/notes.py add  --file implementation-notes.html \
  --type decision --title "..." --body "..." --where "src/foo.ts:41" --spec "§4"
python3 scripts/notes.py resolve --file implementation-notes.html --id n3 --body "..."
```

`--body -` reads from stdin for multi-line text.

## Rules

- Create the file **before** writing code; log each note at the moment you make the choice, not at the end from memory.
- Bar for a note: would the spec's author push back or be surprised? Don't narrate the code — a handful of notes, not thirty.
- Include `--where` file:line refs so a disagreement goes straight to the code.
- If a question **blocks** what you build next, ask in chat now. Otherwise log it with a defensible default and keep going.
- When done, summarize the open questions and consequential deviations in chat — don't just point at the file.
