#!/usr/bin/env bash
# Push the prompt-file updates to GitHub.
# Run from anywhere; it cd's into the repo.
set -euo pipefail

REPO="/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs"
cd "$REPO"

# Stage the project updates (prompts + index). The email draft is left out of the
# code repo by default; add it manually if you want it tracked.
git add prompts/

# Uncomment to also commit the collaborator email draft:
# git add collaborator_email_draft.md

# Show what will be committed
git status --short

# Commit (skip cleanly if nothing is staged)
if git diff --cached --quiet; then
  echo "Nothing staged to commit."
else
  git commit -m "prompts: add #16-#18 (emergent per-curve validation, rich medium, medium-matched allocation + report equations/provenance) and update index"
fi

# Push current branch to origin, setting upstream if needed
BRANCH="$(git branch --show-current)"
git push -u origin "$BRANCH"

echo "Done. Pushed $BRANCH to origin."
