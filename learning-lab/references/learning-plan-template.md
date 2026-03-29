# Learning Plan Template

Use this structure when producing a learning plan from the learning-lab skill.
Replace all `[bracketed]` placeholders. Remove this instruction line before delivering.

---

# [Domain / Role]: [Specific Objective Title]

**Learner:** [Name / handle]
**Time budget:** [X hrs/week]
**Deadline / milestone:** [Date or event]
**Plan created:** [Date]

---

## Why This Plan Exists

*Verbatim quotes from the learner during Genesis Protocol. Do not paraphrase —
exact words reveal motivations that summaries lose. Pull 3–6 quotes that capture
the "why", the constraints, and any frontier material the learner referenced.*

> "[Exact quote 1 — typically the trigger: what prompted this]"

> "[Exact quote 2 — the credibility target or audience]"

> "[Exact quote 3 — constraints or deadline pressure]"

> "[Exact quote 4 — first deliverable or application context, if stated]"

*Distilled motivations (your synthesis, not their words):*

- **[Motivation label]:** [One sentence distillation]
- **[Motivation label]:** [One sentence distillation]

---

## Correctness Conditions

*What must be true for this plan to be considered successful. Drafted during Genesis
Protocol, refined until each is specific and observable. Each level may have more than
one condition — don't collapse distinct conditions into one.*

**Primary** — core capabilities needed, stated independently of method:
- [ ] [Condition 1: "I'll know I've succeeded when [specific, observable outcome]"]
- [ ] [Condition 2 if genuinely distinct from above]

**Supporting** — prerequisites that enable the primary conditions:
- [ ] [Condition: "I can use [concept] fluently in service of Primary condition N"]

**Application** — artifact(s) that prove the learning transferred:
- [ ] [Condition: "The artifact exists, works, and I can explain every decision in it to [specific audience]"]

*Completeness check: Is there any way this plan could satisfy all conditions above and
still feel like a failure? If yes, a condition is missing.*

---

## How to Work Through This Plan

The agent is your Socratic tutor and critic — not your answer generator.

**Default interaction:** You generate first, agent challenges second. For conceptual
questions, expect guiding questions, not direct answers. Direct answers reserved for
tooling, syntax, and debugging.

**The Exercise Loop (every phase):**

| Step | What you do |
|---|---|
| **1. Attempt** | Write what you know before reading/watching anything |
| **2. Consume** | Read, watch, listen — pause to sketch before continuing |
| **3. Build** | Construct the artifact |
| **4. Break** | Deliberately sabotage it — change parameters, find failures |
| **5. Teach** | Explain to agent (Socratic mode) or write for a specific audience |
| **6. Bridge** | Connect to another phase, your job, or a different domain. Write it down. |

**Recommended tools:** [e.g. tools relevant to this domain — pick per phase]

---

## Phase [N]: [Phase Title] ([Week range, X hrs])

**Bloom's level:** [Apply / Analyze / Evaluate / Create]
**Agent mode:** [Socratic / Direct / Mixed]
**Time allocation:** [e.g., 30min Attempt | 1h Reading | 2h Build | 30min Teach]

### 1. Attempt

*Before reading or watching anything, write your answers to:*

- [Question 1 — surfaces prior beliefs about this phase's topic]
- [Question 2]
- [Question 3]

Save your answers. You'll compare them after Consume.

### 2. Consume

*[List curated resources — include why each one, not just what it is]*

- [Resource 1](url) — [what it teaches and why it's on this list]
- [Resource 2](url) — [what it teaches]

### 3. Build

*[The artifact for this phase — code, diagram, explanation, or prototype]*

```[language]
# [starter code or scaffold]
```

### 4. Break

*[Specific sabotage exercises — concrete, not vague]*

- [Specific thing to break and what to observe when it breaks]
- [Edge case to introduce and what it reveals]

### 5. Teach

**Agent Prompt (Socratic):** *"[You explain X to the agent in a specific framing,
agent challenges and pushes back]"*

### 6. Bridge

*[Explicit connection to another phase, the application artifact, or the real job]*

**Write in Key Insights file:** [Specific prompt or question to answer in writing]

### Retrieval Checkpoints

- **+1 day:** [What to recall from memory, without notes]
- **+3 days:** Agent quizzes on: [key concepts]. Identify 2 weakest sub-skills.
- **+1 week:** Drill the weakest sub-skills from day 3.

---

*[Repeat Phase block for each phase]*

---

## Interleaving Map

| During Phase | Revisit From | Exercise |
|---|---|---|
| [Phase N] | [Phase M] | [Specific exercise using earlier concepts in current context] |

---

## Stress Test Log

Every 2 weeks: find one piece of external material at the frontier. Evaluate against
your correctness conditions. Log what changed.

| Date | Source | What it challenged / added | Conditions affected | Plan changes |
|---|---|---|---|---|
| | | | | |

---

## Key Insights File

Maintain a separate `key-insights.md` with:
- Bridge connections between phases (most valuable for transfer)
- Concepts that surprised you or contradicted your Attempt predictions
- Things you got wrong and corrected

---

## Learning Retrospective

When you finish (or step away from) this plan, ask the agent to run a learning retro.
It takes 10–15 minutes and covers what worked, what didn't, and whether you want to
suggest an improvement to the skill itself via a PR at https://github.com/dailyherold/skills.

---

## Research References

For full citations of all the research this plan was build on see `citations.bib` in the learning-lab skill's `references/` directory.
