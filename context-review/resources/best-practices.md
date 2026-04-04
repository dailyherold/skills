# Agent Context Document Best Practices

## Core Principles

### 1. Reference Format, Not Tutorial
- Write for quick lookup, not learning
- Assume technical audience
- Focus on "what" and "how", minimize "why"
- Use bullet points over paragraphs

### 2. Conciseness Over Completeness
- One example per pattern (not three)
- Remove redundant explanations
- Consolidate related information
- Cut motivational language

### 3. Structure for Scanning
- Clear section hierarchy (max 2-3 levels)
- Consistent formatting
- Scannable headings
- Group related content

### 4. AI-Friendly Content
- Actionable patterns over concepts
- Code examples over descriptions
- Specific rules over general guidance
- Direct statements over emphasis markers

---

## Document Structure

### Frontmatter
Frontmatter format varies by harness — validate against the target harness spec:
- **Claude Code**: no frontmatter required for `CLAUDE.md`; `.claude/settings.json` for config
- **Opencode steering**: `inclusion: always` or `inclusion: fileMatch` + `fileMatchPattern`
- **Kiro steering**: same as opencode
- **Skill files**: `name` and `description` required; `allowed-tools` optional

### Recommended Sections
1. **Overview** — 2-3 sentences max
2. **Core Concepts** — key terminology and patterns
3. **Common Patterns** — frequently used examples
4. **Reference** — detailed API/syntax (if applicable)
5. **Troubleshooting** — common issues (optional)

---

## Writing Style

### Do This
```markdown
## Query Pattern

Basic user lookup:
```sql
SELECT id, name, email FROM users WHERE id = 123
```
- Use specific IDs when possible
- Omit unnecessary fields to reduce payload
```

### Not This
```markdown
## Query Pattern

**IMPORTANT:** When you need to query users, it's **CRITICAL** that you follow these patterns carefully!

You can look up users in several ways. The most common approach is by ID...
```

---

## Common Improvements

### Reduce Emphasis
- Before: `**CRITICAL:** Never do X`
- After: `Never do X`

### Consolidate Examples
- Before: Three similar examples with slight variations
- After: One canonical example with inline notes about variations

### Merge Related Sections
- Before: "Finding Users", "User Queries", "User Lookup Patterns"
- After: "User Queries" with subsections

### Remove Redundancy
- Before: Same concept explained in multiple places
- After: Single explanation with cross-references

### Simplify Formatting
- Before: Bold headers, bold keys, bold values
- After: Plain text with minimal bold for actual emphasis

---

## Common Pitfalls

- **Over-emphasis** — too many bold, italics, or "CRITICAL" markers reduces their impact
- **Tutorial style** — explaining concepts step-by-step instead of providing quick reference
- **Redundancy** — repeating the same information in multiple sections
- **Over-nesting** — too many heading levels makes content hard to scan
- **Verbose examples** — three similar examples when one with notes would suffice
- **Missing context** — code examples without brief explanation of when to use them
