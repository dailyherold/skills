# Agent Skills

Helpful skills I've written with agents to help agents work better for me.

## Index

- `lamport-problem-statement`: helps you first reason with a problem and identify correctness criteria for potential solutions before getting lost in...solutioning.
- `nix-sandbox`: leverages nix to pull any needed system packages for agentic work without messing with the host.
- `peer-review`: enables an agent to request a review from another agent, in a different tmux pane, including helpful context and guidance for writing a response for the original requestor to then read.
- `proton-inbox`: empower your agent to assist with managing your proton email using [himalaya](https://github.com/pimalaya/himalaya) interfacing with [protonmail-bridge](https://github.com/ProtonMail/proton-bridge).

## External Skills

I develop my own skills in this repo but also pull in skills from other sources. External skills are cloned into `src/` and symlinked to the root — my agents see them alongside my own skills, but they're not tracked in this repo (each cloner brings in what they want).

### Adding a new external skill

1. Add an entry to the `SKILLS` array in `setup.sh`:
   ```
   "https://github.com/owner/repo  path/to/skill"
   ```
2. Run `./setup.sh` — it clones the repo (once), creates the symlink, and updates `.gitignore` automatically.

Open an issue with smarter ideas (not submodules).
