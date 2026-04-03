## Quality
- After any measurable change to a skill (new skill, updated instructions, added format files, refactored steps, changed triggers), run the `skill-creator` skill, if available, to evaluate and improve it. Use your judgment on what counts as measurable — when in doubt, ask the user whether to run it.

## Skill Authoring Conventions
- Write skill instructions as agent directives (procedural, imperative) — not human documentation prose. Red flag: explanatory asides addressed to a reader rather than an executor.
- Use annotated YAML with `?` for optional fields and inline comments for constraints as the schema format — no tooling, clean, precise.
- Extra resource files belong under `resources/` (or a subdir of it), not at the skill root.
- No hardcoded personal paths (e.g. `/Users/<username>/...` on macOS, `/home/<username>/...` on Linux) in skill files. Use variables, placeholders, or a single configurable comment at the top of the file instead.
