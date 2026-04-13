#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SKILLS_DIR/src"

# ---------------------------------------------------------------------------
# External skills — add entries here: <repo-url> <skill-path>
# ---------------------------------------------------------------------------
declare -a SKILLS=(
  "https://github.com/anthropics/skills  skills/skill-creator"
  "https://github.com/anthropics/skills  skills/pdf"
  "https://github.com/anthropics/skills  skills/xlsx"
  "https://github.com/anthropics/skills  skills/pptx"
  "https://github.com/anthropics/skills  skills/docx"

  # K-Dense-AI/claude-scientific-skills
  "https://github.com/K-Dense-AI/claude-scientific-skills  scientific-skills/markitdown"
  "https://github.com/K-Dense-AI/claude-scientific-skills  scientific-skills/citation-management"
)

# ---------------------------------------------------------------------------
# Helper — clone dir: src/org/repo, symlink name: org-skilldir
# ---------------------------------------------------------------------------
link_skill() {
  local repo="$1" skill_path="$2"
  local repo_slug="${repo#https://github.com/}"
  local org="${repo_slug%%/*}"
  local skill_dir="${skill_path##*/}"
  local symlink_name="$org-$skill_dir"
  local clone_path="$SRC_DIR/$repo_slug"

  mkdir -p "$(dirname "$clone_path")"

  if [ ! -d "$clone_path/.git" ]; then
    echo "Cloning $repo (sparse: $skill_path)"
    git clone --no-checkout --filter=blob:none "$repo" "$clone_path"
    git -C "$clone_path" sparse-checkout init --cone
    git -C "$clone_path" sparse-checkout add "$skill_path"
    git -C "$clone_path" checkout
  else
    echo "Updating sparse checkout: $clone_path (+$skill_path)"
    git -C "$clone_path" sparse-checkout add "$skill_path"
  fi

  local target="$SKILLS_DIR/$symlink_name"
  local relative_target="src/$repo_slug/$skill_path"
  if [ ! -L "$target" ]; then
    ln -s "$relative_target" "$target"
    echo "Linked: $symlink_name -> $relative_target"
  else
    echo "Symlink exists: $symlink_name"
  fi
}

# ---------------------------------------------------------------------------
mkdir -p "$SRC_DIR"

for entry in "${SKILLS[@]}"; do
  link_skill $entry
done

echo "Done."
