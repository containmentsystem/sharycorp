#!/usr/bin/env python3
"""
Builds sscorp.io from the client package "Assets – Updated":

  reference.png                          layout reference (3 phone tiles)
  SSCORP Layout – Mobile_Text 1.svg      tile 1 lettering (over the portrait video)
  SSCORP Layout – Mobile_Text 2a.svg     "Someone who gets sh*t done!"
  SSCORP Layout – Mobile_Text 2b.svg     "CV download"
  SSCORP Layout – Mobile_Text 3.svg      tile 3 lettering (portals + contact)
  180924_new matrix_01 … .mp4            portrait loop (1080x1920, 5 s)
  PFPixelscriptPro.ttf, SyneMono-Regular.ttf

Outlined lettering is inlined into the template as grouped <path>s (fills pulled
from each SVG's own stylesheet, coordinates rounded to 0.1 unit); live <text>
runs stay live and render with the subsetted PF Pixelscript Pro webfont.

    PYTHONPATH=.pylib python3 tools/build_sscorp.py          # needs ffmpeg on PATH
"""
import glob, json, os, re, shutil, subprocess, sys
from fontTools import subset
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = glob.glob(os.path.join(ROOT, 'Assets*Updated'))[0]      # folder name has an en-dash
OUT = os.path.join(ROOT, 'sscorp.io')
TPL = os.path.join(ROOT, 'tools', 'templates', 'sscorp.html')

def asset(pattern):
    hits = glob.glob(os.path.join(ASSETS, pattern))
    if not hits: raise SystemExit('missing asset: ' + pattern)
    return hits[0]

def kb(path): return f'{os.path.getsize(path)/1024:.0f}KB'

# ---------------------------------------------------------------- lettering
TOK = re.compile(r'[A-Za-z]|-?\d*\.?\d+(?:e-?\d+)?')

def compact(d):
    """Re-emits path data with coordinates rounded to 0.1 unit. Tokenised rather than
    regex-substituted because Illustrator writes '4.7.5' for the two numbers 4.7 and .5."""
    out, prev_num = [], False
    for t in TOK.findall(d):
        if t.isalpha(): out.append(t); prev_num = False; continue
        n = f'{float(t):.1f}'.rstrip('0').rstrip('.')
        if n in ('-0', ''): n = '0'
        out.append((',' if prev_num and not n.startswith('-') else '') + n); prev_num = True
    return ''.join(out)

def load_svg(path):
    """Returns (viewBox, [ (fill, d) … in document order ], [ text runs ])."""
    src = open(path, encoding='utf-8').read()
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    style = re.search(r'<style>(.*?)</style>', src, re.S)
    rules = {}
    if style:
        for sel, body in re.findall(r'([^{}]+)\{([^}]*)\}', style.group(1)):
            props = dict(kv.split(':', 1) for kv in (x.strip() for x in body.split(';')) if kv)
            for s in sel.split(','):
                rules.setdefault(s.strip().lstrip('.'), {}).update({k.strip(): v.strip() for k, v in props.items()})
    def cls(attrs):
        m = re.search(r'class="([^"]+)"', attrs); return rules.get(m.group(1), {}) if m else {}
    paths = []
    for m in re.finditer(r'<path\b([^>]*?)/?>', src):
        attrs = m.group(1)
        d = compact(re.search(r'\sd="([^"]+)"', attrs).group(1))
        paths.append((cls(attrs).get('fill', '#000'), d))
    texts = []
    for m in re.finditer(r'<text\b([^>]*)>\s*<tspan[^>]*>(.*?)</tspan>\s*</text>', src, re.S):
        attrs, content = m.groups(); r = cls(attrs)
        tr = re.search(r'translate\(([^)]+)\)', attrs).group(1).split()
        texts.append(dict(x=float(tr[0]), y=float(tr[1]), size=float(r['font-size'].rstrip('px')), fill=r['fill'], text=content))
    return vb, paths, texts

def group(paths, idx):
    return ''.join(f'<path fill="{paths[i][0]}" d="{paths[i][1]}"/>' for i in idx)

def text_el(t, cls):
    return (f'<text class="{cls}" x="{t["x"]:.1f}" y="{t["y"]:.1f}" font-size="{t["size"]:g}" fill="{t["fill"]}">'
            f'{t["text"]}</text>')

def lettering():
    vb1, p1, t1 = load_svg(asset('*Mobile_Text 1.svg'))
    vb2a, p2a, _ = load_svg(asset('*Mobile_Text 2a.svg'))
    vb2b, p2b, _ = load_svg(asset('*Mobile_Text 2b.svg'))
    vb3, p3, t3 = load_svg(asset('*Mobile_Text 3.svg'))
    assert len(p1) == 66 and len(p3) == 80, (len(p1), len(p3))     # layout files as delivered 2026-09-28
    T3 = {t['text']: t for t in t3}
    amp = t1[0]
    return {
        'vb1': vb1, 'vb2a': vb2a, 'vb2b': vb2b, 'vb3': vb3,
        # tile 1 — document order: Sharon Shum · creative ops specialist · is Online (+ ♀, ✳) · renegade performance artist · &
        '1:sharon-shum':  group(p1, range(0, 10)),
        '1:creative-ops': group(p1, range(10, 31)) + text_el(amp, 'pf'),
        '1:is-online':    group(p1, range(31, 41)),
        '1:renegade':     group(p1, range(41, 66)),
        # tile 2
        '2:someone':      group(p2a, range(len(p2a))),
        '2:cv-download':  group(p2b, range(len(p2b))),
        # tile 3 — SS · is Online · me@SScorp.iO · WWW · dots · MMM · creative ops · renegade
        '3:ss':           group(p3, range(0, 2)),
        '3:is-online':    group(p3, range(2, 12)),
        '3:me-at-sscorp': group(p3, range(12, 24)),
        '3:www':          group(p3, range(24, 27)),
        '3:dots':         group(p3, [27, 28, 29, 33]),
        '3:mmm':          group(p3, range(30, 33)),
        '3:creative-ops': group(p3, range(34, 55)),
        '3:renegade':     group(p3, range(55, 80)),
        '3:contact':      text_el(T3['contact'], 'pf'),
        '3:swiim-ing':    text_el(T3['swiim.ing'], 'pf'),
        '3:shary-fyi':    text_el(T3['shary.fyi'], 'pf'),
    }

# ---------------------------------------------------------------- fonts
UNICODES = 'U+0020-007E,U+00A0-00FF,U+2018-201D,U+2026,U+2013,U+2014,U+2022'

def subset_font(src, dst):
    opts = subset.Options(); opts.flavor = 'woff2'; opts.layout_features = ['*']; opts.name_IDs = ['*']
    opts.notdef_outline = True; opts.desubroutinize = True
    font = subset.load_font(src, opts); s = subset.Subsetter(opts)
    s.populate(unicodes=subset.parse_unicodes(UNICODES)); s.subset(font)
    os.makedirs(os.path.dirname(dst), exist_ok=True); subset.save_font(font, dst, opts)
    print('  font', os.path.basename(dst), kb(dst))

def fonts():
    subset_font(asset('PFPixelscriptPro.ttf'), os.path.join(OUT, 'fonts', 'PFPixelscriptPro.woff2'))
    subset_font(asset('SyneMono-Regular.ttf'), os.path.join(OUT, 'fonts', 'SyneMono-Regular.woff2'))

# ---------------------------------------------------------------- portrait loop
def video():
    src = asset('*.mp4'); img = os.path.join(OUT, 'img'); os.makedirs(img, exist_ok=True)
    if not shutil.which('ffmpeg'):
        print('  ffmpeg not found — keeping existing img/portrait.*'); return
    common = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-an', '-vf', 'scale=720:1280']
    subprocess.check_call(common + ['-c:v', 'libx264', '-profile:v', 'main', '-pix_fmt', 'yuv420p', '-crf', '26', '-preset', 'slow',
                                    '-g', '48', '-movflags', '+faststart', os.path.join(img, 'portrait.mp4')])
    subprocess.check_call(common + ['-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '34', '-row-mt', '1', '-deadline', 'good',
                                    os.path.join(img, 'portrait.webm')])
    poster = os.path.join(img, 'portrait-poster.png')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', src, '-frames:v', '1', '-vf', 'scale=720:1280', poster])
    im = Image.open(poster).convert('RGB')
    im.save(os.path.join(img, 'portrait-poster.webp'), quality=80, method=6)
    im.save(os.path.join(img, 'portrait-poster.jpg'), quality=82, optimize=True, progressive=True)   # og:image — link scrapers don't all take WebP
    os.remove(poster)
    for f in ('portrait.mp4', 'portrait.webm', 'portrait-poster.webp', 'portrait-poster.jpg'): print('  video', f, kb(os.path.join(img, f)))

# ---------------------------------------------------------------- assemble
def favicon(groups):
    # the SS monogram from tile 3 (its paths sit at 6,5 – 151,246 in the layout's units), on black
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-52 -5 261 261"><rect x="-52" y="-5" width="261" height="261" fill="#000"/>'
           + groups['3:ss'] + '</svg>')
    open(os.path.join(OUT, 'favicon.svg'), 'w', encoding='utf-8').write(svg); print('  favicon.svg', f'{len(svg)/1024:.0f}KB')

def assemble(groups):
    favicon(groups)
    tpl = open(TPL, encoding='utf-8').read()
    html = re.sub(r'\{\{([0-9a-z:-]+)\}\}', lambda m: groups[m.group(1)], tpl)
    assert '{{' not in html
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
    print('  sscorp.io/index.html', f'{len(html)/1024:.0f}KB')

if __name__ == '__main__':
    steps = sys.argv[1:] or ['fonts', 'video', 'html']
    if 'fonts' in steps: fonts()
    if 'video' in steps: video()
    if 'html' in steps: assemble(lettering())
