#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SKILLS_DIR/src"

# ---------------------------------------------------------------------------
# Third-party skill sources
# Format: "repo-url|clone-dir|skill-subpath|symlink-name"
# ---------------------------------------------------------------------------
THIRD_PARTY=(
  "https://github.com/anthropics/skills|src/anthropic-skills|skills/skill-creator|anthropics-skill-creator"
  "https://github.com/anthropics/skills|src/anthropic-skills|skills/pdf|anthropics-pdf"
  "https://github.com/anthropics/skills|src/anthropic-skills|skills/xlsx|anthropics-xlsx"
  "https://github.com/anthropics/skills|src/anthropic-skills|skills/pptx|anthropics-pptx"
  "https://github.com/anthropics/skills|src/anthropic-skills|skills/docx|anthropics-docx"
)

mkdir -p "$SRC_DIR"

for entry in "${THIRD_PARTY[@]}"; do
  IFS='|' read -r repo clone_dir skill_path symlink_name <<< "$entry"
  clone_path="$SKILLS_DIR/$clone_dir"

  # Clone if not already present
  if [ ! -d "$clone_path/.git" ]; then
    echo "Cloning $repo -> $clone_path"
    git clone "$repo" "$clone_path"
  else
    echo "Already cloned: $clone_path"
  fi

  # Create symlink if missing
  target="$SKILLS_DIR/$symlink_name"
  source="$clone_path/$skill_path"
  if [ ! -L "$target" ]; then
    ln -s "$source" "$target"
    echo "Linked: $symlink_name -> $clone_dir/$skill_path"
  else
    echo "Symlink exists: $symlink_name"
  fi
done

echo "Done."
