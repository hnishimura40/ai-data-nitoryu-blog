import os, shutil, re

SRC_DIR  = r'D:\documents\動画作成関連\野球'
SITE_DIR = r'D:\aiwork\claude\hanshin-keiba'

ILLUST_HTML = (
    '\n  <!-- ===== ILLUSTRATION ===== -->\n'
    '  <div class="art-illust-wrap">\n'
    '    <img src="illust.png" alt="記事イラスト" class="art-illust" loading="lazy">\n'
    '  </div>\n'
)

tasks = [
    ('2026.4.11.png', '2026-04-11-sato-chunichi',   'art-layout'),  # before <div class="art-layout">
    ('2026.4.14.png', '2026-04-14-giants-loss',      'main-content'),# before <div class="main-content">
]

for fname, folder, insert_before in tasks:
    src = os.path.join(SRC_DIR, fname)
    art_dir = os.path.join(SITE_DIR, folder)

    if not os.path.exists(src):
        print(f'  NO IMAGE: {src}')
        continue

    # Copy image
    dst = os.path.join(art_dir, 'illust.png')
    shutil.copy2(src, dst)
    print(f'  Copied {fname} -> {folder}/illust.png')

    # Update HTML
    html_path = os.path.join(art_dir, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'art-illust-wrap' in html:
        print(f'  SKIP HTML (already has illust): {folder}')
        continue

    if insert_before == 'art-layout':
        # Insert before first <div class="art-layout">
        pat = re.compile(r'(\s*<div class="art-layout")')
        new_html, n = pat.subn(ILLUST_HTML + r'\1', html, count=1)
    else:
        # Insert before <!-- ===== MAIN CONTENT ===== --> or <div class="main-content">
        pat = re.compile(r'(\s*(?:<!--[^>]*MAIN CONTENT[^>]*-->\s*)?<div class="main-content")')
        new_html, n = pat.subn(ILLUST_HTML + r'\1', html, count=1)

    if n == 0:
        print(f'  WARN: insert pattern not found in {folder}')
        continue

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  HTML updated: {folder}')

print('Done.')
