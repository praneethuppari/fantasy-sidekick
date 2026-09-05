#!/usr/bin/env bash
# Initialize git with main + develop if the repo is missing or incomplete.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .git/config ]]; then
  rm -rf .git
  git init -b main
fi

# Ensure ignore and core files exist before first commit
git add -A
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git commit -m "$(cat <<'EOF'
Initial project scaffold for Fantasy Sidekick SMS coach.

EOF
)"
fi

if ! git show-ref --verify --quiet refs/heads/develop; then
  git branch develop
fi

git checkout develop
echo "Branches:"
git branch -v
echo "On: $(git branch --show-current)"
