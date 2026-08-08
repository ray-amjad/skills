# peer-sessions

Run a fleet of Claude Code sessions on one machine and make them talk to each other with `SendMessage`.

A message sent between sessions arrives as a **user prompt** in the receiving session. This skill turns that primitive into a working loop: spawn a fleet, hand out briefs, end your turn, collect the replies, and tear it down when you ask (teardown is off by default).

`--placement split|workspace|window` decides where the fleet appears — panes beside your own pane, new workspaces in your window, or a new window.

Needs Claude Code **2.1.224 or newer** (older builds publish no messaging socket) and [`cmux`](https://github.com/anthropics/cmux) for the layout.

Also published on its own at [ray-amjad/peer-sessions](https://github.com/ray-amjad/peer-sessions).
