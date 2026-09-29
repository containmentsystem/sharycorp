#!/usr/bin/env python3
"""
Regenerates the optimised web assets for swiim.ing and shary.fyi (plus the SSCORP CV) from the
reference folder "SSCORP-SWIIM-SHARY WEBSITE".  sscorp.io itself is built by tools/build_sscorp.py.
Requires: pymupdf, pillow, fonttools, brotli.

    PYTHONPATH=<libs> python3 tools/build_assets.py
"""
import io, json, os, re, sys, glob, math
import pymupdf
from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, 'SSCORP-SWIIM-SHARY WEBSITE')
SSCORP, SWIIM, SHARY = (os.path.join(ROOT, d) for d in ('sscorp.io', 'swiim.ing', 'shary.fyi'))
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'tools', '_build')

def out(*p):
    path = os.path.join(*p); os.makedirs(os.path.dirname(path), exist_ok=True); return path

def rp(*p):  # reference path, tolerant of the en-dashes in folder names
    return os.path.join(REF, *p)

def find(pattern):
    hits = glob.glob(os.path.join(REF, '**', pattern), recursive=True)
    if not hits: raise SystemExit('missing reference file: ' + pattern)
    return hits[0]

def kb(path): return f'{os.path.getsize(path)/1024:.0f}KB'

# ---------------------------------------------------------------- fonts
UNICODES = ('U+0020-007E,U+00A0-00FF,U+0152-0153,U+0190,U+02C6,U+02DC,U+2013-2014,U+2018-201A,'
            'U+201C-201E,U+2022,U+2026,U+2030,U+2039-203A,U+2190-2193,U+2122,U+00D7')

def subset_font(src, dst, keep_variable=True):
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = ['*']
    opts.name_IDs = ['*']
    opts.notdef_outline = True
    opts.desubroutinize = True
    font = subset.load_font(src, opts)
    s = subset.Subsetter(opts)
    s.populate(unicodes=subset.parse_unicodes(UNICODES))
    s.subset(font)
    subset.save_font(font, out(dst), opts)
    print('  font', os.path.basename(dst), kb(dst))

def fonts():
    print('fonts')
    subset_font(find('Manrope-VariableFont_wght.ttf'), os.path.join(SWIIM, 'fonts', 'Manrope-VF.woff2'))
    subset_font(find('SyneMono-Regular.ttf'), os.path.join(SWIIM, 'fonts', 'SyneMono-Regular.woff2'))
    subset_font(find('Groteska-Regular.ttf'), os.path.join(SWIIM, 'fonts', 'Groteska-Regular.woff2'))
    subset_font(find('Astloch-Regular.ttf'), os.path.join(SHARY, 'fonts', 'Astloch-Regular.woff2'))
    subset_font(find('Astloch-Bold.ttf'), os.path.join(SHARY, 'fonts', 'Astloch-Bold.woff2'))
    subset_font(find('SpaceMono-Regular.ttf'), os.path.join(SHARY, 'fonts', 'SpaceMono-Regular.woff2'))
    subset_font(find('SpaceMono-Bold.ttf'), os.path.join(SHARY, 'fonts', 'SpaceMono-Bold.woff2'))
    subset_font(find('Helvetica Neue 67 Medium Condensed.otf'), os.path.join(SHARY, 'fonts', 'HelveticaNeue-MedCond.woff2'))
    # VG Aldiviva (sticky note) only exists inside ARCHIVE/Fonts/_SHARON_SHARYFAIRY FONTS.zip
    import zipfile, tempfile
    z = zipfile.ZipFile(find('_SHARON_SHARYFAIRY FONTS.zip'))
    with tempfile.TemporaryDirectory() as td:
        for cut in ('Estate', 'Primavera'):
            name = [n for n in z.namelist() if n.endswith(f'VGAldivivaTrial-{cut}.otf') and '__MACOSX' not in n][0]
            src = z.extract(name, td)
            subset_font(src, os.path.join(SHARY, 'fonts', f'VGAldiviva-{cut}.woff2'))

# ---------------------------------------------------------------- images
def save_img(im, base, widths, quality=82, webp_only=False):
    for w in widths:
        r = im.copy()
        if r.width > w:
            r.thumbnail((w, int(w * 4)), Image.LANCZOS)
        suffix = '' if len(widths) == 1 else f'-{w}'
        p = out(base + suffix + '.webp'); r.save(p, 'WEBP', quality=quality, method=6); print('  ', os.path.basename(p), r.size, kb(p))
        if not webp_only:
            p = out(base + suffix + '.jpg'); r.convert('RGB').save(p, 'JPEG', quality=quality, optimize=True, progressive=True); print('  ', os.path.basename(p), kb(p))

def pdf_image(doc, xref):
    pix = pymupdf.Pixmap(doc, xref)
    if pix.n - pix.alpha >= 4: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return Image.open(io.BytesIO(pix.tobytes('png')))

def images():
    print('images')
    # SWIIM past-work photos
    photos = sorted(glob.glob(os.path.join(REF, '2. SWIIM.ing', '*Past Work*', '*')))
    manifest = []
    for p in photos:
        slug = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(os.path.basename(p))[0].lower()).strip('-')
        im = Image.open(p); im = im.convert('RGB')
        try:
            from PIL import ImageOps; im = ImageOps.exif_transpose(im)
        except Exception: pass
        save_img(im, os.path.join(SWIIM, 'img', 'work', slug), [1600, 800], quality=78)
        manifest.append({'slug': slug, 'w': im.width, 'h': im.height, 'src': os.path.basename(p)})
    json.dump(manifest, open(out(SWIIM, 'img', 'work', 'manifest.json'), 'w'), indent=1)
    # SHARY backgrounds + avatar
    d = pymupdf.open(find('SHARYFYI Layout.pdf'))
    desk = Image.open(find('SHARYFYI BG Desktop.png')).convert('RGB')
    save_img(desk, os.path.join(SHARY, 'img', 'bg-desktop'), [2200, 1400], quality=78)
    # mobile background: page 3 places a 2048x1547 image at bbox (-1776,-1,1615,2560) on a 1173x2556 page
    info = [i for i in d[3].get_image_info(xrefs=True) if i['xref']][0]
    mob = pdf_image(d, info['xref'])
    bx0, by0, bx1, by1 = info['bbox']
    sx = mob.width / (bx1 - bx0); sy = mob.height / (by1 - by0)
    crop = mob.crop((int((0 - bx0) * sx), int((0 - by0) * sy), int((1173 - bx0) * sx), int((2556 - by0) * sy)))
    save_img(crop, os.path.join(SHARY, 'img', 'bg-mobile'), [900], quality=78)
    av = Image.open(find('Shyfy 3d placeholder_1.png')).convert('RGBA')
    save_img(av, os.path.join(SHARY, 'img', 'avatar'), [1100, 600], quality=86, webp_only=True)
    # messenger profile picture = square crop of the avatar's head
    head = av.crop((520, 40, 1480, 1000)); head.thumbnail((240, 240)); head.save(out(SHARY, 'img', 'avatar-head.webp'), 'WEBP', quality=86)

# ---------------------------------------------------------------- svg assets
def clean_svg(src, strip_text=False):
    s = open(src, encoding='utf-8').read()
    s = re.sub(r'<metadata>.*?</metadata>', '', s, flags=re.S)
    s = re.sub(r'\s+xmlns:c2pa="[^"]*"', '', s)
    s = re.sub(r'<\?xml[^>]*\?>\s*', '', s)
    if strip_text:
        s = re.sub(r'<text\b.*?</text>', '', s, flags=re.S)
    s = re.sub(r'>\s+<', '><', s)
    return s.strip()

def svgs():
    print('svgs')
    copies = {
        # SWIIM
        ('SW!M Logomark*Green.svg', SWIIM, 'logomark-green.svg', False),
        ('SW!M Logomark*Blue.svg', SWIIM, 'logomark-blue.svg', False),
        ('SW!M Logo*Text only*Blue.svg', SWIIM, 'wordmark-blue.svg', False),
        ('SW!M Button*Green.svg', SWIIM, 'button-green.svg', False),
        ('Aptos-Network-Full-Logo-Black-RGB.svg', SWIIM, 'client-aptos.svg', False),
        ('Chaos Labs Colored Light horizontal.svg', SWIIM, 'client-chaos-labs.svg', False),
        ('IRL-LogoBlack-knockout.svg', SWIIM, 'client-irl.svg', False),
        ('REFRACTION LOGO*.svg', SWIIM, 'client-refraction.svg', False),
        ('WalletConnect Lockup.svg', SWIIM, 'client-walletconnect.svg', False),
        # SHARY
        ('! Security.svg', SHARY, 'icon-security.svg', True),
        ('Artist CV.svg', SHARY, 'icon-artist-cv.svg', True),
        ('Portfolio.svg', SHARY, 'icon-portfolio.svg', True),
        ('Mail.svg', SHARY, 'icon-mail.svg', True),
        ('My Bio.svg', SHARY, 'icon-my-bio.svg', True),
        ('Output.svg', SHARY, 'icon-output.svg', True),
        ('System.svg', SHARY, 'icon-system.svg', True),
        ('SWM Messenger.svg', SHARY, 'icon-swm-messenger.svg', True),
        ('Swimnet Explorer.svg', SHARY, 'icon-swimnet-explorer.svg', True),
        ('Copyright SSCORP.svg', SHARY, 'copyright-sscorp.svg', False),
        ('Fairyhard.svg', SHARY, 'fairyhard.svg', False),
        ('Start Bar*Mobile.svg', SHARY, 'startbar-mobile.svg', True),
        ('Start Bar*Desktop.svg', SHARY, 'startbar-desktop.svg', True),
    }
    for pat, site, name, strip in sorted(copies):
        s = clean_svg(find(pat), strip)
        p = out(site, 'svg', name); open(p, 'w').write(s); print('  ', name, kb(p))
    # Swimdom XP boot lockup: the SVG asset references the missing "VG Aldiviva" font, so
    # take the fully outlined version from the layout PDF (page 0) instead.
    d = pymupdf.open(find('SHARYFYI Layout.pdf'))
    page = d[0]
    svg = page.get_svg_image(text_as_path=True)
    # drop the page background rect (fill #0f001e) and crop the viewBox to the lockup
    svg = re.sub(r'<path[^>]*fill="#0f001e"[^>]*/>', '', svg)
    drs = [x for x in page.get_drawings() if not (x['rect'].width > 1900)]
    rects = [x['rect'] for x in drs] + [pymupdf.Rect(b['bbox']) for b in page.get_text('dict')['blocks']]
    # lockup = everything in the upper 75% of the page (the loading bar and footer are rebuilt in CSS)
    rects = [r for r in rects if r.y1 < 800]
    x0 = min(r.x0 for r in rects) - 4; y0 = min(r.y0 for r in rects) - 4
    x1 = max(r.x1 for r in rects) + 4; y1 = max(r.y1 for r in rects) + 4
    svg = re.sub(r'width="[^"]*" height="[^"]*" viewBox="[^"]*"',
                 f'viewBox="{x0:.1f} {y0:.1f} {x1-x0:.1f} {y1-y0:.1f}"', svg, count=1)
    svg = re.sub(r'<\?xml[^>]*\?>\s*', '', svg)
    svg = re.sub(r'(\d+\.\d)\d+', r'\1', svg)
    p = out(SHARY, 'svg', 'swimdom-xp-lockup.svg'); open(p, 'w').write(svg); print('   swimdom-xp-lockup.svg', kb(p), 'box', (round(x0), round(y0), round(x1), round(y1)))

# ---------------------------------------------------------------- files
def files():
    print('files')
    import shutil
    src = find('SHARON SHUM RESUME.pdf')
    dst = out(SSCORP, 'files', 'Sharon-Shum-CV.pdf'); shutil.copy(src, dst); print('  ', os.path.basename(dst), kb(dst))

if __name__ == '__main__':
    steps = sys.argv[2:] or ['fonts', 'images', 'svgs', 'files']
    for s in steps: globals()[s]()
