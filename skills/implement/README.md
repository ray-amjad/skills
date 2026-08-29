# implement

Implement a spec while keeping a running `implementation-notes.html` — decisions,
deviations, tradeoffs, and open questions the spec didn't settle. Notes are appended
via `scripts/notes.py` into a single self-contained HTML page. Python 3, no deps.

## Credits

Inspired by [this tweet from Thariq (@trq212)](https://x.com/trq212/status/2056418157305454805):

> Implement `<SPEC>`. As you work maintain a running implementation-notes.html file
> that captures anything I should know about how the implementation diverges from or
> interprets the spec, including:
>
> - Design decisions: choices you made where the spec was ambiguous
> - Deviations: places where you intentionally departed from the spec, and why
> - Tradeoffs: alternatives you considered and why you picked what you did
> - Open questions: anything you'd want me to confirm or revise
