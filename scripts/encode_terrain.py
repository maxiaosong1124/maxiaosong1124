"""Encode Three.js captures into GitHub-compatible looping GIFs."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = Path(__file__).resolve().parents[1]
BG = (11,14,14)


def encode():
    output=ROOT/'assets/native'
    for name,suffix,width in [('desktop','',960),('mobile','-mobile',480)]:
        paths=sorted((ROOT/'_frames'/name).glob('*.png'))
        assert len(paths)==64, 'Incomplete frame sequence'
        frames=[]
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',16 if width>600 else 12)
        for path in paths:
            src=Image.open(path).convert('RGBA')
            scale=width/src.width
            src=src.resize((width,round(src.height*scale)),Image.Resampling.LANCZOS)
            frame=Image.new('RGB',(width,src.height+58),BG)
            frame.paste(src,(0,28),src)
            draw=ImageDraw.Draw(frame)
            draw.text((24,5),'3D CONTRIBUTION TERRAIN',font=font,fill='#b5ff5b')
            draw.text((24,frame.height-24),'HEIGHT = LOG(1 + DAILY CONTRIBUTIONS)',font=font,fill='#9caa9f')
            frames.append(frame)
        palette=frames[0].quantize(colors=128)
        indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
        target=output/f'terrain{suffix}.gif'
        indexed[0].save(target,save_all=True,append_images=indexed[1:],duration=125,loop=0,optimize=True,disposal=1)
        with Image.open(target) as gif:
            assert gif.n_frames>=60 and gif.info['loop']==0
            gif.seek(0);first=gif.convert('RGB')
            gif.seek(16);other=gif.convert('RGB')
            assert ImageChops.difference(first,other).getbbox(), 'GIF does not animate'
        assert target.stat().st_size<8_000_000, 'GIF too large for practical profile loading'
        print(f'{target.name}: {target.stat().st_size:,} bytes, {len(indexed)} frames')


if __name__=='__main__':
    encode()
