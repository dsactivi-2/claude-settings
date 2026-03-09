#!/usr/bin/env bash
#
# Claude Code Settings Sync Setup
# Synchronisiert Claude Settings zwischen Rechnern
#

set -e

echo "🔄 Claude Code Settings Sync Setup"
echo "===================================="
echo ""

CLAUDE_DIR="$HOME/.claude"
REPO_URL="${1:-}" # Git Remote URL als Parameter

cd "$CLAUDE_DIR"

# Git initialisieren (falls noch nicht)
if [ ! -d .git ]; then
    git init
    echo "✅ Git repository initialized"
fi

# .gitignore erstellen (falls nicht vorhanden)
if [ ! -f .gitignore ]; then
    cat > .gitignore << 'EOF'
# Sensitive data
*.key
*.pem
*.token
*secret*
*password*
.env
.env.*

# Session logs (zu groß)
*.jsonl
projects/*/

# Temporary files
*.tmp
*.log
.DS_Store

# Local settings (computer-specific)
settings.local.json
*local.backup*.json

# Caches
.cache/
*.cache
stats-cache.json
mcp-needs-auth-cache.json

# Node modules
node_modules/

# Memory database (zu groß, optional auskommentieren)
# memory.db
EOF
    echo "✅ .gitignore created"
fi

# Wichtige Dateien zum Sync hinzufügen
echo ""
echo "📋 Files to sync:"
echo "  - CLAUDE.md (global instructions)"
echo "  - settings.json (user settings)"
echo "  - agents/ (custom agents)"
echo "  - skills/ (installed skills)"
echo "  - hooks/ (custom hooks)"
echo "  - scripts/ (helper scripts)"
echo "  - memory.db (optional, kann groß sein)"
echo ""

# Add files
git add .gitignore
git add CLAUDE.md 2>/dev/null || echo "⚠️  CLAUDE.md not found"
git add settings.json 2>/dev/null || echo "⚠️  settings.json not found"
git add agents/ 2>/dev/null || echo "⚠️  agents/ not found"
git add skills/ 2>/dev/null || echo "⚠️  skills/ not found"
git add hooks/ 2>/dev/null || echo "⚠️  hooks/ not found"
git add scripts/ 2>/dev/null || echo "⚠️  scripts/ not found"
git add commands/ 2>/dev/null || echo "⚠️  commands/ not found"

# Commit
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    git commit -m "Claude Code settings backup $(date +%Y-%m-%d)"
    echo "✅ Settings committed"
fi

# Remote hinzufügen (falls URL angegeben)
if [ -n "$REPO_URL" ]; then
    git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
    echo "✅ Remote set to: $REPO_URL"

    read -p "Push to remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin master
        echo "✅ Pushed to remote"
    fi
fi

echo ""
echo "=================================="
echo "✅ Sync Setup Complete!"
echo "=================================="
echo ""
echo "Nächste Schritte:"
echo ""
echo "1. Auf diesem Rechner (Mac):"
echo "   cd ~/.claude"
echo "   git remote add origin <YOUR_REPO_URL>"
echo "   git push -u origin master"
echo ""
echo "2. Auf anderem Rechner (Linux Server):"
echo "   git clone <YOUR_REPO_URL> ~/.claude"
echo "   # oder falls ~/.claude schon existiert:"
echo "   cd ~/.claude && git init && git remote add origin <YOUR_REPO_URL>"
echo "   git pull origin master"
echo ""
echo "3. Regelmäßig synchronisieren:"
echo "   # Push (Mac)"
echo "   cd ~/.claude && git add . && git commit -m 'update' && git push"
echo "   "
echo "   # Pull (Server)"
echo "   cd ~/.claude && git pull"
echo ""
echo "Alternative: Private GitHub/GitLab Repo"
echo "  - Erstelle privates Repo: github.com/new"
echo "  - git remote add origin git@github.com:username/claude-settings.git"
echo "  - git push -u origin master"
echo ""
