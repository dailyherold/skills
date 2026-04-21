# Agent Skills

Helpful skills I've written with agents to help agents work better for me.

## Index

- `lamport-problem-statement`: helps you first reason with a problem and identify correctness criteria for potential solutions before getting lost in...solutioning.
- `nix-sandbox`: leverages nix to pull any needed system packages for agentic work without messing with the host.
- `peer-review`: enables an agent to request a review from another agent, in a different tmux pane, including helpful context and guidance for writing a response for the original requestor to then read.
- `portkey-status`: live health check all Portkey virtual key models (basic + tool-use) and list virtual key budget limits. Scripts self-contained in `scripts/` under the skill dir.
- `proton-inbox`: empower your agent to assist with managing your proton email using [himalaya](https://github.com/pimalaya/himalaya) interfacing with [protonmail-bridge](https://github.com/ProtonMail/proton-bridge).

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
