#!/usr/bin/env bash
# Ping IndexNow with every URL in the sitemap.
#
# One submission reaches Bing, Yandex, Seznam and Naver at once -- they share
# the protocol. Google does not participate; it finds changes its own way.
#
# Run it after a deploy that changed page content. It is safe to run again:
# IndexNow is a hint, not a queue, and re-submitting an unchanged URL is a
# no-op rather than an error.
set -euo pipefail

HOST="magicscraper.app"
KEY="d7c1e87c73124673a734d3850d48ab7f"

# The key file must stay reachable -- IndexNow fetches it to prove the
# submission comes from someone who controls the host.
if ! curl -fsS "https://$HOST/$KEY.txt" | grep -q "^$KEY$"; then
  echo "key file missing or wrong at https://$HOST/$KEY.txt" >&2
  exit 1
fi

URLS=$(curl -fsS "https://$HOST/sitemap.xml" \
  | grep -o '<loc>[^<]*</loc>' | sed 's|</\?loc>||g')

BODY=$(python3 -c "
import json, sys
print(json.dumps({
  'host': '$HOST',
  'key': '$KEY',
  'keyLocation': 'https://$HOST/$KEY.txt',
  'urlList': [u for u in sys.stdin.read().split() if u],
}))" <<< "$URLS")

echo "$BODY" | python3 -c "import json,sys; print(len(json.load(sys.stdin)['urlList']), 'urls')"

code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "https://api.indexnow.org/IndexNow" \
  -H 'Content-Type: application/json; charset=utf-8' -d "$BODY")

case "$code" in
  200|202) echo "IndexNow accepted ($code)" ;;
  *)       echo "IndexNow returned $code" >&2; exit 1 ;;
esac
