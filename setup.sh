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
    echo "Cloning $repo -> $clone_path"
    git clone "$repo" "$clone_path"
  else
    echo "Already cloned: $clone_path"
  fi

  local target="$SKILLS_DIR/$symlink_name"
  if [ ! -L "$target" ]; then
    ln -s "$clone_path/$skill_path" "$target"
    echo "Linked: $symlink_name -> src/$repo_slug/$skill_path"
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
