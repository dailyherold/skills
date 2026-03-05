---
name: nix-sandbox
description: "Run commands or tools in an isolated nix-shell sandbox without modifying the system. Use this skill whenever a needed tool or package isn't in PATH, the user says 'without installing' or 'don't touch my system', or you'd otherwise suggest nix-shell or nix run. Trigger automatically on 'command not found' errors when a system-level tool (not a project library) is needed. The skill handles platform detection and constructs the correct sandbox invocation for macOS (sandbox-exec) or Linux (bwrap) automatically."
---

# nix-sandbox

Run a command in an isolated environment using `nix-shell --pure` for environment isolation and platform-specific filesystem sandboxing.

## When to invoke this skill

Use this skill whenever a task requires a package or tool that is not already in PATH. **Do not propose modifying system config, `home.packages`, or `environment.systemPackages` for one-off tasks.** The sandbox pulls packages directly from the Nix store on demand — no install, no system change, no residue.

Trigger automatically when:
- The user asks to run a script, tool, or command that isn't available (`command not found`)
- A task needs a specific language runtime, linter, formatter, or CLI not on the system
- The user says "without installing", "in isolation", "don't touch my system", or similar
- You would otherwise suggest `nix-shell` or `nix run` without isolation

Note on session-level jailing: if this agent was launched via `jailed-claude-code` or `jailed-opencode`, the agent session itself is already sandboxed by bubblewrap. This skill is for sandboxing **individual task invocations** within a session — a separate, composable layer.

## Check for existing dep managers first

Before reaching for nix-sandbox, check whether the working directory has a language-level dep manager (uv, bun, npm, cargo, go.mod, etc.) and route package needs through it instead. Use nix-sandbox for **system-level tools** needed to accomplish a task — not for project library dependencies. When ambiguous, ask: "Is this a tool I'm running, or a library the project imports?" If the latter, use the project's dep manager.

## Parameters

- **packages** — space-separated nixpkgs package names available inside (e.g. `"python3 pytest"`)
- **command** — shell command to run
- **workdir** — read+write working directory (default: auto-created temp dir `/tmp/agent-sandbox-XXXXXX`)
- **project_dir** — path the sandbox may read (optional)
- **network** — `yes` (default) or `no`
- **profile** — macOS only: `default` (default), `network-off`, or `strict`

## What you do

1. Detect platform: run `uname -s` → `Darwin` (macOS) or `Linux`
2. Resolve `SKILL_DIR` — the base directory of this skill, shown in the skill header when loaded (e.g. `Base directory for this skill: /path/to/nix-sandbox`). The `.sb` profiles live at `$SKILL_DIR/profiles/`.
3. Create `SANDBOX_DIR=$(mktemp -d /tmp/agent-sandbox-XXXXXX)` unless workdir was specified
4. Run the sandboxed command using the appropriate wrapper below
5. Read `$SANDBOX_DIR/output.txt` and `$SANDBOX_DIR/exitcode.txt`
6. Report back (see Reporting section)

## macOS — sandbox-exec + nix-shell --pure

```bash
SANDBOX_DIR=$(mktemp -d /tmp/agent-sandbox-XXXXXX)
sandbox-exec \
  -f "$SKILL_DIR/profiles/{profile}.sb" \
  -D SANDBOX_DIR="$SANDBOX_DIR" \
  nix-shell --pure -p coreutils bash {packages} \
    --run "{command} > \"$SANDBOX_DIR/output.txt\" 2>&1; echo \$? > \"$SANDBOX_DIR/exitcode.txt\""
```

- `{profile}` defaults to `default`
- When `network=no`, use the `network-off` profile automatically
- When `project_dir` is set and profile is `strict`, add a `(allow file-read* (subpath "{project_dir}"))` rule — or switch to `default` profile which allows reads everywhere

## Linux — bwrap + nix-shell --pure

```bash
SANDBOX_DIR=$(mktemp -d /tmp/agent-sandbox-XXXXXX)
bwrap \
  --ro-bind /nix /nix \
  --ro-bind /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf \
  --ro-bind /etc/ssl/certs /etc/ssl/certs \
  --tmpfs /tmp \
  --bind "$SANDBOX_DIR" "$SANDBOX_DIR" \
  --proc /proc \
  --dev /dev \
  --unshare-pid \
  --unshare-ipc \
  --unshare-uts \
  --die-with-parent \
  nix-shell --pure -p coreutils bash {packages} \
    --run "{command} > \"$SANDBOX_DIR/output.txt\" 2>&1; echo \$? > \"$SANDBOX_DIR/exitcode.txt\""
```

Modifiers:
- When `project_dir` is set: add `--ro-bind "$project_dir" "$project_dir"` before `nix-shell`
- When `network=no`: add `--unshare-net` and drop the `--ro-bind /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf` line

## Reporting back

After the command completes, report:

- **Platform**: macOS (sandbox-exec + `{profile}` profile) or Linux (bwrap)
- **Packages declared**: the packages you passed + coreutils + bash (always added)
- **Exit code**: from `$SANDBOX_DIR/exitcode.txt`
- **Output**: contents of `$SANDBOX_DIR/output.txt`
- **Sandbox dir**: `$SANDBOX_DIR` — persists until user cleans up or OS reboot

If any of the sandboxed packages seem like they'd be broadly useful at the system level (not just for this task), add a brief note at the end suggesting the user consider adding them permanently — but do not modify any config yourself. Example: "Note: `ffmpeg` might be worth adding to your system packages if you use it regularly."

## Failure modes

- **bwrap: operation not permitted** → check `/proc/sys/kernel/unprivileged_userns_clone` must be `1` (NixOS default)
- **sandbox-exec: initialization failed** → SBPL syntax error; dry-run with `sandbox-exec -n -f <profile>.sb /bin/true`
- **DNS fails in bwrap** → ensure using `/run/systemd/resolve/stub-resolv.conf` not `/etc/resolv.conf` (NixOS systemd-resolved makes the latter a dangling symlink)
- **nix-shell can't reach Nix daemon in sandbox-exec** → the profile needs `(allow file-read* file-write* (literal "/private/var/run/nix-daemon.sock"))`; `default.sb` and `network-off.sb` allow this via `(allow default)`; `strict.sb` has it explicitly
- **strict.sb: macOS logging fails inside sandbox** → uncomment the `mach-lookup` line in `strict.sb`
