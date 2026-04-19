# GA4 カスタムディメンション 登録チェックリスト

GA4 管理画面「管理 → プロパティ → カスタム定義 → カスタム ディメンション → 作成」
で以下を順に登録する。**parameter名は大文字小文字・アンダースコアまで正確に**入力すること。

登録作業はすべてイベントスコープ（セッションやユーザースコープではない）。

---

## 優先度 高（最初の運用開始前に必ず8件登録）

| ✓ | 表示名 | parameter名 | scope | 用途 |
|---|---|---|---|---|
| ☐ | Article Slug | `article_slug` | event | 記事別ランキングの主キー |
| ☐ | Article Title | `article_title` | event | レポートで記事が読めるように |
| ☐ | Article Category | `article_category` | event | baseball / keiba / economy / static_page の比較 |
| ☐ | Scroll Percent | `scroll_percent` | event | 50 / 90 の到達率可視化 |
| ☐ | Target URL | `target_url` | event | 外部遷移先の把握（高カーディナリティ注意） |
| ☐ | Link Position | `link_position` | event | header / sidebar / article_body / article_footer 等 |
| ☐ | Affiliate Program | `affiliate_program` | event | a8 / rakuten / amazon / other_affiliate |
| ☐ | Form Name | `form_name` | event | 問い合わせフォーム識別 |

---

## 優先度 中（回遊/遷移の深掘り時に追加）

| ✓ | 表示名 | parameter名 | scope | 用途 |
|---|---|---|---|---|
| ☐ | Target Slug | `target_slug` | event | related_article_click の遷移先記事識別 |
| ☐ | From Category | `from_category` | event | category_click 起点 |
| ☐ | To Category | `to_category` | event | category_click 遷移先 |
| ☐ | Link Text | `link_text` | event | 同一URLへのボタン文言別CTR |

---

## 注意事項

- **反映まで24〜48時間**: 登録してもすぐExploreの選択肢には出ない。翌日〜翌々日に再確認。
- **イベントパラメータは既に送信されていれば自動収集**: 登録前のデータでも、GA4は過去14日以内のパラメータなら遡って検出する。
- **「Webストリーム」でのイベント送信確認を先に**: 管理画面の「データ収集・修正」→「データストリーム」→ ストリーム選択 → 右上の「過去30分のイベント」で受信状況を確認できる。
- **削除は慎重に**: 一度削除したカスタムディメンションのパラメータ名は、30日経過するまで再利用できないケースがある。命名時から慎重に。

---

## parameter 名 / 送信元イベント 対応表

| parameter | 送信元イベント |
|---|---|
| `article_slug` | article_scroll, related_article_click, youtube_click, affiliate_click, category_click |
| `article_title` | 同上 |
| `article_category` | 同上（category_clickでは `from_category` として送信） |
| `scroll_percent` | article_scroll |
| `target_url` | related_article_click, youtube_click, affiliate_click |
| `target_slug` | related_article_click |
| `link_position` | すべてのクリック系 |
| `link_text` | すべてのクリック系 |
| `affiliate_program` | affiliate_click |
| `from_category` | category_click |
| `to_category` | category_click |
| `form_name` | contact_submit |
| `page_path` | すべて（記事クエリ除去済み pathname） |
