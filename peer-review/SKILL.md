---
name: peer-review
description: >
  Request a second opinion or cross-check from another AI agent running in a
  different tmux pane (opencode, kiro, another Claude Code instance, etc.).
  Writes context to ~/dev/ai/skills/peer-review/reviews/, discovers available panes, and injects a
  review prompt into the target pane via tmux send-keys.
allowed-tools:
  - Bash
  - Read
  - Write
trigger-phrases:
  - "get a second opinion"
  - "ask opencode to review"
  - "peer review this"
  - "have kiro check this"
  - "cross-check with"
  - "clean up comms"
  - "clean peer review files"
parameters:
  - name: session
    description: A short identifier for this review session (e.g. "20260304-auth-refactor"). Used as the filename prefix for `{session}-request.md` and `{session}-response.md`. Defaults to YYYYMMDD-{derived-slug} if not provided.
    required: false
  - name: target
    description: tmux target for the reviewing agent pane. Accepts session:window.pane format (e.g. "main:opencode.0") or pane ID (e.g. "%1"). If not provided, the skill lists available panes for the user to choose.
    required: false
  - name: question
    description: Specific question or focus area for the reviewer. Optional — if omitted, the reviewer is asked for general feedback.
    required: false
---

# peer-review skill

## Purpose

Bridge between agent harnesses running in separate tmux panes. Use when you
want to: check your own work, get a second opinion on a design decision, have
another agent verify a refactor, or collaborate on a multi-step task.

Also handles cleanup of comms files — trigger with: "clean up comms", "clean peer review files".

## Step-by-step instructions

### Step 1 — Establish session name

If a `session` parameter was provided, use it. Otherwise derive one from the
current date and the subject being reviewed:

```bash
date +%Y%m%d
```

Combine that date with a 2-3 word kebab-case slug you infer from what's being
reviewed — e.g. `20260304-jwt-refactor`, `20260304-rate-limiter`,
`20260304-email-fix`. Prefer concrete nouns over generic terms like "code" or
"review". If two sessions might collide, append `-2` etc.

This format sorts chronologically in `ls` output while staying readable.

### Step 2 — Discover available panes (if no target provided)

Run this command and present the output to the user so they can identify the
target pane:

```bash
tmux list-panes -a -F '#{pane_id}  #{session_name}:#{window_name}.#{pane_index}  cmd=#{pane_current_command}  path=#{pane_current_path}'
```

Present the list to the user and wait for them to pick a target pane.
Do not choose or default a pane yourself — the user knows which agent
they want and may have specific reasons for their choice.
Accept either `session:window.pane` or pane ID (`%N`) — both work with
`tmux send-keys -t`.

Note: kiro panes may show `fish` as the command due to a known bug. Use the
`session:window.pane` format (matches the tmux status bar) to identify them.

### Step 3 — Write context files

First, capture the current UTC timestamp:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```
Run that command and use its output as the `timestamp` value below — not the
command itself, the actual output.

Write the request file directly to the comms directory (no subdirectories, no `mkdir`).

**`~/dev/ai/skills/peer-review/reviews/{session}-request.md`** — YAML front matter followed by the body:

```
---
agent: {your harness name — e.g. "Claude Code", "opencode", "kiro", not the model ID}
model: {model ID}
working_dir: {current working directory}
timestamp: {output of the date command above}
prompt: |
  {verbatim text of the most recent user message that led to this request}
focus: "{specific question from question parameter}"
---
```

Omit the `focus` field entirely if no `question` parameter was provided.

Body (after front matter) — put everything the reviewer needs here:
- What is being reviewed (file paths, code snippet, or description)
- Relevant background context
- Any pre-analysis or findings you want to share
- The specific question (if provided via `question` parameter)

### Step 4 — Inject prompt into target pane

Send a review request to the target pane. The prompt should be self-contained
so the reviewing agent knows exactly what to do without any other context.

Template (adapt as needed):
```
Peer review requested. Use the Write tool to create a file — do not just reply here.

1. Read ~/dev/ai/skills/peer-review/reviews/{session}-request.md
2. Use the Write tool to write your review to ~/dev/ai/skills/peer-review/reviews/{session}-response.md

Your output must go to that file. The requesting agent will read it from there.
```

Send it with:
```bash
tmux send-keys -t '{target}' 'Peer review requested. Use the Write tool to create a file — do not just reply here.

1. Read ~/dev/ai/skills/peer-review/reviews/{session}-request.md
2. Use the Write tool to write your review to ~/dev/ai/skills/peer-review/reviews/{session}-response.md

Your output must go to that file. The requesting agent will read it from there.' Enter
```

### Step 5 — Confirm and wait

Tell the user:
- The request has been written to `~/dev/ai/skills/peer-review/reviews/{session}-request.md`
- The prompt has been sent to the target pane
- When the reviewer is done, `~/dev/ai/skills/peer-review/reviews/{session}-response.md` will appear
- To read the review: `Read ~/dev/ai/skills/peer-review/reviews/{session}-response.md`

Do NOT poll or loop waiting for `response.md`. The human will come back and ask
you to read it when the reviewing agent has finished.

**Proactive cleanup check:** After confirming the review is sent, run:
```bash
ls ~/dev/ai/skills/peer-review/reviews/*.md 2>/dev/null | wc -l
```
If the count is 10 or more, mention it briefly — e.g. "By the way, there are
N review files in the reviews directory — want me to help clean up old ones
when we're done here?" Don't block on it; just flag it and move on.

## Reading a review (follow-up)

When the user asks you to read the review after the reviewing agent has
finished, use the Read tool on:

```
~/dev/ai/skills/peer-review/reviews/{session}-response.md
```

Then summarize the reviewer's feedback and suggest next steps.

### Step 6 — Cleanup (optional)

After reading and summarizing the review, ask:
"Would you like to clean up the files for this session?"

If confirmed, check each file and delete only those that exist, using the
**exact fully-qualified path** — never globs, wildcards, or relative paths:

```bash
test -f /Users/e133949/dev/ai/skills/peer-review/reviews/{session}-request.md && rm /Users/e133949/dev/ai/skills/peer-review/reviews/{session}-request.md
test -f /Users/e133949/dev/ai/skills/peer-review/reviews/{session}-response.md && rm /Users/e133949/dev/ai/skills/peer-review/reviews/{session}-response.md
```

Never use `rm -rf` or wildcards.

## Cleanup trigger

When invoked with "clean up comms" or "clean peer review files" (without starting a new review):

1. List all `.md` files in `~/dev/ai/skills/peer-review/reviews/`:
   ```bash
   ls ~/dev/ai/skills/peer-review/reviews/*.md
   ```
2. Group by session prefix and present to the user.
3. Ask which session(s) to remove.
4. For each confirmed session, delete its files individually by exact path (see Step 6 above).

## Notes

- Context files are ephemeral scratch space. Don't rely on them persisting across days.
- If both agents are Claude Code instances in the same session, consider using
  native Claude Code Teams instead (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`).
  This skill is primarily for cross-harness coordination (Claude Code ↔ opencode, etc.).
- For multi-step collaboration (not just review), use `{session}-request.md` and
  `{session}-response.md` as a back-and-forth scratch pad, incrementally appending.
