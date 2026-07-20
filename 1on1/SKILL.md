---
name: 1on1
description: >
  Prepares holistic, structured briefings before 1:1 meetings by pulling
  context from Google Calendar, the shared 1:1 Google Doc, recent emails,
  and the Obsidian vault (daily notes + person profile). Outputs a ready-to-review
  prep block per person, then seeds it into today's Obsidian daily note.
  Trigger on any of: "1:1", "one on one", "one-on-one", "meeting with [name]",
  "about to talk to [name]", "talking with [name]", "prep for [name]",
  "prep me for", "getting on a call with", or any request to prepare for
  an upcoming conversation with a specific person. Also trigger proactively
  when the user's calendar shows a 1:1 within the next 2 hours and no prep
  has been done yet.
---

# 1on1 Prep

Produce a focused, three-section briefing for each upcoming 1:1:
- **Personal context** — life/work signals worth acknowledging
- **Discuss** — agenda items drawn from the 1:1 doc, daily notes, and email
- **Action items** — only open items: strikethrough = done in GDocs (checkbox state not API-visible); `[x]` = done in Obsidian

Then seed the briefing into today's Obsidian daily note.

---

## Configuration

<!-- Edit these lines for your setup -->
<!-- vault_name: YOUR_VAULT_NAME -->
<!-- calendar_id: primary -->
<!-- initials: YOUR_INITIALS -->     e.g. "AB" — used to match 1:1 event/doc titles like "1:1 - Name:AB"
<!-- workspace_tag: YOUR_TAG -->     e.g. "acme" — prefixes the 1:1 block in the daily note, e.g. "#acme 1:1 with ..."

---

## Step 1 — Identify the person(s)

Extract the name from the user's message. If ambiguous (e.g. "my 1:1"), check
today's calendar for 1:1-pattern events (title contains "1:1", your
initials, or the person's name).

```bash
# Today's calendar events
TODAY_START=$(date -u +%Y-%m-%dT00:00:00Z)
TODAY_END=$(date -u +%Y-%m-%dT23:59:59Z)
gws calendar events list \
  --params "{\"calendarId\":\"primary\",\"timeMin\":\"$TODAY_START\",\"timeMax\":\"$TODAY_END\",\"singleEvents\":true,\"orderBy\":\"startTime\"}" \
  --format json 2>/dev/null
```

Filter for events whose summary matches 1:1 naming patterns:
`1:1`, your initials, `/ <initials>`, `<initials> /`, or attendee names
matching the user's request.

---

## Step 2 — Gather sources in parallel

For each person, fire all lookups simultaneously:

### 2a. Person profile (Obsidian)

```bash
# Search Permanent/ for the person's profile note
obsidian vault=YOUR_VAULT_NAME search query="$FIRSTNAME $LASTNAME" 2>/dev/null
obsidian vault=YOUR_VAULT_NAME search:context query="$FIRSTNAME $LASTNAME" 2>/dev/null
```

Read the matching profile note. Key fields to extract:
- Personal context: location, timezone, family, hobbies, calendar aversions
- Patterns & Insights section
- Open Questions section
- Voice Corpus (if simulating)

### 2b. Daily notes (Obsidian) — last 3 weeks

```bash
# Read recent daily notes and search for person mentions
obsidian vault=YOUR_VAULT_NAME search:context query="$FIRSTNAME" 2>/dev/null
```

Also read the last 14–21 days of daily notes directly if the search results
are sparse. Look for: meeting notes, action items, tensions, decisions, context
drops about this person.

### 2c. 1:1 Google Doc

The doc link is usually in the calendar event's description or attachments.
Title pattern: `1:1 - Name:<initials>` or `Notes - <initials> / Name`.

```bash
# Extract doc ID from calendar event attachment fileUrl or description
# Then fetch:
gws docs documents get --params "{\"documentId\":\"$DOC_ID\"}" \
  --format json 2>/dev/null | \
  jq -r '[.body.content[].paragraph?.elements[]?.textRun?.content] |
         map(select(. != null)) | join("")'
```

**Reading action item state accurately**

Two different completion signals depending on the source:

**Google Docs 1:1 docs — strikethrough only**

These docs use `GLYPH_TYPE_UNSPECIFIED` checkbox lists, but the GDocs REST
API v1 does not expose checkbox checked/unchecked state in the JSON response.
The checked state is invisible in the API. **Strikethrough is the only
reliable completion signal.** A checked-but-not-struck-through item looks
identical to an open item in the API — treat it as open.

```bash
gws docs documents get --params "{\"documentId\":\"$DOC_ID\"}" \
  --format json 2>/dev/null | jq -r '
  .body.content[] |
  select(.paragraph != null) |
  .paragraph |
  {
    strikethrough: ([.elements[]? | .textRun?.textStyle?.strikethrough // false] | any),
    text: ([.elements[]?.textRun?.content] | map(select(. != null)) | join(""))
  } |
  select(.text | length > 2) |
  "[\(if .strikethrough then "DONE" else "OPEN" end)] \(.text)"
'
```

An item is **done** if `strikethrough: true`. An item is **open** if
`strikethrough: false` AND it reads as an action (not a heading, frontmatter
field, or discussion topic label like "Action Items"). Do not infer completion
from context — only trust strikethrough.

**Practical implication for the user:** to mark an action done in the 1:1 doc
in a way the agent can detect, use strikethrough — not just the checkbox.

**Obsidian daily notes — markdown checkbox state**

- `- [ ]` = open
- `- [x]` = done

Use the `tasks` command to read these accurately:

```bash
obsidian vault=YOUR_VAULT_NAME tasks file="YYYYMMDD-daily" verbose 2>/dev/null
```

An item is open if checkbox is `[ ]` and not tagged `#todo-done`. An item is
done if checkbox is `[x]` or tagged `#todo-done`.

If no doc is found in the calendar event, check the person's profile note for
a linked 1:1 doc, or ask the user.

### 2d. Email

```bash
# Recent emails to/from the person
gws gmail users messages list \
  --params "{\"userId\":\"me\",\"q\":\"from:$EMAIL OR to:$EMAIL\",\"maxResults\":10}" \
  --format json 2>/dev/null | jq -r '.messages[].id'
```

Read subject lines and snippets. Flag any thread that is:
- Active today (sent/received same day as the 1:1)
- About a topic that's on the 1:1 agenda
- From a third party that this person is involved with

---

## Step 3 — Build the briefing

Produce one block per person. Keep it tight — this is a scanning document,
not a summary document. Each section should be readable in under 30 seconds.

```
### HH:MM — [Name]:[initials] (or Name / initials)

**Personal context**
[1–3 bullets: life signals worth opening with, timezone/schedule notes,
anything notable from profile or recent daily notes]

**Discuss**
[Bulleted agenda items, sourced from:]
- Today's entry in the 1:1 doc (highest priority — these were written recently)
- Open items from prior 1:1 doc sessions that weren't resolved
- Daily notes mentions in the last 2 weeks
- Active email threads today
- Profile open questions worth advancing

[Order: doc agenda first, then daily notes signal, then email, then profile]

**Action items**
[Only OPEN items from the 1:1 doc: no strikethrough in GDocs, or `[ ]` in Obsidian daily notes]
- [ ] Item text *(owner — YYYYMMDD)*
[If no open items: "No open action items."]
```

### What to include vs. exclude

**Include:**
- Considerate reminders from person's profile or personal frontmatter (e.g. birthday reminder, kid updates)
- Discussion items explicitly listed in the 1:1 doc for today's session
- Unresolved items from prior sessions that are still relevant
- Fresh signal from daily notes (last 7–14 days weighted more heavily)
- Active email threads from today
- Profile open questions that are overdue for follow-up

**Exclude:**
- Completed/struck-through items (never surface these)
- Stale discussion topics from sessions 2+ months ago unless still clearly live
- Vague items like "history" or "create 1:1 series" from initial setup sessions

---

## Step 4 — Present for review

Output all briefings in the chat for the user to review. Mention that you'll
seed them into today's daily note once they confirm.

If reviewing with Plannotator: wait for the user to return with feedback
annotations before seeding.

---

## Step 5 — Seed into today's daily note

After user confirms (or returns from Plannotator review), append each 1:1
block to today's Obsidian daily note.

### Format

Follow the vault's 1:1 block convention (from `AGENTS.md` and existing daily
note patterns):

```markdown
- #<workspace_tag> 1:1 with [[YYYYMMDDHHMM-firstname-lastname|Name]]
  - Personal context
    - [bullet]
  - Discuss
    - [bullet]
    - [bullet]
  - Action items
    - [ ] Item *(owner — YYYYMMDD)* #todo
```

Use `[[filename|display]]` wikilink format for the person. Look up their
profile filename first:

```bash
obsidian vault=YOUR_VAULT_NAME search query="$FIRSTNAME $LASTNAME" 2>/dev/null
```

### Append command

```bash
# Get today's daily note path
DAILY="Daily/$(date +%Y%m%d)-daily.md"

# Append the block
obsidian vault=YOUR_VAULT_NAME append path="$DAILY" content="$BLOCK"
```

Read back after each append to verify:

```bash
obsidian vault=YOUR_VAULT_NAME read path="$DAILY" 2>/dev/null | tail -20
```

Append one person at a time; read back between each to catch issues early.

---

## Handling missing sources

| Missing source | Action |
|---|---|
| No 1:1 doc in calendar event | Check person's Obsidian profile for a linked doc; if still not found, ask the user |
| No Obsidian profile | Surface what you found in daily notes and email; note the gap |
| No calendar event found | Ask the user which person(s) to prep for |
| Person not in email | Skip email section silently; don't surface the absence |
| Obsidian app not running | CLI will fail — tell the user to open the app |

---

## Conventions

- All vault interactions go through `obsidian vault=YOUR_VAULT_NAME` — never
  direct file writes
- Use `[[filename|display]]` wikilink format — never bare names
- Action items in daily note blocks get `#todo` tag per vault convention
- If the meeting has already happened (start time is past), note that and ask
  whether to seed post-meeting notes instead
