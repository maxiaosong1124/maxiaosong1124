"""Render GitHub-native dark profile modules; no CSS or JavaScript required."""
from datetime import datetime
from html import escape
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

BG = '#0b0e0e'
TEXT = '#e6ebe4'
MUTED = '#9caa9f'
GREEN = '#b5ff5b'
PINK = '#f08dc2'
LINE = '#29382d'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
CJK_FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
SITE = 'https://maxiaosong1124.github.io/maxiaosong1124/'


class Panel:
    def __init__(self, width):
        self.width = width
        self.margin = 32 if width > 600 else 24
        self.image = Image.new('RGB', (width, 6000), BG)
        self.draw = ImageDraw.Draw(self.image)
        self.y = 28

    def font(self, size=22, cjk=False, bold=False):
        path = CJK_FONT if cjk else str(FONT_DIR / ('DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf'))
        return ImageFont.truetype(path, size)

    def label(self, value, color=GREEN):
        self.draw.text((self.margin, self.y), value, font=self.font(16), fill=color)
        self.y += 34

    def paragraph(self, value, size=22, color=TEXT, cjk=False, bold=False, width=None):
        font = self.font(size, cjk, bold)
        available = width or self.width - self.margin * 2
        # Tokenize English by words and CJK by characters; split long tokens only as needed.
        tokens = list(value) if cjk else re.findall(r'\S+\s*', value)
        lines, line = [], ''
        for token in tokens:
            if self.draw.textlength(line + token, font=font) <= available:
                line += token
                continue
            if line:
                lines.append(line.rstrip())
                line = ''
            for char in token.lstrip():
                if self.draw.textlength(line + char, font=font) > available:
                    lines.append(line.rstrip())
                    line = ''
                line += char
        if line:
            lines.append(line.rstrip())
        for line in lines:
            self.draw.text((self.margin, self.y), line, font=font, fill=color)
            self.y += int(size * 1.65)
        self.y += 14

    def rule(self):
        self.y += 8
        self.draw.line((self.margin, self.y, self.width-self.margin, self.y), fill=LINE, width=1)
        self.y += 26

    def save(self, path, bottom=20):
        assert self.y + bottom < self.image.height, 'Profile module exceeds canvas height'
        self.image.crop((0, 0, self.width, self.y + bottom)).save(path, optimize=True)


def build_native(data, output, avatar_path):
    assets = output / 'assets/native'
    assets.mkdir(parents=True, exist_ok=True)
    personal = data['personal']
    modules = []

    def module(name, alt, renderer, link=None):
        for width, suffix in [(960, ''), (480, '-mobile')]:
            panel = Panel(width)
            renderer(panel)
            panel.save(assets / f'{name}{suffix}.png')
        modules.append({'name': name, 'alt': alt, 'link': link, 'ext': 'png'})

    def header(p):
        p.label('MX / ENGINEERING TERMINAL')
        p.rule()
        p.paragraph(data['user']['login'], size=46 if p.width > 600 else 30, bold=True)
        p.paragraph('SYSTEMS / HPC / ML INFERENCE', size=20 if p.width > 600 else 17, color=GREEN)
        p.paragraph('RL-Kernel Core Contributor', size=22 if p.width > 600 else 19, color=PINK)
        p.paragraph('Hangzhou, CN  /  UTC+08:00', size=16, color=MUTED)
        p.rule()
        p.paragraph(' / '.join(personal['languages']), size=20, color=GREEN)
        p.paragraph('vLLM / PyTorch', size=20, color=MUTED)
        if p.width > 600:
            avatar = Image.open(avatar_path).convert('RGB').resize((100,100), Image.Resampling.LANCZOS)
            p.image.paste(avatar,(p.width-145,91))
            p.draw.rectangle((p.width-150,86,p.width-40,196),outline=LINE,width=2)
    module('header', data['user']['login'] + ' | RL-Kernel Core Contributor | Systems, HPC, ML inference', header, 'https://github.com/RL-Align/RL-Kernel')

    def entry(p):
        p.draw.rectangle((p.margin,8,p.width-p.margin,93),fill='#18241a',outline=GREEN,width=1)
        p.y=20
        p.draw.text((p.margin+16,p.y),'交互主页 / INTERACTIVE TERMINAL',font=p.font(22 if p.width>600 else 18,cjk=True),fill=GREEN)
        p.draw.text((p.margin+16,p.y+38),'OPEN FULL EXPERIENCE  ->',font=p.font(17),fill=MUTED)
        p.y=93
    module('interactive', '交互主页 / Interactive Terminal: 3D rotation and activity filters', entry, SITE)

    for name, label, key in [('about','00 / ABOUT ME · 个人介绍','intro'),('learning','CURRENTLY LEARNING · 当前学习方向','learning'),('vision','FUTURE VISION · 未来愿景','vision')]:
        def section(p, label=label, key=key):
            p.draw.text((p.margin,p.y),label,font=p.font(19,cjk=True),fill=PINK if key=='vision' else GREEN)
            p.y+=43
            p.paragraph(personal[key],cjk=True)
            if key=='intro':
                p.paragraph(personal['exploration'],cjk=True)
            p.rule()
            p.paragraph(personal['en'][key],size=21,color=MUTED)
            if key=='intro':
                p.paragraph(personal['en']['exploration'],size=21,color=MUTED)
        alt = personal[key] + ' / ' + personal['en'][key]
        module(name,alt,section)

    def telemetry(p):
        p.rule()
        p.label('01 / CONTRIBUTION TELEMETRY')
        values=[(data['total'],'CONTRIBUTIONS'),(data['active'],'ACTIVE DAYS'),(data['best'],'LONGEST STREAK'),(data['user']['public_repos'],'PUBLIC REPOS')]
        cols=4 if p.width>600 else 2
        col_width=(p.width-p.margin*2)//cols
        start=p.y
        for i,(value,label) in enumerate(values):
            x=p.margin+(i%cols)*col_width
            y=start+(i//cols)*112
            p.draw.text((x,y),str(value),font=p.font(40),fill=TEXT)
            p.draw.text((x,y+58),label,font=p.font(14),fill=MUTED)
        p.y=start+((len(values)+cols-1)//cols)*112
        p.paragraph(f'{data["days"][0]["date"]} / {data["days"][-1]["date"]}',size=16,color=MUTED)
    module('telemetry','Contribution statistics: '+str(data['total'])+' contributions',telemetry)
    modules.append({'name':'terrain','alt':'Animated 3D contribution terrain. Height = log(1 + daily contributions).','link':None,'ext':'gif'})

    def signal(p):
        p.label('02 / DAILY SIGNAL')
        recent=data['days'][-30:]
        p.paragraph(str(sum(d['count'] for d in recent))+' contributions / 30 days',size=22,color=TEXT)
        top=p.y+10
        height=160 if p.width>600 else 115
        bottom=top+height
        for y in range(top,bottom+1,40):
            p.draw.line((p.margin,y,p.width-p.margin,y),fill=LINE)
        peak=max(1,max(d['count'] for d in recent))
        step=(p.width-2*p.margin)/len(recent)
        for i,day in enumerate(recent):
            x=p.margin+i*step
            bar=max(2,day['count']/peak*height)
            p.draw.rectangle((x,bottom-bar,x+step*.65,bottom),fill=GREEN if day['count']==peak else '#679937')
        p.y=bottom+20
        p.paragraph(recent[0]['date']+' / '+recent[-1]['date'],size=16,color=MUTED)
    module('signal','Daily contributions over the last 30 days',signal)

    def title(label):
        def paint(p):
            p.rule()
            p.label(label)
        return paint
    module('projects','Open source contributions',title('03 / OPEN SOURCE'))
    for i,project in enumerate(data['showcase']['projects']):
        def project_panel(p,project=project):
            p.paragraph(project['repo']+'  ->',size=24,color=TEXT)
            p.paragraph('CORE CONTRIBUTOR' if project['repo']=='RL-Align/RL-Kernel' else 'PUBLIC CONTRIBUTIONS',size=16,color=PINK if project['repo']=='RL-Align/RL-Kernel' else GREEN)
        module(f'project-{i}',project['repo'],project_panel,project['url'])
    module('featured','Featured personal repositories',title('FEATURED REPOSITORIES'))
    for i,repo in enumerate(data['showcase']['featured']):
        def repo_panel(p,repo=repo):
            p.paragraph(repo['name'],size=24)
            p.paragraph(str(repo['stargazers_count'])+' STARS  /  '+(repo['language'] or ''),size=18,color=GREEN)
            if repo['description']:
                p.paragraph(repo['description'],size=19,color=MUTED)
        module(f'featured-{i}',repo['name']+' · '+str(repo['stargazers_count'])+' stars',repo_panel,repo['html_url'])
    module('events','Recent public activity, Asia/Shanghai time',title('04 / ACTIVITY STREAM'))
    for i,event in enumerate(data['events'][:6]):
        date=datetime.fromisoformat(event['date'].replace('Z','+00:00')).astimezone(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')
        label=event['label']+(f' #{event["number"]}' if event['number'] else '')
        def event_panel(p,event=event,date=date,label=label):
            p.label(date+' / UTC+8',color=MUTED)
            p.paragraph(label,size=22,color=GREEN)
            p.paragraph(event['repo'],size=20,color=TEXT)
            if event['title']:
                p.paragraph(event['title'],size=17,color=MUTED)
            p.draw.line((p.margin,p.y,p.width-p.margin,p.y),fill=LINE)
        module(f'event-{i}',date+' '+label+' '+event['repo'],event_panel,event['url'])
    module('contact','Establish connection',title('05 / ESTABLISH CONNECTION'))
    def email(p):
        p.label('EMAIL',MUTED)
        p.paragraph('maxiaosong1234@outlook.com',size=22 if p.width>600 else 20,color=GREEN)
    module('email','Email: maxiaosong1234@outlook.com',email,'mailto:maxiaosong1234@outlook.com')
    def end(p):
        p.paragraph('>_ END OF TRANSMISSION',size=18,color=GREEN)
        p.paragraph('SNAPSHOT / '+data['updated'][:16].replace('T',' ')+' UTC',size=14,color=MUTED)
    module('footer','Data snapshot '+data['updated'],end)
    version=re.sub(r'\D','',data['updated'])
    blocks=[]
    for item in modules:
        path='assets/native/'+item['name']
        ext=item['ext']
        image=f'<picture><source media="(max-width: 600px)" srcset="{path}-mobile.{ext}?v={version}"><img src="{path}.{ext}?v={version}" alt="{escape(item["alt"],quote=True)}" width="960" align="top"></picture>'
        if item['link']:
            image=f'<a href="{escape(item["link"],quote=True)}">{image}</a>'
        blocks.append(image)
    markdown='<p align="center">\n'+'<br>\n'.join(blocks)+'\n</p>\n\n'
    markdown+='<details>\n<summary>文字版 / Accessible text</summary>\n\n'
    markdown+='### maxiaosong1124 · RL-Kernel Core Contributor\n\n'
    for key in ['intro','exploration','learning','vision']:
        markdown+=personal[key]+'\n\n'+personal['en'][key]+'\n\n'
    markdown+='Tech stack: '+', '.join(personal['languages'])+'\n\nFrameworks: '+', '.join(personal['frameworks'])+'\n\n'
    for project in data['showcase']['projects']:
        markdown+=f'- [{project["repo"]}]({project["url"]})\n'
    markdown+='\n[Email](mailto:maxiaosong1234@outlook.com) · [Interactive terminal]('+SITE+')\n\nPublic activity: latest 100-event snapshot. Project discovery: public authored PRs and issues.\n\n</details>\n'
    (output/'README.md').write_text(markdown,encoding='utf-8')
    print(f'Generated {len(modules)-1} desktop/mobile native image modules and README.')
