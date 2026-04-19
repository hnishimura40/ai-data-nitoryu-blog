# GA4 実装 監査レポート

ainitoryu.com の GA4 計測実装について、現行コードベースを実ファイルベースで検証した結果をまとめる。
（検証日: 2026-04-19 / 対象ブランチ: `main` / 対象ワーキングツリー: `heuristic-pascal-cd6f80`）

---

## 1. 検証対象ファイル

| 種別 | パス | 備考 |
|---|---|---|
| 計測モジュール | `assets/js/analytics.js` | GA4タグ+イベント実装本体 |
| 注入スクリプト | `_inject_analytics.py` | 全HTMLへの冪等注入 |
| フォームハンドラ | `assets/js/main.js` | `contactForm` のバリデーション＆成功表示 |
| HTML (全56) | `**/*.html` | `GA4:ainitoryu` マーカーでgrep済み |

---

## 2. カバレッジ

| 項目 | 期待 | 実測 | 判定 |
|---|---|---|---|
| HTML総数 | 56 | 56 | — |
| `GA4:ainitoryu` マーカー | 全HTML | **56/56** | ✅ |
| `googletagmanager.com/gtag/js` | 全HTML | **56/56** | ✅ |
| `assets/js/analytics.js` 参照 | 全HTML | **56/56** | ✅ |
| `data-page-type="article"` | 記事のみ | **46** (economy 23 + baseball 22 + keiba 1) | ✅ |
| 静的ページへの article data 属性漏れ | 0 | 0 | ✅ |

### カテゴリ分類結果

- `economy` : 23 (すべて `economy-stocks/2026-*`)
- `baseball`: 22 (`hanshin-keiba/` 配下の試合分析・球団分析)
- `keiba`  : 1 (`hanshin-keiba/2026-04-19-satsukisho`)
- `static_page`: 10 (index, contact, profile, privacy-policy, channels, mobile-test, hanshin-keiba/index, hanshin-keiba/page2, hanshin-keiba/analysis, economy-stocks/index)

---

## 3. イベント実装の確認結果

| イベント | 発火条件 | 多重発火防止 | パラメータ | 個人情報 | try/catch |
|---|---|---|---|---|---|
| `article_scroll` | 記事のみ、50% / 90% | ✅ `fired[50\|90]` フラグ | slug / title / category / page_path / scroll_percent | なし | ✅ |
| `related_article_click` | 関連記事エリア or 記事本文内の同一サイト記事リンク | — (クリック毎) | +target_url / target_slug / link_text / link_position | なし | ✅ |
| `youtube_click` | URLが YouTube系 | — | +target_url / link_text / link_position | なし | ✅ |
| `affiliate_click` | URLドメイン一致 or `data-affiliate` 属性 | — | +target_url / affiliate_program / link_text / link_position | なし | ✅ |
| `category_click` | `.gate-card` / `.site-nav` / カテゴリトップURL | — | from_category / to_category / link_text / link_position | なし | ✅ |
| `contact_submit` | **main.jsバリデーション通過後** にカスタムイベント `contact:submit-success` 経由 | — (1回送信で遷移) | form_name / page_path | なし | ✅ |

- クリック委譲は `capture: true` で一度だけ登録。
- 全体を trycatch で包み、失敗時もページ表示は継続。

---

## 4. 実装報告との差分（監査で発見した問題）

| # | 重要度 | 問題 | 状態 |
|---|---|---|---|
| 1 | 重大 | `isYouTube()` の正規表現 `(^|\.)youtu\.be\/` が `https://youtu.be/xxx` に**マッチしない**（`youtu.be` の直前は `/` で `^` も `\.` も成立しない）。youtu.be 短縮URLが youtube_click として取れていなかった。 | **修正済み** |
| 2 | 重要 | `contact_submit` が submit イベント直接捕捉だったため、main.js のバリデーション失敗時にも発火していた。ユーザー仕様の「送信成功時のみ」を満たしていなかった。 | **修正済み**（main.js で `contact:submit-success` CustomEvent を発火し、analytics.js はそれだけを拾う構成に変更） |
| 3 | 軽微 | `page_path` が `location.search` を含んでいた。現状 URL クエリは使われていないが、将来 `?utm_*` や `?ref=xxx` が付いた場合に GA4 標準レポートとの重複カーディナリティを招く。contactフォームが誤って GET 送信された場合の PII 混入リスクもわずかに存在。 | **修正済み**（pathname のみに変更。gtag config に `page_location` と `page_path` をクエリ除去で明示指定） |
| 4 | 軽微 | `getArticleCategory()` のフォールバックが `/hanshin-keiba/` 配下を無条件に `baseball` と判定していた。category 先頭ページなど非記事でカテゴリ混入の可能性。 | **修正済み**（data属性無しなら `static_page` を返す） |
| 5 | 情報 | `anonymize_ip: true` は GA4 では事実上常時ONのため不要。ただし明示しておくのは安全寄りの選択なので保持。 | 保持 |

### 修正後の diff 要約

```
assets/js/analytics.js
- isYouTube regex を (?:youtube\.com|youtu\.be)\/ ベースに書き換え
- pagePath() を location.pathname のみ返却に
- gtag config に page_location/page_path をクエリ除去して明示
- getArticleCategory() のパスフォールバック廃止 → static_page固定
- submit listener を削除し、window 'contact:submit-success' を購読

assets/js/main.js
- contactForm の成功ブロック直前で window.dispatchEvent(new CustomEvent('contact:submit-success', {...})) を発火
```

---

## 5. 個人情報非送信の確認結果

| 観点 | 結果 |
|---|---|
| フォーム入力値 (name/email/subject/message) | **送信しない**（submit 直接捕捉をやめ、main.jsの成功後カスタムイベント経由に変更） |
| URLクエリ | **送信しない**（page_path / page_location を pathname のみに上書き） |
| リファラ | GA4標準の `document.referrer` はそのまま記録（通常のアクセス元計測用途、個人情報に該当せず） |
| Cookie ID / Client ID | GA4標準の `_ga` Cookie のみ（個人特定不可の匿名ID） |
| IP | `anonymize_ip: true`（GA4側で保存されない） |
| Google Signals / 広告関連信号 | `allow_google_signals: false` / `allow_ad_personalization_signals: false` |
| article_title | HTMLの `<h1>` または `data-article-title` から取得（編集コンテンツ、個人情報なし） |
| target_url | リンクhrefそのまま（外部URLで個人情報が含まれるリンクは存在しない） |
| link_text | リンクテキスト（編集コンテンツ、個人情報なし） |

判定: **個人情報送信のリスク面は解消されている**。

---

## 6. 残る注意点（未修正、運用でカバー）

| # | 内容 | 推奨対応 |
|---|---|---|
| A | `GA_MEASUREMENT_ID = 'G-XXXXXXXXXX'` が仮ID。現状は無効なID相当で実計測されない | **運用開始前**に本番IDへ差し替え（[ga4_setup_guide.md](./ga4_setup_guide.md) の §1 参照） |
| B | affiliate 判定で `amazon.co.jp` を無条件にAmazon扱い。アフィリエイト無しリンク（書籍参照など）もカウントされる | 運用でOK、必要なら `<a data-affiliate="none">` を付与 |
| C | 今後 hanshin-keiba/ 配下に新規 keiba 記事を増やす際、`_inject_analytics.py` の自動判定に頼るとタイトル/スラグのキーワードで振り分けられる。誤判定時は `<body>` の `data-article-category` を手動上書き | 新規記事投入後に DebugView で `article_category` を目視確認（運用メモに記載） |
| D | `category_click` の `to_category` は `hanshin-keiba` を `baseball_or_keiba` と統合表示。具体分類は遷移先ページ側に任せる | 必要になったら個別 slug 判定に拡張 |

---

## 7. 総合判定

| 項目 | 判定 |
|---|---|
| 全ページにGA4タグ | ✅ |
| 記事data属性 | ✅ |
| カテゴリ分類 | ✅ |
| 6イベント実装 | ✅ （重要2件を当監査で修正） |
| 個人情報非送信 | ✅ |
| 表示崩れ・デザイン影響 | ✅ なし |
| **本番投入可否** | **caution** — 仮IDのまま投入すると計測されないので、§5-Aの本番IDへの差し替えを完了させてから投入すること。それ以外の技術的ブロッカーは無し。 |
