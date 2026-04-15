// AIデータ二刀流ブログ - メインJS

document.addEventListener('DOMContentLoaded', function () {

  // =====================
  // ハンバーガーメニュー
  // =====================
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.site-nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      const isOpen = nav.classList.contains('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });

    // 外クリックで閉じる
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.site-header')) {
        nav.classList.remove('open');
      }
    });
  }

  // =====================
  // アクティブナビ
  // =====================
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.site-nav a');
  navLinks.forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && currentPath.includes(href) && href !== '/' && href !== '/index.html') {
      link.classList.add('active');
    }
  });

  // =====================
  // 記事ページ 目次（TOC）自動生成
  // =====================
  (function buildToc() {
    const artBody = document.querySelector('.art-body, article.art-body');
    if (!artBody) return;

    // h2・h3 を収集（summary-box の中の見出しは除外）
    const headings = Array.from(
      artBody.querySelectorAll('h2, h3')
    ).filter(function(h) {
      // サマリーボックス・インライン style 直書きの「わかること」は除外
      return !h.closest('.summary-box') &&
             !h.closest('.side-box') &&
             h.textContent.trim().length > 0;
    });

    if (headings.length < 2) return; // 見出し2個未満なら生成しない

    // 見出しに ID を自動付与（既存 ID 優先）
    const slugs = {};
    headings.forEach(function(h, i) {
      if (!h.id) {
        let base = 'h-' + i;
        h.id = base;
      }
      slugs[i] = h.id;
    });

    // TOC HTML を組み立て
    let tocHtml = '<nav class="art-toc" aria-label="目次"><div class="art-toc-title">目次</div><ol class="art-toc-list">';
    headings.forEach(function(h, i) {
      const isH3 = h.tagName === 'H3';
      const text = h.textContent.replace(/^[\d０-９]+[.．\s]+/, '').trim(); // 先頭の番号除去
      tocHtml += '<li class="art-toc-item' + (isH3 ? ' art-toc-sub' : '') + '">'
               + '<a href="#' + slugs[i] + '">' + text + '</a>'
               + '</li>';
    });
    tocHtml += '</ol></nav>';

    // 挿入位置: summary-box の直後、なければ最初の <p> の前
    const summaryBox = artBody.querySelector('.summary-box');
    const tocEl = document.createElement('div');
    tocEl.innerHTML = tocHtml;
    const toc = tocEl.firstChild;

    if (summaryBox && summaryBox.nextSibling) {
      artBody.insertBefore(toc, summaryBox.nextSibling);
    } else {
      const firstP = artBody.querySelector('p');
      if (firstP) {
        artBody.insertBefore(toc, firstP);
      } else {
        artBody.prepend(toc);
      }
    }
  })();

  // =====================
  // お問い合わせフォーム (フロント確認のみ)
  // =====================
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const name = contactForm.querySelector('#name').value.trim();
      const email = contactForm.querySelector('#email').value.trim();
      const message = contactForm.querySelector('#message').value.trim();

      if (!name || !email || !message) {
        alert('必須項目をすべてご入力ください。');
        return;
      }

      const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailReg.test(email)) {
        alert('有効なメールアドレスを入力してください。');
        return;
      }

      // 送信完了メッセージを表示 (実際の送信処理はバックエンドで)
      const formWrap = contactForm.closest('.form-wrap');
      formWrap.innerHTML = `
        <div style="text-align:center; padding: 40px 0;">
          <div style="font-size:3rem; margin-bottom:16px;">✉️</div>
          <h3 style="font-size:1.1rem; margin-bottom:10px; color:#1a2744;">お問い合わせを受け付けました</h3>
          <p style="font-size:0.88rem; color:#666; line-height:1.8;">
            ご連絡いただきありがとうございます。<br>
            内容を確認のうえ、数日以内にご返信いたします。
          </p>
          <a href="/" style="display:inline-block; margin-top:24px; padding:10px 28px; background:#1a2744; color:#fff; border-radius:6px; font-size:0.88rem; font-weight:600; text-decoration:none;">
            トップページへ戻る
          </a>
        </div>
      `;
    });
  }

});
