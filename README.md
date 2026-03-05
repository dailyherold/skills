# Agent Skills

Helpful skills I've written with agents to help agents work better for me.

## Index

- `lamport-problem-statement`: helps you first reason with a problem and identify correctness criteria for potential solutions before getting lost in...solutioning.
- `nix-sandbox`: leverages nix to pull any needed system packages for agentic work without messing with the host.
- `peer-review`: enables an agent to request a review from another agent, in a different tmux pane, including helpful context and guidance for writing a response for the original requestor to then read.
- `proton-inbox`: empower your agent to assist with managing your proton email using [himalaya](https://github.com/pimalaya/himalaya) interfacing with [protonmail-bridge](https://github.com/ProtonMail/proton-bridge).

## 3rd Party Skills

I develop my own skills in this repo but also use `setup.sh` to clone other skills into the `src/` directory and symlink the desired skill directories to the root. I then have my various agentic friends looking at this skills directory in their respective config. Open an issue with smarter ideas (not submodules).
