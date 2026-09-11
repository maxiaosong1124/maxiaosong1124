"""Build evidence-backed project summaries from public GitHub search snapshots."""
import json
from html import escape
from urllib.parse import quote


def build_showcase(root, user, repos):
    projects = {}
    for filename, kind in [('pull-requests.json', 'prs'), ('issues.json', 'issues')]:
        result = json.loads((root / 'data' / filename).read_text())
        if result['incomplete_results'] or len(result['items']) != result['total_count']:
            raise ValueError(f'Incomplete search snapshot: {filename}; fetch all pages before building.')
        for item in result['items']:
            repo = '/'.join(item['repository_url'].split('/')[-2:])
            if repo.lower().startswith(user['login'].lower() + '/'):
                continue
            project = projects.setdefault(repo, {'repo': repo, 'prs': 0, 'merged': 0, 'issues': 0})
            project[kind] += 1
            if kind == 'prs' and item['pull_request'].get('merged_at'):
                project['merged'] += 1
    projects = sorted(projects.values(), key=lambda p: (p['repo'] != 'RL-Align/RL-Kernel', -p['prs'], p['repo']))
    featured = sorted([r for r in repos if not r['fork'] and r['stargazers_count'] > 0], key=lambda r: (-r['stargazers_count'], r['name']))[:3]
    rows, markdown, table = [], [], []
    for p in projects:
        repo = p['repo']
        p['url'] = f'https://github.com/{repo}/issues?q=' + quote(f'author:{user["login"]}', safe='')
        role = 'CORE CONTRIBUTOR' if repo == 'RL-Align/RL-Kernel' else 'PUBLIC CONTRIBUTIONS'
        rows.append(f'<a class="project" href="{escape(p["url"], quote=True)}" target="_blank" rel="noreferrer"><span><span class="project-name">{escape(repo)}</span><span class="project-sub">{role}</span></span><span class="project-arrow">↗</span></a>')
        markdown.append(f'| [{repo}]({p["url"]}) | {role} |')
        table.append(f'<tr><td><a href="{escape(p["url"], quote=True)}">{escape(repo)}</a></td><td>{role}</td></tr>')
    own = ''.join(f'<a class="project featured-project" href="{escape(r["html_url"], quote=True)}" target="_blank" rel="noreferrer"><span><span class="project-name">{escape(r["name"])}</span><span class="project-sub">{escape(r["description"] or "")}</span><span class="project-sub">{escape(r["language"] or "")}</span></span><span class="project-right">★ {r["stargazers_count"]}<small>STARS ↗</small></span></a>' for r in featured)
    return {'projects': projects, 'featured': featured, 'projects_html': ''.join(rows), 'featured_html': own, 'table_html': ''.join(table), 'markdown': markdown}
