---
name: context-review
description: >
  Reviews agent context documents — CLAUDE.md, AGENTS.md, opencode steering docs,
  system prompts, skill files, or any markdown that guides AI agent behavior — against
  best practices for conciseness, structure, and AI-friendliness. Use this skill whenever
  the user wants to review, audit, improve, or get feedback on a context doc, steering doc,
  CLAUDE.md, AGENTS.md, or system prompt. Also trigger when the user asks "how's my
  context doc", "check this CLAUDE.md", "review this steering doc", "is this well-written
  for an agent", or any request to evaluate agent-facing instructions.
allowed-tools:
  - Read
---

# context-review

Reviews agent context documents against best practices and returns concrete, prioritized feedback.

## What counts as an agent context document

Any file that provides instructions, conventions, or reference material to an AI agent:
- `CLAUDE.md` / `.claude/CLAUDE.md`
- `AGENTS.md`
- Opencode steering docs (`.md` files in `.opencode/steering/`)
- Kiro steering docs (`.md` files in `.kiro/steering/`)
- System prompts
- Skill `SKILL.md` files
- Any other markdown file written to guide agent behavior

## Step-by-step

### Step 1 — Identify the target

If the user specified a file, use it. If not, ask which file to review.

### Step 2 — Load references

Read both reference files before reviewing:
- `resources/best-practices.md` — principles for writing effective context docs
- `resources/review-checklist.md` — detailed checklist to apply

### Step 3 — Read the target file

Read the full content of the file being reviewed.

### Step 4 — Review and report

Apply the checklist to the file. Structure your feedback as:

**What's working**
- Bullet list of strengths (be specific, reference actual content)

**Issues — High priority**
- Things that meaningfully hurt agent comprehension or usability

**Issues — Lower priority**
- Polish items, minor redundancy, style

**Suggested rewrites** (optional)
- If a section is significantly improvable, show a before/after

Keep feedback direct and actionable. Reference specific sections or line content. Don't pad with encouragement.

### Step 5 — Offer to apply fixes

Ask if the user wants you to apply any of the changes directly.
