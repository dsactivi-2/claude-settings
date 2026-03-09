#!/usr/bin/env bash
# Quick Push Script - synchronisiert lokale Änderungen
cd ~/.claude
git add -A
git commit -m "Settings sync $(date +%Y-%m-%d_%H:%M:%S)" || echo "No changes"
git push
echo "✅ Pushed to remote"
