#!/usr/bin/env python3
"""
AgentDB Memory Query — Semantic vector search over stored memories.

3-Layer Architecture:
  Layer 1 HEISS: SESSION-STATE.md + notepad.md (always loaded, ~2-3KB)
  Layer 2 WARM:  project-memory.json (on-demand, ~10KB)
  Layer 3 KALT:  SQLite + HNSW vectors (semantic search, unlimited)

This script handles Layer 3 (KALT). Layers 1+2 are handled by hooks.

Usage:
  mem-query.py "search query"                    — semantic search
  mem-query.py "query" -n decisions --top 3      — filtered search
  mem-query.py --list                            — list all entries
  mem-query.py --stats                           — database stats
  mem-query.py --all-layers "query"              — search across all 3 layers
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/memory.db")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

VALID_NAMESPACES = ["decisions", "techstack", "patterns", "errors", "projects", "preferences", "default"]


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


def cosine_similarity_batch(query_vec, stored_vecs):
    """Compute cosine similarity between query and all stored vectors."""
    import numpy as np

    query = np.array(query_vec, dtype=np.float32)
    stored = np.array(stored_vecs, dtype=np.float32)

    query_norm = query / (np.linalg.norm(query) + 1e-10)
    norms = np.linalg.norm(stored, axis=1, keepdims=True)
    norms[norms == 0] = 1
    stored_norm = stored / norms

    return stored_norm @ query_norm


def search_memories(query_text, namespace=None, mem_type=None, top_k=5, threshold=0.25):
    """Semantic search over memories."""
    conn = sqlite3.connect(DB_PATH)
    try:
        where_parts = ["status = 'active'", "embedding IS NOT NULL"]
        params = []
        if namespace:
            where_parts.append("namespace = ?")
            params.append(namespace)
        if mem_type:
            where_parts.append("type = ?")
            params.append(mem_type)

        where_clause = " AND ".join(where_parts)

        rows = conn.execute(f"""
            SELECT id, key, namespace, content, type, embedding, tags,
                   access_count, created_at
            FROM memory_entries
            WHERE {where_clause}
        """, params).fetchall()

        if not rows:
            return []

        query_embedding = generate_embedding(query_text)

        ids, embeddings, metadata_list = [], [], []
        for row in rows:
            emb = json.loads(row[5])
            if len(emb) == EMBEDDING_DIM:
                ids.append(row[0])
                embeddings.append(emb)
                metadata_list.append({
                    "id": row[0], "key": row[1], "namespace": row[2],
                    "content": row[3], "type": row[4],
                    "tags": json.loads(row[6] or "[]"),
                    "access_count": row[7], "created_at": row[8]
                })

        if not embeddings:
            return []

        similarities = cosine_similarity_batch(query_embedding, embeddings)

        results = []
        for i, sim in enumerate(similarities):
            if sim >= threshold:
                results.append({**metadata_list[i], "similarity": float(sim)})

        results.sort(key=lambda x: x["similarity"], reverse=True)

        now_ms = int(datetime.now().timestamp() * 1000)
        for r in results[:top_k]:
            conn.execute(
                "UPDATE memory_entries SET access_count = access_count + 1, last_accessed_at = ? WHERE id = ?",
                (now_ms, r["id"])
            )
        conn.commit()

        return results[:top_k]
    finally:
        conn.close()


def search_layer1(query_lower):
    """Search Layer 1 (HEISS): SESSION-STATE.md + notepad.md"""
    results = []
    for base in [os.getcwd(), os.path.expanduser("~")]:
        for rel in [".omc/SESSION-STATE.md", ".omc/notepad.md"]:
            path = os.path.join(base, rel)
            if os.path.isfile(path):
                try:
                    with open(path, "r") as f:
                        content = f.read()
                    if query_lower in content.lower():
                        name = os.path.basename(path)
                        lines = [l.strip() for l in content.split("\n") if query_lower in l.lower() and l.strip()]
                        for line in lines[:3]:
                            results.append({"layer": "HEISS", "source": name, "content": line[:120]})
                except Exception:
                    pass
    return results


def search_layer2(query_lower):
    """Search Layer 2 (WARM): project-memory.json"""
    results = []
    for base in [os.getcwd(), os.path.expanduser("~")]:
        path = os.path.join(base, ".omc/project-memory.json")
        if os.path.isfile(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                flat = json.dumps(data, ensure_ascii=False)
                if query_lower in flat.lower():
                    for section, val in data.items():
                        val_str = json.dumps(val, ensure_ascii=False) if not isinstance(val, str) else val
                        if query_lower in val_str.lower():
                            results.append({"layer": "WARM", "source": f"project-memory/{section}", "content": val_str[:120]})
            except Exception:
                pass
    return results


def list_memories(namespace=None):
    """List all memories."""
    conn = sqlite3.connect(DB_PATH)
    where = "WHERE status = 'active'"
    params = []
    if namespace:
        where += " AND namespace = ?"
        params.append(namespace)

    rows = conn.execute(f"""
        SELECT id, namespace, type, content, tags, access_count, created_at
        FROM memory_entries {where}
        ORDER BY created_at DESC
    """, params).fetchall()
    conn.close()
    return rows


def get_stats():
    """Get database statistics."""
    conn = sqlite3.connect(DB_PATH)
    stats = {}

    stats["total"] = conn.execute("SELECT COUNT(*) FROM memory_entries WHERE status='active'").fetchone()[0]
    stats["with_embedding"] = conn.execute("SELECT COUNT(*) FROM memory_entries WHERE embedding IS NOT NULL AND status='active'").fetchone()[0]

    ns_rows = conn.execute("SELECT namespace, COUNT(*) FROM memory_entries WHERE status='active' GROUP BY namespace").fetchall()
    stats["namespaces"] = {r[0]: r[1] for r in ns_rows}

    type_rows = conn.execute("SELECT type, COUNT(*) FROM memory_entries WHERE status='active' GROUP BY type").fetchall()
    stats["types"] = {r[0]: r[1] for r in type_rows}

    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    stats["db_size_mb"] = round(db_size / 1024 / 1024, 2)

    top_rows = conn.execute("SELECT content, access_count FROM memory_entries WHERE status='active' ORDER BY access_count DESC LIMIT 3").fetchall()
    stats["most_accessed"] = [(r[0][:60], r[1]) for r in top_rows]

    vi = conn.execute("SELECT name, dimensions, metric, hnsw_m FROM vector_indexes").fetchall()
    stats["vector_indexes"] = [{"name": r[0], "dims": r[1], "metric": r[2], "hnsw_m": r[3]} for r in vi]

    conn.close()
    return stats


def format_compact(results, query):
    """Token-efficient output (~100 tokens)."""
    if not results:
        print(f'=== 0 results for "{query}" ===')
        return

    print(f'=== {len(results)} results for "{query}" ===')
    for r in results:
        tags_str = f' (tags: {",".join(r["tags"])})' if r["tags"] else ""
        content = r["content"][:80].replace("\n", " ")
        print(f'[{r["similarity"]:.2f}] {r["namespace"]}/{r["type"]}: "{content}"{tags_str}')


def format_all_layers(l1, l2, l3, query):
    """Format results from all 3 layers."""
    total = len(l1) + len(l2) + len(l3)
    print(f'=== {total} results for "{query}" (3 layers) ===')

    if l1:
        print(f"\n-- HEISS (SESSION-STATE/notepad) --")
        for r in l1:
            print(f'  [{r["source"]}] {r["content"]}')

    if l2:
        print(f"\n-- WARM (project-memory) --")
        for r in l2:
            print(f'  [{r["source"]}] {r["content"]}')

    if l3:
        print(f"\n-- KALT (AgentDB vectors) --")
        for r in l3:
            tags_str = f' (tags: {",".join(r["tags"])})' if r["tags"] else ""
            content = r["content"][:80].replace("\n", " ")
            print(f'  [{r["similarity"]:.2f}] {r["namespace"]}/{r["type"]}: "{content}"{tags_str}')

    if total == 0:
        print("Keine Treffer in allen 3 Schichten.")


def main():
    parser = argparse.ArgumentParser(description="Semantic memory search (AgentDB)")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-n", "--namespace", default=None, choices=VALID_NAMESPACES)
    parser.add_argument("-t", "--type", default=None, choices=["semantic", "episodic", "procedural", "working", "pattern"], dest="mem_type")
    parser.add_argument("-k", "--top", type=int, default=5, help="Number of results")
    parser.add_argument("--threshold", type=float, default=0.25, help="Min similarity")
    parser.add_argument("--list", action="store_true", help="List all memories")
    parser.add_argument("--stats", action="store_true", help="Show DB stats")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--compact", action="store_true", help="Token-efficient output")
    parser.add_argument("--all-layers", action="store_true", help="Search all 3 layers")

    args = parser.parse_args()

    if args.stats:
        stats = get_stats()
        if args.json:
            print(json.dumps(stats, indent=2, ensure_ascii=False))
        else:
            print(f"=== AgentDB Memory Stats ===")
            print(f"Total entries:    {stats['total']}")
            print(f"With embeddings:  {stats['with_embedding']}")
            print(f"DB size:          {stats['db_size_mb']} MB")
            print(f"Namespaces:       {stats['namespaces']}")
            print(f"Types:            {stats['types']}")
            if stats["most_accessed"]:
                print(f"Most accessed:")
                for content, cnt in stats["most_accessed"]:
                    print(f"  [{cnt}x] {content}")
            for vi in stats["vector_indexes"]:
                print(f"Index '{vi['name']}': {vi['dims']}-dim {vi['metric']} HNSW(M={vi['hnsw_m']})")
        return

    if args.list:
        rows = list_memories(args.namespace)
        if not rows:
            print("Keine Eintraege.")
            return
        print(f"=== {len(rows)} Memories ===")
        for r in rows:
            tags = json.loads(r[4] or "[]")
            tags_str = f" [{','.join(tags)}]" if tags else ""
            dt = datetime.fromtimestamp(r[6] / 1000).strftime("%Y-%m-%d") if r[6] else "?"
            content = r[3][:70].replace("\n", " ")
            print(f"  #{r[0][:8]} {r[1]}/{r[2]}: {content}{tags_str} ({dt}, {r[5]}x)")
        return

    if not args.query:
        parser.print_help()
        return

    if args.all_layers:
        query_lower = args.query.lower()
        l1 = search_layer1(query_lower)
        l2 = search_layer2(query_lower)
        l3 = search_memories(args.query, args.namespace, args.mem_type, args.top, args.threshold)
        format_all_layers(l1, l2, l3, args.query)
        return

    results = search_memories(args.query, args.namespace, args.mem_type, args.top, args.threshold)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
    else:
        format_compact(results, args.query)


if __name__ == "__main__":
    main()
