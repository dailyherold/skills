---
name: peer-review
description: >
  Request a second opinion or cross-check from another AI agent running in a
  different tmux pane (opencode, kiro, another Claude Code instance, etc.).
  Writes context to a reviews/ subdirectory of the skill's base directory, discovers available panes, and injects a
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

## Data Exchange Formats

Try each format in order. Stop at first success. Each linked file specifies where to write, success/failure detection, reviewer prompt, and cleanup for that format. Request content schema is identical across all formats — only the destination varies.

1. [Local Markdown](./resources/formats/local-markdown.md)
2. [Obsidian](./resources/formats/obsidian.md)
3. [Logseq](./resources/formats/logseq.md)

If the user requests multiple formats, write to each and send a reviewer prompt per format.

## Step-by-step instructions

### Step 0 — Resolve the reviews directory

The skill loader injects a line at the bottom of this skill content:

```
Base directory for this skill: file:///path/to/peer-review
```

Extract the path by removing the `file://` scheme prefix from the URL. For example, `file:///Users/foo/.config/opencode/skills/peer-review` becomes `/Users/foo/.config/opencode/skills/peer-review`. Then append `/reviews` to get the reviews directory.

Use this as `{reviews_dir}` in all subsequent steps. This is not a user-supplied parameter — it is derived from the skill loader. Do not hardcode any path.

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

### Step 3 — Write context using the first available format

First, capture the current UTC timestamp:
```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```
Use its output as `{timestamp}` below.

**Iterate through the Data Exchange Formats list** (above). For each format in order:

1. Extract the relative path from the markdown link (e.g. `[Local Markdown](./resources/formats/local-markdown.md)` → `./resources/formats/local-markdown.md`), then resolve it against `{base_dir}` to get an absolute path (e.g. `{base_dir}/resources/formats/local-markdown.md`)
2. Read that file — it contains write instructions and a reviewer prompt template
3. Attempt to write the request using the `## Write` instructions in that file
4. **On success**: record which format was used, load its `## Reviewer Prompt Template` for Step 4, and stop
5. **On failure**: tell the user (e.g. "Logseq unavailable, trying next format...") and continue to the next format

If every format fails, report to the user and stop.

**Multi-format broadcast**: If the user explicitly asks for multiple formats, write to each specified format (don't stop at first success) and send a reviewer prompt per format.

**Request schema**: see `{base_dir}/resources/schema.md` — read it before writing the request content.

### Step 4 — Inject prompt into target pane

Use the **reviewer prompt template** from the format file chosen in Step 3. Each format file has a `## Reviewer Prompt Template` section — substitute actual values (no placeholders) before sending.

The prompt must be self-contained — the reviewing agent has no other context. Every template should make explicit:
- exactly where to read the request and where to write the response (tool name, page name, or absolute path)

Send with:
```bash
tmux send-keys -t '{target}' '{filled-in prompt from format file}' Enter
```

Where `{session-slug}` is the human-readable part of the session name (e.g. `nix-config-conundrum`, `jwt-refactor`) — not the full session ID with date prefix.

### Step 5 — Confirm and wait

Tell the user:
- The format used (e.g. "Written via Logseq" or "Fell back to local markdown")
- Where the request was written (page name, vault path, or file path)
- The prompt has been sent to the target pane
- Where the response will appear when the reviewer is done (per the format file's "Response location" section)
- How to read the review when ready (tool and location)

Do NOT poll or loop waiting for `response.md`. The human will come back and ask
you to read it when the reviewing agent has finished.

**Proactive cleanup check:** After confirming the review is sent, run:
```bash
ls {reviews_dir}/*.md 2>/dev/null | wc -l
```
If the count is 10 or more, mention it briefly — e.g. "By the way, there are
N review files in the reviews directory — want me to help clean up old ones
when we're done here?" Don't block on it; just flag it and move on.

## Reading a review (follow-up)

When the user asks you to read the review, use the **Response Location** specified in the format file that was used (see its `## Response Location` section). For local markdown (the current default): `Read {reviews_dir}/{session}-response.md`

Then summarize the reviewer's feedback and suggest next steps.

### Step 6 — Cleanup (optional)

After reading and summarizing the review, ask: "Would you like to clean up this session?"

Cleanup is format-dependent — follow the `## Cleanup` section in the format file used. For local markdown, check each file and delete only those that exist using exact fully-qualified paths:

```bash
test -f {reviews_dir}/{session}-request.md && rm {reviews_dir}/{session}-request.md
test -f {reviews_dir}/{session}-response.md && rm {reviews_dir}/{session}-response.md
```

Never use `rm -rf` or wildcards.

## Cleanup trigger

When invoked with "clean up comms" or "clean peer review files" (without starting a new review):

1. List all `.md` files in `{reviews_dir}/`:
   ```bash
   ls {reviews_dir}/*.md
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
