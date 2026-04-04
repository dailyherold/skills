# Agent Context Document Review Checklist

## Frontmatter

- [ ] Frontmatter exists and is valid YAML (if required by target harness)
- [ ] Frontmatter uses the correct keys for the target harness (see best-practices.md)
- [ ] Empty line after closing `---`

## Markdown Structure

- [ ] Valid markdown syntax
- [ ] Code blocks have language specified
- [ ] Headings follow hierarchy (no skipped levels)
- [ ] Lists are properly formatted
- [ ] Links are valid and descriptive

---

## Content Quality

### Conciseness
- [ ] No redundant sections covering the same topic
- [ ] No repeated explanations
- [ ] Examples are minimal but complete
- [ ] One canonical example per pattern (not 3-5)
- [ ] No verbose explanations where brief notes suffice

### Structure
- [ ] Clear section hierarchy (max 3 levels)
- [ ] Related content is grouped together
- [ ] Sections are logically ordered
- [ ] Headings are descriptive and scannable
- [ ] No orphaned content without a clear section

### Tone and Style
- [ ] Technical tone (not conversational)
- [ ] Reference format (not tutorial)
- [ ] Direct statements (not motivational)
- [ ] Assumes technical audience
- [ ] Minimal use of emphasis (bold/italics)
- [ ] No excessive "CRITICAL" or "IMPORTANT" markers

### AI-Friendliness
- [ ] Actionable patterns over abstract concepts
- [ ] Code examples over lengthy descriptions
- [ ] Specific rules over general guidance
- [ ] Scannable structure (bullets, short paragraphs)
- [ ] Consistent formatting throughout

---

## Content Completeness

### Essential Elements
- [ ] Purpose/overview is clear
- [ ] Key terminology defined where needed
- [ ] Common patterns documented
- [ ] Examples for each pattern
- [ ] Error handling or edge cases noted (if applicable)

### Code Examples
- [ ] Each example has brief context
- [ ] Code is syntactically correct
- [ ] Language specified in code blocks
- [ ] Comments used sparingly

---

## Redundancy Scan

Look for:
- [ ] Same concept explained in multiple places
- [ ] Similar examples with minor variations
- [ ] Duplicate information across sections
- [ ] Overlapping section topics

---

## Length Assessment

- [ ] Document is as short as possible while complete
- [ ] No sections that could be merged
- [ ] No verbose explanations that could be bullets
- [ ] No unnecessary examples

---

## Improvement Suggestions

### If Too Verbose
1. Identify redundant sections → merge
2. Find repeated explanations → consolidate
3. Locate multiple similar examples → keep one
4. Convert paragraphs to bullets where possible

### If Poorly Structured
1. Group related content together
2. Create clear section hierarchy
3. Add descriptive headings
4. Reorder for logical flow

### If Too Tutorial-Like
1. Remove step-by-step explanations
2. Convert to reference format
3. Focus on patterns over process
4. Assume technical knowledge

### If Over-Emphasized
1. Remove excessive bold/italics
2. Reduce "CRITICAL" markers to truly critical items
3. Let content speak for itself

---

## Quality Levels

### Excellent
- All checklist items pass
- Concise and scannable
- Clear patterns and examples
- AI-friendly reference format
- No redundancy

### Good
- Most checklist items pass
- Generally concise with clear structure
- Minor redundancy or verbosity

### Needs Improvement
- Several checklist items fail
- Verbose or redundant
- Tutorial-like style or over-emphasized

### Poor
- Many checklist items fail
- Very verbose or poorly structured
- Not AI-friendly
