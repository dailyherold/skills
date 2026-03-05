---
name: generating-lamport-problem-statements
description: "Use this skill to apply Leslie Lamport's method whenever the user is in solution-mode without a clear problem statement. Trigger on: \"should I use X or Y?\", \"I'm thinking of using [approach]\", \"we're debating between A and B\", \"going back and forth on whether to\", \"what are the tradeoffs between\", \"which is better\", \"what should the acceptance criteria be\", or any explicit request to apply Lamport's method. Also trigger when someone proposes a specific technology or architecture before stating what problem it solves. The skill contains an intervention framework and output format — use it rather than engaging with solution details directly when no problem statement has been established yet."
license: MIT
allowed-tools: Read
---

# Lamport Problem Statement

People naturally jump to solutions. This skill helps redirect that energy: before
evaluating *how* to solve something, get clear on *what* you're solving and *what
correct looks like*. Once correctness conditions are explicit, comparing solutions
becomes objective rather than intuitive.

## When to gently intervene

If the user is already deep in solution-mode — proposing an approach, debating
tradeoffs, or asking "should I use X or Y?" — pause and check: has the problem
been stated? Have correctness conditions been defined? If not, offer to establish
them first. Frame it as making the rest of the conversation easier, not as a
correction.

## Process

1. **State the problem** — What needs to change, and for whom? State it
   independently of any solution. If the user hasn't stated it, offer a draft
   and align via conversation. Keep it to 1–3 sentences.

2. **Define correctness conditions** — What must be true for any solution to
   be considered correct? These are the criteria a solution will be judged
   against. Draft them if the user hasn't, and refine until they feel complete
   and specific. (Also called: success criteria, acceptance criteria.)

3. **Capture the solution** *(optional)* — Once problem + conditions exist,
   record the proposed solution. If multiple solutions are on the table, this
   is where they get named.

4. **Prove or evaluate** *(optional)* — Show how the solution satisfies (or
   doesn't satisfy) each correctness condition. If conditions aren't met,
   surface that explicitly.

## Output format

When producing a problem statement, use this structure:

> **Problem:** [1–3 sentence statement of what needs solving, independent of solution]
>
> **Correctness conditions:**
> - [Condition 1]
> - [Condition 2]
> - ...
>
> **Solution:** [if available]
>
> **Evaluation:** [how the solution maps to each condition, if both are present]

If you're mid-conversation and only have problem + conditions so far, output
just those and offer to return once a solution is proposed.
