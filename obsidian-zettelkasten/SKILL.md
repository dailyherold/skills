---
name: obsidian-zettelkasten
description: Manage a zettelkasten in Obsidian — capturing notes, promoting ideas from daily → fleeting → permanent, finding connections, surfacing index opportunities, and navigating the knowledge graph. Use this skill whenever the user mentions their Obsidian vault, zettelkasten, taking notes, processing their inbox, finding connections between ideas, capturing a thought or reading, or anything related to their personal knowledge management workflow. Also trigger when user says things like "add this to my notes", "what notes do I have on X", "what should I link this to", "process my fleeting notes", "I've been thinking about X", or "make a note of this".
---

# Obsidian Zettelkasten

## Vault

<!-- Configure: edit the two lines below -->
<!-- - **vault_name**: myvault -->
<!-- - **vault_path**: /path/to/vault -->
- **CLI**: `obsidian vault={vault_name} <command>`
- **Requires Obsidian app to be running** (the CLI talks to the running app)

## Folder structure

| Folder | Purpose | Naming |
|--------|---------|--------|
| `Daily/` | Journal / default capture inbox | `YYYYMMDD-daily.md` |
| `Fleeting/` | Half-formed ideas worth developing | `YYYYMMDDHHMM-slug.md` |
| `Literature/` | Notes on sources (books, papers, articles) | `@citekey.md` (Zotero-style) |
| `Permanent/` | Atomic, evergreen ideas | `YYYYMMDDHHMM-slug.md` |
| `Templates/` | Note templates | |

Root-level files are older permanent notes — treat them the same as `Permanent/`.

---

## Capture

### Default: today's daily note

Unless the user explicitly says "fleeting", capture goes to today's daily note.

```bash
# Get today's daily note path
DAILY="Daily/$(date +%Y%m%d)-daily.md"

# Check if it exists; create with header if not
obsidian vault={vault_name} file "$DAILY" 2>/dev/null || \
  obsidian vault={vault_name} create path="$DAILY" \
    content="# $(date +%Y%m%d) Daily\nCreated: $(date '+%Y-%m-%d')\n\n## Captures\n"

# Append the capture as a bullet
obsidian vault={vault_name} append path="$DAILY" \
  content="- $(date '+%H:%M') $THOUGHT"
```

Format each capture as a timestamped bullet: `- HH:MM thought here`

**A quick capture is just a bullet. Do not create a fleeting note, add tags, expand content, or create any additional files unless the user explicitly asks. The daily note is the inbox — let it be messy.**

### Explicit fleeting note

When the user says "fleeting", "make this a fleeting note", or "expand this":

```bash
ID=$(date +%Y%m%d%H%M)
SLUG="some-short-slug"  # lowercase-hyphenated from title
obsidian vault={vault_name} create path="Fleeting/${ID}-${SLUG}.md" \
  content="# $TITLE\nCreated: $(date '+%Y-%m-%d %H:%M')\n\n$CONTENT\n\n## References\n1."
```

### Literature note

When capturing from a source (book, paper, article):

```bash
obsidian vault={vault_name} create path="Literature/@${CITEKEY}.md" \
  content="---\ntitle: $TITLE\nauthors: $AUTHORS\nyear: $YEAR\nreference: $REF\n---\n\n$SYNTHESIS\n\n## References\n1."
```

- `@citekey` format: `@lastnameYYYYword` (e.g. `@ahrensHowTakeSmart2017`)
- Content should be the user's **own synthesis**, not just copy-paste
- Quotes are fine as supporting evidence — mark them with page numbers like `(p. 42)`

---

## Promotion

The zettelkasten workflow moves ideas upstream: **daily → fleeting → permanent**.

### Daily item → fleeting note

When a daily note bullet deserves to be developed:

1. Read the daily note to find the item
2. Create a new fleeting note with the idea expanded
3. Replace the bullet in the daily note with a wikilink: `- [[YYYYMMDDHHMM-slug|original text]]`

```bash
# Create the fleeting note
ID=$(date +%Y%m%d%H%M)
obsidian vault={vault_name} create path="Fleeting/${ID}-${SLUG}.md" \
  content="# $TITLE\nCreated: $(date '+%Y-%m-%d %H:%M')\n\n$EXPANDED_CONTENT\n\n## References\n1. [[$(date +%Y%m%d)-daily]]"

# Update daily note — replace the bullet with a link
# (use append to add a note, or ask user to do the edit if complex)
```

### Fleeting → permanent note

This is where the real thinking happens. A fleeting note is ready to promote when:
- It expresses one clear, atomic idea
- The idea would be useful to your future self out of context
- It can be stated as a claim or insight, not just a topic

When promoting:
1. Read the fleeting note
2. **Rewrite it** — the permanent note should be distilled, not just copied. The title should read like a statement ("Context switching compounds cognitive debt") not a topic ("Context switching")
3. Move the file using `obsidian move` (don't just create a copy):

```bash
# Move the file to Permanent/
obsidian vault={vault_name} move path="Fleeting/${ID}-${SLUG}.md" \
  path="Permanent/${ID}-${SLUG}.md"

# Or if renaming (new title → new slug):
obsidian vault={vault_name} move file="${ID}-${SLUG}" \
  path="Permanent/${NEW_ID}-${NEW_SLUG}.md"
```

4. Add a link back to the source: `## References\n1. [[source-note]]`
5. After moving, suggest 2-3 existing notes it could link to

**Atomic note checklist** — before confirming, verify the note:
- [ ] Makes one claim (not a list of loosely related thoughts)
- [ ] Has a title that could stand alone as a sentence
- [ ] Has at least one outgoing link (to a related note, literature note, or index)

---

## Processing

When the user asks to "process notes", "check my inbox", or "what needs attention":

1. **Show recent daily notes** with unlinked bullets (bullets that aren't wikilinks yet):
```bash
# List recent daily notes
obsidian vault={vault_name} files folder=Daily

# Read today's and recent ones to find raw bullets
obsidian vault={vault_name} read path="Daily/$(date +%Y%m%d)-daily.md"
```

2. **Show fleeting notes** — especially old ones that haven't become permanent:
```bash
obsidian vault={vault_name} files folder=Fleeting
```

3. For each unprocessed item, offer options:
   - **Promote** → turn into permanent note
   - **Link** → it's already captured elsewhere, just add a wikilink
   - **Discard** → not worth keeping
   - **Later** → leave it, check again next session

When the user has 5 minutes, process 2-3 items. When they have more time, go deeper.

---

## Finding connections

Use this proactively — whenever a note is created or promoted, suggest relationships.

```bash
# Search by keyword/concept
obsidian vault={vault_name} search query="$KEYWORD"
obsidian vault={vault_name} search:context query="$KEYWORD"

# Find what links to a note
obsidian vault={vault_name} backlinks file="$NOTE"

# Find all notes with a tag
obsidian vault={vault_name} tag name="$TAG" verbose

# Find orphans (no incoming links — potential connection targets)
obsidian vault={vault_name} orphans

# Find dead-ends (no outgoing links — need connections)
obsidian vault={vault_name} deadends
```

**When to proactively suggest connections:**
- After any capture: search for related notes by keywords from the captured thought
- After promoting a fleeting note: search for 2-3 permanent notes that could link to it
- During processing: when you read a note, check its backlinks and suggest additions

Surface connections as: "This note relates to [[note-name]] — want me to add a link?"

---

## Index notes

Index notes are entry points into a cluster of related permanent notes. They're not summaries — they're **maps**: an ordered list of links that tells the story of how the ideas connect.

### When to suggest an index

Check tag counts periodically or after capturing:

```bash
obsidian vault={vault_name} tags counts format=json
```

If a tag has **5+ notes** and no index note exists for that topic, suggest creating one:
"You have 7 notes tagged `#leadership` — want me to create an index for that cluster?"

Also suggest for named entities (companies, projects, jobs) when 3+ notes reference them.

### Creating an index

```bash
obsidian vault={vault_name} create path="Permanent/$(date +%Y%m%d%H%M)-${TOPIC}-index.md" \
  content="# $TOPIC Index\n#index #$TAG\n\n## Notes\n1. [[note-one|claim]]\n2. [[note-two|claim]]\n"
```

Index conventions:
- Tag it `#index` plus the topic tag
- Order notes by narrative/conceptual flow, not date
- Each link should have an alias that states the note's claim: `[[note-id|The claim this note makes]]`

---

## Tags

Tags live inline in the note body (not frontmatter), like `#leadership` or `#beyondmidi`.

When to suggest a tag:
- If the content clearly maps to an existing tag in the vault, suggest it
- Don't invent granular tags for one-off ideas — a wikilink is usually better
- Reserve tags for recurring themes worth indexing

```bash
# See all existing tags before suggesting new ones
obsidian vault={vault_name} tags counts format=json
```

---

## Vault as context (for agents)

Any agent starting work that might benefit from the user's accumulated thinking should query the vault first. This is how you avoid starting from scratch when the user has already thought deeply about something.

### Before starting a task

Search for relevant notes by topic, tag, or keyword:

```bash
# Search by concept
obsidian vault={vault_name} search query="$TOPIC"
obsidian vault={vault_name} search:context query="$TOPIC"

# Find notes with a relevant tag
obsidian vault={vault_name} tag name="$TAG" verbose

# Check if there's an index for this domain
obsidian vault={vault_name} search query="#index $TOPIC"
```

Read any relevant permanent notes — these represent the user's most distilled thinking:

```bash
obsidian vault={vault_name} read file="$NOTE_NAME"
obsidian vault={vault_name} backlinks file="$NOTE_NAME"
```

### Surfacing context proactively

If you're working on something and notice it connects to the user's zettelkasten — mention it:
"I see you have notes on `#leadership` that might be relevant here — want me to pull those in?"

### Helping capture and curate

Agents can write to the vault on the user's behalf:
- Drop observations into today's daily note (use the capture pattern above)
- Flag when something worth a permanent note emerges from a work session
- Suggest relationships: "this pattern we just found in the codebase connects to your note on [[202304220651-docs-as-code]]"

Agent-generated captures should be clearly marked so the user can review and curate:

```bash
# Append with agent attribution
obsidian vault={vault_name} append path="Daily/$(date +%Y%m%d)-daily.md" \
  content="- $(date '+%H:%M') [agent] $OBSERVATION"
```

The `[agent]` marker signals "review this — I thought it was worth saving but you decide."

---

## Guardrails

- **Never open in Obsidian** unless the user explicitly asks ("open it", "open in Obsidian")
- **Never auto-delete** anything — always confirm before any destructive action
- **Confirm before moving** fleeting → permanent (show the rewritten note first)
- When in doubt about where something belongs, default to the daily note — it's the inbox
- If Obsidian isn't running, the CLI will fail — tell the user to open the app

## CLI quick reference

```bash
# All commands need vault={vault_name}
obsidian vault={vault_name} <command>

# Read a note
obsidian vault={vault_name} read path="Folder/note.md"
obsidian vault={vault_name} read file="note-name"   # resolves by name like wikilinks

# Create
obsidian vault={vault_name} create path="Folder/name.md" content="..."

# Append
obsidian vault={vault_name} append path="Folder/name.md" content="..."

# Move / rename
obsidian vault={vault_name} move file="old-name" path="Folder/new-name.md"

# Search
obsidian vault={vault_name} search query="keyword"
obsidian vault={vault_name} search:context query="keyword"

# Links
obsidian vault={vault_name} backlinks file="note-name"
obsidian vault={vault_name} orphans
obsidian vault={vault_name} deadends

# Tags
obsidian vault={vault_name} tags counts format=json
obsidian vault={vault_name} tag name="tagname" verbose

# Files
obsidian vault={vault_name} files folder=Fleeting
obsidian vault={vault_name} files folder=Daily
```
