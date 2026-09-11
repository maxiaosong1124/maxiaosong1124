"""Build offline previews and GitHub-compatible assets from public snapshots."""
import json
from collections import Counter
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from terrain import terrain_svg
from showcase import build_showcase

ROOT = Path(__file__).resolve().parents[1]


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}
        self.tip = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "td" and "data-date" in attrs:
            self.days[attrs["id"]] = {"date": attrs["data-date"], "level": int(attrs["data-level"]), "count": None}
        if tag == "tool-tip":
            self.tip = attrs.get("for")

    def handle_data(self, text):
        if self.tip in self.days and "contribution" in text:
            first = text.strip().split()[0]
            self.days[self.tip]["count"] = 0 if first == "No" else int(first.replace(",", ""))

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.tip = None


def svg(width, height, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<rect width="100%" height="100%" fill="#0b0e0e"/><style>text{{font-family:Consolas,'Liberation Mono',monospace;fill:#e5eae4}}.muted{{fill:#86948a}}.green{{fill:#b5ff5b}}.pink{{fill:#f08dc2}}</style>{body}</svg>'''


def text(x, y, value, size=12, cls="", extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{escape(str(value))}</text>'


def build(profile_only=False):
    user = json.loads((ROOT / "data/user.json").read_text())
    personal = json.loads((ROOT / "data/personal.json").read_text())
    repos = json.loads((ROOT / "data/repos.json").read_text())
    raw_events = json.loads((ROOT / "data/events.json").read_text())
    parser = CalendarParser()
    parser.feed((ROOT / "data/contributions.html").read_text())
    days = sorted(parser.days.values(), key=lambda d: d["date"])
    if len(days) < 350 or any(d["count"] is None for d in days):
        raise ValueError("Incomplete contribution calendar; keep previous generated assets.")
    events = []
    contributed = Counter()
    contribution_types = {"PushEvent", "PullRequestEvent", "PullRequestReviewEvent", "PullRequestReviewCommentEvent", "IssuesEvent", "IssueCommentEvent"}
    for event in raw_events:
        payload = event["payload"]
        repo = event["repo"]["name"]
        kind = event["type"]
        item = payload.get("pull_request", payload.get("issue", {}))
        number = payload.get("number", item.get("number"))
        action = payload.get("action", "")
        labels = {"PullRequestEvent": f"{action} pull request", "PullRequestReviewEvent": "reviewed pull request", "PushEvent": "pushed code", "CreateEvent": f"created {payload.get('ref_type', 'branch')}", "IssueCommentEvent": "commented on issue / PR", "IssuesEvent": f"{action} issue", "WatchEvent": "starred repository", "ForkEvent": "forked repository", "PullRequestReviewCommentEvent": "commented on review", "DeleteEvent": f"deleted {payload.get('ref_type', 'branch')}"}
        link = payload.get("review", {}).get("html_url") or payload.get("comment", {}).get("html_url") or item.get("html_url")
        if not link:
            link = f"https://github.com/{repo}" + (f"/pull/{number}" if number and kind.startswith("PullRequest") else "")
        events.append({"date": event["created_at"], "type": kind, "repo": repo, "label": labels.get(kind, kind.removesuffix("Event")), "number": number, "title": item.get("title") or payload.get("pull_request", {}).get("head", {}).get("ref", ""), "url": link})
        if kind in contribution_types and not repo.lower().startswith(user["login"].lower() + "/"):
            contributed[repo] += 1
    total = sum(d["count"] for d in days)
    active = sum(d["count"] > 0 for d in days)
    best = streak = 0
    for day in days:
        streak = streak + 1 if day["count"] else 0
        best = max(best, streak)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    data = {"user": user, "repos": repos, "events": events, "days": days, "contributed": contributed.most_common(), "total": total, "active": active, "best": best, "updated": stamp}
    data["personal"] = personal
    data["showcase"] = build_showcase(ROOT, user, repos)
    (ROOT / "data/profile.js").write_text("window.PROFILE = " + json.dumps(data, ensure_ascii=True) + ";\n")
    assets = ROOT / "profile/assets"
    assets.mkdir(parents=True, exist_ok=True)
    banner = '<path d="M0 1H960M0 279H960" stroke="#33432b"/><path d="M0 1H110" stroke="#b5ff5b" stroke-width="3"/>'
    banner += text(32, 36, "MX / ENGINEERING TERMINAL", 11, "green") + text(740, 36, "PUBLIC ACCESS // 01", 10, "muted")
    banner += text(32, 104, "maxiaosong1124", 48, extra='font-weight="bold"')
    banner += text(34, 141, " / ".join(personal["languages"]), 15, "green")
    banner += text(34, 171, "SYSTEMS / HPC / ML INFERENCE  ·  vLLM / PyTorch", 13, "muted")
    banner += text(34, 204, "RL-KERNEL MAINTAINER", 16, "pink")
    banner += '<rect x="485" y="112" width="24" height="3" fill="#b5ff5b"><animate attributeName="opacity" values="1;1;0;0;1" dur="1.6s" repeatCount="indefinite"/></rect>'
    banner += '<path d="M0 278H120" stroke="#b5ff5b" stroke-width="2"><animateTransform attributeName="transform" type="translate" values="-120 0;960 0" dur="6s" repeatCount="indefinite"/></path>'
    banner += text(34, 242, "HANGZHOU, CN", 11, "muted") + text(650, 242, "[ BUILD. PROFILE. OPTIMIZE. ]", 11, "pink")
    for i in range(7):
        banner += f'<path d="M{688+i*29} 70v{40+i*7}l-24 24v40" fill="none" stroke="#283b26"/>'
        banner += f'<rect x="{661+i*29}" y="{173+i*7}" width="5" height="5" fill="{["#b5ff5b", "#f08dc2", "#314828"][i%3]}"/>'
    (assets / "header.svg").write_text(svg(960, 280, banner))
    body = text(28, 33, "01 / CONTRIBUTION TELEMETRY", 12, "green")
    for i, (value, label) in enumerate([(total, "CONTRIBUTIONS"), (active, "ACTIVE DAYS"), (best, "LONGEST STREAK"), (user["public_repos"], "PUBLIC REPOS")]):
        x = 28 + i * 235
        body += text(x, 95, value, 38) + text(x, 124, label, 11, "muted")
    body += text(28, 160, f"{days[0]['date']} — {days[-1]['date']}  /  GitHub public snapshot", 10, "muted")
    (assets / "stats.svg").write_text(svg(960, 180, body))
    colors = ["#18201b", "#2e4923", "#507b31", "#84b847", "#b5ff5b"]
    body = text(28, 30, "02 / CONTRIBUTION MATRIX", 12, "green")
    last_month = ""
    for i, day in enumerate(days):
        x, y = 29 + (i // 7) * 17, 65 + (i % 7) * 17
        month = day["date"][:7]
        if month != last_month and i % 7 == 0:
            body += text(x, 53, datetime.fromisoformat(day["date"]).strftime("%b"), 9, "muted")
            last_month = month
        body += f'<rect x="{x}" y="{y}" width="13" height="13" rx="2" fill="{colors[day["level"]]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
    body += text(28, 208, f"{total:,} contributions / {len(days)} days", 11, "muted")
    (assets / "contributions.svg").write_text(svg(960, 232, body))
    (assets / "contributions.svg").write_text(terrain_svg(days))
    recent = days[-30:]
    maximum = max(1, max(d["count"] for d in recent))
    body = text(28, 32, "03 / DAILY SIGNAL — LAST 30 DAYS", 12, "green")
    for y in [60, 100, 140, 180]:
        body += f'<path d="M28 {y}H935" stroke="#202a23"/>'
    for i, day in enumerate(recent):
        height = day["count"] / maximum * 110
        body += f'<rect x="{32+i*30}" y="{180-height}" width="17" height="{max(1,height)}" fill="{colors[4] if i == 29 else colors[2]}"><title>{day["date"]}: {day["count"]}</title></rect>'
    body += text(28, 210, recent[0]["date"], 10, "muted") + text(845, 210, recent[-1]["date"], 10, "muted")
    (assets / "activity.svg").write_text(svg(960, 235, body))
    lines = ['![maxiaosong1124 - Engineering Terminal](assets/header.svg)', '', '[GitHub](https://github.com/maxiaosong1124) · [Email](mailto:maxiaosong1234@outlook.com) · Hangzhou, CN', '', '![Contribution statistics](assets/stats.svg)', '', '![Annual contribution calendar](assets/contributions.svg)', '', '![Daily activity](assets/activity.svg)', '', '### 04 / Open Source Contributions', '', 'Public contribution events in the latest 100-event snapshot. Forks and stars are excluded.', '', '| Project | Events |', '| :--- | ---: |']
    lines[-4:] = ['', '', '| Project | Contribution |', '| :--- | :--- |']
    lines += data['showcase']['markdown']
    lines += ['', '#### Featured Repositories', '']
    lines += [f'- [{r["name"]}]({r["html_url"]}) · **{r["stargazers_count"]} stars** — {r["description"] or ""}' for r in data['showcase']['featured']]
    lines += ['', '### 05 / Recent Activity', '', '| Date (UTC) | Activity | Project |', '| :--- | :--- | :--- |']
    lines += [f'| {e["date"][:10]} | [{e["label"]}{" #"+str(e["number"]) if e["number"] else ""}]({e["url"]}) | {e["repo"]} |' for e in events[:8]]
    lines[4:4] = ['### 00 / 个人介绍 · About Me', '', personal['intro'], '', personal['exploration'], '', personal['en']['intro'], '', personal['en']['exploration'], '', '**技术栈 / Tech stack**：' + ' · '.join(personal['languages']), '', '**熟悉的框架 / Familiar frameworks**：' + ' · '.join(personal['frameworks']), '', '**当前学习方向 / Currently learning**', '', personal['learning'], '', personal['en']['learning'], '', '**未来愿景 / Future vision**', '', personal['vision'], '', personal['en']['vision'], '']
    lines += ['', '---', '', f'Public data snapshot: {stamp}. Activity is limited to the latest 100 public events; it is not a complete contribution history.', '']
    lines[4:4] = ['**[RL-Kernel Maintainer](https://github.com/RL-Align/RL-Kernel)**', '']
    lines[0] = '[![maxiaosong1124 - Engineering Terminal](assets/header.svg)](https://maxiaosong1124.github.io/maxiaosong1124/)'
    lines[2:2] = ['### [进入交互主页 / Open Interactive Terminal ↗](https://maxiaosong1124.github.io/maxiaosong1124/)', '']
    (ROOT / "profile/README.md").write_text('\n'.join(lines))
    if not profile_only:
        from build_preview import build_preview
        build_preview()
    print(f"Built: {len(days)} days, {total} contributions, {len(events)} events, {len(contributed)} contributed projects.")


if __name__ == "__main__":
    build()
