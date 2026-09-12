#!/usr/bin/env python3
"""Injects the extracted SSCORP lettering (tools/build_assets.py → sscorp_lettering.json) into the template."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(sys.argv[1]))
tpl = open(os.path.join(ROOT, 'tools', 'templates', 'sscorp.html')).read()
def sub(m):
    page, name = m.group(1), m.group(2)
    return data[page]['groups'][name]['svg']
html = re.sub(r'\{\{group:(\d):([a-z0-9-]+)\}\}', sub, tpl)
assert '{{' not in html
open(os.path.join(ROOT, 'sscorp.io', 'index.html'), 'w').write(html)
print('sscorp.io/index.html', f'{len(html)/1024:.0f}KB')
