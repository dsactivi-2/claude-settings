#!/usr/bin/env python3
"""
Duplicate Skills Finder using pgvector + Haiku
Workflow: pgvector similarity → Haiku review → Delete duplicates
"""

import psycopg2
import json
import sys
from typing import List, Dict, Tuple

# Config
SIMILARITY_THRESHOLD = 0.90  # 90% similar = potential duplicate
DB_CONFIG = {
    "host": "localhost",
    "database": "oi_memory",
    "user": "dsselmanovic"
}


def find_similar_pairs(threshold: float = SIMILARITY_THRESHOLD) -> List[Tuple]:
    """Use pgvector to find semantically similar skill pairs"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    print(f"🔍 Searching for similar pairs (threshold: {threshold})...")

    # pgvector similarity search
    cur.execute("""
        SELECT
            s1.id as id1,
            s1.name as name1,
            s1.description as desc1,
            s1.installs as inst1,
            s2.id as id2,
            s2.name as name2,
            s2.description as desc2,
            s2.installs as inst2,
            1 - (s1.embedding <=> s2.embedding) as similarity
        FROM skills s1, skills s2
        WHERE s1.id < s2.id
        AND 1 - (s1.embedding <=> s2.embedding) >= %s
        ORDER BY similarity DESC;
    """, (threshold,))

    pairs = cur.fetchall()
    conn.close()

    print(f"✅ Found {len(pairs)} potential duplicate pairs")
    return pairs


def format_pairs_for_haiku(pairs: List[Tuple]) -> str:
    """Format pairs for Haiku analysis"""
    prompt = """Analyze these skill pairs for duplicates.

For each pair, determine:
1. Are they DUPLICATES? (yes/no)
2. If yes, which one to KEEP? (1 or 2)
3. Reasoning (1 sentence)

Respond in JSON format:
```json
[
  {
    "pair_id": 1,
    "is_duplicate": true,
    "keep": 1,
    "delete": 2,
    "reason": "Skill 1 has more installs and better documentation"
  }
]
```

PAIRS TO ANALYZE:
"""

    for idx, pair in enumerate(pairs, 1):
        id1, name1, desc1, inst1, id2, name2, desc2, inst2, similarity = pair

        prompt += f"""
---
PAIR {idx} (Similarity: {similarity:.2%})

Skill 1:
  ID: {id1}
  Name: {name1}
  Description: {desc1[:100]}...
  Installs: {inst1:,}

Skill 2:
  ID: {id2}
  Name: {name2}
  Description: {desc2[:100]}...
  Installs: {inst2:,}
"""

    prompt += "\n\nProvide your analysis as JSON array."
    return prompt


def review_with_haiku(pairs: List[Tuple]) -> List[Dict]:
    """Send pairs to Haiku for duplicate determination"""
    print(f"\n🤖 Sending {len(pairs)} pairs to Haiku for review...")

    prompt = format_pairs_for_haiku(pairs)

    # Calculate token estimate
    token_estimate = len(prompt) // 4
    cost_estimate = (token_estimate * 0.80 + 2000 * 4.00) / 1_000_000
    print(f"   Estimated tokens: ~{token_estimate:,}")
    print(f"   Estimated cost: ${cost_estimate:.4f}")

    # In real implementation, call Haiku API here
    # For now, show what would be sent
    print(f"\n📝 Prompt preview (first 500 chars):")
    print(prompt[:500] + "...")

    print("\n⚠️  SIMULATION MODE - Would call Haiku API here")
    print("   To enable: Set ANTHROPIC_API_KEY and uncomment API call")

    # Simulated response for demo
    simulated_response = []
    for idx, pair in enumerate(pairs[:3], 1):  # Only first 3 for demo
        id1, name1, desc1, inst1, id2, name2, desc2, inst2, similarity = pair

        # Simple logic: keep higher installs
        if inst1 > inst2:
            keep, delete = 1, 2
            keep_id, delete_id = id1, id2
        else:
            keep, delete = 2, 1
            keep_id, delete_id = id2, id1

        simulated_response.append({
            "pair_id": idx,
            "is_duplicate": similarity > 0.95,
            "keep": keep,
            "delete": delete,
            "keep_id": keep_id,
            "delete_id": delete_id,
            "reason": f"Skill {keep} has {max(inst1, inst2):,} installs vs {min(inst1, inst2):,}"
        })

    return simulated_response


def delete_duplicates(decisions: List[Dict], dry_run: bool = True):
    """Delete duplicate skills based on Haiku's decisions"""
    to_delete = [d['delete_id'] for d in decisions if d['is_duplicate']]

    if not to_delete:
        print("\n✅ No duplicates to delete")
        return

    print(f"\n🗑️  Would delete {len(to_delete)} duplicate skills:")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for skill_id in to_delete:
        cur.execute("SELECT name FROM skills WHERE id = %s", (skill_id,))
        name = cur.fetchone()[0]
        print(f"   - {name} (ID: {skill_id})")

    if dry_run:
        print("\n⚠️  DRY RUN - No actual deletion")
        print("   To delete for real: python find-duplicates.py --delete")
    else:
        confirm = input("\n⚠️  DELETE THESE SKILLS? (yes/no): ")
        if confirm.lower() == 'yes':
            for skill_id in to_delete:
                cur.execute("DELETE FROM skills WHERE id = %s", (skill_id,))
            conn.commit()
            print(f"✅ Deleted {len(to_delete)} duplicate skills")
        else:
            print("❌ Deletion cancelled")

    conn.close()


def main():
    print("=" * 80)
    print("DUPLICATE SKILLS FINDER (pgvector + Haiku)")
    print("=" * 80)

    # Step 1: pgvector similarity search
    pairs = find_similar_pairs(threshold=0.90)

    if not pairs:
        print("\n✅ No potential duplicates found (similarity > 90%)")
        return

    # Step 2: Haiku review
    decisions = review_with_haiku(pairs)

    # Step 3: Show results
    print(f"\n📊 HAIKU'S DECISIONS:")
    print("=" * 80)

    duplicates = [d for d in decisions if d['is_duplicate']]
    not_duplicates = [d for d in decisions if not d['is_duplicate']]

    if duplicates:
        print(f"\n✅ CONFIRMED DUPLICATES: {len(duplicates)}")
        for d in duplicates:
            print(f"   Pair {d['pair_id']}: Keep skill {d['keep']}, Delete skill {d['delete']}")
            print(f"   Reason: {d['reason']}")

    if not_duplicates:
        print(f"\n➖ NOT DUPLICATES: {len(not_duplicates)}")
        for d in not_duplicates:
            print(f"   Pair {d['pair_id']}: {d['reason']}")

    # Step 4: Delete (dry run by default)
    if duplicates:
        dry_run = '--delete' not in sys.argv
        delete_duplicates(duplicates, dry_run=dry_run)

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"  Potential pairs found: {len(pairs)}")
    print(f"  Confirmed duplicates: {len(duplicates)}")
    print(f"  False positives: {len(not_duplicates)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
