#!/bin/bash
# Simple Skills-DB Search (direct SQL)
# Usage: search-skills-simple.sh "category"

CATEGORY="$1"

psql -d oi_memory -c "
SELECT
    name,
    installs,
    array_to_string(category, ', ') as categories,
    left(description, 80) as description
FROM skills
WHERE '$CATEGORY' = ANY(category)
ORDER BY installs DESC
LIMIT 5;
"
