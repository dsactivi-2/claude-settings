#!/usr/bin/env python3
"""
AgentDB Memory Store — Stores memories with OpenAI vector embeddings.
Usage:
  mem-store.py "text" [-n namespace] [-t type] [--tags "a,b"] [-k key] [-q]
"""

import sqlite3
import json
import os
import hashlib
import sys
import argparse
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/memory.db")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

VALID_NAMESPACES = ["decisions", "techstack", "patterns", "errors", "projects", "preferences", "default"]
VALID_TYPES = ["semantic", "episodic", "procedural", "working", "pattern"]


def ensure_db_ready(conn):
    """One-time migration: update 768->1536 dims if needed."""
    cur = conn.execute("SELECT dimensions FROM vector_indexes WHERE name='default'")
    row = cur.fetchone()
    if row and row[0] != EMBEDDING_DIM:
        now_ms = int(datetime.now().timestamp() * 1000)
        conn.execute(
            "UPDATE vector_indexes SET dimensions=?, updated_at=? WHERE dimensions=?",
            (EMBEDDING_DIM, now_ms, row[0])
        )
        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value, updated_at) VALUES (?, ?, ?)",
            ("embedding_model", EMBEDDING_MODEL, now_ms)
        )
        conn.commit()


def generate_embedding(text):
    """Generate embedding via OpenAI API."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=[text])
    return response.data[0].embedding


def store_memory(text, namespace="default", mem_type="semantic", tags=None, key=None, quiet=False):
    """Store a memory entry with embedding."""
    conn = sqlite3.connect(DB_PATH)
    ensure_db_ready(conn)

    embedding = generate_embedding(text)

    mem_id = hashlib.sha256(
        f"{text[:50]}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    if not key:
        slug = text[:40].lower()
        for ch in [" ", "\n", "\t", "/", "\\", ":", "."]:
            slug = slug.replace(ch, "_")
        key = f"{slug}_{mem_id[:8]}"

    now_ms = int(datetime.now().timestamp() * 1000)
    tags_json = json.dumps(tags.split(",") if tags else [])
    meta_json = json.dumps({"source": "manual", "created_by": "mem-store"})

    try:
        conn.execute("""
            INSERT INTO memory_entries
            (id, key, namespace, content, type, embedding, embedding_model,
             embedding_dimensions, tags, metadata, created_at, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (
            mem_id, key, namespace, text, mem_type,
            json.dumps(embedding), EMBEDDING_MODEL, EMBEDDING_DIM,
            tags_json, meta_json, now_ms, now_ms
        ))
        conn.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            mem_id = hashlib.sha256(
                f"{text[:50]}{datetime.now().isoformat()}_retry".encode()
            ).hexdigest()[:16]
            key = f"{key}_{mem_id[:4]}"
            conn.execute("""
                INSERT INTO memory_entries
                (id, key, namespace, content, type, embedding, embedding_model,
                 embedding_dimensions, tags, metadata, created_at, updated_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                mem_id, key, namespace, text, mem_type,
                json.dumps(embedding), EMBEDDING_MODEL, EMBEDDING_DIM,
                tags_json, meta_json, now_ms, now_ms
            ))
            conn.commit()
        else:
            raise
    finally:
        conn.close()

    if quiet:
        print(mem_id)
    else:
        print(f"Stored: [{mem_id}] namespace={namespace} type={mem_type} ({EMBEDDING_DIM}-dim)")

    return mem_id


def main():
    parser = argparse.ArgumentParser(description="Store memory with vector embedding")
    parser.add_argument("text", help="Memory content to store")
    parser.add_argument("-n", "--namespace", default="default", choices=VALID_NAMESPACES)
    parser.add_argument("-t", "--type", default="semantic", choices=VALID_TYPES, dest="mem_type")
    parser.add_argument("--tags", default=None, help="Comma-separated tags")
    parser.add_argument("-k", "--key", default=None, help="Custom unique key")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()
    store_memory(args.text, args.namespace, args.mem_type, args.tags, args.key, args.quiet)


if __name__ == "__main__":
    main()
