"""Render profile content at build time; JavaScript only enhances the result."""
import json
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from zoneinfo import ZoneInfo

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Element:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def html(self):
        attrs = ''.join(f' {key}' if value is None else f' {key}="{escape(value, quote=True)}"' for key, value in self.attrs.items())
        content = ''.join(child.html() if isinstance(child, Element) else child for child in self.children)
        if not self.tag:
            return content
        return f'<{self.tag}{attrs}>' + ('' if self.tag in VOID else content + f'</{self.tag}>')

    def find(self, **attrs):
        for child in self.children:
            if isinstance(child, Element):
                if all(child.attrs.get(key) == value for key, value in attrs.items()):
                    return child
                found = child.find(**attrs)
                if found:
                    return found


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.root = Element('')
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        if self.stack[-1].tag == tag:
            self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def handle_decl(self, decl):
        self.handle_data(f'<!{decl}>')

    def handle_entityref(self, name):
        self.handle_data(f'&{name};')

    def handle_charref(self, name):
        self.handle_data(f'&#{name};')


def render_static(source, root):
    data = json.loads((root / 'data/profile.js').read_text().removeprefix('window.PROFILE = ').strip().removesuffix(';'))
    personal = data['personal']
    doc = Document(source).root
    e = lambda value: escape(str(value), quote=True)

    def fill(id, html):
        doc.find(id=id).children = [html]

    intro = f'<div class="personal-copy"><div lang="zh-CN"><p>{e(personal["intro"])}</p><p>{e(personal["exploration"])}</p></div><div lang="en" class="english-copy"><p>{e(personal["en"]["intro"])}</p><p>{e(personal["en"]["exploration"])}</p></div></div>'
    tech = f'<p><strong>技术栈 / Tech stack：</strong>{e(" · ".join(personal["languages"]))}</p><p><strong>熟悉的框架 / Familiar frameworks：</strong>{e(" · ".join(personal["frameworks"]))}</p>'
    learning = f'<div><span class="section-meta">CURRENTLY LEARNING / 当前学习方向</span><p lang="zh-CN">{e(personal["learning"])}</p><p lang="en" class="english-copy">{e(personal["en"]["learning"])}</p></div>'
    vision = f'<div class="vision"><span class="section-meta">FUTURE VISION / 未来愿景</span><p lang="zh-CN">{e(personal["vision"])}</p><p lang="en" class="english-copy">{e(personal["en"]["vision"])}</p></div>'
    terminal = doc.find(id='terminal-view')
    bottom = doc.find(id='about')
    bottom.attrs.pop('id')
    about = bottom.find(**{'class': 'section blank-section'})
    bottom.children.remove(about)
    about.attrs.update({'id': 'about', 'class': 'section profile-intro'})
    about.children = ['<h2><span>00 /</span> 个人介绍 <span class="section-meta">ABOUT ME</span></h2>', intro, f'<div class="personal-copy profile-directions">{learning}{vision}</div>']
    terminal.children.insert(terminal.children.index(doc.find(**{'class': 'subnav'})), about)
    horizon = bottom.find(**{'class': 'section blank-section'})
    bottom.children.remove(horizon)
    doc.find(**{'class': 'role'}).children = ['SYSTEMS <span>/</span> HPC <span>/</span> ML INFERENCE']
    doc.find(**{'class': 'stack'}).children = [''.join(f'<span>{e(name)}</span>' for name in personal['languages']) + '<b>/</b>' + ''.join(f'<span>{e(name)}</span>' for name in personal['frameworks'])]
    fill('metrics', ''.join(f'<div class="metric"><div class="metric-value">{n}<small>{unit}</small></div><div class="metric-label">{label}</div></div>' for n, label, unit in [(data['total'], 'TOTAL CONTRIBUTIONS', '/ year'), (data['active'], 'ACTIVE DAYS', 'days'), (data['best'], 'LONGEST STREAK', 'days'), (data['user']['public_repos'], 'PUBLIC REPOSITORIES', 'repos')]))
    fill('date-range', f'{data["days"][0]["date"]} — {data["days"][-1]["date"]}')
    fill('heatmap', ''.join(f'<span data-level="{day["level"]}" title="{day["date"]} · {day["count"]} contributions"></span>' for day in data['days']))
    months, previous = [], ''
    for i, day in enumerate(data['days']):
        if i % 7 == 0 and day['date'][:7] != previous:
            months.append(f'<span style="grid-column:{i//7+1}">{datetime.fromisoformat(day["date"]).strftime("%b")}</span>')
            previous = day['date'][:7]
    fill('month-labels', ''.join(months))
    fill('contributed-projects', ''.join(f'<a class="project" href="https://github.com/{e(repo)}"><span><span class="project-name">{e(repo)}</span><span class="project-sub">PUBLIC CONTRIBUTIONS</span></span><span class="project-right">{count}<small>EVENTS ↗</small></span></a>' for repo, count in data['contributed']))
    fill('personal-repos', ''.join(f'<a class="repo-row" href="{e(repo["html_url"])}">{e(repo["name"])}<span><i class="lang-dot"></i>{e(repo["language"] or "—")} ↗</span></a>' for repo in [r for r in data['repos'] if not r['fork']][:3]))
    days = data['days'][-30:]
    maximum = max(1, max(day['count'] for day in days))
    fill('signal-total', str(sum(day['count'] for day in days)))
    fill('signal-period', '/ LAST 30 DAYS')
    fill('signal-bars', ''.join(f'<button style="height:{max(1,day["count"]/maximum*92)}%" title="{day["date"]} · {day["count"]} contributions" aria-label="{day["date"]}: {day["count"]} contributions"></button>' for day in days))
    fill('signal-start', days[0]['date'])
    fill('signal-end', days[-1]['date'])
    fill('signal-readout', f'{sum(day["count"] > 0 for day in days)} active days / peak {maximum} contributions')
    rows = []
    for event in data['events'][:6]:
        date = datetime.fromisoformat(event['date'].replace('Z', '+00:00')).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')
        label = e(event['label']) + (f' #{event["number"]}' if event['number'] else '')
        rows.append(f'<a class="event-row" href="{e(event["url"])}"><time class="event-date">{date}</time><span class="event-main"><span class="event-icon">⑂</span><span><span class="event-label">{label}</span><span class="event-title">{e(event["title"])}</span></span></span><span class="event-repo">{e(event["repo"])}</span><span class="event-arrow">↗</span></a>')
    fill('activity-list', ''.join(rows))
    fill('event-count', f'6 / {len(data["events"])} EVENTS · 公开活动快照')
    fill('snapshot-time', 'SNAPSHOT / ' + e(data['updated']))
    readme = doc.find(**{'class': 'readme-body'})
    headings = [node for node in readme.children if isinstance(node, Element) and node.tag == 'h3']
    old_about = next(node for node in headings if 'About Me' in node.html())
    readme.children.remove(old_about)
    stats = next(node for node in readme.children if isinstance(node, Element) and node.attrs.get('src') == 'profile/assets/stats.svg')
    readme.children.insert(readme.children.index(stats), '<h3>00 / 个人介绍 · About Me</h3>' + intro + tech + learning + '<h4>未来愿景 / Future vision</h4>' + f'<p lang="zh-CN">{e(personal["vision"])}</p><p lang="en">{e(personal["en"]["vision"])}</p>')
    last_heading = next(node for node in headings if 'Next Horizon' in node.html())
    readme.children.remove(last_heading)
    fill('readme-projects', ''.join(f'<tr><td><a href="https://github.com/{e(repo)}">{e(repo)}</a></td><td>{count}</td></tr>' for repo, count in data['contributed']))
    fill('readme-events', ''.join(f'<tr><td>{event["date"][:10]}</td><td><a href="{e(event["url"])}">{e(event["label"])}{(" #"+str(event["number"])) if event["number"] else ""}</a></td><td>{e(event["repo"])}</td></tr>' for event in data['events'][:8]))
    fill('readme-stamp', 'Public data snapshot: ' + e(data['updated']) + '. Activity is limited to the latest 100 public events; it is not a complete contribution history.')
    showcase = data['showcase']
    badge = '<a class="contributor-role" href="https://github.com/RL-Align/RL-Kernel">RL-Kernel Core Contributor ↗</a>'
    doc.find(**{'class': 'role'}).children.append(badge)
    fill('contributed-projects', showcase['projects_html'])
    fill('personal-repos', showcase['featured_html'])
    doc.find(id='projects').find(**{'class': 'data-note'}).attrs['hidden'] = None
    fill('readme-projects', showcase['table_html'])
    project_table = next(node for node in readme.children if isinstance(node, Element) and node.tag == 'table')
    next(node for node in project_table.children if isinstance(node, Element) and node.tag == 'thead').children = ['<tr><th>Project</th><th>Contribution</th></tr>']
    for node in readme.children:
        if isinstance(node, Element) and node.tag == 'p' and 'latest 100-event snapshot' in node.html():
            node.attrs['hidden'] = None
    readme.children.insert(readme.children.index(project_table) + 1, '<h4>Featured Repositories</h4>' + showcase['featured_html'])
    readme.children.insert(1, badge)
    return doc.html()
