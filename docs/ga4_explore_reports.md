# GA4 Explore レポート 設定手順書

以下3本のレポートを **Explore（データ探索）→ 空白（自由形式）** で作成する。
カスタムディメンション登録から24〜48時間経ってからが正確。

GA4の Explore 用語:
- **Dimensions（ディメンション）**: 行や列に使う切り口（カテゴリデータ）
- **Metrics（指標）**: 数値として集計される値
- **Rows（行）**: 縦に並ぶ切り口
- **Values（値）**: 各行の数値列
- **Filters（フィルタ）**: 条件で絞り込み

---

## レポート① 記事別PVランキング

「どの記事が読まれているか」の基本ビュー。

### 作成手順

1. Explore → **空白（自由形式）** を新規作成
2. 名前を「記事別PVランキング」に
3. 左側 **Dimensions** に `+` で以下を追加
   - `Article Slug`
   - `Article Title`
   - `Article Category`
4. 左側 **Metrics** に `+` で以下を追加
   - `views`（表示回数）
   - `Total users`（合計ユーザー数）
   - `Engaged sessions`（エンゲージメントのあったセッション）
   - `Average engagement time`（平均エンゲージメント時間）
5. 中央の **設定** カラムで：
   - **Technique**: 自由形式
   - **Rows**: `Article Slug` / `Article Title` / `Article Category`（この順）
   - **Values**: `views` / `Total users` / `Engaged sessions` / `Average engagement time`
   - **行の最大数**: 50
   - **Rows の ネストされた行** は ON（記事タイトルを読みやすく）
6. **Filters**:
   - `Article Category` に **含む**: `baseball`, `keiba`, `economy`
     （= static_page を除外して記事だけ集計）
   - または event_name = `page_view` に絞る

### 読み方

- `views` 降順が記事別PVランキング。
- `Average engagement time` が60秒未満なら読まれていない記事。
- `Engaged sessions / Total users` が低い記事は離脱が早い = 導入文改善候補。
- `Article Category` 列でカテゴリ偏りを確認。

---

## レポート② 記事別 スクロール到達率

「記事がどこまで読まれているか」のビュー。

### 作成手順

1. Explore → **空白（自由形式）** を新規作成、名前「記事別スクロール到達率」
2. **Dimensions**
   - `Article Slug`
   - `Article Title`
   - `Scroll Percent`
3. **Metrics**
   - `Event count`（イベント数）
4. **設定**
   - **Rows**: `Article Slug` / `Article Title`
   - **Columns**: `Scroll Percent` （列展開して50/90を横並びに）
   - **Values**: `Event count`
5. **Filters**:
   - `Event name` **完全一致**: `article_scroll`

### 読み方

- 行ごとに `50` 列と `90` 列の数値が並ぶ。
- **90/50 比率**が読了率の近似値。
  - 60%以上: 読み切られている良記事
  - 30〜60%: 平均的
  - 30%未満: 後半離脱が多い＝後半の密度を見直す候補
- `50` 列自体が極端に少ない記事は、そもそも流入が少ないか、ファーストビュー離脱が多い。

### 派生レポート

同じ設定で **Filters** に `Article Category = keiba` を足せば競馬記事だけの読了率を見られる。

---

## レポート③ 記事別 外部導線クリック

「記事からYouTube・関連記事・アフィリエイトへどれだけ流れたか」のビュー。
収益導線と回遊導線を同じ画面で比較できる。

### 作成手順

1. Explore → **空白（自由形式）** を新規作成、名前「記事別外部導線クリック」
2. **Dimensions**
   - `Article Slug`
   - `Article Title`
   - `Event name`
   - `Link Position`
3. **Metrics**
   - `Event count`
4. **設定**
   - **Rows**: `Article Slug` / `Article Title` / `Link Position`
   - **Columns**: `Event name`（youtube_click / related_article_click / affiliate_click を横並び）
   - **Values**: `Event count`
5. **Filters**:
   - `Event name` **いずれかと一致**: `youtube_click`, `related_article_click`, `affiliate_click`

### 読み方

- 行ごとに3つのクリック種別が横並びで見える。
- `affiliate_click` がまったく立たない記事 = 収益導線が薄い＝ASP商品挿入の候補。
- `related_article_click` が多い記事 = 回遊起点として優秀＝テンプレ化して他記事に横展開。
- `youtube_click` は動画連携の効き具合。チャンネル登録者獲得の記事特定に使える。
- `Link Position` 次元を追加したことで、「記事本文内クリック」vs「記事末尾の関連記事リスト」のどちらが効いているかが一目で分かる。

### 派生レポート（affiliate_program別）

設定カラムで:
- **Rows**: `Affiliate Program` / `Article Slug`
- **Values**: `Event count`
- **Filters**: `Event name = affiliate_click`

これで「どのASPがどの記事から多く発生しているか」が見える。

---

## 全レポート共通の注意

- **24〜48時間待つ**: カスタムディメンション登録直後は値が `(not set)` ばかり。翌日再確認。
- **ブックマーク**: 作成したExploreの左上「★」で星マークを付けると左メニューに常時表示される。
- **共有**: 右上「共有」→ 閲覧リンクでチームメンバーに共有可能。
- **保存**: Explore は自動保存されるが、重要な設定変更後は右上「保存」で明示。

---

## 運用開始後に Explore で追加しておくと便利なビュー

| 名前 | Dimensions | Metrics | Filters | 用途 |
|---|---|---|---|---|
| カテゴリ間回遊マトリクス | `From Category` × `To Category` | `Event count` | `Event name = category_click` | 野球 ⇔ 経済 のクロス回遊 |
| リンク位置別CTR | `Link Position` | `Event count` | `Event name = related_article_click` | サイドバー vs 記事下 どちらが効くか |
| ASP別収益導線 | `Affiliate Program` / `Article Slug` | `Event count` / `Total users` | `Event name = affiliate_click` | 記事 × ASPの収益マッピング |
