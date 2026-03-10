#!/usr/bin/env bash
#
# GitHub Push Setup - Quick Commands
#

set -e

echo "🚀 GitHub Push Setup"
echo "===================="
echo ""

# Check if remote exists
if git remote get-url origin &>/dev/null; then
    echo "✅ Remote 'origin' already configured"
    git remote -v
    echo ""
    read -p "Push to remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        echo "✅ Pushed to GitHub"
    fi
else
    echo "⚠️  No remote configured yet"
    echo ""
    echo "Schritt 1: Erstelle GitHub Repo"
    echo "  Browser: https://github.com/new"
    echo "  Name: claude-settings"
    echo "  Privacy: PRIVATE ⚠️"
    echo ""
    read -p "GitHub Username: " USERNAME
    echo ""

    REPO_URL="git@github.com:${USERNAME}/claude-settings.git"

    echo "Schritt 2: Remote hinzufügen"
    git remote add origin "$REPO_URL"
    echo "✅ Remote added: $REPO_URL"
    echo ""

    echo "Schritt 3: Push to GitHub"
    read -p "Push jetzt? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin master
        echo "✅ Pushed to GitHub!"
        echo ""
        echo "Repository URL: https://github.com/${USERNAME}/claude-settings"
    else
        echo "⏳ Push später mit:"
        echo "   cd ~/.claude && git push -u origin master"
    fi
fi

echo ""
echo "===================="
echo "✅ Setup Complete"
echo "===================="
echo ""
echo "Nächste Schritte:"
echo "1. Auf anderem Rechner clonen:"
echo "   git clone git@github.com:${USERNAME:-YOUR_USERNAME}/claude-settings.git ~/.claude"
echo ""
echo "2. Regelmäßig synchronisieren:"
echo "   Mac:    ~/.claude/sync-push.sh"
echo "   Server: ~/.claude/sync-pull.sh"
echo ""
