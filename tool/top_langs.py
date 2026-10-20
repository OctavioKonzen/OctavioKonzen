# Gera top-langs.svg: as linguagens de todos os repositórios (sem forks),
# pela quantidade de código, no mesmo visual dos outros cartões do README.
import json
import math
import os
import sys
import urllib.request

USER = os.environ.get('GH_USER', 'OctavioKonzen')
TOKEN = os.environ.get('GITHUB_TOKEN', '')
COLORS = {
    'Dart': '#00B4AB', 'JavaScript': '#F1E05A', 'Python': '#3572A5', 'CSS': '#663399',
    'HTML': '#E34C26', 'Kotlin': '#A97BFF', 'Shell': '#89E051', 'Java': '#B07219',
    'C': '#555555', 'C++': '#F34B7D', 'TypeScript': '#3178C6', 'Swift': '#F05138',
    'Nix': '#7E7EFF', 'C#': '#178600', 'Go': '#00ADD8', 'Rust': '#DEA584',
}
TOP = 6


def get(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', **({'Authorization': f'Bearer {TOKEN}'} if TOKEN else {})})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def languages():
    total = {}
    for repo in get(f'https://api.github.com/users/{USER}/repos?per_page=100&type=owner'):
        if repo['fork']:
            continue
        for lang, size in get(repo['languages_url']).items():
            total[lang] = total.get(lang, 0) + size
    return total


def svg(total):
    whole = sum(total.values()) or 1
    # As linguagens com menos de 1% do código entram juntas em "Outras".
    items = [kv for kv in sorted(total.items(), key=lambda kv: -kv[1]) if kv[1] / whole >= 0.01]
    items = items[:TOP]
    rest = whole - sum(v for _, v in items)
    items += [('Outras', rest)] if rest else []
    whole = sum(v for _, v in items) or 1
    w, h, cx, cy, r, stroke = 340, 200, 250, 110, 50, 20
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
             f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="4.5" fill="#0d1117" stroke="#e4e2e2" stroke-opacity="0.2"/>',
             '<text x="30" y="40" font-family="Segoe UI, Ubuntu, sans-serif" font-size="22" fill="#58a6ff">Top Languages by Code</text>']
    angle = -math.pi / 2
    for i, (lang, size) in enumerate(items):
        color = COLORS.get(lang, '#8b949e')
        frac = size / whole
        y = 68 + i * 18
        parts.append(f'<rect x="30" y="{y - 10}" width="12" height="12" fill="{color}"/>')
        parts.append(f'<text x="48" y="{y}" font-family="Segoe UI, Ubuntu, sans-serif" font-size="13" fill="#c3d1d9">{lang} {frac * 100:.1f}%</text>')
        if frac >= 0.9999:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}"/>')
            continue
        end = angle + frac * 2 * math.pi
        x1, y1 = cx + r * math.cos(angle), cy + r * math.sin(angle)
        x2, y2 = cx + r * math.cos(end), cy + r * math.sin(end)
        large = 1 if frac > 0.5 else 0
        parts.append(f'<path d="M{x1:.2f} {y1:.2f} A{r} {r} 0 {large} 1 {x2:.2f} {y2:.2f}" fill="none" stroke="{color}" stroke-width="{stroke}"/>')
        angle = end
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


if __name__ == '__main__':
    data = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else languages()
    open('top-langs.svg', 'w').write(svg(data))
