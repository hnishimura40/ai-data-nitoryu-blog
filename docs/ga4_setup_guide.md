# GA4 運用開始ガイド (ainitoryu.com)

このドキュメントは、**GA4管理画面で人間が行う作業**をそのまま実行できる形でまとめたもの。
コード側の実装は [ga4_audit_report.md](./ga4_audit_report.md) で完了確認済み。

---

## 1. 本番測定IDへの差し替え

現在コードには仮ID `G-XXXXXXXXXX` が入っている。以下の2箇所を本番IDに置換すること。

### 1-1. analytics.js の定数

ファイル: `assets/js/analytics.js`

```js
// 23行目付近
var GA_MEASUREMENT_ID = 'G-XXXXXXXXXX';  // ← 本番IDに置換
```

### 1-2. 全HTMLの gtag スクリプトタグ

各HTMLの `</head>` 直前に以下が入っている。

```html
<!-- GA4:ainitoryu -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script src="{相対パス}/assets/js/analytics.js"></script>
```

### 推奨: sed で一括置換

```bash
# プロジェクトルートで実行
NEW_ID="G-ABCD1234EF"   # ← 本番IDに
# HTML
grep -rl "G-XXXXXXXXXX" --include="*.html" . | xargs sed -i "s/G-XXXXXXXXXX/${NEW_ID}/g"
# analytics.js
sed -i "s/G-XXXXXXXXXX/${NEW_ID}/g" assets/js/analytics.js
# 注入スクリプト（今後の新規記事にも反映されるよう）
sed -i "s/G-XXXXXXXXXX/${NEW_ID}/g" _inject_analytics.py
```

差し替え後は `git diff` を確認してからコミット→push→Cloudflare Pagesで自動デプロイ。

---

## 2. GA4 管理画面で登録するカスタムディメンション

管理画面パス: **管理 → プロパティ → カスタム定義 → カスタム ディメンション → 作成**

### 2-1. 優先度：高（最初に必ず登録）

| 表示名 | スコープ | イベントパラメータ | 用途 |
|---|---|---|---|
| Article Slug | イベント | `article_slug` | 記事別ランキングの主キー |
| Article Title | イベント | `article_title` | レポート可読性（slug が機械的なので） |
| Article Category | イベント | `article_category` | baseball / keiba / economy / static_page の比較 |
| Scroll Percent | イベント | `scroll_percent` | 50 / 90 の到達率可視化 |
| Target URL | イベント | `target_url` | 外部遷移先の把握 |
| Link Position | イベント | `link_position` | header / sidebar / article_body / article_footer などCTA位置別CTR |
| Affiliate Program | イベント | `affiliate_program` | a8 / rakuten / amazon / other_affiliate 別比較 |
| Form Name | イベント | `form_name` | 問い合わせフォーム識別（今後フォーム追加時用） |

### 2-2. 優先度：中（記事回遊を深掘りする時）

| 表示名 | スコープ | イベントパラメータ | 用途 |
|---|---|---|---|
| Target Slug | イベント | `target_slug` | related_article_click の遷移先記事分析 |
| From Category | イベント | `from_category` | category_click 起点カテゴリ |
| To Category | イベント | `to_category` | category_click 遷移先カテゴリ |
| Link Text | イベント | `link_text` | 同一URLへのボタン文言別CTR比較 |

### 2-3. 登録手順（UI操作）

1. GA4 左下「管理」→ プロパティ列の「カスタム定義」
2. 「カスタム ディメンション」タブ → 「カスタム ディメンションを作成」
3. 以下を入力して保存
   - ディメンション名: 上表の「表示名」
   - 範囲: **イベント**
   - 説明: 任意（例: 「記事スラッグ（URLの最終セグメント）」）
   - イベントパラメータ: 上表の「イベントパラメータ」を**正確に**入力（大文字小文字・アンダースコア一致）
4. 2-1 の 8 件を最初にまとめて作成

> ⚠ **重要**: GA4はカスタムディメンション登録後、実データの収集が始まっていてもレポートに反映されるまで **24〜48時間** かかる。運用開始初日にExploreで見えなくても焦らない。

---

## 3. DebugView での確認手順（リアルタイム）

DebugView は**即時**で送信イベントが見えるので、運用開始前の動作確認に必須。

### 3-1. 有効化

1. Chrome拡張 [Google Analytics Debugger](https://chrome.google.com/webstore/detail/google-analytics-debugger/jnkmfdileelhofjcijamephohjechhna) をインストール
2. 拡張アイコンON → ainitoryu.com を開く
3. GA4管理画面 → 左メニュー「管理」→ プロパティ →「DebugView」

### 3-2. 確認すべきイベント

サイトで以下を操作し、DebugView にリアルタイム表示されることを確認：

| 操作 | 期待イベント | 期待パラメータ |
|---|---|---|
| トップページ表示 | `page_view` | `page_path=/` |
| 記事ページ表示（例: 皐月賞） | `page_view` | `page_path=/hanshin-keiba/2026-04-19-satsukisho/` |
| 記事を50%までスクロール | `article_scroll` | `scroll_percent=50`, `article_slug`, `article_category` |
| 記事を90%までスクロール | `article_scroll` | `scroll_percent=90` |
| 記事内サイドバーの関連記事クリック | `related_article_click` | `target_slug`, `link_position=sidebar` |
| 記事内YouTube埋め動画の直下リンククリック | `youtube_click` | `target_url=youtu.be/...` |
| TOPの「野球・競馬を読む」クリック | `category_click` | `to_category=baseball_or_keiba`, `link_position=category_section` |
| お問い合わせフォームを正しく入力して送信 | `contact_submit` | `form_name=contactForm` |
| お問い合わせフォームを空で送信 | （**発火しないこと**を確認） | — |

### 3-3. プライバシーチェック

DebugView の各イベントをクリックし、パラメータ一覧に以下が**含まれていないこと**を確認：

- ❌ `name` / `email` / `message` / `subject`（フォーム入力値）
- ❌ URLに `?name=...` のようなクエリ文字列
- ✅ `anonymize_ip` 効果で IP 情報は見えない
- ✅ Google Signals 無効なので地域・年齢・性別の詳細な広告プロファイルは推定されない

---

## 4. Explore で作るべきレポート3本

詳細は [ga4_explore_reports.md](./ga4_explore_reports.md) を参照。
この §4 はサマリのみ。

1. **記事別PVランキング** — 記事単位の基本指標
2. **記事別 スクロール到達率** — 読了傾向
3. **記事別 外部導線クリック** — YouTube・関連記事・アフィリエイト

---

## 5. 高カーディナリティ対策（データ爆発防止）

GA4は1プロパティあたりのカスタムディメンション固有値が **500 / 日** を超えると `(other)` にまとめられてしまう。

| ディメンション | カーディナリティ見込み | 警戒度 |
|---|---|---|
| `article_slug` | 記事数に比例（現在46、月+30見込み） | 低 — 数年は問題なし |
| `article_title` | 記事数同等 | 低 |
| `target_url` | **外部サイト分すべて** — YouTube動画URL、アフィ先、関連記事URL | **中** — 1日500を超え始めたら `target_slug` やドメイン抽出に切り替え検討 |
| `link_text` | リンク文言のバリエーション | 中 — 動的生成テキストがある場合注意 |
| `scroll_percent` | 50 / 90 の2値 | 極小 |
| `affiliate_program` | 固定列挙（5種） | 極小 |
| `link_position` | 固定列挙（7種） | 極小 |

**推奨**: `target_url` は登録しつつも、レポートの主軸には使わず、必要時の深掘り用途に限定。代わりに `target_slug` や `link_position` を主軸にする。

---

## 6. 運用開始前チェックリスト

運用開始（本番ID差し替え→push）の**直前と直後**に確認する。

### 6-1. 差し替え前

- [ ] analytics.js / 全HTML / `_inject_analytics.py` に `G-XXXXXXXXXX` が残っていない
- [ ] `node -c` などで analytics.js / main.js の構文OK
- [ ] ローカルで任意の記事ページを開き DevTools Console にエラーが出ない
- [ ] DevTools Network で `gtag/js?id=G-XXXXXXXXXX` のリクエストが200で完了する（仮IDでも404にはならない）

### 6-2. 差し替え直後（本番デプロイ後15分以内）

- [ ] GA4 リアルタイムレポートに自分のアクセスが表示される
- [ ] DebugView で 3-2 のイベント表が全パス
- [ ] プライバシーチェック（3-3）全パス
- [ ] 任意のアフィリエイトリンクを貼った記事で `affiliate_click` が `affiliate_program` とともに記録される

### 6-3. 72時間以内

- [ ] Explore の3レポートで、記事別データが `(not set)` だらけでないこと
- [ ] 直帰率・平均エンゲージメント時間が極端に異常値（0秒や1時間）でないこと

---

## 7. 運用開始後に最初の7日で見るべき指標

| 優先度 | 指標 | どこで見るか | 期待/警戒ライン |
|---|---|---|---|
| A | 全ページ PV / UU | レポート → ライフサイクル → エンゲージメント → ページとスクリーン | 既存の他計測（あれば）と桁が合う |
| A | `article_scroll` の 90% 到達率 | [ga4_explore_reports.md](./ga4_explore_reports.md) レポート②  | 記事による差はあるが、良記事で40-60%、問題記事で10%未満 |
| A | `affiliate_click` 件数 | [ga4_explore_reports.md](./ga4_explore_reports.md) レポート③ | 0件が続いたら判定ロジックに漏れがある可能性 |
| B | `category_click` from_category 分布 | Explore 自由形式 | TOPからの流入経路（野球→経済のクロス回遊が起きているか） |
| B | `youtube_click` | レポート③ | 動画導線の効きを記事別で比較 |
| B | `contact_submit` | イベントレポート | 1日1件以上あればフォーム経路が生きている証拠 |
| C | 直帰率 | エンゲージメントレポート | 極端に高い記事 = リード文が弱い候補 |
| C | モバイル比率 | テクノロジー → デバイス | 70%超が通常。モバイル特有のJS不具合監視に |

### 7-1. 初日にやること

1. DebugView を開きっぱなしで自分のスマホ・PCからサイトを一周
2. すべてのイベントが取れることを確認
3. 1時間後に「リアルタイム」レポートで自分の滞在を確認
4. 翌日のGA4標準レポートに数字が入っていれば運用開始OK

### 7-2. 48時間後にやること

- カスタムディメンションがExploreで選択肢に表示されるようになる
- レポート①②③を作成し、ブックマーク（左メニューの「★」）

### 7-3. 7日後にやること

- 記事別 CTR (engagements/pageviews) の傾向把握
- `affiliate_click` 率（affiliate_click / session）を計算
- 回遊起点ページTop5を特定し、導線改善ネタとして記録

---

## 8. 新規記事追加時の運用メモ

1. 記事HTMLを `hanshin-keiba/{slug}/` or `economy-stocks/{slug}/` に追加
2. プロジェクトルートで `python _inject_analytics.py` 実行
   - 既にタグ注入済みのファイルは `<!-- GA4:ainitoryu -->` マーカーで**自動スキップ**（冪等）
   - 新規記事のみ GA4タグ＋body data属性が追加される
3. カテゴリ自動判定結果を目視確認
   - `hanshin-keiba/` 配下の記事は、タイトル/スラッグに「皐月賞」「ダービー」「競馬」「血統」「予想」等があれば `keiba`、なければ `baseball`
   - 誤判定した場合は `<body>` の `data-article-category="keiba"` を手動修正
4. コミット → main push → 自動デプロイ
5. 本番反映後、DebugView で新記事URLのイベントが正しい `article_category` で届くことを1度だけ確認
