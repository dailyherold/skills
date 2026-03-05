# Theory of Constraints (TOC) Summary

## Core Measurements (Key Principles)
TOC defines a system's **goal** as making money now and in the future, measured by:
- **Throughput (T)**: Rate of generating money via sales (not production).
- **Inventory (I)**: Money invested in things to sell (raw materials, WIP, FG).
- **Operating Expense (OE)**: Money to run the system (labor, utilities, etc.).

Net Profit = T - OE; ROI = (T - OE)/I. Improve by ↑T, ↓I, ↓OE.

**Constraints**: Limits to goal achievement. **Physical** (e.g., machine capacity); **Policy** (rules, measurements like local efficiencies causing excess I). Most real constraints are policy (e.g., batch policies, not actual capacity lacks).

## 5 Focusing Steps (Drum-Buffer-Rope Process)
Cycle continuously; few constraints exist (Boy Scout hike analogy: whole group pace set by slowest).

1. **Identify Constraint**: Pinpoint what limits T (bottleneck). Prioritize by goal impact. Use data/walk floor; often policy (e.g., Goal's NCX-10/robot efficiencies build I, not T).
2. **Exploit Constraint**: Maximize usage without extra cost/capacity (e.g., ensure perfect quality/feed/setup; no idle time).
3. **Subordinate Everything Else**: Non-constraints supply exactly what constraint needs (e.g., no excess production upstream; pace to \"drum\" of constraint).
4. **Elevate Constraint**: If needed, invest to increase capacity (e.g., outsource/add shifts/new equipment).
5. **Repeat/Repeat**: If broken, inertia creates new policy constraint (e.g., Goal's oven/NCX-10 fixed via policy changes, not buying new).

**Improvement Trinity**: What to change? (core problem); To what? (simple solution); How? (induce invention).

## Examples from *The Goal*
- **Plant**: Alex Rogo saves failing plant. Constraints shift: NCX-10 (exploit via parts priority), heat treat/oven (exploit: continuous flow), assembly (policy: balanced imbalance).
- **NCX-10**: Policy ignored capacity; focused on efficiencies → excess I. Subordinate: match releases to constraint.
- **Oven**: Policy batches → WIP fires risk; exploit: drum scheduling.

**Software Eng Applicability**:
- **Bottlenecks**: Dev team capacity (slow reviewer), deploy pipelines (CI/CD waits), QA (manual tests).
  - Identify: Monitor cycle time/lead time (e.g., slowest stage via DORA metrics).
  - Exploit: Prioritize bottleneck work; buffer it.
  - Subordinate: Upstream (coding) paced to bottleneck; no over-dev.
  - Elevate: Automate tests/add reviewers/parallel pipelines.
  - Policy: Fix \"efficiency\" traps (e.g., large PRs like big batches → long reviews).

## Thinking Tools
- **Effect-Cause-Effect (CRT precursor)**: From undesirable effect → hypothesize cause → predict/verify different effect. Builds logical tree to core problem (e.g., robots ↑efficiency but ↑I/↓due dates).
- **Evaporating Cloud (Conflict Resolution)**:
  ```
  A (Objective: ↑Throughput)
  ↓
  B ←→ C (Requirements, e.g., ↓Setup Cost vs ↓Carrying Cost)
     ↓     ↓
    D    ¬D (Conflict: Large vs Small Batch)
  ```
  - Verbalize/inject assumptions (e.g., batch=process=transfer → separate: large process-batch on bottleneck, small transfer-batch everywhere).
  - Evaporate via global goal (T/I/OE), not compromise (EBQ).

**Software**: Cloud for \"fast features vs reliable deploys\" → Assumption: full tests always; inject: trunk-based dev + feature flags.

## Implementation (Socratic/Jonah)
- **Process of Change**: Improvement=change → threat → resistance. Overcome via stronger positive emotion: **induce invention** (ownership beats logic).
- **Socratic Method/Jonah Role**: Ask questions to guide self-discovery (e.g., Jonah to Alex: \"Did inventories drop?\"). Novel format aids immersion.
  - Rules: Present as *their* problem (Effect-Cause-Effect proof); no answers (blocks ownership).
- **Steps**: Consensus on core problem → pilot → elevate politically → review policies.
  - Psychology: Avoid fear/insecurity; use intuition verbalization.
- **Ongoing**: No inertia; policy constraints dominate post-physical fixes.

**Software Applicability**: Jonah-coach devs: \"Does deploy pipeline limit throughput?\" → Induce: \"Separate deploy/release via flags.\" Teams own fixes → sustained agility.

*Generic for reuse; ~850 words.*