#!/bin/bash
# Skills-DB Search Helper
# Usage: search-skills.sh "query"

set -euo pipefail

QUERY="$1"

# Extract category from query keywords
CATEGORY=""
case "$QUERY" in
    *api*|*rest*|*backend*|*server*) CATEGORY="backend" ;;
    *agent*|*rag*|*llm*|*ai*|*prompt*) CATEGORY="ai" ;;
    *docker*|*k8s*|*kubernetes*|*devops*|*ci*) CATEGORY="devops" ;;
    *test*|*jest*|*pytest*) CATEGORY="testing" ;;
    *mobile*|*ios*|*android*) CATEGORY="mobile" ;;
    *cloud*|*aws*|*azure*|*gcp*) CATEGORY="cloud" ;;
    *security*|*auth*) CATEGORY="security" ;;
    *mlops*|*model*|*training*) CATEGORY="mlops" ;;
    *database*|*sql*|*postgres*) CATEGORY="database" ;;
esac

if [ -z "$CATEGORY" ]; then
    echo "❌ No category detected from query: '$QUERY'"
    echo ""
    echo "Try keywords: backend, api, agent, rag, docker, test, mobile, cloud, security, mlops, database"
    echo ""
    echo "Or use: ~/.claude/scripts/filter-skills.sh --category X"
    exit 1
fi

# Run simple SQL search
psql -d oi_memory -t -c "
SELECT
    '📦 ' || name || ' (' || installs || ' installs)' || E'\n' ||
    '   ' || left(description, 100) || '...' || E'\n'
FROM skills
WHERE '$CATEGORY' = ANY(category)
ORDER BY installs DESC
LIMIT 5;
"
