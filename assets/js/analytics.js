/**
 * AIデータ二刀流ブログ — GA4 共通計測スクリプト
 *
 * 目的: 記事別の閲覧状況・回遊・外部導線・収益導線の把握
 * 個人情報（IP・氏名・メール・フォーム入力値）は送信しない方針。
 *
 * イベント:
 *   article_scroll        — 記事ページで 50% / 90% 到達時
 *   related_article_click — 関連記事リンククリック
 *   youtube_click         — YouTubeリンククリック
 *   affiliate_click       — アフィリエイトリンククリック
 *   category_click        — カテゴリ導線クリック
 *   contact_submit        — 問い合わせフォーム送信成功時
 */
(function () {
  'use strict';

  // 失敗してもページ表示に影響しないよう try/catch で全体を包む
  try {

  // ========== 設定 ==========
  // 差し替え用: 本番GA4計測IDを入れ替えるだけで有効化できる
  var GA_MEASUREMENT_ID = 'G-Z46KWRF7TH';

  // ========== gtag 初期化 ==========
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  gtag('js', new Date());
  // IP匿名化（GA4標準。明示）、広告関連信号抑制、
  // page_location/page_path はクエリを除去して送信（PII混入防止）
  gtag('config', GA_MEASUREMENT_ID, {
    anonymize_ip: true,
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    page_location: location.origin + location.pathname,
    page_path: location.pathname
  });

  // ========== ユーティリティ ==========
  var body = document.body || document.documentElement;

  function getPageType() {
    return (body && body.dataset && body.dataset.pageType) || 'static_page';
  }

  function isArticle() {
    return getPageType() === 'article';
  }

  function getArticleSlug() {
    if (body && body.dataset && body.dataset.articleSlug) return body.dataset.articleSlug;
    // フォールバック: URLの最終セグメント
    var path = location.pathname.replace(/\/+$/, '');
    var seg = path.split('/').pop();
    return seg || '';
  }

  function getArticleCategory() {
    if (body && body.dataset && body.dataset.articleCategory) return body.dataset.articleCategory;
    // data-article-category が無い = 記事ページではない扱い
    return 'static_page';
  }

  function getArticleTitle() {
    if (body && body.dataset && body.dataset.articleTitle) return body.dataset.articleTitle;
    var h1 = document.querySelector('h1');
    if (h1) return (h1.textContent || '').trim().slice(0, 150);
    return (document.title || '').split('|')[0].trim().slice(0, 150);
  }

  function pagePath() {
    // 将来URLパラメータが増えてもPII混入しないよう pathname のみ
    return location.pathname;
  }

  function baseArticleParams() {
    return {
      article_slug: getArticleSlug(),
      article_title: getArticleTitle(),
      article_category: getArticleCategory(),
      page_path: pagePath()
    };
  }

  function send(eventName, params) {
    try { gtag('event', eventName, params || {}); } catch (e) { /* noop */ }
  }

  // リンクの「おおまかな位置」を推定
  function detectLinkPosition(el) {
    if (!el || !el.closest) return 'other';
    if (el.closest('header, .site-header')) return 'header';
    if (el.closest('footer, .site-footer')) return 'article_footer';
    if (el.closest('.art-sidebar, .sidebar-toc, .sidebar-meta')) return 'sidebar';
    if (el.closest('.related-list, .related-item')) return 'article_footer';
    if (el.closest('.art-body, article, main.art-body')) return 'article_body';
    if (el.closest('.article-grid, .article-card')) return 'home_card';
    if (el.closest('.gate-card, .entry-gates')) return 'category_section';
    if (el.closest('.channel-grid, .channel-card')) return 'category_section';
    if (el.closest('.section')) return 'category_section';
    return 'other';
  }

  function isYouTube(url) {
    // https://youtu.be/xxx / https://www.youtube.com/... の両方に対応
    return /(?:^https?:\/\/)?(?:[\w-]+\.)*(?:youtube\.com|youtu\.be)\//i.test(url);
  }

  // アフィリエイト判定: URLドメイン/パターンで自動判定
  function detectAffiliate(url) {
    if (!url) return null;
    if (/(a8\.net|a8\.st)/i.test(url)) return 'a8';
    if (/(rakuten\.co\.jp|hb\.afl\.rakuten|rakuten-affiliate)/i.test(url)) return 'rakuten';
    if (/(amazon\.co\.jp|amazon\.com|amzn\.to)/i.test(url)) return 'amazon';
    if (/(valuecommerce\.com|ck\.jp\.ap\.valuecommerce|px\.a8)/i.test(url)) return 'other_affiliate';
    if (/(afi\.moshimo\.com|moshimo\.com)/i.test(url)) return 'other_affiliate';
    if (/(accesstrade|linksynergy|janet\.jp|admatrix|felmat)/i.test(url)) return 'other_affiliate';
    // data-affiliate 属性があれば尊重
    return null;
  }

  // 関連記事リンク判定
  function isRelatedArticleLink(el) {
    if (!el) return false;
    if (el.closest && el.closest('.related-list, .related-item')) return true;
    if (el.dataset && el.dataset.linkType === 'related') return true;
    // 記事本文内で、同一サイト内の別記事ディレクトリへのリンクは関連記事扱い
    if (isArticle() && el.closest && el.closest('.art-body')) {
      var href = el.getAttribute('href') || '';
      if (href && /^(?:\/|\.\.\/|\.\/)/.test(href)
          && /(hanshin-keiba|economy-stocks)\//.test(href)
          && !/^https?:/i.test(href)) {
        return true;
      }
    }
    return false;
  }

  // カテゴリ導線判定: カテゴリトップ・ゲートカード・セクション間遷移
  function isCategoryLink(el) {
    if (!el) return false;
    var href = el.getAttribute('href') || '';
    // ゲートカード内・ナビ内・セクションヘッダ下のCTA
    if (el.closest && el.closest('.gate-card')) return true;
    if (el.closest && el.closest('.site-nav')) return true;
    // カテゴリトップ（/hanshin-keiba/ or /economy-stocks/ 直下）へのリンク
    if (/^\/?(hanshin-keiba|economy-stocks|channels)\/?(\?|#|$)/.test(href)) return true;
    if (el.dataset && el.dataset.linkType === 'category') return true;
    return false;
  }

  function categoryOf(href) {
    if (!href) return '';
    if (/hanshin-keiba/.test(href)) return 'baseball_or_keiba';
    if (/economy-stocks/.test(href)) return 'economy';
    if (/channels/.test(href)) return 'channel';
    if (/profile/.test(href)) return 'static_page';
    if (/contact/.test(href)) return 'static_page';
    return '';
  }

  function targetSlug(href) {
    if (!href) return '';
    var clean = href.split('#')[0].split('?')[0].replace(/\/+$/, '');
    var seg = clean.split('/').pop();
    return seg || '';
  }

  function linkText(el) {
    var t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    return t.slice(0, 120);
  }

  // ========== クリックイベント委譲 ==========
  document.addEventListener('click', function (ev) {
    try {
      var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '';
      if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) return;

      var pos = detectLinkPosition(a);
      var txt = linkText(a);
      var base = baseArticleParams();

      // 1. アフィリエイト判定（最優先）
      var aff = (a.dataset && a.dataset.affiliate) || detectAffiliate(href);
      if (aff) {
        send('affiliate_click', Object.assign({}, base, {
          target_url: href,
          affiliate_program: aff,
          link_text: txt,
          link_position: pos
        }));
        return;
      }

      // 2. YouTube判定
      if (isYouTube(href)) {
        send('youtube_click', Object.assign({}, base, {
          target_url: href,
          link_text: txt,
          link_position: pos
        }));
        return;
      }

      // 3. 関連記事判定
      if (isRelatedArticleLink(a)) {
        send('related_article_click', Object.assign({}, base, {
          target_url: href,
          target_slug: targetSlug(href),
          link_text: txt,
          link_position: pos
        }));
        return;
      }

      // 4. カテゴリ導線判定
      if (isCategoryLink(a)) {
        send('category_click', {
          article_slug: base.article_slug,
          article_title: base.article_title,
          from_category: base.article_category,
          to_category: categoryOf(href),
          page_path: base.page_path,
          link_text: txt,
          link_position: pos
        });
        return;
      }
    } catch (e) { /* noop */ }
  }, { capture: true });

  // ========== スクロール計測（記事のみ、50% / 90%） ==========
  if (isArticle()) {
    var fired = { 50: false, 90: false };
    var ticking = false;

    function checkScroll() {
      ticking = false;
      var doc = document.documentElement;
      var winH = window.innerHeight || doc.clientHeight;
      var scrollTop = window.pageYOffset || doc.scrollTop || 0;
      var docH = Math.max(
        document.body.scrollHeight, doc.scrollHeight,
        document.body.offsetHeight, doc.offsetHeight
      );
      var scrollable = Math.max(docH - winH, 1);
      var pct = Math.min(100, Math.round(((scrollTop + winH) / docH) * 100));
      // より安定した基準: (scrollTop / scrollable) * 100 を使用
      var pct2 = Math.min(100, Math.round((scrollTop / scrollable) * 100));
      var effective = Math.max(pct, pct2);

      [50, 90].forEach(function (threshold) {
        if (!fired[threshold] && effective >= threshold) {
          fired[threshold] = true;
          send('article_scroll', Object.assign({}, baseArticleParams(), {
            scroll_percent: threshold
          }));
        }
      });

      if (fired[50] && fired[90]) {
        window.removeEventListener('scroll', onScroll);
      }
    }

    function onScroll() {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(checkScroll);
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    // 初期状態でも確認（短い記事・ロード時に既に超えているケース）
    setTimeout(checkScroll, 400);
  }

  // ========== 問い合わせフォーム送信 ==========
  // main.js 側でバリデーション通過後に 'contact:submit-success' を発火する。
  // ここではそのカスタムイベントだけを拾う（submitイベント直接拾いだと
  // バリデーション失敗時にも発火してしまうため）。入力値は一切送らない。
  window.addEventListener('contact:submit-success', function (ev) {
    try {
      var name = (ev && ev.detail && ev.detail.formName) || 'contact';
      send('contact_submit', {
        form_name: name,
        page_path: pagePath()
      });
    } catch (e) { /* noop */ }
  });

  } catch (e) { /* analytics failure must not break the page */ }
})();
