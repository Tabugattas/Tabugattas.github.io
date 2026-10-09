(function () {
  "use strict";
 var cfg = window.SITE_CONFIG || {};

  // Warm up only the first screen immediately; external fonts/music must not
  // delay it, and decoding every later image competes with the opening animation.
  ["hero-background", "hero-photo"].forEach(function (name) {
    var image = new Image();
    image.fetchPriority = "high";
    image.src = "images/" + name + ".webp";
  });

  function loadSectionAssets(section) {
    section.querySelectorAll("[data-background]").forEach(function (el) {
      el.style.backgroundImage = 'url("' + el.dataset.background + '")';
      el.removeAttribute("data-background");
    });
    section.querySelectorAll("[data-src]").forEach(function (el) {
      if (el.tagName.toLowerCase() === "img") el.src = el.dataset.src;
      else el.setAttribute("href", el.dataset.src);
      el.removeAttribute("data-src");
    });
  }

  var panels = document.querySelectorAll("#page-invitation .panel");
  if ("IntersectionObserver" in window) {
    var assetObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        loadSectionAssets(entry.target);
        assetObserver.unobserve(entry.target);
      });
    }, { rootMargin: Math.max(window.innerHeight, 800) + "px 0px" });
    panels.forEach(function (panel) { assetObserver.observe(panel); });
  } else {
    panels.forEach(loadSectionAssets);
  }

  // Warm later sections in order after the hero decodes, rather than waiting
  // for a fast scroll to discover them. One decode at a time keeps Safari responsive.
  var heroImage = document.querySelector(".env-card img");
  var warmQueue = heroImage.decode ? heroImage.decode().catch(function () {}) : Promise.resolve();
  panels.forEach(function (panel) {
    panel.querySelectorAll("[data-background], [data-src]").forEach(function (el) {
      var src = el.dataset.background || el.dataset.src;
      warmQueue = warmQueue.then(function () {
        var image = new Image();
        image.fetchPriority = "low";
        image.src = src;
        return image.decode ? image.decode().catch(function () {}) : Promise.resolve();
      });
    });
    warmQueue = warmQueue.then(function () { loadSectionAssets(panel); });
  });

  var envelope = document.getElementById("page-envelope");
  var invitation = document.getElementById("page-invitation");
  var audio = document.getElementById("music");

  // ---------- Mailing address button ----------
  document.getElementById("mail-btn").href = cfg.mailingAddressUrl || "#";

  // ---------- Music ----------
  var ytId = parseYouTubeId(cfg.youtube || "");
  var ytPlayer = null, ytReady = false, wantPlay = false, playing = false, fadeTimer = null;
  var volume = typeof cfg.musicVolume === "number" ? cfg.musicVolume : 0.7;

  function parseYouTubeId(s) {
    s = String(s).trim();
    if (!s) return "";
    var m = s.match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/);
    return m ? m[1] : (/^[\w-]{11}$/.test(s) ? s : "");
  }

  var youtubeRequested = false;
  function loadYouTube() {
    if (youtubeRequested) return;
    youtubeRequested = true;
    window.onYouTubeIframeAPIReady = function () {
      ytPlayer = new YT.Player("yt-player", {
        width: 200, height: 200, videoId: ytId,
        playerVars: { autoplay: 0, controls: 0, loop: 1, playlist: ytId, playsinline: 1 },
        events: {
          onReady: function () {
            ytReady = true;
            ytPlayer.setVolume(Math.round(volume * 100));
            if (wantPlay) ytPlayer.playVideo();
          },
          onStateChange: function (e) {
            if (e.data === YT.PlayerState.PLAYING) setPlaying(true);
            else if (e.data === YT.PlayerState.PAUSED || e.data === YT.PlayerState.ENDED) setPlaying(false);
          }
        }
      });
    };
    var tag = document.createElement("script");
    tag.src = "https://www.youtube.com/iframe_api";
    document.head.appendChild(tag);
  }

  if (!ytId && cfg.musicFile) {
    audio.src = cfg.musicFile;
    audio.volume = volume;
  }

  function setPlaying(p) {
    playing = p;
  }

  function playMusic() {
    wantPlay = true;
    clearInterval(fadeTimer);
    if (ytId) {
      loadYouTube();
      if (ytReady) { ytPlayer.setVolume(Math.round(volume * 100)); ytPlayer.playVideo(); }
      return;
    }
    audio.volume = volume;
    var p = audio.play();
    if (p && p.then) {
      p.then(function () { setPlaying(true); })
       .catch(function () { setPlaying(false); armFirstInteraction(); });
    } else setPlaying(true);
  }

  function pauseMusic(fade) {
    wantPlay = false;
    clearInterval(fadeTimer);
    if (ytId) { if (ytReady) ytPlayer.pauseVideo(); setPlaying(false); return; }
    if (!fade || audio.paused) { audio.pause(); setPlaying(false); return; }
    fadeTimer = setInterval(function () {
      audio.volume = Math.max(0, audio.volume - volume / 12);
      if (audio.volume <= 0.001) { clearInterval(fadeTimer); audio.pause(); audio.volume = volume; }
    }, 50);
    setPlaying(false);
  }

  // Browsers block sound until the visitor interacts with the page. If the
  // invitation was opened directly (not via the envelope), start on first touch.
  var armed = false;
  function armFirstInteraction() {
    if (armed) return;
    armed = true;
    var start = function (e) {
      disarm();
      if (invitation.classList.contains("is-active") && !playing) playMusic();
    };
    var disarm = function () {
      armed = false;
      ["pointerdown", "keydown", "touchstart"].forEach(function (t) { document.removeEventListener(t, start, true); });
    };
    ["pointerdown", "keydown", "touchstart"].forEach(function (t) { document.addEventListener(t, start, true); });
  }

  window.weddingMusic = { isPlaying: function () { return playing; } };

  // ---------- Page switching ----------
  var opening = false, openingTimer = null;
  var card = envelope.querySelector(".env-card");
  var flap = envelope.querySelector(".flap-layer");
  var scenePrepared = false, sceneTimer = null;

  function prepareOpeningScene() {
    if (scenePrepared) return;
    scenePrepared = true;
    envelope.classList.add("is-prepared");
    invitation.classList.add("is-prepared");
    invitation.inert = true;
  }

  function queueOpeningScene() {
    clearTimeout(sceneTimer);
    sceneTimer = setTimeout(function () {
      if (!opening && envelope.classList.contains("is-active")) prepareOpeningScene();
    }, 200);
  }

  function show(page) {
    var inv = page === "invitation";
    clearTimeout(openingTimer);
    clearTimeout(sceneTimer);
    scenePrepared = false;
    opening = false;
    // Keep transitions disabled until the next opening. Flush the closed state
    // before revealing the envelope so no stale animation can paint behind the map.
    envelope.classList.add("no-anim");
    envelope.classList.remove("is-opening", "is-leaving", "is-prepared");
    // Apply the reset while Safari cannot paint the envelope.
    envelope.style.visibility = "hidden";
    void getComputedStyle(card).transform;
    void getComputedStyle(flap).transform;
    envelope.classList.toggle("is-active", !inv);
    invitation.classList.remove("is-revealing", "is-prepared");
    invitation.classList.toggle("is-active", inv);
    void envelope.offsetWidth;
    envelope.style.visibility = "";
    envelope.inert = inv;
    invitation.inert = !inv;
    window.scrollTo(0, 0);
    if (inv) { if (!playing) armFirstInteraction(); }
    else { pauseMusic(true); queueOpeningScene(); }
  }

  function route() {
    var h = location.hash.toLowerCase();
    show(h === "#savethedate2" || h === "#invitation" ? "invitation" : "envelope");
  }

  function openInvitation() {
    if (!opening) return;
    if (location.hash !== "#SavetheDate2") history.pushState(null, "", "#SavetheDate2");
    show("invitation");
  }

  document.getElementById("open-invitation").addEventListener("click", function (e) {
    e.preventDefault();
    if (opening) return;
    prepareOpeningScene();
    playMusic(); // inside the click so the browser allows sound
    opening = true;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { openInvitation(); return; }
    envelope.classList.remove("no-anim");
    // Flush the visible, prepared flap rather than a display:none card.
    // Matching perspective/rotation functions let WebKit interpolate the hinge.
    void getComputedStyle(flap).transform;
    void card.offsetWidth;
    // Render the destination underneath the envelope for the final crossfade.
    invitation.classList.remove("is-prepared");
    invitation.classList.add("is-active", "is-revealing");
    invitation.inert = true;
    envelope.classList.add("is-opening");
    // Fallback for browsers that fail to deliver animationend.
    var animation = getComputedStyle(card);
    var duration = parseFloat(animation.animationDuration) + parseFloat(animation.animationDelay);
    openingTimer = setTimeout(openInvitation, (duration * 1000) + 300);
  });

  envelope.addEventListener("animationend", function (e) {
    if (e.target === envelope && e.animationName === "envelopeHandoff") openInvitation();
  });

  document.getElementById("go-back").addEventListener("click", function (e) {
    e.preventDefault();
    history.pushState(null, "", location.pathname + location.search);
    show("envelope");
  });

  window.addEventListener("popstate", route);
  window.addEventListener("hashchange", route);
  route();

  // ---------- Countdown ----------
  var target = new Date(cfg.weddingDate || "2027-07-22T00:00:00+04:00").getTime();
  var els = ["days", "hours", "minutes", "seconds"].map(function (k) { return document.getElementById("cd-" + k); });
  function pad(n) { return n < 10 ? "0" + n : String(n); }
  function tick() {
    var diff = Math.max(0, target - Date.now());
    var s = Math.floor(diff / 1000);
    els[0].textContent = String(Math.floor(s / 86400));
    els[1].textContent = pad(Math.floor(s / 3600) % 24);
    els[2].textContent = pad(Math.floor(s / 60) % 60);
    els[3].textContent = pad(s % 60);
  }
  tick();
  setInterval(tick, 1000);
})();
