---
name: theory-of-constraints
description: "Use this skill when the user is struggling with a bottleneck, asking what to fix first, or deciding between competing improvements. Trigger on: \"reviews are taking forever\", \"CI/CD is slowing us down\", \"should we hire or automate?\", \"we can't ship fast enough\", \"the team is overwhelmed\", or any question about what's limiting throughput. Also trigger when someone is optimizing something that might not be the real constraint. This skill applies Goldratt's 5 Focusing Steps — use it rather than guessing at process fixes."
license: Apache-2.0
allowed-tools: Read
---

# Theory of Constraints Skill

Goldratt's TOC gives a principled, formula-backed way to decide what to fix — not by gut feel, but by measuring what's actually limiting the system's goal.

## The three measures (always anchor analysis here)

- **Throughput (T)** — rate at which the system produces its goal (shipped features, revenue, deployments)
- **Inventory (I)** — work in progress: PRs open, tickets in flight, features built but unreleased
- **Operating Expense (OE)** — cost to keep the system running (headcount, infra, tooling)

**Net Profit = T − OE. ROI = (T − OE) / I.**

Improvement priority: ↑T first, then ↓I, then ↓OE. A local efficiency gain that doesn't move T is not an improvement — it's noise.

## Step 0: Diagnose before prescribing (Jonah approach)

Don't declare the constraint until you understand the system. Ask questions that guide the user to see it themselves — this produces better analysis *and* ownership of the fix:

- "Where does work queue up or wait the longest?"
- "What's the one thing, if it went faster, would let everything else go faster?"
- "Where do you feel the pain most — is that also where work piles up, or somewhere else?"
- "What happens when demand spikes — what breaks first?"
- "Are there stages that finish fast but then just wait for the next stage?"

If the user has metrics (cycle time, lead time, DORA), use them. If not, the answers to the above are usually enough to identify the constraint. Only proceed to the 5 steps once you have a clear picture.

## 5 Focusing Steps

1. **Identify** — name the primary constraint explicitly
2. **Exploit** — squeeze maximum throughput from the constraint without new resources
3. **Subordinate** — align everything else to serve the constraint; upstream stages should not overproduce
4. **Elevate** — if exploitation isn't enough, invest to increase constraint capacity
5. **Repeat** — once this constraint is broken, find the next one (don't coast)

See [goldratt.md](references/goldratt.md) for detailed theory, examples from *The Goal*, and the Evaporating Cloud conflict resolution tool.

## Output format

A TOC analysis should be concrete and actionable, not theoretical. Structure it as:

1. **The constraint** — name it explicitly (e.g. "code review turnaround", "manual QA step")
2. **Exploit** — what can be done *right now* to get more out of it without adding resources
3. **Subordinate** — what should the rest of the system stop doing / slow down / change to support the constraint
4. **Elevate** — only if exploitation is already maxed out: what investment would expand capacity
5. **Efficiency traps** — call out any local optimizations that look good but hurt global throughput

Keep recommendations specific to the user's system. Avoid generic advice.