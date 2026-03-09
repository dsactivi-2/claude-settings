#!/usr/bin/env python3
"""
Update Skills Metadata
Auto-generate subcategories and quality scores for all skills
"""

import psycopg2
import re
from typing import List, Dict, Any

# Subcategory keyword mappings
SUBCATEGORY_KEYWORDS = {
    "backend": {
        "API": ["api", "rest", "graphql", "endpoint", "routing"],
        "Database": ["database", "db", "sql", "postgres", "mysql", "mongo", "orm", "query"],
        "Authentication": ["auth", "login", "jwt", "oauth", "session", "passport"],
        "Caching": ["cache", "redis", "memcache"],
        "Queue": ["queue", "job", "worker", "bull", "sidekiq"],
        "Validation": ["validation", "schema", "validate"],
        "Logging": ["log", "logging", "winston", "pino"],
        "Testing": ["test", "testing", "jest", "mocha", "pytest"],
    },
    "ai-building": {
        "RAG": ["rag", "retrieval", "embedding", "vector"],
        "Agents": ["agent", "autonomous", "tool"],
        "Prompts": ["prompt", "template", "chain"],
        "Training": ["train", "fine-tune", "model"],
        "Inference": ["inference", "completion", "generation"],
        "LLM": ["llm", "language model", "gpt", "claude"],
    },
    "devops": {
        "CI/CD": ["ci", "cd", "pipeline", "github actions", "jenkins"],
        "Containers": ["docker", "container", "dockerfile"],
        "Kubernetes": ["k8s", "kubernetes", "helm"],
        "Monitoring": ["monitor", "metrics", "prometheus", "grafana"],
        "Deploy": ["deploy", "deployment", "release"],
        "IaC": ["terraform", "ansible", "infrastructure"],
    },
    "frontend": {
        "Framework": ["react", "vue", "angular", "svelte"],
        "UI Components": ["component", "button", "form", "modal"],
        "State Management": ["state", "redux", "zustand", "pinia"],
        "Styling": ["css", "tailwind", "styled", "sass"],
        "Build Tools": ["webpack", "vite", "rollup", "esbuild"],
    },
    "data-science": {
        "Analysis": ["analysis", "pandas", "numpy"],
        "Visualization": ["viz", "plot", "chart", "graph"],
        "ML": ["machine learning", "sklearn", "ml"],
        "Statistics": ["stats", "statistical"],
    },
    "mobile": {
        "iOS": ["ios", "swift", "objective-c"],
        "Android": ["android", "kotlin", "java"],
        "Cross-Platform": ["react native", "flutter", "xamarin"],
    },
    "security": {
        "Encryption": ["encrypt", "crypto", "hash"],
        "Vulnerability": ["vulnerability", "scan", "audit"],
        "Auth": ["auth", "oauth", "jwt"],
    },
    "testing": {
        "Unit": ["unit test", "jest", "mocha", "pytest"],
        "Integration": ["integration test", "e2e"],
        "Performance": ["performance", "load test", "benchmark"],
    },
    "database": {
        "SQL": ["sql", "postgres", "mysql", "sqlite"],
        "NoSQL": ["nosql", "mongo", "redis", "dynamo"],
        "ORM": ["orm", "prisma", "sequelize", "typeorm"],
    },
}

def detect_subcategories(skill: Dict[str, Any]) -> List[str]:
    """Auto-detect subcategories from description and use_cases"""
    text = ""
    if skill.get('description'):
        text += skill['description'].lower() + " "
    if skill.get('use_cases'):
        text += " ".join(skill['use_cases']).lower()
    
    subcats = set()
    
    # Check each category
    for category in skill.get('category', []):
        cat_lower = category.lower().replace(" ", "-")
        if cat_lower in SUBCATEGORY_KEYWORDS:
            # Check each subcategory's keywords
            for subcat, keywords in SUBCATEGORY_KEYWORDS[cat_lower].items():
                for keyword in keywords:
                    if keyword in text:
                        subcats.add(subcat)
                        break
    
    return sorted(list(subcats))

def calculate_quality_score(skill: Dict[str, Any]) -> int:
    """Calculate quality score (1-100) based on multiple factors"""
    score = 0.0
    
    # 1. Installs (40% weight) - logarithmic scale
    installs = skill.get('installs', 0)
    if installs > 0:
        import math
        # Scale: 1k=20, 10k=40, 100k=60, 1M=80, 10M+=100
        install_score = min(100, (math.log10(installs) - 3) * 20 + 20)
        score += install_score * 0.4
    
    # 2. Description quality (20% weight)
    desc = skill.get('description', '')
    desc_score = 0
    if len(desc) > 100:
        desc_score += 40
    if len(desc) > 200:
        desc_score += 30
    if len(desc) > 300:
        desc_score += 30
    score += desc_score * 0.2

    # 3. Use cases count (20% weight)
    use_cases = skill.get('use_cases', [])
    uc_score = min(100, len(use_cases) * 25)  # 4 use cases = 100
    score += uc_score * 0.2

    # 4. Category relevance (20% weight)
    categories = skill.get('category', [])
    cat_score = min(100, len(categories) * 50)  # 2 categories = 100
    score += cat_score * 0.2
    
    return max(1, min(100, int(round(score))))

def update_skills_metadata():
    """Update all skills with subcategories and quality scores"""
    conn = psycopg2.connect(
        host="localhost",
        database="oi_memory",
        user="dsselmanovic"
    )
    
    try:
        with conn.cursor() as cur:
            # Fetch all skills
            cur.execute("""
                SELECT id, name, category, description, installs, use_cases
                FROM skills
            """)
            skills = []
            for row in cur.fetchall():
                skills.append({
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'description': row[3],
                    'installs': row[4],
                    'use_cases': row[5],
                })
            
            print(f"Processing {len(skills)} skills...")
            
            updated = 0
            for skill in skills:
                # Detect subcategories
                subcats = detect_subcategories(skill)
                
                # Calculate quality score
                quality = calculate_quality_score(skill)
                
                # Update database
                cur.execute("""
                    UPDATE skills 
                    SET subcategory = %s, 
                        quality_score = %s,
                        last_updated = NOW()
                    WHERE id = %s
                """, (subcats, quality, skill['id']))
                
                updated += 1
                if updated % 10 == 0:
                    print(f"  Updated {updated}/{len(skills)} skills...")
            
            conn.commit()
            print(f"✅ Updated {updated} skills with metadata")
            
            # Show statistics
            cur.execute("""
                SELECT
                    AVG(quality_score) as avg_quality,
                    MIN(quality_score) as min_quality,
                    MAX(quality_score) as max_quality
                FROM skills
            """)
            row = cur.fetchone()

            cur.execute("""
                SELECT COUNT(DISTINCT subcat) as unique_subcats
                FROM (SELECT unnest(subcategory) as subcat FROM skills WHERE subcategory IS NOT NULL) s
            """)
            unique_subcats = cur.fetchone()[0]

            print(f"\nStatistics:")
            print(f"  Avg Quality Score: {row[0]:.2f}")
            print(f"  Quality Range: {row[1]} - {row[2]}")
            print(f"  Unique Subcategories: {unique_subcats}")
            
    finally:
        conn.close()

if __name__ == "__main__":
    update_skills_metadata()
