# Agent Skills

Helpful skills I've written with agents to help agents work better for me.

## Index

| Skill | What it does | Deps |
|---|---|---|
| `1on1` | pulls context from Calendar, the shared 1:1 doc, email, and Obsidian to build a pre-meeting briefing, then seeds it into today's daily note. | `gws` CLI (Google Workspace), Obsidian app running |
| `context-review` | audits CLAUDE.md/AGENTS.md/system-prompt-style docs for conciseness and AI-friendliness — the meta-skill for tuning the skills in this repo. | none |
| `gmail-inbox` | read, search, send, triage, and organize Gmail via the `gws` CLI. | `gws` CLI (Google Workspace), `jq` |
| `lamport-problem-statement` | forces a problem statement before you're allowed to debate solutions — Lamport's method for when you catch yourself already picking a tech. | none |
| `learning-lab` | designs and runs a structured, evidence-based learning plan — professor + study buddy for ramping on a new domain or role. | none |
| `logseq-db-query` | queries a Logseq DB graph straight from the command line. | [`@logseq/cli`](https://www.npmjs.com/package/@logseq/cli) (`npm install -g @logseq/cli`) |
| `nix-sandbox` | leverages nix to pull any needed system packages for agentic work without messing with the host. | `nix` (nix-shell) |
| `obsidian-zettelkasten` | manages the zettelkasten workflow — daily → fleeting → permanent, connection-finding, index surfacing. | Obsidian app running, Obsidian CLI |
| `peer-review` | enables an agent to request a review from another agent, in a different tmux pane, including helpful context and guidance for writing a response for the original requestor to then read. | `tmux` |
| `portkey-status` | live health check all Portkey virtual key models (basic + tool-use) and list virtual key budget limits. Scripts self-contained in `scripts/` under the skill dir. | `uv` |
| `proton-inbox` | empower your agent to assist with managing your proton email using [himalaya](https://github.com/pimalaya/himalaya) interfacing with [protonmail-bridge](https://github.com/ProtonMail/proton-bridge). | `himalaya` CLI, Proton Mail Bridge running |
| `teams-extractor` | reads Microsoft Teams messages straight out of the local Chromium IndexedDB cache. | `uv` and `git` (see [`scripts/vendor/VENDORED.md`](teams-extractor/scripts/vendor/VENDORED.md) for why `git` and vendoring approach) |
| `theory-of-constraints` | applies Goldratt's 5 Focusing Steps before you optimize the wrong bottleneck. | none |

External skills (`docx`, `pdf`, `xlsx`, `pptx`, `markitdown`, `citation-management`,
`gws-*`, `plannotator-*`, `sembi-orgchart`, `last30days`) are vendored from other
repos via `setup.sh` — see each skill's own `SKILL.md` for its requirements.

## License

MIT, see `LICENSE`. A few skills also carry their own `license:` field in frontmatter — that's for when a single skill folder gets pulled out and shared standalone, per the [Agent Skills spec](https://agentskills.io/specification).

## External Skills

External skills are cloned (sparse) into `src/` and symlinked to the root. The symlinks are committed to this repo so agents discover them automatically; the `src/` clones are local-only and gitignored.

### If you cloned this repo

The symlinks will appear broken until you populate `src/` by running:

```sh
./setup.sh
```

To start fresh without any external skills, remove the entries you don't want from the `SKILLS` array in `setup.sh`, delete their symlinks, and remove `src/`.

### Adding a new external skill

1. Add an entry to the `SKILLS` array in `setup.sh`:
   ```
   "https://github.com/owner/repo  path/to/skill"
   ```
2. Run `./setup.sh` — sparse-clones the repo and creates the symlink.
3. Commit: `git add <skill-name> setup.sh && git commit`

Open an issue with smarter ideas (not submodules).
