#!/usr/bin/env bash
# Quick Pull Script - holt aktuelle Settings vom Remote
cd ~/.claude
git stash  # Lokale Änderungen sichern
git pull
git stash pop 2>/dev/null || echo "No stashed changes"
echo "✅ Pulled from remote"
