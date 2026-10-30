# When a surface is out of reach

A surface you can't drive is the most likely place for an unproven bug. Never drop it silently. Name the blocker, offer the unlock, and let the user decide whether it is worth the setup.

| Blocker | Unlock to suggest |
|---|---|
| The app needs services that aren't running (Postgres, Redis, a queue) | `docker compose up` with the repo's compose file, or write a minimal one for verification. If there's no Docker, the database's own local install or an in-memory/SQLite mode if the app has one. |
| The app only runs in a cloud environment, or setup would touch the user's real machine state | Run it in a sandbox: a dev container, a throwaway Docker container, or a cloud sandbox or remote dev box. Tell the user which setup steps the sandbox does that their real environment won't. |
| Login or SSO in the way | A seeded test user created by a script, a dev-only auth bypass that already exists in the repo, or a saved browser session (Playwright `storageState`). Or open a visible browser, let the user sign in once, and continue from the saved session. Never use the user's real account or type their password. |
| Email or one-time-code sign-in | A fresh plus-address per run (`you+run123@yourdomain.com`) whose inbox the agent can search, or a local mail catcher (Mailpit). Read the code from the message text. Screenshot before spending a one-time link. |
| Behaviour differs by role or plan | One seeded account per role or plan, driven in separate browser contexts. Confirm which user each context is signed in as before the first check. |
| OS- or browser-specific behaviour (Windows, Safari) | A real machine or cloud runner with that OS or browser. Emulation layers hide the bugs you are looking for. If none is available, mark it not covered and name the platform. |
| Rare states (trial ending, pending payment) and OAuth connect flows | A seed script that creates the state, runs the flow and removes it. For OAuth, a local fake of the provider; on a live provider, stop at the consent screen and mark the rest not covered. |
| Paid or external APIs (Stripe, OpenAI, Twilio, email) | The provider's test mode and keys, its local emulator or CLI (`stripe listen`, Mailpit, LocalStack, Firebase/Supabase local), or a recorded fixture at the network boundary. Mock only where the app already isolates that service. |
| No browser available to the agent | Install Playwright (`npx playwright install chromium`) and drive headless, or connect a browser tool (Playwright MCP, Claude in Chrome). |
| Native desktop or mobile app | Electron/Tauri: launch with a debug port and drive through CDP. iOS: Simulator with `xcrun simctl`. Android: an emulator with `adb`. If none of these exist on this machine, say which machine could run it. |
| Production-only data or behaviour | A staging URL with a test account, or a seed script that creates a realistic local copy. Never verify by writing to production. |
| Destructive actions (delete, publish, send, charge) | A dry-run flag if one exists (check what it actually skips by watching files, network and git), a disposable target (a test inbox, a scratch bucket), or leave it undriven and say so in the receipt. |
| Port, profile or data dir shared with the user's own running copy | A separate port, a temp data dir (`mktemp -d`), a separate browser profile and tmux socket. If the app can't run twice, the skill must refuse to drive an instance it didn't start. |
| Needs secrets the agent doesn't have | Ask the user to add them through their normal secret store. Don't ask them to paste secrets into the chat. |

When you present an unlock, give the user the cost: "about 5 minutes once, then nothing per run", or "needs a Stripe test account". Let them choose. Record unlocks they turn down in the generated skill's Gotchas so the next agent knows that surface is unproven and why.
