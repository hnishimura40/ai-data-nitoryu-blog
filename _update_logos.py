import glob, os, re

os.chdir('D:/aiwork/claude')

# Collect all HTML files (excluding .claude/ and .git/)
all_files = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['.claude', '.git', 'node_modules']]
    for f in files:
        if f.endswith('.html'):
            all_files.append(os.path.join(root, f))

print(f'Found {len(all_files)} HTML files')

favicon_tag = '  <link rel="icon" type="image/png" href="/assets/img/logo.png">\n  <link rel="apple-touch-icon" href="/assets/img/logo.png">'

pat_viewport = re.compile(r'(<meta name="viewport"[^>]*>)')

# Pattern A: logo-main/logo-sub (non-article pages)
old_logo_a = '        <span class="logo-main">AIデータ二刀流ブログ</span>\n        <span class="logo-sub">野球・競馬 × 経済・株式</span>'
new_logo_a  = '        <img src="/assets/img/logo.png" alt="AIデータ二刀流" class="logo-img" width="40" height="40">\n        <div>\n          <span class="logo-main">AIデータ二刀流ブログ</span>\n          <span class="logo-sub">野球・競馬 × 経済・株式</span>\n        </div>'

# Pattern B: article page simple text logo
old_logo_b = '>AI<span>データ</span>二刀流</a>'
new_logo_b  = '><img src="/assets/img/logo.png" alt="" class="logo-img" width="36" height="36">AI<span>データ</span>二刀流</a>'

# Gate card icons
old_sports_icon = '<span class="gate-icon">⚾🐎</span>'
new_sports_icon = '<img src="/assets/img/logo.png" alt="野球・競馬" class="gate-logo">'

old_econ_icon = '<span class="gate-icon">📈💹</span>'
new_econ_icon = '<img src="/assets/img/logo-economy.png" alt="経済・株式" class="gate-logo">'

# Economy page hero
old_econ_h1 = '<h1>📈 経済・時事・株式分析</h1>'
new_econ_h1  = '<div class="page-hero-logo"><img src="/assets/img/logo-economy.png" alt="" width="72" height="72"></div>\n    <h1>経済・時事・株式分析</h1>'

stats = {'favicon': 0, 'logo_a': 0, 'logo_b': 0, 'gate_sports': 0, 'gate_econ': 0, 'econ_hero': 0}

for fpath in all_files:
    with open(fpath, 'r', encoding='utf-8') as fp:
        content = fp.read()
    orig = content

    # 1. Add favicon if missing
    if 'rel="icon"' not in content:
        content = pat_viewport.sub(r'\1\n' + favicon_tag, content, count=1)
        stats['favicon'] += 1

    # 2. Pattern A logo
    if old_logo_a in content:
        content = content.replace(old_logo_a, new_logo_a, 1)
        stats['logo_a'] += 1

    # 3. Pattern B logo
    if old_logo_b in content:
        content = content.replace(old_logo_b, new_logo_b, 1)
        stats['logo_b'] += 1

    # 4. Gate icons
    if old_sports_icon in content:
        content = content.replace(old_sports_icon, new_sports_icon, 1)
        stats['gate_sports'] += 1
    if old_econ_icon in content:
        content = content.replace(old_econ_icon, new_econ_icon, 1)
        stats['gate_econ'] += 1

    # 5. Economy hero
    if old_econ_h1 in content:
        content = content.replace(old_econ_h1, new_econ_h1, 1)
        stats['econ_hero'] += 1

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as fp:
            fp.write(content)

for k, v in stats.items():
    print(f'  {k}: {v} files updated')
