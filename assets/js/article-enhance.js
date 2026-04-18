/**
 * 記事ページ共通ビジュアル強化
 * - data-table の数値列を自動検出してCSSバーを重ねる
 * - sec-head 直後の最初のp要素に「KEY POINT」ラベルを付ける
 */
(function () {
  'use strict';

  // ========== 1. data-table 自動バー ==========
  // 単位を末尾から抽出して、数値部分を返す
  function parseNumber(text) {
    if (!text) return null;
    // strong タグ内の数値などを拾うため textContent ベースで処理
    const t = String(text).replace(/<[^>]+>/g, '').trim();
    // マイナスや小数、カンマ、％、兆億万千円、倍、ドル、年、件 等を許容
    const m = t.match(/^(-?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\-?\d+(?:\.\d+)?)\s*(%|兆円|億円|万円|千円|億ドル|兆ドル|ドル|円|倍|件|点|本|回|銘柄|人|社|兆|億)?\s*$/);
    if (!m) return null;
    const num = parseFloat(m[1].replace(/,/g, ''));
    const unit = m[2] || '';
    return isNaN(num) ? null : { num: num, unit: unit, raw: t };
  }

  function enhanceTable(table) {
    const rows = Array.from(table.querySelectorAll('tbody tr, tr'));
    if (rows.length < 2) return;

    // 各列ごとに parse 結果を収集
    const colCount = Math.max.apply(null, rows.map(function (r) {
      return r.children.length;
    }));

    for (let c = 0; c < colCount; c++) {
      const cellData = rows.map(function (r) {
        const cell = r.children[c];
        if (!cell) return { cell: null, parsed: null };
        // th は対象外
        if (cell.tagName === 'TH') return { cell: cell, parsed: null };
        return { cell: cell, parsed: parseNumber(cell.innerHTML) };
      });

      const parsedCount = cellData.filter(function (d) {
        return d.parsed && d.cell;
      }).length;

      // 2つ以上が数値として解釈できる列だけバー追加
      if (parsedCount < 2) continue;

      // 最大絶対値で正規化
      const maxAbs = Math.max.apply(null, cellData
        .filter(function (d) { return d.parsed; })
        .map(function (d) { return Math.abs(d.parsed.num); }));
      if (maxAbs <= 0) continue;

      // バー注入
      cellData.forEach(function (d) {
        if (!d.parsed || !d.cell) return;
        if (d.cell.querySelector('.cell-bar')) return; // 二重注入防止
        const pct = Math.min(100, Math.max(2, Math.round((Math.abs(d.parsed.num) / maxAbs) * 100)));
        const bar = document.createElement('div');
        bar.className = 'cell-bar';
        bar.innerHTML = '<span class="cell-bar-fill" style="width:' + pct + '%"></span>';
        d.cell.appendChild(bar);
        d.cell.classList.add('has-bar');
      });
    }
  }

  function enhanceAllTables() {
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(enhanceTable);
  }

  // ========== 2. セクション冒頭 KEY POINT ラベル ==========
  function addKeyPointLabels() {
    const secs = document.querySelectorAll('.sec-head');
    secs.forEach(function (sec) {
      let next = sec.nextElementSibling;
      // sec-head の直後の最初の <p> を拾う（summary-box などはスキップ）
      while (next && next.tagName !== 'P' && next.tagName !== 'UL' && next.tagName !== 'OL' && next.tagName !== 'TABLE') {
        next = next.nextElementSibling;
        if (!next) return;
      }
      if (!next || next.tagName !== 'P') return;
      if (next.classList.contains('sec-lede')) return;
      if (next.classList.contains('sec-sub')) return;
      next.classList.add('sec-lede');
    });
  }

  // ========== 3. 実行 ==========
  function init() {
    try { enhanceAllTables(); } catch (e) { console.warn('table enhance failed', e); }
    try { addKeyPointLabels(); } catch (e) { console.warn('keypoint failed', e); }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
