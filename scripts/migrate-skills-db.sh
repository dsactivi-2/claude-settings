#!/usr/bin/env bash
# Skills Database Migration Script
# Auto-migrates skills database from local PostgreSQL to remote server
# Usage: ./migrate-skills-db.sh [--dry-run] [--rollback]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
MIGRATION_DIR="$HOME/.claude/skills-db"
LOG_FILE="$MIGRATION_DIR/migration.log"
BACKUP_DIR="$MIGRATION_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Source database (local)
SRC_DB_HOST="${DB_HOST:-localhost}"
SRC_DB_PORT="${DB_PORT:-5432}"
SRC_DB_USER="${DB_USER:-dsselmanovic}"
SRC_DB_NAME="${DB_NAME:-oi_memory}"
SRC_DB_PASS="${DB_PASS:-}"

# Target database (from environment)
TGT_DB_HOST="${SKILLS_DB_HOST:-}"
TGT_DB_PORT="${SKILLS_DB_PORT:-5432}"
TGT_DB_USER="${SKILLS_DB_USER:-}"
TGT_DB_NAME="${SKILLS_DB_NAME:-oi_memory}"
TGT_DB_PASS="${SKILLS_DB_PASS:-}"

# Modes
DRY_RUN=false
ROLLBACK=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --rollback)
            ROLLBACK=true
            ;;
        --help)
            echo "Skills Database Migration Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Simulate migration without making changes"
            echo "  --rollback   Restore from last backup"
            echo "  --help       Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  SKILLS_DB_HOST    Target database host"
            echo "  SKILLS_DB_PORT    Target database port (default: 5432)"
            echo "  SKILLS_DB_USER    Target database user"
            echo "  SKILLS_DB_NAME    Target database name (default: oi_memory)"
            echo "  SKILLS_DB_PASS    Target database password"
            exit 0
            ;;
    esac
done

# Initialize directories
mkdir -p "$MIGRATION_DIR" "$BACKUP_DIR"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac

    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Check if migration is needed
check_migration_needed() {
    if [ -z "$TGT_DB_HOST" ]; then
        log WARN "SKILLS_DB_HOST not set. No migration needed."
        log INFO "To trigger migration, set environment variable:"
        log INFO "  export SKILLS_DB_HOST=your-server.com"
        log INFO "  export SKILLS_DB_USER=username"
        log INFO "  export SKILLS_DB_PASS=password"
        exit 0
    fi

    if [ "$TGT_DB_HOST" = "localhost" ] || [ "$TGT_DB_HOST" = "127.0.0.1" ]; then
        log WARN "Target host is localhost. No migration needed."
        exit 0
    fi

    log SUCCESS "Migration needed: $SRC_DB_HOST -> $TGT_DB_HOST"
}

# Create backup
create_backup() {
    local backup_file="$BACKUP_DIR/skills_backup_${TIMESTAMP}.sql"

    log INFO "Creating backup: $backup_file"

    PGPASSWORD="$SRC_DB_PASS" pg_dump \
        -h "$SRC_DB_HOST" \
        -p "$SRC_DB_PORT" \
        -U "$SRC_DB_USER" \
        -d "$SRC_DB_NAME" \
        -t skills \
        --no-owner \
        --no-acl \
        -f "$backup_file"

    if [ $? -eq 0 ]; then
        log SUCCESS "Backup created: $(du -h "$backup_file" | cut -f1)"
        echo "$backup_file"
    else
        log ERROR "Backup failed"
        exit 1
    fi
}

# Test target connection
test_target_connection() {
    log INFO "Testing target database connection..."

    PGPASSWORD="$TGT_DB_PASS" psql \
        -h "$TGT_DB_HOST" \
        -p "$TGT_DB_PORT" \
        -U "$TGT_DB_USER" \
        -d "$TGT_DB_NAME" \
        -c "SELECT version();" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log SUCCESS "Target database connection successful"
    else
        log ERROR "Cannot connect to target database"
        exit 1
    fi
}

# Migrate skills table
migrate_skills() {
    local backup_file=$1

    log INFO "Migrating skills table to $TGT_DB_HOST..."

    if [ "$DRY_RUN" = true ]; then
        log WARN "DRY RUN - Would restore from: $backup_file"
        return
    fi

    # Restore to target
    PGPASSWORD="$TGT_DB_PASS" psql \
        -h "$TGT_DB_HOST" \
        -p "$TGT_DB_PORT" \
        -U "$TGT_DB_USER" \
        -d "$TGT_DB_NAME" \
        -f "$backup_file" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log SUCCESS "Skills table migrated successfully"
    else
        log ERROR "Migration failed"
        exit 1
    fi
}

# Update configuration files
update_configs() {
    local config_files=(
        "$HOME/.local/pipx/venvs/open-interpreter/lib/python3.12/site-packages/interpreter/profiles/default.yaml"
        "$HOME/Library/Application Support/open-interpreter/profiles/default.yaml"
        "$HOME/Library/Application Support/open-interpreter/profiles/advanced.py"
        "$HOME/Library/Application Support/open-interpreter/profiles/default.py"
    )

    log INFO "Updating configuration files..."

    for config_file in "${config_files[@]}"; do
        if [ -f "$config_file" ]; then
            if [ "$DRY_RUN" = true ]; then
                log WARN "DRY RUN - Would update: $config_file"
            else
                # Backup original
                cp "$config_file" "${config_file}.backup_${TIMESTAMP}"

                # Update PostgreSQL connection strings
                sed -i.tmp "s/localhost:5432/$TGT_DB_HOST:$TGT_DB_PORT/g" "$config_file"
                sed -i.tmp "s/host=localhost/host=$TGT_DB_HOST/g" "$config_file"
                rm -f "${config_file}.tmp"

                log SUCCESS "Updated: $config_file"
            fi
        fi
    done
}


# Update helper scripts
update_scripts() {
    local scripts=(
        "$HOME/.local/bin/oi-status"
        "$HOME/.local/bin/oi-healthcheck"
        "$HOME/.local/bin/oi-optimize"
    )

    log INFO "Updating helper scripts..."

    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if [ "$DRY_RUN" = true ]; then
                log WARN "DRY RUN - Would update: $script"
            else
                # Backup
                cp "$script" "${script}.backup_${TIMESTAMP}"

                # Update connection strings
                sed -i.tmp "s/localhost:5432/$TGT_DB_HOST:$TGT_DB_PORT/g" "$script"
                sed -i.tmp "s/host=localhost/host=$TGT_DB_HOST/g" "$script"
                rm -f "${script}.tmp"

                log SUCCESS "Updated: $script"
            fi
        fi
    done
}

# Verify migration
verify_migration() {
    log INFO "Verifying migration..."

    # Count skills in target
    local count=$(PGPASSWORD="$TGT_DB_PASS" psql \
        -h "$TGT_DB_HOST" \
        -p "$TGT_DB_PORT" \
        -U "$TGT_DB_USER" \
        -d "$TGT_DB_NAME" \
        -t -c "SELECT COUNT(*) FROM skills;" | xargs)

    if [ "$count" -gt 0 ]; then
        log SUCCESS "Verification passed: $count skills in target database"
    else
        log ERROR "Verification failed: No skills found in target"
        exit 1
    fi
}

# Rollback from backup
rollback() {
    log INFO "Rolling back from latest backup..."

    local latest_backup=$(ls -t "$BACKUP_DIR"/skills_backup_*.sql 2>/dev/null | head -1)

    if [ -z "$latest_backup" ]; then
        log ERROR "No backup found for rollback"
        exit 1
    fi

    log INFO "Restoring from: $latest_backup"

    PGPASSWORD="$SRC_DB_PASS" psql \
        -h "$SRC_DB_HOST" \
        -p "$SRC_DB_PORT" \
        -U "$SRC_DB_USER" \
        -d "$SRC_DB_NAME" \
        -c "DROP TABLE IF EXISTS skills;" > /dev/null 2>&1

    PGPASSWORD="$SRC_DB_PASS" psql \
        -h "$SRC_DB_HOST" \
        -p "$SRC_DB_PORT" \
        -U "$SRC_DB_USER" \
        -d "$SRC_DB_NAME" \
        -f "$latest_backup" > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        log SUCCESS "Rollback completed"
    else
        log ERROR "Rollback failed"
        exit 1
    fi
}

# Main execution
main() {
    log INFO "========================================"
    log INFO "Skills Database Migration"
    log INFO "========================================"
    log INFO "Timestamp: $TIMESTAMP"
    log INFO "Source: $SRC_DB_HOST:$SRC_DB_PORT/$SRC_DB_NAME"
    log INFO "Target: $TGT_DB_HOST:$TGT_DB_PORT/$TGT_DB_NAME"
    log INFO "Mode: $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "LIVE")"
    log INFO "========================================"

    if [ "$ROLLBACK" = true ]; then
        rollback
        exit 0
    fi

    # Check if migration is needed
    check_migration_needed

    # Create backup
    backup_file=$(create_backup)

    # Test target connection
    test_target_connection

    # Perform migration
    migrate_skills "$backup_file"

    # Update configurations
    update_configs
    update_scripts

    # Verify
    if [ "$DRY_RUN" = false ]; then
        verify_migration
    fi

    log INFO "========================================"
    log SUCCESS "Migration completed successfully"
    log INFO "========================================"
    log INFO "Backup saved: $backup_file"
    log INFO "Log file: $LOG_FILE"

    if [ "$DRY_RUN" = false ]; then
        log INFO ""
        log INFO "Changed files backed up with suffix: .backup_${TIMESTAMP}"
        log INFO "To rollback, run: $0 --rollback"
    fi
}

# Run main
main
