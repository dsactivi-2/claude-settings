# 🔄 Claude Code Settings Sync

Synchronisiere deine Claude Code Einstellungen zwischen mehreren Rechnern.

## 📦 Was wird synchronisiert?

- ✅ **CLAUDE.md** - Globale User Instructions
- ✅ **settings.json** - User Settings
- ✅ **agents/** - Custom Agents (120+ agents!)
- ✅ **skills/** - Installierte Skills (40+ skills!)
- ✅ **hooks/** - Custom Hooks & Scripts
- ✅ **commands/** - Slash Commands
- ✅ **scripts/** - Helper Scripts

**NICHT synchronisiert:**
- ❌ Session Logs (*.jsonl) - zu groß
- ❌ settings.local.json - rechner-spezifisch
- ❌ API Keys/Secrets - Sicherheit
- ❌ Cache Files

---

## 🚀 Methode 1: Git Sync (Empfohlen)

### Erstmaliges Setup (bereits erledigt auf Mac!)

✅ Git Repository wurde bereits erstellt
✅ Alle wichtigen Dateien committed

### Schritt 1: GitHub Repo erstellen

```bash
# Erstelle privates GitHub Repo
# Gehe zu: https://github.com/new
# Name: claude-settings
# Privacy: Private ⚠️
```

### Schritt 2: Remote hinzufügen (Mac)

```bash
cd ~/.claude
git remote add origin git@github.com:DEIN_USERNAME/claude-settings.git
git push -u origin master
```

### Schritt 3: Auf anderem Rechner clonen (Linux Server)

```bash
# Option A: Falls ~/.claude noch nicht existiert
git clone git@github.com:DEIN_USERNAME/claude-settings.git ~/.claude

# Option B: Falls ~/.claude bereits existiert
cd ~/.claude
git init
git remote add origin git@github.com:DEIN_USERNAME/claude-settings.git
git pull origin master
```

### Regelmäßiges Sync

**Mac (Push):**
```bash
~/.claude/sync-push.sh
# oder manuell:
cd ~/.claude && git add -A && git commit -m "update" && git push
```

**Linux Server (Pull):**
```bash
~/.claude/sync-pull.sh
# oder manuell:
cd ~/.claude && git pull
```

---

## 🔗 Methode 2: Cloud Sync (Dropbox/iCloud)

### Setup

**Mac:**
```bash
# Verschiebe ~/.claude in Cloud-Ordner
mv ~/.claude ~/Dropbox/claude-settings
ln -s ~/Dropbox/claude-settings ~/.claude
```

**Linux Server:**
```bash
# Installiere Dropbox CLI oder rclone
# Dann sync:
ln -s ~/Dropbox/claude-settings ~/.claude
```

**Vorteile:**
- ✅ Automatischer Sync
- ✅ Keine Git-Kenntnisse nötig

**Nachteile:**
- ❌ Keine Versionskontrolle
- ❌ Konflikte bei gleichzeitiger Nutzung

---

## 📡 Methode 3: rsync (Manuell)

Für einmalige oder seltene Syncs:

```bash
# Von Mac zu Server
rsync -avz --exclude='*.jsonl' --exclude='projects/' \
  ~/.claude/ root@100.101.110.104:~/.claude/

# Von Server zu Mac
rsync -avz --exclude='*.jsonl' --exclude='projects/' \
  root@100.101.110.104:~/.claude/ ~/.claude/
```

---

## 🛠️ Quick Commands

### Mac (wo du gerade bist)

```bash
# Push aktuelle Settings
~/.claude/sync-push.sh

# Status prüfen
cd ~/.claude && git status

# Log ansehen
cd ~/.claude && git log --oneline -10
```

### Linux Server

```bash
# Pull aktuelle Settings
~/.claude/sync-pull.sh

# Verify sync
ls -la ~/.claude/

# Check git status
cd ~/.claude && git status
```

---

## ⚠️ Wichtige Hinweise

### API Keys

**CLAUDE.md kann API Keys enthalten!**

Überprüfe vor dem Push:
```bash
grep -i "api" ~/.claude/CLAUDE.md
grep -i "key" ~/.claude/CLAUDE.md
grep -i "token" ~/.claude/CLAUDE.md
```

Wenn API Keys drin sind:
1. **Option A:** Entfernen und in `.env` auslagern
2. **Option B:** Private Repo verwenden (empfohlen)

### Konflikte vermeiden

- Nicht gleichzeitig auf beiden Rechnern editieren
- Vor Änderungen: `git pull`
- Nach Änderungen: `git push`

### Hooks Verzeichnis

Das `hooks/` Verzeichnis ist ein Git Submodule. Separate Synchronisation:

```bash
cd ~/.claude/hooks
git pull origin main
```

---

## 🎯 Empfohlener Workflow

### Tägliches Arbeiten auf Mac

```bash
# Morgens: Pull latest
~/.claude/sync-pull.sh

# Arbeiten...
# (Skills installieren, Agents erstellen, Settings ändern)

# Abends: Push changes
~/.claude/sync-push.sh
```

### Auf Linux Server arbeiten

```bash
# Vor Session: Pull latest
~/.claude/sync-pull.sh

# Nach Session: Push changes (falls was geändert)
cd ~/.claude && git add -A && git commit -m "server updates" && git push
```

---

## 📊 Status Check

Prüfe, ob Sync funktioniert:

```bash
# Auf beiden Rechnern:
cd ~/.claude
git log --oneline -5
git remote -v

# Sollte gleich sein!
```

---

## 🔧 Troubleshooting

### "Permission denied (publickey)"

SSH-Key für GitHub einrichten:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub
# Copy zu GitHub: https://github.com/settings/keys
```

### "fatal: remote origin already exists"

```bash
cd ~/.claude
git remote remove origin
git remote add origin git@github.com:username/claude-settings.git
```

### Merge Conflicts

```bash
cd ~/.claude
git stash
git pull
git stash pop
# Konflikte manuell lösen
```

---

## 📋 Nächste Schritte

1. ✅ Git Repo erstellt (erledigt!)
2. ⏳ GitHub Repo erstellen (https://github.com/new)
3. ⏳ Remote hinzufügen: `git remote add origin <URL>`
4. ⏳ Push: `git push -u origin master`
5. ⏳ Auf Server clonen: `git clone <URL> ~/.claude`
6. ✅ Sync Scripts nutzen: `~/.claude/sync-push.sh`
