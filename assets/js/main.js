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
