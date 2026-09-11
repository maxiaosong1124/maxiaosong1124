"""Refresh the public profile atomically; never embed authentication in outputs."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
USERNAME = 'maxiaosong1124'


def download(url):
    headers = {'User-Agent': 'maxiaosong1124-profile-refresh'}
    if url.startswith('https://api.github.com/'):
        headers.update({'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
        token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
        if token:
            headers['Authorization'] = 'Bearer ' + token
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=headers), timeout=45) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError(f'Unable to fetch public data: {url}') from None
            time.sleep(2 ** attempt)


def api(path, **params):
    url = 'https://api.github.com/' + path
    if params:
        url += '?' + urlencode(params)
    return json.loads(download(url))


def search(kind):
    query = f'author:{USERNAME} is:{kind}'
    items, page = [], 1
    while True:
        result = api('search/issues', q=query, per_page=100, page=page, sort='created', order='asc')
        total = result['total_count']
        if result['incomplete_results'] or total > 1000:
            raise RuntimeError('Incomplete GitHub search; keep previous profile and split query by date before retrying.')
        items.extend(result['items'])
        if len(items) >= total:
            if len({item['id'] for item in items}) != total:
                raise RuntimeError('Search changed during pagination; keep previous profile and retry.')
            return {'total_count': total, 'incomplete_results': False, 'items': items}
        if not result['items']:
            raise RuntimeError('Missing GitHub search page.')
        page += 1


def refresh():
    with tempfile.TemporaryDirectory(prefix='github-profile-') as folder:
        work = Path(folder)
        data = work / 'data'
        data.mkdir()
        def save(name, value):
            (data / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        save('user.json', api(f'users/{USERNAME}'))
        repos, page = [], 1
        while True:
            batch = api(f'users/{USERNAME}/repos', per_page=100, page=page, sort='full_name')
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        save('repos.json', repos)
        save('events.json', api(f'users/{USERNAME}/events/public', per_page=100))
        save('pull-requests.json', search('pr'))
        save('issues.json', search('issue'))
        (data / 'contributions.html').write_bytes(download(f'https://github.com/users/{USERNAME}/contributions'))
        shutil.copyfile(ROOT / 'data/personal.json', data / 'personal.json')
        sys.path.insert(0, str(ROOT / 'tools'))
        spec = importlib.util.spec_from_file_location('profile_builder', ROOT / 'tools/build.py')
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        builder.ROOT = work
        builder.build(profile_only=True)
        for name in ['index.html', 'style.css', 'app.js', 'terrain.js']:
            shutil.copyfile(ROOT / 'web' / name, work / name)
        shutil.copytree(ROOT / 'web/assets', work / 'assets')
        import build_preview
        build_preview.ROOT = work
        build_preview.build_preview(production=True)
        generated = work / 'profile'
        for source in [generated / 'README.md', *(generated / 'assets').glob('*.svg')]:
            target = ROOT / source.relative_to(generated)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        site = ROOT / '_site'
        site.mkdir(exist_ok=True)
        shutil.copyfile(work / 'preview.html', site / 'index.html')
        print('Updated README, SVG assets and interactive website from the same public data.')


if __name__ == '__main__':
    refresh()
