/*
  受講者ハンドアウト 共通スクリプト（session1 / 2 / 3 で共用）
  ------------------------------------------------------------------
  対になる CSS: assets/handout.css
  file:// でのダブルクリック起動を前提にしているため、ES モジュールや
  fetch は使わず、素の <script src> で読み込める書き方に揃えている。

  HTML 側の前提:
    <main>
      <section class="page" id="p1" data-title="オリエンテーション" data-time="0–15 分"> … </section>
      <section class="page" id="p2" data-title="講義①：生成 AI とは？" data-time="15–30 分"> … </section>
      …
    </main>
    <nav class="toc"><h2>目次</h2><ul id="toc-list"></ul></nav>
  ※ data-title は目次と前へ／次へに表示する名前。
    data-time はアジェンダとの対応を残すための注記で、現在は画面には出していない。

  やること:
    1. section.page から目次を自動生成（id 付きの h3 は第 2 階層として展開）
    2. 1 ページずつ表示し、前へ／次へと URL ハッシュで移動
    3. 「全ページを表示」トグル（ページ内検索・通し読み用）
    4. コードブロックのコピー、画面キャプチャのフォールバック
    5. pre.mermaid の描画（mermaid.min.js を読み込んだページのみ）
    6. 印刷時は全ページ＋<details> をすべて展開

  JS が読み込まれなかった場合は全ページがそのまま縦に並ぶため、
  ハンドアウトとしては読める状態が保たれる。
*/
(function () {
  "use strict";

  /* ============================================================
     画面キャプチャ（assets/images/*.png）が無い場合は
     代替のインライン SVG 説明図を表示する
     ============================================================ */
  function initShotFallback() {
    var imgs = Array.prototype.slice.call(document.querySelectorAll("figure.shot img"));
    imgs.forEach(function (img) {
      function fallback() {
        var fig = img.parentNode;
        while (fig && !(fig.classList && fig.classList.contains("shot"))) fig = fig.parentNode;
        if (fig) fig.classList.add("shot--missing");
        if (img.parentNode) img.parentNode.removeChild(img);
      }
      img.addEventListener("error", fallback);
      if (img.complete && img.naturalWidth === 0) fallback();
    });
  }

  /* ============================================================
     コードブロックのコピー（file:// でも動くよう execCommand を使用）
     ============================================================ */
  function initCopyButtons() {
    var btns = Array.prototype.slice.call(document.querySelectorAll(".copy-btn[data-copy-target]"));
    btns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var target = document.getElementById(btn.getAttribute("data-copy-target"));
        if (!target) return;
        var ta = document.createElement("textarea");
        ta.value = target.textContent;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.focus();
        ta.select();
        try {
          document.execCommand("copy");
          btn.textContent = "コピーしました";
          btn.classList.add("copied");
          setTimeout(function () {
            btn.textContent = "コピー";
            btn.classList.remove("copied");
          }, 1500);
        } catch (e) {
          alert("コピーに失敗しました。手動で選択してコピーしてください。");
        }
        document.body.removeChild(ta);
      });
    });
  }

  /* ============================================================
     Mermaid（pre.mermaid）の描画
     mermaid.min.js を読み込んでいないページでは何もしない。
     描画は必ずページ送りを有効にする前に終わらせる：
     display:none の中で描画すると文字幅が測れず図が潰れるため、
     完了（または失敗・タイムアウト）を待って next() を呼ぶ
     ============================================================ */
  function initMermaid(next) {
    var done = false;
    function once() {
      if (done) return;
      done = true;
      next();
    }
    if (typeof mermaid === "undefined" || !document.querySelector("pre.mermaid")) {
      once();
      return;
    }
    // mermaid の読み込みや描画が失敗しても、ページ送りは必ず有効にする
    window.setTimeout(once, 3000);
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "default",
        themeVariables: { primaryColor: "#0366d6" }
      });
      var ret = mermaid.run({ querySelector: "pre.mermaid" });
      if (ret && typeof ret.then === "function") ret.then(once, once);
      else once();
    } catch (e) {
      once();
    }
  }

  /* ============================================================
     印刷時は折りたたみをすべて開く（印刷後に元へ戻す）
     ============================================================ */
  function initPrintExpand() {
    var reopened = [];
    function expand() {
      reopened = [];
      Array.prototype.slice.call(document.querySelectorAll("details:not([open])")).forEach(function (d) {
        d.open = true;
        reopened.push(d);
      });
    }
    function restore() {
      reopened.forEach(function (d) { d.open = false; });
      reopened = [];
    }
    window.addEventListener("beforeprint", expand);
    window.addEventListener("afterprint", restore);
    // Safari など beforeprint が無い環境向け
    if (window.matchMedia) {
      var mql = window.matchMedia("print");
      var onChange = function (m) { if (m.matches) expand(); else restore(); };
      if (mql.addEventListener) mql.addEventListener("change", onChange);
      else if (mql.addListener) mql.addListener(onChange);
    }
  }

  /* ============================================================
     ページ送り本体
     ============================================================ */
  function initPager() {
    var main = document.querySelector("main");
    var tocList = document.getElementById("toc-list");
    if (!main) return;

    var pages = Array.prototype.slice.call(main.children).filter(function (el) {
      return el.tagName === "SECTION" && el.classList.contains("page");
    });
    if (pages.length < 2) return; // 1 ページしかないならページ送りは不要

    document.body.classList.add("js-paged");

    var current = 0;
    var pageLinks = [];   // 目次のページ項目
    var subLinkSets = []; // ページごとの第 2 階層リンク

    function titleOf(pg, i) {
      return pg.getAttribute("data-title") || ("ページ " + (i + 1));
    }

    /* ---------- id が無いページには連番を振る ---------- */
    pages.forEach(function (pg, i) {
      if (!pg.id) pg.id = "p" + (i + 1);
    });

    /* ---------- 目次を生成 ---------- */
    if (tocList) {
      tocList.innerHTML = "";
      pages.forEach(function (pg, i) {
        var li = document.createElement("li");

        var a = document.createElement("a");
        a.href = "#" + pg.id;
        a.className = "toc-page";
        var num = document.createElement("span");
        num.className = "toc-num";
        num.textContent = String(i + 1);
        a.appendChild(num);
        a.appendChild(document.createTextNode(titleOf(pg, i)));
        li.appendChild(a);
        pageLinks.push(a);

        // 第 2 階層：id が振られた h3 だけを拾う（章立てしたいページで id を付ける運用）
        var subs = Array.prototype.slice.call(pg.querySelectorAll("h3[id]"));
        var subLinks = [];
        if (subs.length) {
          var ul = document.createElement("ul");
          ul.className = "toc-sub";
          subs.forEach(function (h) {
            var sli = document.createElement("li");
            var sa = document.createElement("a");
            sa.href = "#" + h.id;
            sa.textContent = h.getAttribute("data-toc") || h.textContent;
            sli.appendChild(sa);
            ul.appendChild(sli);
            subLinks.push({ link: sa, heading: h });
          });
          li.appendChild(ul);
        }
        subLinkSets.push(subLinks);
        tocList.appendChild(li);
      });

      // 「全ページを表示」トグル
      var toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "toc-toggle";
      toggle.id = "toggle-all";
      toggle.setAttribute("aria-pressed", "false");
      toggle.textContent = "全ページを表示";
      toggle.addEventListener("click", function () {
        var on = !document.body.classList.contains("show-all");
        document.body.classList.toggle("show-all", on);
        toggle.setAttribute("aria-pressed", on ? "true" : "false");
        toggle.textContent = on ? "ページ送りに戻す" : "全ページを表示";
        if (on) {
          // 通し表示に切り替えたら、いま見ていたページの位置へ寄せる
          pages[current].scrollIntoView();
        } else {
          window.scrollTo(0, 0);
        }
      });
      tocList.parentNode.appendChild(toggle);
    }

    /* ---------- 前へ／次へ ---------- */
    var pager = document.createElement("nav");
    pager.className = "pager";
    pager.setAttribute("aria-label", "ページ送り");
    main.appendChild(pager);

    function buildPagerLink(idx, dir) {
      var a = document.createElement("a");
      a.href = "#" + pages[idx].id;
      a.className = dir === "prev" ? "pager__prev" : "pager__next";
      var d = document.createElement("span");
      d.className = "pager__dir";
      d.textContent = dir === "prev" ? "← 前へ" : "次へ →";
      var l = document.createElement("span");
      l.className = "pager__label";
      l.textContent = (idx + 1) + ". " + titleOf(pages[idx], idx);
      a.appendChild(d);
      a.appendChild(l);
      return a;
    }

    function updatePager() {
      pager.innerHTML = "";
      if (current > 0) pager.appendChild(buildPagerLink(current - 1, "prev"));
      else {
        var sp = document.createElement("span");
        sp.className = "pager__spacer";
        pager.appendChild(sp);
      }
      if (current < pages.length - 1) pager.appendChild(buildPagerLink(current + 1, "next"));
    }

    /* ---------- 表示切り替え ---------- */
    function updateToc() {
      pageLinks.forEach(function (a, i) {
        a.classList.toggle("active", i === current);
        if (a.parentNode) a.parentNode.classList.toggle("is-current", i === current);
      });
    }

    function showPage(idx, keepScroll) {
      if (idx < 0) idx = 0;
      if (idx > pages.length - 1) idx = pages.length - 1;
      current = idx;
      pages.forEach(function (p, i) { p.classList.toggle("is-active", i === idx); });
      updateToc();
      updatePager();
      updateSubSpy();
      if (!keepScroll) window.scrollTo(0, 0);
    }

    function pageIndexOf(el) {
      for (var i = 0; i < pages.length; i++) {
        if (pages[i] === el || pages[i].contains(el)) return i;
      }
      return -1;
    }

    function applyHash() {
      var id = (location.hash || "").replace(/^#/, "");
      var target = id ? document.getElementById(id) : null;
      var idx = target ? pageIndexOf(target) : -1;

      if (idx < 0) {
        // #top など、ページに属さないアンカー
        if (!document.body.classList.contains("show-all")) showPage(current);
        return;
      }
      var isPageItself = pages[idx] === target;
      if (document.body.classList.contains("show-all")) {
        // 通し表示中はスクロールするだけ。ページ送りへ戻したときに
        // 同じ位置から再開できるよう現在ページだけ更新しておく
        current = idx;
        updateToc();
        updatePager();
        target.scrollIntoView();
        return;
      }
      showPage(idx, !isPageItself);
      if (!isPageItself) target.scrollIntoView();
    }

    /* ---------- 表示中ページ内の中見出しハイライト ---------- */
    function updateSubSpy() {
      var subs = subLinkSets[current] || [];
      if (!subs.length) return;
      var pos = window.scrollY + 120;
      var activeIndex = -1;
      subs.forEach(function (s, i) {
        var top = s.heading.getBoundingClientRect().top + window.scrollY;
        if (top <= pos) activeIndex = i;
      });
      subs.forEach(function (s, i) { s.link.classList.toggle("active", i === activeIndex); });
    }

    window.addEventListener("hashchange", applyHash);
    window.addEventListener("scroll", updateSubSpy, { passive: true });

    // 初期表示：ハッシュがあればそのページ、無ければ 1 ページ目
    var startIdx = 0;
    var startId = (location.hash || "").replace(/^#/, "");
    if (startId) {
      var startEl = document.getElementById(startId);
      var i = startEl ? pageIndexOf(startEl) : -1;
      if (i >= 0) startIdx = i;
    }
    showPage(startIdx, true);
    if (startId) {
      var el = document.getElementById(startId);
      if (el && pages[startIdx] !== el) el.scrollIntoView();
    }
  }

  /* ============================================================ */
  function init() {
    initShotFallback();
    initCopyButtons();
    initPrintExpand();
    // 図の描画が終わってからページ送りへ（潰れた図が残らないようにする）
    initMermaid(initPager);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
