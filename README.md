# SSCORP.io · SWIIM.ing · SHARY.fyi

Three mobile-first static sites built from the client packages `SSCORP-SWIIM-SHARY WEBSITE/`
(swiim.ing / shary.fyi: layout `.ai`/`.pdf` files, the copy `.docx`, fonts, logos, photos) and
`Assets – Updated/` (sscorp.io: `reference.png`, the four `SSCORP Layout – Mobile_Text *.svg` lettering
files, the portrait loop `.mp4`, PF Pixelscript Pro and Syne Mono). No framework, no build step at
deploy time — each folder is self-contained and deploys to its own domain.

| Folder       | Domain      | What it is |
|--------------|-------------|------------|
| `sscorp.io/` | sscorp.io   | Three phone tiles (portrait loop · bio · portals) from `Assets – Updated/reference.png`; stacked with scroll-snap on phones, side by side from 900 px. Lettering is the delivered SVG vectors; `swiim.ing`, `shary.fyi`, `contact` and `&` are live text in PF Pixelscript Pro. |
| `swiim.ing/` | swiim.ing   | Splash → home → About / Values / Clients / Services / Contact (hash routes `#about` …). |
| `shary.fyi/` | shary.fyi   | "Swimdom XP" desktop: boot screen, icons, windows (My Bio, Output, System, SWM Messenger, Swimnet Explorer), CV/Portfolio dialog, start bar. |
| `index.html` | —           | Redirects to `sscorp.io/`, the hub. Its handwritten SWIIM.ING / SHARY×FYI lettering links to the other two sites (live domains in production, sibling folders when previewed locally). |

## Preview locally

```bash
python3 -m http.server 8788 --bind 127.0.0.1
```

then open <http://127.0.0.1:8788/> (lands on sscorp.io, the hub).

## Regenerating assets

`tools/build_sscorp.py` builds sscorp.io from `Assets – Updated/`: subsets the two fonts to WOFF2, re-encodes the
portrait loop (720×1280 H.264 + VP9, ~1 MB / 0.6 MB, plus a WebP poster) and inlines the lettering SVGs into
`tools/templates/sscorp.html` → `sscorp.io/index.html` (edit the template, not the output). Needs `ffmpeg` on PATH
for the video step; `html` alone is fast:

```bash
python3 -m pip install --target .pylib pymupdf pillow fonttools brotli
PYTHONPATH=.pylib python3 tools/build_sscorp.py            # fonts video html
PYTHONPATH=.pylib python3 tools/build_sscorp.py html       # template change only
```

`tools/build_assets.py` rebuilds the swiim.ing / shary.fyi assets from `SSCORP-SWIIM-SHARY WEBSITE/`:
WOFF2 font subsets, WebP + JPEG photo renditions (1600 / 800 px), backgrounds, the 3D avatar,
metadata-stripped SVGs, the outlined Swimdom XP lockup, and copies the SSCORP CV.
`swiim.ing/index.html` is generated from `tools/templates/swiim.html` + `swiim.ing/img/work/manifest.json`.

```bash
PYTHONPATH=.pylib python3 tools/build_assets.py /tmp/shary-build
```

## Things to edit later (all plain text in the HTML)

* **Contact forms** — `FORM_ENDPOINT` in `swiim.ing/index.html` and `shary.fyi/index.html`.
  Empty = the form opens the visitor's mail app pre-filled (ss@swiim.ing / fairy@shary.fyi).
* **Selected works** — `WORKS` array in `shary.fyi/index.html` (titles from the copy doc; descriptions and media are placeholders).
* **Downloads** — `shary.fyi/files/Sharyfairy-Artist-CV.pdf` and `Sharyfairy-Portfolio.pdf` are not in the package yet
  (paths set in `DOWNLOADS`). `sscorp.io/files/Sharon-Shum-CV.pdf` is the résumé from `ARCHIVE/Website/File Links/`.
* **Announcements note** — the yellow sticky in `shary.fyi/index.html`. Set in VG Aldiviva Primavera (light lines) and Estate (bold lines), taken from the *trial* fonts in `ARCHIVE/Fonts/_SHARON_SHARYFAIRY FONTS.zip` — check licensing before launch.
* **Email links** — `me@sscorp.io` (SSCORP "me@SScorp.iO"), `ss@swiim.ing`, `fairy@shary.fyi`.
* **SSCORP bio copy** — the five `<p>`s in `tools/templates/sscorp.html` (transcribed from `reference.png`), then `tools/build_sscorp.py html`.

## Test deployment on GitHub Pages (one domain)

Push the repo and enable Pages for the `main` branch (root). The site comes up at `https://<user>.github.io/<repo>/`:
the root `index.html` redirects to `sscorp.io/`, and the handwritten portals / Swimnet Explorer links resolve to the
sibling folders (`swiim.ing/`, `shary.fyi/`) automatically whenever the sites are served from their folder names.
`.nojekyll` keeps GitHub from running Jekyll over the files. Both client packages are git-ignored and never pushed
(the push is ~17 MB).

## Launch checklist (real domains)

Deploy each site folder to its own domain (any static host: Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3…).
Only the three site folders are needed — not `SSCORP-SWIIM-SHARY WEBSITE/`, `tools/`, `.claude/` or the root `index.html`.

* Cross-site links (`https://swiim.ing`, `https://shary.fyi`, `https://sscorp.io`) are absolute in production;
  they switch to sibling folders only while the sites are co-hosted under their folder names (local / GitHub Pages).
* Set `FORM_ENDPOINT` in `swiim.ing/index.html` and `shary.fyi/index.html` if you want form posts instead of mail-app hand-off.
* Add `shary.fyi/files/Sharyfairy-Artist-CV.pdf` and `Sharyfairy-Portfolio.pdf` when available — until then the download
  dialog shows "Not available yet" instead of a 404.
* Confirm `me@sscorp.io`, `ss@swiim.ing` and `fairy@shary.fyi` mailboxes exist.
* VG Aldiviva on shary.fyi is a *trial* font from the archive zip — check the licence before going live.
* Serve with gzip/brotli (SVG and HTML compress ~4×) and long cache headers for `/img`, `/svg`, `/fonts`.
* The sscorp.io portrait loop is cut from `180924_new matrix_01 – working file not final export.mp4`. When the final
  export arrives, drop it in `Assets – Updated/` and run `tools/build_sscorp.py video` — nothing else changes.
* sscorp.io: the loop pauses off-screen and stays on its poster frame under `prefers-reduced-motion`.
