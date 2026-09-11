"""Build the single clickable banner used by the GitHub profile README."""
from html import escape
from PIL import Image
from native_profile import Panel, GREEN, MUTED, PINK, LINE, SITE


def build_entry(data, output, avatar_path):
    assets = output / 'assets/entry'
    assets.mkdir(parents=True, exist_ok=True)
    for width, suffix in [(960, ''), (480, '-mobile')]:
        p = Panel(width)
        p.label('>_ ENGINEERING TERMINAL', GREEN)
        p.rule()
        p.paragraph(data['user']['login'], size=48 if width>600 else 30, bold=True)
        p.paragraph('RL-Kernel Core Contributor', size=22 if width>600 else 19, color=PINK)
        if width>600:
            avatar=Image.open(avatar_path).convert('RGB').resize((96,96),Image.Resampling.LANCZOS)
            p.image.paste(avatar,(width-152,84))
            p.draw.rectangle((width-157,79,width-51,185),outline=LINE,width=2)
        p.rule()
        p.paragraph('进入个人主页',size=25,cjk=True,color=GREEN)
        p.paragraph('ENTER MY TERMINAL  ->',size=22 if width>600 else 20,color=MUTED)
        p.save(assets/f'terminal{suffix}.png')
    alt=escape(data['user']['login']+' | RL-Kernel Core Contributor | 进入个人主页 / Enter My Terminal',quote=True)
    readme=f'''<p align="center">
  <a href="{SITE}">
    <picture>
      <source media="(max-width: 600px)" srcset="assets/entry/terminal-mobile.png">
      <img src="assets/entry/terminal.png" width="960" align="top" alt="{alt}">
    </picture>
  </a>
</p>
'''
    (output/'README.md').write_text(readme,encoding='utf-8')
    print('Generated a single clickable desktop/mobile profile banner.')
