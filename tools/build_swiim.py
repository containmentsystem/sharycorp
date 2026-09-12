#!/usr/bin/env python3
"""Renders swiim.ing/index.html from tools/templates/swiim.html + the optimised photo manifest."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
man = json.load(open(os.path.join(ROOT, 'swiim.ing', 'img', 'work', 'manifest.json')))
photos = [{'s': m['slug'], 'w': m['w'], 'h': m['h']} for m in man]
# six tiles laid out like the sketch (percent of the float box, 306×160)
TILES = [(8, 0, 25, 34), (60, 0, 20, 28), (38, 9, 22, 32), (10, 41, 39, 31), (33, 50, 29, 50), (56, 37, 32, 44)]
tiles = []
for t, (x, y, w, h) in enumerate(TILES):
    p = photos[t]
    tiles.append(f'''      <div class="tile" style="--x:{x}%;--y:{y}%;--w:{w}%;--h:{h}%;--ad:{t * 0.45:.2f}s;--gd:{t * 0.7:.1f}s" data-p="{t}">
        <button type="button" class="ph" aria-label="Past work photo, open full size"><img src="img/work/{p['s']}-800.webp" alt="SW!M past work — event photo {t + 1}" width="{p['w']}" height="{p['h']}" decoding="async"><img class="g g1" src="img/work/{photos[(t + 7) % len(photos)]['s']}-800.webp" alt="" aria-hidden="true" loading="lazy"><img class="g g2" src="img/work/{photos[(t + 13) % len(photos)]['s']}-800.webp" alt="" aria-hidden="true" loading="lazy"></button>
      </div>''')
tpl = open(os.path.join(ROOT, 'tools', 'templates', 'swiim.html')).read()
html = tpl.replace('{{TILES}}', '\n'.join(tiles)).replace('{{PHOTOS_JSON}}', json.dumps(photos, separators=(',', ':')))
assert '{{' not in html
open(os.path.join(ROOT, 'swiim.ing', 'index.html'), 'w').write(html)
print('swiim.ing/index.html', f'{len(html) // 1024}KB', len(photos), 'photos')
