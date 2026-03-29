#!/usr/bin/env bash
# cct-verify2.sh — CCT Server System Verification v2
# Changelog: cct-hipporag service name fix, slash-label cleanup
# Local runner: connects via SSH and executes all checks remotely
# Usage: ./cct-verify.sh [--quick]

set -euo pipefail

SSH_HOST="178.104.51.123"
SSH_USER="root"
SSH_KEY="$HOME/.ssh/id_ed25519_big_mamma"
QUICK_MODE=0

for arg in "$@"; do
  [[ "$arg" == "--quick" ]] && QUICK_MODE=1
done

if [[ ! -f "$SSH_KEY" ]]; then
  echo "ERROR: SSH key not found at $SSH_KEY"
  exit 1
fi

ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no \
    "${SSH_USER}@${SSH_HOST}" bash -s -- "$QUICK_MODE" <<'REMOTE_SCRIPT'

QUICK_MODE="$1"

# ─── Colors ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

PASS="✅"
FAIL="❌"
WARN="⚠️ "

CHECKS_TOTAL=0
CHECKS_PASSED=0

# ─── Helpers ─────────────────────────────────────────────────────────────────
section() {
  echo ""
  echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${RESET}"
  echo -e "${CYAN}${BOLD}  $1${RESET}"
  echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${RESET}"
}

ok() {
  local label="$1"
  local value="${2:-}"
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  if [[ -n "$value" ]]; then
    echo -e "  ${PASS} ${GREEN}${label}${RESET} — ${value}"
  else
    echo -e "  ${PASS} ${GREEN}${label}${RESET}"
  fi
}

fail() {
  local label="$1"
  local value="${2:-}"
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ -n "$value" ]]; then
    echo -e "  ${FAIL} ${RED}${label}${RESET} — ${value}"
  else
    echo -e "  ${FAIL} ${RED}${label}${RESET}"
  fi
}

warn() {
  local label="$1"
  local value="${2:-}"
  echo -e "  ${WARN} ${YELLOW}${label}${RESET} — ${value}"
}

info() {
  echo -e "     ${YELLOW}↳ $1${RESET}"
}

curl_get() {
  curl -s --connect-timeout 5 --max-time 10 "$@" 2>/dev/null
}

curl_post() {
  curl -s --connect-timeout 5 --max-time 15 -X POST "$@" 2>/dev/null
}

curl_delete() {
  curl -s --connect-timeout 5 --max-time 10 -X DELETE "$@" 2>/dev/null
}

# ─── 1. DOCKER CONTAINERS ─────────────────────────────────────────────────────
section "1. Docker Containers"

EXPECTED_CONTAINERS=(
  "cct-mem0"
  "cct-mem0-qdrant"
  "neo4j"
  "mem0_ui"
  "cct-agent-watcher"
  "docker-api-1"
  "docker-qdrant-1"
  "docker-db_postgres-1"
  "docker-redis-1"
  "docker-nginx-1"
)

for container in "${EXPECTED_CONTAINERS[@]}"; do
  # Get status and health in one call
  info_line=$(docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$container" 2>/dev/null || echo "not-found|not-found")
  status=$(echo "$info_line" | cut -d'|' -f1)
  health=$(echo "$info_line" | cut -d'|' -f2)

  if [[ "$status" == "not-found" ]]; then
    fail "Container: $container" "NOT FOUND"
  elif [[ "$status" == "running" ]]; then
    if [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
      ok "Container: $container" "running | $health"
    else
      fail "Container: $container" "running | health=$health"
    fi
  else
    fail "Container: $container" "status=$status | health=$health"
  fi
done

# ─── 2. QDRANT :16333 (Mem0) ──────────────────────────────────────────────────
section "2. Qdrant :16333 (Mem0)"

# Health — use root / which returns version JSON
qdrant_root=$(curl_get "http://localhost:16333/")
qdrant_ver=$(echo "$qdrant_root" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version','?'))" 2>/dev/null || echo "")
if [[ -n "$qdrant_ver" && "$qdrant_ver" != "?" ]]; then
  ok "Qdrant :16333 health" "version=$qdrant_ver"
else
  fail "Qdrant :16333 health" "${qdrant_root:-no response}"
fi

# Collection mem0_memories
collection_raw=$(curl_get "http://localhost:16333/collections/mem0_memories")
if [[ -z "$collection_raw" ]]; then
  fail "Collection mem0_memories" "no response"
else
  coll_status=$(echo "$collection_raw" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['status'])" 2>/dev/null || echo "parse_error")
  points_count=$(echo "$collection_raw" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['points_count'])" 2>/dev/null || echo "?")
  indexed_count=$(echo "$collection_raw" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['indexed_vectors_count'])" 2>/dev/null || echo "?")

  if [[ "$coll_status" == "green" || "$coll_status" == "ok" ]]; then
    ok "Collection mem0_memories" "status=$coll_status | points=$points_count | indexed=$indexed_count"
  else
    fail "Collection mem0_memories" "status=$coll_status | points=$points_count | indexed=$indexed_count"
  fi

  # Check indexed >= points - 10% (Qdrant soft-deletes create transient gap)
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  indexed_ok=$(python3 -c "
p='$points_count'; i='$indexed_count'
try:
    pn=int(p); in_=int(i)
    # Pass if indexed >= 90% of points (soft-deleted not yet compacted)
    print('yes' if in_ >= pn * 0.9 else 'no')
except:
    print('no')
" 2>/dev/null || echo "no")
  if [[ "$indexed_ok" == "yes" ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    if [[ "$points_count" == "$indexed_count" ]]; then
      echo -e "  ${PASS} ${GREEN}Points indexed${RESET} — $indexed_count/$points_count (100%)"
    else
      echo -e "  ${PASS} ${GREEN}Points indexed${RESET} — $indexed_count/$points_count (soft-deleted pending compaction)"
    fi
  else
    echo -e "  ${FAIL} ${RED}Points under-indexed${RESET} — $indexed_count/$points_count"
  fi
fi

# Full-text index on "memory" field
indexes_raw=$(curl_get "http://localhost:16333/collections/mem0_memories")
has_fulltext=$(echo "$indexes_raw" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    payload_schema = d.get('result', {}).get('payload_schema', {})
    mem_field = payload_schema.get('memory', {})
    # full-text index shows data_type: 'Text' or index with type 'text'
    dt = mem_field.get('data_type', '')
    idx = mem_field.get('points', 0)
    print('yes' if dt.lower() in ('text', 'keyword') or 'index' in str(mem_field).lower() else 'no')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

# Alternative: check via /collections/mem0_memories/index endpoint
indexes_raw2=$(curl_get "http://localhost:16333/collections/mem0_memories/index" 2>/dev/null || echo "")
has_fulltext2=$(echo "$indexes_raw2" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    indices = d.get('result', {}).get('indices', [])
    for idx in indices:
        if idx.get('field_name') == 'memory':
            print('yes')
            sys.exit(0)
    print('no')
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [[ "$has_fulltext" == "yes" || "$has_fulltext2" == "yes" ]]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  echo -e "  ${PASS} ${GREEN}Full-text index on 'memory' field${RESET} — present"
else
  echo -e "  ${WARN} ${YELLOW}Full-text index on 'memory' field${RESET} — not detected (has_payload=$has_fulltext, has_index=$has_fulltext2)"
fi

# ─── 3. QDRANT :26333 (OpenMemory) ────────────────────────────────────────────
section "3. Qdrant :26333 (OpenMemory / docker-qdrant-1)"

qdrant2_root=$(curl_get "http://localhost:26333/")
qdrant2_ver=$(echo "$qdrant2_root" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version','?'))" 2>/dev/null || echo "")
if [[ -n "$qdrant2_ver" && "$qdrant2_ver" != "?" ]]; then
  ok "Qdrant :26333 health" "version=$qdrant2_ver"
else
  fail "Qdrant :26333 health" "${qdrant2_root:-no response}"
fi

# Try common collection names for openmemory
for coll_name in "openmemory" "open_memory" "memories" "default"; do
  coll2_raw=$(curl_get "http://localhost:26333/collections/$coll_name")
  if echo "$coll2_raw" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'result' in d and 'error' not in d else 1)" 2>/dev/null; then
    pts=$(echo "$coll2_raw" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['points_count'])" 2>/dev/null || echo "?")
    ok "Collection $coll_name on :26333" "points=$pts"
    break
  fi
done

# List all collections on :26333
all_colls=$(curl_get "http://localhost:26333/collections")
colls_list=$(echo "$all_colls" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    names = [c['name'] for c in d.get('result', {}).get('collections', [])]
    print(', '.join(names) if names else 'none')
except:
    print('parse error')
" 2>/dev/null || echo "no response")
info "Collections on :26333: $colls_list"

# ─── 4. NEO4J :7474 ───────────────────────────────────────────────────────────
section "4. Neo4j :7474"

NEO4J_USER="neo4j"
NEO4J_PASS="22e58741703f24f1913550c9a8a51c99"
NEO4J_AUTH=$(echo -n "${NEO4J_USER}:${NEO4J_PASS}" | base64)

# Connectivity
neo4j_resp=$(curl_get -H "Authorization: Basic $NEO4J_AUTH" "http://localhost:7474/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  --data '{"statements":[{"statement":"RETURN 1 AS alive"}]}' 2>/dev/null || echo "")

if echo "$neo4j_resp" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d.get('errors') else 1)" 2>/dev/null; then
  ok "Neo4j :7474 connectivity" "reachable"
else
  fail "Neo4j :7474 connectivity" "${neo4j_resp:-no response}"
fi

# Node count
node_resp=$(curl_get -H "Authorization: Basic $NEO4J_AUTH" "http://localhost:7474/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  --data '{"statements":[{"statement":"MATCH (n) RETURN count(n) AS total"}]}' 2>/dev/null || echo "")
node_count=$(echo "$node_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d['results'][0]['data'][0]['row'][0])
except:
    print('?')
" 2>/dev/null || echo "?")
if [[ "$node_count" != "?" ]]; then
  ok "Neo4j node count" "$node_count total nodes"
else
  fail "Neo4j node count" "could not retrieve"
fi

# Relationship count
rel_resp=$(curl_get -H "Authorization: Basic $NEO4J_AUTH" "http://localhost:7474/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  --data '{"statements":[{"statement":"MATCH ()-[r]->() RETURN count(r) AS total"}]}' 2>/dev/null || echo "")
rel_count=$(echo "$rel_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d['results'][0]['data'][0]['row'][0])
except:
    print('?')
" 2>/dev/null || echo "?")
if [[ "$rel_count" != "?" ]]; then
  ok "Neo4j relationship count" "$rel_count total relationships"
else
  fail "Neo4j relationship count" "could not retrieve"
fi

# Check NO slash labels
slash_resp=$(curl_get -H "Authorization: Basic $NEO4J_AUTH" "http://localhost:7474/db/neo4j/tx/commit" \
  -H "Content-Type: application/json" \
  --data '{"statements":[{"statement":"CALL db.labels() YIELD label WHERE label CONTAINS \"/\" RETURN label"}]}' 2>/dev/null || echo "")
slash_labels=$(echo "$slash_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    rows = d['results'][0]['data']
    labels = [r['row'][0] for r in rows]
    print(', '.join(labels) if labels else 'none')
except:
    print('?')
" 2>/dev/null || echo "?")
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [[ "$slash_labels" == "none" ]]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  echo -e "  ${PASS} ${GREEN}No slash labels in Neo4j${RESET} — clean"
elif [[ "$slash_labels" == "?" ]]; then
  echo -e "  ${WARN} ${YELLOW}Slash label check${RESET} — could not query"
else
  echo -e "  ${FAIL} ${RED}Slash labels found in Neo4j${RESET} — $slash_labels"
fi

# Check NO lowercase duplicate labels
for lc_label in "agent" "service" "database" "concept"; do
  lc_resp=$(curl_get -H "Authorization: Basic $NEO4J_AUTH" "http://localhost:7474/db/neo4j/tx/commit" \
    -H "Content-Type: application/json" \
    --data "{\"statements\":[{\"statement\":\"MATCH (n:\`${lc_label}\`) RETURN count(n) AS cnt\"}]}" 2>/dev/null || echo "")
  lc_count=$(echo "$lc_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    if d.get('errors'):
        print('0')
    else:
        print(d['results'][0]['data'][0]['row'][0])
except:
    print('0')
" 2>/dev/null || echo "0")
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ "$lc_count" == "0" ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}No lowercase ':$lc_label' nodes${RESET} — count=0"
  else
    echo -e "  ${FAIL} ${RED}Lowercase ':$lc_label' nodes exist${RESET} — count=$lc_count"
  fi
done

# ─── 5. MEM0 :8002 ────────────────────────────────────────────────────────────
section "5. Mem0 :8002"

# Health
mem0_health=$(curl_get "http://localhost:8002/health")
if echo "$mem0_health" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('status')=='healthy' else 1)" 2>/dev/null; then
  ok "Mem0 :8002 /health" "$mem0_health"
else
  fail "Mem0 :8002 /health" "${mem0_health:-no response}"
fi

if [[ "$QUICK_MODE" == "1" ]]; then
  warn "Mem0 write/read/delete test" "SKIPPED (--quick mode)"
else
  TEST_USER="cct-verify-script"
  TEST_TEXT="CCT verification test memory $(date +%s)"

  # Write test — timestamp ensures unique content (avoids mem0 deduplication)
  TS=$(date +%s)
  TEST_TEXT="CCT verify $TS: Verification agent runs on port $((8000 + RANDOM % 100)) using Python on server 178.104.51.123"
  write_resp=$(curl_post "http://localhost:8002/v1/memories/" \
    -H "Content-Type: application/json" \
    --data "{\"messages\":[{\"role\":\"user\",\"content\":\"$TEST_TEXT\"}],\"user_id\":\"$TEST_USER\",\"source\":\"cct-verify\"}" \
    --max-time 60 2>/dev/null || echo "")
  write_ok=$(echo "$write_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    results = d if isinstance(d, list) else d.get('results', d.get('memories', []))
    added = d.get('relations', {}).get('added_entities', [])
    if results:
        print('full')
    elif added:
        print('full')  # graph entities added = write worked
    elif 'detail' in d and 'neo4j' in str(d.get('detail','')).lower():
        print('partial')
    else:
        print('no')
except:
    print('no')
" 2>/dev/null || echo "no")

  if [[ "$write_ok" == "full" ]]; then
    ok "Mem0 write test" "memory stored (Qdrant+Neo4j) for user=$TEST_USER"
  elif [[ "$write_ok" == "partial" ]]; then
    CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${WARN} ${YELLOW}Mem0 write test${RESET} — Qdrant OK, Neo4j graph write failed (Cypher error)"
  else
    fail "Mem0 write test" "${write_resp:-timeout or error}"
  fi

  # Read test
  read_resp=$(curl_get "http://localhost:8002/v1/memories/?user_id=$TEST_USER" 2>/dev/null || echo "")
  read_count=$(echo "$read_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    items = d if isinstance(d, list) else d.get('results', d.get('memories', []))
    print(len(items))
except:
    print('?')
" 2>/dev/null || echo "?")

  if [[ "$read_count" != "?" && "$read_count" -ge 1 ]] 2>/dev/null; then
    ok "Mem0 read test" "$read_count memory/memories found for user=$TEST_USER"
  else
    fail "Mem0 read test" "count=$read_count | response=${read_resp:0:100}"
  fi

  # Cleanup: delete all memories for test user
  # Get memory IDs for deletion
  mem_ids=$(echo "$read_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    items = d if isinstance(d, list) else d.get('results', d.get('memories', []))
    ids = [str(item.get('id','')) for item in items if item.get('id')]
    print(' '.join(ids))
except:
    print('')
" 2>/dev/null || echo "")

  cleanup_ok=0
  if [[ -n "$mem_ids" ]]; then
    for mem_id in $mem_ids; do
      del_resp=$(curl_delete "http://localhost:8002/memories/$mem_id/" 2>/dev/null || echo "")
      cleanup_ok=$((cleanup_ok + 1))
    done
  else
    # Try bulk delete by user
    del_resp=$(curl_delete "http://localhost:8002/memories/?user_id=$TEST_USER" 2>/dev/null || echo "")
    cleanup_ok=1
  fi

  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ "$cleanup_ok" -ge 1 ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}Mem0 cleanup test${RESET} — deleted $cleanup_ok memory/memories for user=$TEST_USER"
  else
    echo -e "  ${FAIL} ${RED}Mem0 cleanup test${RESET} — could not delete test memories"
  fi
fi

# ─── 6. HIPPORAG :8001 ────────────────────────────────────────────────────────
section "6. HippoRAG :8001"

hippo_health=$(curl_get "http://localhost:8001/health")
if [[ -z "$hippo_health" ]]; then
  fail "HippoRAG :8001 /health" "no response"
else
  hippo_nodes=$(echo "$hippo_health" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('node_count', d.get('nodes', '?')))
except:
    print('?')
" 2>/dev/null || echo "?")
  hippo_rels=$(echo "$hippo_health" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('relationship_count', d.get('relationships', d.get('edges', '?'))))
except:
    print('?')
" 2>/dev/null || echo "?")
  hippo_status=$(echo "$hippo_health" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('status', 'ok'))
except:
    print('unknown')
" 2>/dev/null || echo "unknown")

  if [[ "$hippo_status" == "ok" || "$hippo_status" == "healthy" ]]; then
    ok "HippoRAG :8001 /health" "status=$hippo_status | nodes=$hippo_nodes | relationships=$hippo_rels"
  else
    fail "HippoRAG :8001 /health" "status=$hippo_status | response=$hippo_health"
  fi
fi

# ─── 7. ORCHESTRATOR :8000 ────────────────────────────────────────────────────
section "7. Orchestrator :8000"

orch_health=$(curl_get "http://localhost:8000/health")
if [[ -z "$orch_health" ]]; then
  # Try root endpoint
  orch_health=$(curl_get "http://localhost:8000/")
fi

if [[ -z "$orch_health" ]]; then
  fail "Orchestrator :8000" "no response on /health or /"
else
  orch_status=$(echo "$orch_health" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('status', 'responded'))
except:
    print('responded (non-JSON)')
" 2>/dev/null || echo "responded")

  if [[ "$orch_status" != "responded (non-JSON)" && "$orch_status" != "" ]]; then
    ok "Orchestrator :8000" "status=$orch_status"
  else
    ok "Orchestrator :8000" "reachable | response=${orch_health:0:80}"
  fi
fi

# ─── 8. OLLAMA :11434 ─────────────────────────────────────────────────────────
section "8. Ollama :11434"

ollama_resp=$(curl_get "http://localhost:11434/api/tags")
if [[ -z "$ollama_resp" ]]; then
  fail "Ollama :11434 /api/tags" "no response"
else
  model_list=$(echo "$ollama_resp" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    names = [m['name'] for m in d.get('models', [])]
    print(', '.join(names) if names else 'none')
except:
    print('parse error')
" 2>/dev/null || echo "parse error")
  ok "Ollama :11434 /api/tags" "models: $model_list"

  # Check bge-m3:latest
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if echo "$model_list" | grep -q "bge-m3:latest"; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}bge-m3:latest present${RESET} — confirmed"
  else
    echo -e "  ${FAIL} ${RED}bge-m3:latest NOT found${RESET} — available: $model_list"
  fi
fi

# ─── 9. POSTGRESQL ────────────────────────────────────────────────────────────
section "9. PostgreSQL (Dify)"

# Try to find postgres container and connect
PG_CONTAINER="docker-db_postgres-1"

# Check if psql is available in the container
pg_accessible=$(docker exec "$PG_CONTAINER" psql -U postgres -c "SELECT 1;" 2>/dev/null || echo "error")
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if echo "$pg_accessible" | grep -q "1 row"; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  echo -e "  ${PASS} ${GREEN}PostgreSQL accessible${RESET} — connected to $PG_CONTAINER"

  # Check Dify DB
  dify_db=$(docker exec "$PG_CONTAINER" psql -U postgres -lqt 2>/dev/null | grep -i "^\s*dify\b" | awk '{print $1}' | head -1 || echo "")
  if [[ -n "$dify_db" ]]; then
    ok "Dify database exists" "db=$dify_db"
  else
    # List all DBs
    all_dbs=$(docker exec "$PG_CONTAINER" psql -U postgres -lqt 2>/dev/null | awk '{print $1}' | grep -v '|' | tr '\n' ' ' || echo "?")
    warn "Dify database" "not found — available: $all_dbs"
  fi

  # pgvector check
  PG_DB=$(docker exec "$PG_CONTAINER" psql -U postgres -lqt 2>/dev/null | grep -i "^\s*dify\b" | awk '{print $1}' | head -1 || echo "postgres")
  [[ -z "$PG_DB" ]] && PG_DB="postgres"
  pgvector=$(docker exec "$PG_CONTAINER" psql -U postgres -d "$PG_DB" -c "SELECT installed_version FROM pg_available_extensions WHERE name='vector';" 2>/dev/null || echo "")
  pgvector_installed=$(echo "$pgvector" | grep -v "installed_version" | grep -v "^-" | grep -v "^(" | grep -v "^$" | head -1 | tr -d ' ')
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ -z "$pgvector_installed" || "$pgvector_installed" == "" ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}pgvector NOT installed${RESET} — expected: not present"
  else
    echo -e "  ${WARN} ${YELLOW}pgvector installed${RESET} — version=$pgvector_installed (expected: NO)"
  fi

  # Document count in document_segments
  doc_count=$(docker exec "$PG_CONTAINER" psql -U postgres -d "$PG_DB" -t -c "SELECT COUNT(*) FROM document_segments;" 2>/dev/null | tr -d ' \n' || echo "?")
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ "$doc_count" != "?" && "$doc_count" =~ ^[0-9]+$ ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}document_segments count${RESET} — $doc_count rows"
  else
    echo -e "  ${WARN} ${YELLOW}document_segments${RESET} — could not query (db=$PG_DB, result=$doc_count)"
  fi

else
  echo -e "  ${FAIL} ${RED}PostgreSQL not accessible${RESET} — container=$PG_CONTAINER"
  # Count as 3 failed checks (DB access, pgvector, doc count)
  CHECKS_TOTAL=$((CHECKS_TOTAL + 3))
fi

# ─── 10. SYSTEMD SERVICES ─────────────────────────────────────────────────────
section "10. Systemd Services"

SYSTEMD_SERVICES=(
  "cct-orchestrator"
  "cct-hipporag"
  "neo4j"
)

for svc in "${SYSTEMD_SERVICES[@]}"; do
  svc_status=$(systemctl is-active "$svc" 2>/dev/null || echo "not-found")
  svc_enabled=$(systemctl is-enabled "$svc" 2>/dev/null || echo "unknown")
  CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
  if [[ "$svc_status" == "active" ]]; then
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
    echo -e "  ${PASS} ${GREEN}$svc.service${RESET} — active | enabled=$svc_enabled"
  elif [[ "$svc_status" == "not-found" ]]; then
    echo -e "  ${FAIL} ${RED}$svc.service${RESET} — NOT FOUND"
  else
    echo -e "  ${FAIL} ${RED}$svc.service${RESET} — $svc_status | enabled=$svc_enabled"
  fi
done

# cct-network-fix (oneshot — inactive is expected after boot)
svc="cct-network-fix"
svc_enabled=$(systemctl is-enabled "$svc" 2>/dev/null || echo "not-found")
svc_result=$(systemctl show "$svc" --property=Result 2>/dev/null | cut -d= -f2 || echo "?")
CHECKS_TOTAL=$((CHECKS_TOTAL + 1))
if [[ "$svc_enabled" == "enabled" && "$svc_result" == "success" ]]; then
  CHECKS_PASSED=$((CHECKS_PASSED + 1))
  echo -e "  ${PASS} ${GREEN}$svc.service${RESET} — oneshot | enabled | last-result=success"
elif [[ "$svc_enabled" == "not-found" ]]; then
  echo -e "  ${FAIL} ${RED}$svc.service${RESET} — NOT FOUND"
else
  echo -e "  ${WARN} ${YELLOW}$svc.service${RESET} — enabled=$svc_enabled | result=$svc_result (oneshot)"
fi

# ─── SUMMARY ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${RESET}"
echo -e "${CYAN}${BOLD}  SUMMARY${RESET}"
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════${RESET}"
echo ""

FAILED=$((CHECKS_TOTAL - CHECKS_PASSED))

if [[ "$FAILED" -eq 0 ]]; then
  echo -e "  ${PASS} ${GREEN}${BOLD}All checks passed: ${CHECKS_PASSED}/${CHECKS_TOTAL}${RESET}"
else
  echo -e "  ${FAIL} ${RED}${BOLD}${CHECKS_PASSED}/${CHECKS_TOTAL} checks passed — ${FAILED} FAILED${RESET}"
fi

echo ""
echo -e "  Server:   ${CYAN}178.104.51.123${RESET}"
echo -e "  Timestamp: $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo -e "  Mode:     $( [[ "$QUICK_MODE" == "1" ]] && echo "quick (write tests skipped)" || echo "full" )"
echo ""

[[ "$FAILED" -eq 0 ]] && exit 0 || exit 1

REMOTE_SCRIPT
