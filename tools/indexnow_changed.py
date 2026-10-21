#!/usr/bin/env python3
"""Submit the pages a deploy changed to IndexNow (Bing, Yandex, Seznam, Naver).

Reads changed file paths on stdin (one per line, as `git diff --name-only`
prints them), turns each published page into its clean URL, waits until the
page is live, and sends the list in one POST. Pages marked noindex, and pages
that are not meant to be found (admin, thanks, goodbye, welcome, 404), are
left out. tools/indexnow.sh still submits the whole sitemap when that is wanted.
Run by .github/workflows/indexnow.yml after every push to main.
"""
import json, os, re, sys, time, urllib.request, urllib.error

HOST = 'magicscraper.app'
KEY = 'd7c1e87c73124673a734d3850d48ab7f'
SKIP = {'404.html', 'thanks.html', 'goodbye.html', 'welcome.html', 'admin-requests.html'}
UA = {'User-Agent': 'magicscraper-indexnow/1.0'}


def url_for(path):
    if not path.endswith('.html') or path.startswith(('tools/', 'src/', 'node_modules/')):
        return None
    if os.path.basename(path) in SKIP or not os.path.exists(path):
        return None
    head = open(path, encoding='utf-8', errors='replace').read(6000)
    if re.search(r'<meta name="robots" content="[^"]*noindex', head):
        return None
    clean = path[:-5]
    if clean == 'index':
        clean = ''
    elif clean.endswith('/index'):
        clean = clean[:-5]
    return f'https://{HOST}/{clean}'


def status(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def main():
    urls = sorted({u for u in (url_for(l.strip()) for l in sys.stdin) if u})
    if not urls:
        print('no indexable pages changed; nothing to submit')
        return 0
    if status(f'https://{HOST}/{KEY}.txt') != 200:
        print('key file is not reachable; IndexNow would reject the submission', file=sys.stderr)
        return 1
    # A new page answers 404 until Cloudflare has deployed it. Wait for it, up to 6 minutes.
    deadline = time.time() + 360
    live = []
    for u in urls:
        while status(u) != 200 and time.time() < deadline:
            time.sleep(15)
        (live.append(u) if status(u) == 200 else print('not live yet, skipped:', u))
    if not live:
        return 1
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt',
                       'urlList': live}).encode()
    req = urllib.request.Request('https://api.indexnow.org/IndexNow', data=body, method='POST',
                                 headers={'Content-Type': 'application/json; charset=utf-8', **UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    print(f'IndexNow answered {code} for {len(live)} page(s):')
    for u in live:
        print('  ' + u)
    return 0 if code in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main())
