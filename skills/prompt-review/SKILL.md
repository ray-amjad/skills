---
name: prompt-review
description: Review the current coding session and give the user direct, specific feedback on their prompting — what worked, what didn't, and the exact rewrites that would have gotten better results faster. Run at the end of a session, once the work landed — "/prompt-review", "how could I have prompted that better", "review my prompts".
---

# Prompt review

Review this coding session and provide feedback on the user's prompting style. The goal is to help them communicate with the assistant so they get better results faster. Analyze the conversation and provide:

## 1. Prompts that worked well

- What did the user say that was effective?
- Why did it work?

## 2. Prompts that could have been better

For each problematic prompt:

- **What the user said:** quote their actual prompt.
- **The issue:** why it was unclear, ambiguous, or led to wrong results.
- **What they should have said:** a rewritten version that would have gotten the result they wanted faster.
- **Why it's better:** brief explanation.

## 3. Patterns to fix

- Too vague in certain areas?
- Too much or too little context?
- Wrong terminology for this codebase?
- Asking for multiple things that should be broken up — or the reverse?

## 4. Missing context they should have provided

- What did the assistant have to ask for or guess at?
- What should be included upfront next time?

## 5. Quick reference for next session

Three to five concrete rules for prompting on this codebase, based on the mistakes made in this session.

Be direct and specific. Actionable feedback, not general advice. Best run at the *end* of a session, once the change the user wanted has actually landed — that's when the full arc of what worked and what needed pushing is visible.
