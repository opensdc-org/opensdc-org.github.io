# -*- coding: utf-8 -*-
"""Refresh the repository facts in data/software.json from the GitHub API. Python 3.9+; standard library only.

Updates licence, languages, build files, last push, archived flag and latest release for every entry whose
`repo` is a github.com URL, and reports repositories that have moved or disappeared. Entries hosted elsewhere
are left untouched. Set GITHUB_TOKEN (or log in with `gh`) to avoid the anonymous rate limit.

    python3 scripts/refresh_repos.py            # rewrite data/software.json
    python3 scripts/refresh_repos.py --check    # report only
"""
import datetime, json, os, pathlib, subprocess, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / 'data/software.json'
BUILD = [('CMakeLists.txt', 'CMake'), ('Makefile', 'Make'), ('configure', 'Autotools'), ('pyproject.toml', 'Python 包'),
         ('setup.py', 'Python 包'), ('Cargo.toml', 'Cargo'), ('Dockerfile', 'Docker')]
LICENSE = {'NOASSERTION': '有 LICENSE 文件（非标准模板）', None: '仓库未声明许可证'}


def token():
    if os.environ.get('GITHUB_TOKEN'):
        return os.environ['GITHUB_TOKEN']
    try:
        return subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ''


TOKEN = token()


def api(path):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'opensdc-survey'}
    if TOKEN:
        headers['Authorization'] = 'Bearer ' + TOKEN
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.github.com/' + path, headers=headers), timeout=30) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return {'_status': e.code}


def facts(full_name):
    repo = api('repos/' + full_name)
    if 'full_name' not in repo:
        return None
    name = repo['full_name']
    langs = api('repos/%s/languages' % name)
    files = api('repos/%s/contents' % name)
    release = api('repos/%s/releases/latest' % name)
    names = [f['name'] for f in files] if isinstance(files, list) else []
    build = []
    for f, label in BUILD:
        if f in names and label not in build:
            build.append(label)
    out = {
        'repo': repo['html_url'],
        'license': LICENSE.get((repo.get('license') or {}).get('spdx_id'), (repo.get('license') or {}).get('spdx_id')),
        'lang': '、'.join(sorted((k for k in langs if not k.startswith('_')), key=langs.get, reverse=True)[:3]),
        'build': '、'.join(build) or '见 README',
        'pushed': repo['pushed_at'][:7],
        'archived': repo['archived'],
    }
    if release.get('tag_name'):
        out['release'] = release['tag_name']
    return out


def main():
    check = '--check' in sys.argv
    catalog = json.loads(PATH.read_text(encoding='utf-8'))
    today = datetime.date.today().isoformat()
    changed = missing = 0
    for item in catalog['items']:
        if not item['repo'].startswith('https://github.com/'):
            continue
        new = facts(item['repo'][len('https://github.com/'):])
        if new is None:
            missing += 1
            print('MISSING  %-16s %s' % (item['id'], item['repo']))
            continue
        diff = {k: (item.get(k), v) for k, v in new.items() if item.get(k) != v}
        if 'release' in item and 'release' not in new:
            diff['release'] = (item['release'], None)
        if diff:
            changed += 1
            print('CHANGED  %-16s %s' % (item['id'], '; '.join('%s: %s -> %s' % (k, a, b) for k, (a, b) in diff.items())))
        if not check:
            item.update(new)
            if 'release' not in new:
                item.pop('release', None)
            item['checked'] = today
    if not check:
        PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'entries': len(catalog['items']), 'changed': changed, 'missing': missing, 'written': not check}, ensure_ascii=False))


if __name__ == '__main__':
    main()
