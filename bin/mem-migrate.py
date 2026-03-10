#!/usr/bin/env python3
"""
Migrate existing ~/claude-memories.json entries into AgentDB SQLite.
Usage:
  mem-migrate.py              — migrate all entries
  mem-migrate.py --dry-run    — show what would be migrated
"""

import json
import os
import sys
import argparse

# Add bin dir to path for importing mem-store
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module

SOURCE_FILE = os.path.expanduser("~/claude-memories.json")

# Map old categories to new namespaces
CATEGORY_MAP = {
    "projekte": "projects",
    "business": "projects",
    "techstack": "techstack",
    "testing": "patterns",
    "style": "preferences",
    "templates": "patterns",
    "standards": "patterns",
    "general": "default",
}


def main():
    parser = argparse.ArgumentParser(description="Migrate JSON memories to AgentDB")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated")
    args = parser.parse_args()

    if not os.path.exists(SOURCE_FILE):
        print(f"ERROR: {SOURCE_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    memories = data.get("memories", [])
    if not memories:
        print("No memories to migrate.")
        return

    print(f"Found {len(memories)} entries in {SOURCE_FILE}")

    if args.dry_run:
        print("\n--- DRY RUN ---")
        for m in memories:
            ns = CATEGORY_MAP.get(m.get("category", "general"), "default")
            print(f"  #{m['id']} [{m['category']}] -> namespace={ns}: {m['text'][:60]}...")
        print(f"\nWould migrate {len(memories)} entries. Run without --dry-run to execute.")
        return

    # Import store function
    mem_store = import_module("mem-store")

    migrated = 0
    errors = 0
    for m in memories:
        ns = CATEGORY_MAP.get(m.get("category", "general"), "default")
        key = f"migrated_{m['id']}_{m.get('category', 'general')}"

        try:
            mem_store.store_memory(
                text=m["text"],
                namespace=ns,
                mem_type="semantic",
                tags=m.get("category", ""),
                key=key,
                quiet=True
            )
            migrated += 1
            print(f"  Migrated #{m['id']} [{m['category']}] -> {ns}")
        except Exception as e:
            errors += 1
            print(f"  ERROR #{m['id']}: {e}", file=sys.stderr)

    print(f"\nDone: {migrated} migrated, {errors} errors.")


if __name__ == "__main__":
    main()
