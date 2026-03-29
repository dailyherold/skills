# Example Learning Plan

This is a filled example to calibrate output quality — showing what sharp correctness
conditions, concrete exercises, and explicit Bridge connections look like in practice.
The domain is AI strategy for a non-technical leader. Use this as a reference when
producing plans, but don't let the domain shape outputs for unrelated topics.

---

# AI Strategy: Board-Ready in 8 Weeks

**Learner:** Jordan (VP of Product, no ML background)
**Time budget:** 6 hrs/week
**Deadline / milestone:** Board presentation, Week 8
**Plan created:** 2026-03-21

---

## Why This Plan Exists

> "I just got put in charge of AI strategy and I don't know where to start."

> "We're presenting to the board in 8 weeks."

> "Our CTO and the board — I need to not embarrass myself in front of either of them."

> "I want to be the person who shapes the direction, not the one who gets corrected."

*Distilled motivations:*

- **Authority gap, not knowledge gap:** Jordan isn't trying to become an ML engineer.
  The need is credibility with two specific audiences who have different expectations.
- **Hard deadline shapes everything:** 8 weeks means scope must be ruthlessly narrow.
  Depth on anything not serving the board presentation is out of scope.

---

## Correctness Conditions

*What must be true for this plan to be considered successful.*

**Primary** — core capabilities needed:
- [ ] "I can walk through our AI strategy in 20 minutes, field the CTO's technical
      challenges without pausing, and have the board asking follow-up questions rather
      than basic clarifying ones."
- [ ] "I can answer 'why not just use ChatGPT for everything?' and 'what's our
      competitive moat in AI?' without notes or hesitation."

**Supporting** — prerequisites that enable the primary conditions:
- [ ] "I can distinguish between foundation models, fine-tuning, RAG, and agents —
      and explain in one sentence which use cases call for which."
- [ ] "I can characterize the AI strategies of 3 competitors and say what makes each
      one defensible or not, using the same framework consistently."

**Application** — artifact that proves the learning transferred:
- [ ] "The board presentation exists: under 15 slides, grounded in our actual business
      context, stress-tested by the CTO before the board meeting."

*Completeness check: Could Jordan satisfy all of the above and still feel like a
failure? Only if the CTO stress test revealed gaps not caught during prep — which
is why Phase 3 builds that session in explicitly.*

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

**Recommended tools:** Slides (Google or PowerPoint) for the application artifact;
plain markdown for notes and drafts.

---

## Phase 1: The Vocabulary Floor (Weeks 1–2, 12 hrs)

**Bloom's level:** Understand → Apply
**Agent mode:** Socratic for concepts, Direct for definitions
**Time allocation:** 1hr Attempt | 3hr Consume | 4hr Build | 2hr Teach | 2hr Bridge

*Goal: Close the vocabulary gap fast. You can't evaluate AI strategy options you
can't name. This phase is about building just enough conceptual model to have
informed opinions — not technical depth.*

### 1. Attempt

*Before reading or watching anything, write your answers to:*

- What do you think the difference is between "AI" and "machine learning" and "LLMs"?
  Sketch a diagram if it helps.
- Name every AI-related term you've heard in the last 3 months that you couldn't
  confidently define. (This is your vocabulary gap list — you'll revisit it at the end.)
- What do you think makes an AI product defensible vs. a commodity? First instinct only.

Save your answers. You'll compare them after Consume.

### 2. Consume

- [AI for Everyone — Andrew Ng, Coursera](https://www.coursera.org/learn/ai-for-everyone)
  — Week 1 & 2 only. Specifically designed for non-technical leaders. Gives you the
  vocabulary and mental model without requiring math.
- [The AI Landscape in 2024 — a16z State of AI](https://a16z.com/ai/) — Skim for
  terminology and the strategic framing VCs use. This is the vocabulary your board
  probably has.
- One competitor's recent earnings call or press release that mentions AI — chosen
  based on your actual industry. Read for how they frame AI to non-technical investors.

### 3. Build

Write a one-page "AI vocabulary glossary" for yourself — 10–15 terms, each defined
in one sentence you could say out loud to a board member without sounding like you're
reading. No jargon in the definitions.

Then: revisit your Attempt answers. Mark every place your first instinct was wrong or
incomplete. These are your actual gaps.

### 4. Break

Take your glossary to the agent and ask it to play a skeptical board member. For each
term: can you explain it without using the term itself? Can you give a real example
from your industry? Can you explain what it's *not*?

The goal is to find the terms you defined correctly on paper but can't actually use
in conversation. Those get flagged for Phase 2 reinforcement.

### 5. Teach

**Agent Prompt (Socratic):** *"I'm going to explain the difference between fine-tuning
and RAG to you as if you're a board member who just asked why we can't just use
ChatGPT. Push back on anything that sounds like jargon or that you don't think a
board member would find meaningful."*

### 6. Bridge

*Connect to the board presentation:*

**Write in Key Insights file:** "Which 3 terms from my glossary are the ones the
board is most likely to ask about? Which 3 is the CTO most likely to challenge me on?
Are those the same 3?"

This distinction matters: board questions are about risk and ROI; CTO challenges are
about technical accuracy. Phase 3 requires handling both simultaneously.

### Retrieval Checkpoints

- **+1 day:** Without notes, write the 3 most important things that changed from your
  Attempt answers. Where were your priors most wrong?
- **+3 days:** Agent quizzes on 5 terms from your glossary. Identify the 2 you had
  to think hardest about.
- **+1 week:** Drill those 2 terms: explain each one 3 different ways — to a
  technical peer, to a business executive, to a skeptical investor.

---

## Phase 2: Strategic Framing (Weeks 3–5, 18 hrs)

**Bloom's level:** Analyze → Evaluate
**Agent mode:** Socratic throughout
**Time allocation:** 1hr Attempt | 4hr Consume | 6hr Build | 4hr Teach | 3hr Bridge

*Goal: Develop a framework for evaluating AI strategic options — not absorbing best
practices, but building judgment. The deliverable here is a structured point of view
on your company's position, not a summary of what others are doing.*

### 1. Attempt

*Before reading or watching anything, write your answers to:*

- What do you think makes an AI investment defensible for a company like yours?
  List your top 3 criteria.
- Pick one competitor. What do you think their AI strategy is, based on what you
  already know? What's the biggest risk in that strategy?
- What would "winning" at AI look like for your company in 3 years? Be specific.

### 2. Consume

- [Hamilton Helmer — 7 Powers](https://7powers.com/) — Chapter summaries are
  sufficient. The framework for competitive moats applies directly to AI strategy.
  You want "counter-positioning" and "network effects" in your vocabulary.
- 2–3 AI strategy case studies from companies in adjacent spaces (not direct
  competitors — you want pattern recognition, not copying). Look for ones that
  include what went wrong, not just what worked.
- Your company's last 3 board decks — specifically how AI/technology has been framed.
  What language has worked? What got challenged?

### 3. Build

Draft a 2-page "AI strategic position" memo:
1. Where we are today (honest)
2. Where we could play (3 options, each with a one-sentence risk)
3. Where we should play (your recommendation, with the reasoning)
4. What "winning" looks like in 18 months (specific and measurable)

This memo is the intellectual core of the board presentation. The slides in Phase 3
are this memo made visual.

### 4. Break

Give the memo to the agent with this framing: *"You're a board member who has been
through 3 failed AI initiatives at other companies. Find every place this memo is
vague, optimistic without evidence, or doesn't answer 'why us, why now.'"*

Then: swap one of your 3 strategic options for a clearly worse one. Does your
reasoning framework still work? If the bad option passes your own criteria, the
criteria aren't sharp enough.

### 5. Teach

**Agent Prompt (Socratic):** *"I'm going to defend our AI strategy recommendation
to you as a skeptical CTO who thinks we're underinvesting in infrastructure and
overinvesting in product features. I'll explain the reasoning; you challenge the
tradeoffs."*

### 6. Bridge

**Write in Key Insights file:** "Which terms from my Phase 1 glossary did I actually
use in the memo? Which ones turned out not to matter for our strategy? Which Phase 1
gaps came back to bite me in Phase 2?"

This is far-transfer in action: the vocabulary you built in Phase 1 either shows up
in Phase 2's strategic reasoning or it doesn't. If it doesn't, that's a signal — either
the vocab was the wrong vocab, or the strategy doesn't engage with the technology deeply
enough.

### Retrieval Checkpoints

- **+1 day:** From memory: what are the 3 strategic options you identified, and your
  one-sentence risk for each?
- **+3 days:** Agent asks: "Why that option over the other two?" You answer without
  referring to the memo.
- **+1 week:** Drill the weakest part of your recommendation — the place the agent
  challenged hardest. Rewrite that section from scratch without looking at the original.

---

## Phase 3: The Presentation (Weeks 6–8, 18 hrs)

**Bloom's level:** Create → Evaluate
**Agent mode:** Critique throughout
**Time allocation:** 2hr Attempt | 1hr Consume | 8hr Build | 4hr Break | 3hr Teach

*Goal: Turn the Phase 2 memo into a board-ready presentation and stress-test it until
it's solid. The build is the application artifact. The Break step here is the CTO
stress test — it should be uncomfortable.*

### 1. Attempt

*Before building anything:*

- Sketch the presentation on paper, slide by slide. What's the one thing each slide
  needs the audience to believe when they leave it?
- Write down the 5 hardest questions you expect from the board. Write down the 3
  hardest questions you expect from the CTO. Are you actually ready to answer them?
- What does success look like at the end of the meeting — specifically? What do you
  want people to decide, feel, or do?

### 2. Consume

- Review your Phase 1 vocabulary glossary and Phase 2 memo one more time — not to
  add content, but to find anything you still can't say fluently out loud.
- One strong board presentation on a technical topic (not AI) — study the structure,
  not the content. How does it handle complexity for a non-technical audience?

### 3. Build

Build the board presentation: under 15 slides, no jargon, every claim grounded in
either data or explicit reasoning. Structure:

1. Why AI strategy matters now (not in general — for this company, this moment)
2. Where we are today (honest, no spin)
3. The strategic options we considered (shows rigor)
4. Our recommendation (clear, defensible)
5. What we need to succeed (resources, decisions, runway)
6. How we'll know if it's working (specific metrics, 18-month horizon)

### 4. Break

Run two stress tests:

**CTO stress test:** Share the deck with your CTO before the board meeting. Ask them
to find every technical claim that's imprecise, every place the strategy doesn't
engage with real constraints, and every slide where a board member could misunderstand
the technical reality. Incorporate the feedback.

**Hostile board member test:** Ask the agent to play a board member who has seen 5
AI strategy presentations this year and is skeptical of all of them. Go through the
deck slide by slide. The agent challenges every claim that isn't backed by evidence
or reasoning.

### 5. Teach

**Agent Prompt (Critique):** *"I'm going to present the full deck to you as if you're
the board. After each section, you ask the question a board member would most likely
ask. After I answer, tell me: was that answer board-ready, or did it reveal a gap?"*

### 6. Bridge

**Write in Key Insights file:** "What changed from the Phase 2 memo to the final
presentation? What did the CTO stress test reveal that I hadn't caught myself? What
would I do differently in Phase 1 and 2 if I were starting over?"

This is the transfer check — not just "did I build the thing" but "what does having
built the thing teach me about the learning process itself."

### Retrieval Checkpoints

- **+1 day:** Without looking at slides: walk through the presentation structure from
  memory. Where do you go blank?
- **+3 days:** Answer the 5 hardest board questions you wrote in the Attempt step —
  without notes.
- **+1 week:** (Post-presentation) What actually got asked that you didn't anticipate?
  What would you add to a future Phase 1 vocabulary list based on what came up?

---

## Interleaving Map

| During Phase | Revisit From | Exercise |
|---|---|---|
| Phase 2 | Phase 1 | For each strategic option in the memo, identify which vocabulary terms are load-bearing. If you can't define them fluently, the strategy argument that depends on them is shaky. |
| Phase 3 | Phase 1 | Audit every slide for jargon. Replace any term from your glossary with plain language — if the slide gets weaker, the argument was hiding behind the terminology. |
| Phase 3 | Phase 2 | The recommendation slide is the Phase 2 memo compressed to 3 bullets. If you can't compress it without losing the reasoning, the reasoning isn't sharp enough yet. |

---

## Stress Test Log

Every 2 weeks: find one piece of external material at the frontier. Evaluate against
your correctness conditions. Log what changed.

| Date | Source | What it challenged / added | Conditions affected | Plan changes |
|---|---|---|---|---|
| Week 2 | Competitor earnings call | They announced a specific AI product we hadn't considered — introduced "retrieval-augmented generation" in a business context | Supporting condition 1 (vocabulary) | Added RAG to glossary; added competitor to Phase 2 case studies |
| Week 4 | a16z AI report | Reframed "moat" away from data toward workflow integration — challenged our Phase 2 recommendation | Primary condition 2 (competitive moat answer) | Revised memo section 3; updated recommendation reasoning |

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

Full citations for all learning science referenced in this plan:
see `citations.bib` in the learning-lab skill's `references/` directory.
