"""Project the contribution columns into a standalone isometric SVG."""
from html import escape
from math import log1p


def terrain_svg(days):
    peak = max(1, max(day['count'] for day in days))
    colors = ['#26382d', '#456730', '#679937', '#93c84d', '#b5ff5b']
    def point(x, z, height=0):
        return f'{90+x*14+z*15:.1f},{135-x*1.2+z*17-height:.1f}'
    def face(points, color):
        return f'<polygon points="{" ".join(point(*p) for p in points)}" fill="{color}" stroke="#0b0e0e" stroke-width="0.6"/>'
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="370" viewBox="0 0 960 370" role="img"><title>3D GitHub contribution terrain</title><rect width="960" height="370" fill="#0b0e0e"/>', '<g font-family="Consolas,monospace" fill="#8c998e" font-size="11"><text x="28" y="30" fill="#b5ff5b">02 / CONTRIBUTION TERRAIN</text><text x="28" y="330">HEIGHT = LOG(1 + DAILY CONTRIBUTIONS)</text><text x="28" y="352">' + escape(days[0]['date'] + ' — ' + days[-1]['date']) + '</text></g>']
    out.append(face([(-1,-1,-3),(54,-1,-3),(54,8,-3),(-1,8,-3)], '#121d17'))
    for i in sorted(range(len(days)), key=lambda i: (i % 7, -(i // 7))):
        day = days[i]
        x, z = i//7, i%7
        h = 2 + log1p(day['count']) / log1p(peak) * 85
        out.append(f'<g><title>{day["date"]}: {day["count"]} contributions</title>')
        out.append(face([(x,z,h),(x,z+.8,h),(x,z+.8,0),(x,z,0)], '#365329' if day['count'] else '#1c2a21'))
        out.append(face([(x,z+.8,h),(x+.8,z+.8,h),(x+.8,z+.8,0),(x,z+.8,0)], '#608837' if day['count'] else '#223327'))
        out.append(face([(x,z,h),(x+.8,z,h),(x+.8,z+.8,h),(x,z+.8,h)], colors[day['level']]))
        out.append('</g>')
    out.append('</svg>')
    return ''.join(out)
