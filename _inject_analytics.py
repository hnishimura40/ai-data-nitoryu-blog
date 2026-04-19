"""
全HTMLに GA4 タグと analytics.js を注入するスクリプト。
- <head> の </head> 直前に gtag + analytics.js を追加
- 記事ページの <body> に data-page-type / data-article-slug / data-article-category / data-article-title を付与
- 既に注入済みのHTMLはスキップ（冪等）
"""
import os, re, pathlib, html as htmlmod

ROOT = pathlib.Path(__file__).parent.resolve()

GA_ID = "G-XXXXXXXXXX"
MARKER = "<!-- GA4:ainitoryu -->"

# 競馬記事判定キーワード（hanshin-keiba/配下で true のものは keiba、それ以外は baseball）
KEIBA_KEYWORDS = [
    "keiba", "satsukisho", "derby", "oaks", "tenno", "arima",
    "kikka", "nhk-mile", "yushun", "hanshin-juvenile",
    "hansen",  # 開幕戦馬券？→ 実際はサイト内の分析。人手確認必要
]

# 上記では誤判定の可能性があるため、タイトル/本文ベースでの判定も併用
def is_keiba_article(path: pathlib.Path, html_text: str) -> bool:
    slug = path.parent.name
    s = slug.lower()
    # URLスラッグに明確な競馬ワード
    if any(k in s for k in ["satsukisho", "derby", "oaks", "tenno", "arima", "kikka"]):
        return True
    # タイトル/見出しから判定
    title_m = re.search(r"<title>([^<]+)</title>", html_text, re.I)
    h1_m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.I | re.S)
    blob = ((title_m.group(1) if title_m else "") + " " +
            (h1_m.group(1) if h1_m else ""))
    keiba_tokens = ["皐月賞", "ダービー", "オークス", "菊花賞", "天皇賞", "有馬記念",
                    "NHKマイル", "桜花賞", "G1", "GI ", "GⅠ", "競馬", "レース回顧",
                    "血統", "予想", "馬券", "中山2000", "東京芝", "阪神芝", "京都芝"]
    # 阪神タイガースの「阪神」との誤判定を避けるため、「阪神タイガース」「阪神戦」は除外シグナル
    baseball_tokens = ["阪神タイガース", "タイガース", "ヤクルト", "DeNA", "中日", "広島", "巨人",
                       "ジャイアンツ", "カープ", "スワローズ", "ベイスターズ", "ドラゴンズ",
                       "試合分析", "試合", "打線", "先発", "投手", "打撃", "ローテ"]
    bscore = sum(1 for t in baseball_tokens if t in blob)
    kscore = sum(1 for t in keiba_tokens if t in blob)
    return kscore > bscore

def detect_category(path: pathlib.Path, html_text: str):
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("economy-stocks/"):
        # カテゴリトップ/ページング以外は article
        return "economy"
    if rel.startswith("hanshin-keiba/"):
        return "keiba" if is_keiba_article(path, html_text) else "baseball"
    return "static_page"

def is_article_page(path: pathlib.Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    # カテゴリトップ / ページング / ルート系はarticleではない
    if rel in ("index.html", "mobile-test.html"): return False
    if rel.endswith("/index.html"):
        dir_rel = rel[:-len("/index.html")]
        # カテゴリトップ
        if dir_rel in ("hanshin-keiba", "economy-stocks", "channels", "contact",
                       "profile", "privacy-policy",
                       "hanshin-keiba/page2", "hanshin-keiba/analysis"):
            return False
        # article配下
        if dir_rel.startswith("hanshin-keiba/") or dir_rel.startswith("economy-stocks/"):
            return True
    return False

def extract_h1(html_text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.I | re.S)
    if not m: return ""
    # タグ剥がし
    t = re.sub(r"<[^>]+>", "", m.group(1))
    t = htmlmod.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def ga_snippet(rel_js_path: str) -> str:
    return (
        f"  {MARKER}\n"
        f"  <script async src=\"https://www.googletagmanager.com/gtag/js?id={GA_ID}\"></script>\n"
        f"  <script src=\"{rel_js_path}\"></script>\n"
    )

def js_relpath(path: pathlib.Path) -> str:
    # path は .html ファイル。ROOTからの相対で assets/js/analytics.js を指す相対パスを返す
    rel = path.relative_to(ROOT).parent
    depth = len(rel.parts)
    prefix = "../" * depth if depth > 0 else ""
    return prefix + "assets/js/analytics.js"

def update_file(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return "skip"

    changed = False

    # 1. <head> に GA4 を挿入（</head> 直前）
    rel_js = js_relpath(path)
    snippet = ga_snippet(rel_js)
    new_text, n = re.subn(r"</head>", snippet + "</head>", text, count=1, flags=re.I)
    if n == 0:
        return "no-head"
    text = new_text
    changed = True

    # 2. 記事ページなら body に data 属性付与
    if is_article_page(path):
        slug = path.parent.name
        cat = detect_category(path, text)
        title = extract_h1(text).replace('"', '&quot;')
        # <body ...> を置換（既存属性を保持）
        def body_sub(m):
            attrs = m.group(1) or ""
            # 既存の data-page-type があればスキップ
            if "data-page-type" in attrs:
                return m.group(0)
            add = (
                f' data-page-type="article"'
                f' data-article-slug="{slug}"'
                f' data-article-category="{cat}"'
                f' data-article-title="{title}"'
            )
            return f"<body{attrs}{add}>"
        text, nb = re.subn(r"<body([^>]*)>", body_sub, text, count=1)

    path.write_text(text, encoding="utf-8")
    return "updated"

def main():
    results = {"updated": [], "skip": [], "no-head": []}
    for p in ROOT.rglob("*.html"):
        if ".git" in p.parts: continue
        r = update_file(p)
        results[r].append(str(p.relative_to(ROOT)))
    print(f"Updated: {len(results['updated'])}")
    print(f"Skipped: {len(results['skip'])}")
    print(f"No <head>: {len(results['no-head'])}")
    for p in results["updated"]:
        print("  +", p)
    if results["no-head"]:
        print("MISSING </head>:")
        for p in results["no-head"]:
            print("  !", p)

if __name__ == "__main__":
    main()
