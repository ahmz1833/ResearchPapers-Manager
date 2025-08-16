#!/usr/bin/env bash
set -euo pipefail

host="$1"
port="$2"
name="$3"

for i in {1..30}; do
  if nc -z "$host" "$port"; then
    echo "$name is up"
    exit 0
  fi
  echo "Waiting for $name ($host:$port)..."
  sleep 2
done

echo "Timeout waiting for $name" >&2
exit 1
