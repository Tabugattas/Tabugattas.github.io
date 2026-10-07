(function () {
  "use strict";
  var cfg = window.SITE_CONFIG || {};

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

  if (ytId) {
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
  } else if (cfg.musicFile) {
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
  function show(page) {
    var inv = page === "invitation";
    envelope.classList.toggle("is-active", !inv);
    invitation.classList.toggle("is-active", inv);
    envelope.classList.remove("is-opening", "is-leaving");
    window.scrollTo(0, 0);
    if (inv) { if (!playing) playMusic(); }
    else pauseMusic(true);
  }

  function route() { show(location.hash === "#invitation" ? "invitation" : "envelope"); }

  var opening = false;
  function openInvitation() {
    opening = false;
    if (location.hash !== "#invitation") history.pushState(null, "", "#invitation");
    show("invitation");
  }

  document.getElementById("open-invitation").addEventListener("click", function (e) {
    e.preventDefault();
    if (opening) return;
    playMusic(); // inside the click so the browser allows sound
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { openInvitation(); return; }
    opening = true;
    envelope.classList.add("is-opening");
    setTimeout(function () { envelope.classList.add("is-leaving"); }, 4000);
    setTimeout(openInvitation, 4700);
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
