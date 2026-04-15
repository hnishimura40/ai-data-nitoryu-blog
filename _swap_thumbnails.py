"""
サムネイル差し替えスクリプト
1. 各記事内: ogp-hero CSS カード → illust.png に置換 + art-illust-wrap 削除
2. hanshin-keiba/index.html: 一覧サム → illust.png
3. index.html(トップ): カードサム → illust.png
"""

import os, re

SITE = r'D:\aiwork\claude'
HANSHIN = os.path.join(SITE, 'hanshin-keiba')

# ─────────────────────────────────────────────
# ユーティリティ: ogp-hero div をネスト考慮で除去
# ─────────────────────────────────────────────
def replace_ogp_hero(html):
    start_tag = '<div class="ogp-hero">'
    start = html.find(start_tag)
    if start == -1:
        return html, False

    pos = start + len(start_tag)
    depth = 1
    while depth > 0 and pos < len(html):
        nxt_open  = html.find('<div', pos)
        nxt_close = html.find('</div>', pos)
        if nxt_close == -1:
            return html, False
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + 4
        else:
            depth -= 1
            pos = nxt_close + 6

    img = '    <img src="illust.png" alt="サムネイル" class="art-thumb-img" loading="lazy">\n'
    return html[:start] + img + html[pos:], True


def remove_illust_wrap(html):
    pat = re.compile(
        r'\s*<!-- ===== ILLUSTRATION ===== -->\s*'
        r'<div class="art-illust-wrap">.*?</div>',
        re.DOTALL
    )
    return pat.sub('', html)


# ─────────────────────────────────────────────
# 1. 各記事 index.html の ogp-hero 置換
# ─────────────────────────────────────────────
WITH_ILLUST = [
    '2026-03-29-12-6-giants',
    '2026-03-31-saiki-dena',
    '2026-04-01-lucas-dena',
    '2026-04-02-kimura-dena',
    '2026-04-03-murakami-hiroshima',
    '2026-04-04-kimura-carp',
    '2026-04-05-hiroshima-loss',
    '2026-04-07-saiki-yakult',
    '2026-04-08-yakult-loss',
    '2026-04-09-ibaraki-yakult',
    '2026-04-10-maekawa-chunichi',
    '2026-04-11-sato-chunichi',
    '2026-04-12-haruto-chunichi',
    '2026-04-14-giants-loss',
]

for folder in WITH_ILLUST:
    path = os.path.join(HANSHIN, folder, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    html, swapped = replace_ogp_hero(html)
    html = remove_illust_wrap(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  {"SWAPPED" if swapped else "no ogp-hero"}: {folder}')


# ─────────────────────────────────────────────
# 2. hanshin-keiba/index.html 一覧サム置換
# ─────────────────────────────────────────────
LIST_PATH = os.path.join(HANSHIN, 'index.html')
with open(LIST_PATH, encoding='utf-8') as f:
    html = f.read()

# 各 article-list-item の thumb を img に置換
# パターン: href="FOLDER/..." の直後の article-list-thumb div
pat_item = re.compile(
    r'(<a href="([^"]+)/index\.html" class="article-list-item">)\s*'
    r'<div class="article-list-thumb[^"]*">[^<]*</div>',
    re.DOTALL
)

def list_thumb_replacer(m):
    full_a = m.group(1)
    folder = m.group(2)
    illust = os.path.join(HANSHIN, folder, 'illust.png')
    if os.path.exists(illust):
        return (full_a + '\n            '
                '<div class="article-list-thumb">'
                f'<img src="{folder}/illust.png" alt="サムネイル" loading="lazy">'
                '</div>')
    return m.group(0)  # イラストなしはそのまま

new_html = pat_item.sub(list_thumb_replacer, html)
count = html.count('article-list-thumb') - new_html.count('sports-thumb')
with open(LIST_PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)
print(f'\n  List page updated ({count} thumbs swapped)')


# ─────────────────────────────────────────────
# 3. index.html トップページ カードサム置換
# ─────────────────────────────────────────────
TOP_PATH = os.path.join(SITE, 'index.html')
with open(TOP_PATH, encoding='utf-8') as f:
    html = f.read()

# パターン: href="hanshin-keiba/FOLDER/" の直後の article-card-thumb div
pat_card = re.compile(
    r'(<a href="hanshin-keiba/([^/]+)/" class="article-card">)\s*'
    r'<div class="article-card-thumb[^"]*">[^<]*</div>',
    re.DOTALL
)

def card_thumb_replacer(m):
    full_a = m.group(1)
    folder = m.group(2)
    illust = os.path.join(HANSHIN, folder, 'illust.png')
    if os.path.exists(illust):
        return (full_a + '\n            '
                '<div class="article-card-thumb">'
                f'<img src="hanshin-keiba/{folder}/illust.png" alt="サムネイル" loading="lazy">'
                '</div>')
    return m.group(0)

new_html = pat_card.sub(card_thumb_replacer, html)
with open(TOP_PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)
print('  Top page card thumbs updated')
