import os
import shutil
import re

SRC_DIR  = r'D:\documents\動画作成関連\野球\_未整理\_画像'
SITE_DIR = r'D:\aiwork\claude\hanshin-keiba'

# date → article folder, prefer .png over .jpg
MAPPING = [
    ('2026.3.29',  '2026-03-29-12-6-giants'),
    ('2026.3.31',  '2026-03-31-saiki-dena'),
    ('2026.4.1',   '2026-04-01-lucas-dena'),
    ('2026.4.2',   '2026-04-02-kimura-dena'),
    ('2026.4.3',   '2026-04-03-murakami-hiroshima'),
    ('2026.4.4',   '2026-04-04-kimura-carp'),
    ('2026.4.5',   '2026-04-05-hiroshima-loss'),
    ('2026.4.7',   '2026-04-07-saiki-yakult'),
    ('2026.4.8',   '2026-04-08-yakult-loss'),
    ('2026.4.9',   '2026-04-09-ibaraki-yakult'),
    ('2026.4.10',  '2026-04-10-maekawa-chunichi'),
    ('2026.4.12',  '2026-04-12-haruto-chunichi'),
]

# Illustration HTML to insert before <div class="art-layout">
ILLUST_HTML = (
    '\n  <!-- ===== ILLUSTRATION ===== -->\n'
    '  <div class="art-illust-wrap">\n'
    '    <img src="illust.png" alt="記事イラスト" class="art-illust" loading="lazy">\n'
    '  </div>\n'
)

# Pattern to insert before art-layout
PAT_LAYOUT = re.compile(r'(\s*(?:<!--[^>]*-->)?\s*<div class="art-layout")')

copied  = []
updated = []
errors  = []

for date_str, folder in MAPPING:
    # Find source image (prefer .png)
    src_png = os.path.join(SRC_DIR, date_str + '.png')
    src_jpg = os.path.join(SRC_DIR, date_str + '.jpg')
    if os.path.exists(src_png):
        src = src_png
    elif os.path.exists(src_jpg):
        src = src_jpg
    else:
        errors.append(f'  NO IMAGE for {date_str} ({folder})')
        continue

    art_dir = os.path.join(SITE_DIR, folder)
    if not os.path.isdir(art_dir):
        errors.append(f'  NO DIR: {art_dir}')
        continue

    # Copy image as illust.png
    dst = os.path.join(art_dir, 'illust.png')
    shutil.copy2(src, dst)
    copied.append(f'  {date_str} → {folder}/illust.png  (from {os.path.basename(src)})')

    # Update HTML
    html_path = os.path.join(art_dir, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'art-illust-wrap' in html:
        updated.append(f'  SKIP (already has illust): {folder}')
        continue

    new_html, n = PAT_LAYOUT.subn(ILLUST_HTML + r'\1', html, count=1)
    if n == 0:
        # Fallback: insert before </main> if art-layout not found
        errors.append(f'  art-layout NOT FOUND in {folder}, skipping HTML update')
        continue

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    updated.append(f'  HTML updated: {folder}')

print(f'Copied {len(copied)} images:')
for m in copied: print(m)
print(f'\nUpdated {len(updated)} HTML files:')
for m in updated: print(m)
if errors:
    print(f'\nIssues ({len(errors)}):')
    for m in errors: print(m)
