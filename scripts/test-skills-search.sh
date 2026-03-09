#!/usr/bin/env bash
# Skills Database Search Test Script
# Tests semantic search functionality

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Skills Database Search Test${NC}"
echo -e "${BLUE}=====================================${NC}"

# Test queries
QUERIES=(
    "backend API development"
    "AI and machine learning pipelines"
    "cloud deployment automation"
    "testing and quality assurance"
    "mobile app development"
    "database optimization"
    "security and authentication"
    "monitoring and observability"
)

# Python test script
~/.local/pipx/venvs/open-interpreter/bin/python << 'EOF'
from sentence_transformers import SentenceTransformer
import psycopg2
import sys

# Test queries
queries = [
    "backend API development",
    "AI and machine learning pipelines",
    "cloud deployment automation",
    "testing and quality assurance",
    "mobile app development",
    "database optimization",
    "security and authentication",
    "monitoring and observability",
]

# Initialize model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to database
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='dsselmanovic',
        database='oi_memory'
    )
    cur = conn.cursor()

    # Get total skills count
    cur.execute("SELECT COUNT(*) FROM skills;")
    total_skills = cur.fetchone()[0]
    print(f"Total skills in database: {total_skills}\n")

    # Test each query
    for query in queries:
        print(f"\033[1;33mQuery: '{query}'\033[0m")

        # Generate embedding
        query_embedding = model.encode(query).tolist()

        # Search
        cur.execute("""
            SELECT
                name,
                category,
                installs,
                1 - (embedding <=> %s::vector) as similarity
            FROM skills
            ORDER BY embedding <=> %s::vector
            LIMIT 5;
        """, (query_embedding, query_embedding))

        results = cur.fetchall()

        for i, (name, category, installs, similarity) in enumerate(results, 1):
            print(f"  \033[0;32m{i}. {name}\033[0m ({similarity:.2%} match)")
            print(f"     Categories: {', '.join(category)}")
            print(f"     Installs: {installs:,}")

        print()

    cur.close()
    conn.close()

    print("\033[0;32m====================================\033[0m")
    print("\033[0;32mAll tests completed successfully\033[0m")
    print("\033[0;32m====================================\033[0m")

except Exception as e:
    print(f"\033[0;31mError: {e}\033[0m")
    sys.exit(1)
EOF
