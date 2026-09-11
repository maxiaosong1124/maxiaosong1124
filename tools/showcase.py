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
        role = 'MAINTAINER' if repo == 'RL-Align/RL-Kernel' else 'PUBLIC CONTRIBUTIONS'
        rows.append(f'<a class="project" href="{escape(p["url"], quote=True)}" target="_blank" rel="noreferrer"><span><span class="project-name">{escape(repo)}</span><span class="project-sub">{role}</span></span><span class="project-arrow">↗</span></a>')
        markdown.append(f'| [{repo}]({p["url"]}) | {role} |')
        table.append(f'<tr><td><a href="{escape(p["url"], quote=True)}">{escape(repo)}</a></td><td>{role}</td></tr>')
    descriptions = json.loads((root / 'data/personal.json').read_text()).get('featured_projects', {})
    own = []
    for repo in featured:
        description = descriptions.get(repo['name'])
        summary = description['summary'] if description else (repo['description'] or '')
        details = ''
        if description:
            details = '<div class="featured-details"><p lang="zh-CN">' + escape(summary) + '</p><p lang="en">' + escape(description['summary_en']) + '</p><ul>'
            details += ''.join('<li><p lang="zh-CN">' + escape(item['zh']) + '</p><p lang="en">' + escape(item['en']) + '</p></li>' for item in description['highlights'])
            details += '</ul></div>'
        if not details:
            details = '<div class="featured-details"><p>' + escape(summary) + '</p></div>'
        own.append(f'<details class="featured-item"><summary class="project featured-project"><span><span class="project-name">{escape(repo["name"])}</span><span class="project-sub">{escape(repo["language"] or "")}</span></span><span class="project-right">★ {repo["stargazers_count"]}<small>STARS</small></span></summary>{details}<a class="text-link featured-repo-link" href="{escape(repo["html_url"], quote=True)}" target="_blank" rel="noreferrer">查看仓库 / View repository ↗</a></details>')
    own = ''.join(own)
    return {'projects': projects, 'featured': featured, 'projects_html': ''.join(rows), 'featured_html': own, 'table_html': ''.join(table), 'markdown': markdown}
