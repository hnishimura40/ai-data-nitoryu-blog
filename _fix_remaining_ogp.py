"""残り2記事の ogp-hero をイラスト img に置換（role属性付きパターン対応）"""
import os, re

HANSHIN = r'D:\aiwork\claude\hanshin-keiba'

def replace_ogp_hero_flexible(html):
    """class="ogp-hero" を含む開きタグ（他属性あり可）を対象に除去"""
    # 開始タグを正規表現で探す
    pat_start = re.compile(r'<div\s[^>]*class="ogp-hero"[^>]*>')
    m = pat_start.search(html)
    if not m:
        return html, False

    start = m.start()
    pos = m.end()
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

    img = '  <img src="illust.png" alt="サムネイル" class="art-thumb-img" loading="lazy">\n'
    return html[:start] + img + html[pos:], True


folders = ['2026-04-04-kimura-carp', '2026-04-08-yakult-loss']

for folder in folders:
    path = os.path.join(HANSHIN, folder, 'index.html')
    with open(path, encoding='utf-8') as f:
        html = f.read()

    html, ok = replace_ogp_hero_flexible(html)
    print(f'  {"SWAPPED" if ok else "FAILED"}: {folder}')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
