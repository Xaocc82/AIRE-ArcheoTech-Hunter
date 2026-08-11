#!/usr/bin/env bash
set -euo pipefail

compose=(docker compose --env-file .env.production.example -f compose.production.yaml)

"${compose[@]}" config --quiet
"${compose[@]}" build app
"${compose[@]}" up -d

for _ in {1..30}; do
  if curl --fail --silent --show-error http://127.0.0.1:8088/healthz >/dev/null; then
    break
  fi
  sleep 2
done

curl --fail --silent --show-error http://127.0.0.1:8088/healthz >/dev/null
test "$("${compose[@]}" exec -T app id -u)" -ne 0
"${compose[@]}" exec -T app test -w /var/lib/aire-archeotech/storage
test "$("${compose[@]}" ps -q postgres | xargs docker inspect --format '{{.State.Health.Status}}')" = healthy
test "$("${compose[@]}" ps -q app | xargs docker inspect --format '{{.State.Health.Status}}')" = healthy
grep -Fq '127.0.0.1:8088:8088' compose.production.yaml
