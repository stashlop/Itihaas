/**
 * Itihaas — shared front-end behaviour, loaded on every page.
 *
 *  - Adds the CSRF token to every same-origin state-changing fetch()/jQuery request.
 *  - Toast notifications (server flashes + window.Itihaas.toast()).
 *  - Graceful fallback for images whose file is missing.
 *  - Language switcher, password visibility toggles, submit loading states,
 *    quantity steppers.
 */
(function () {
  "use strict";

  var csrfMeta = document.querySelector('meta[name="csrf-token"]');
  var CSRF_TOKEN = csrfMeta ? csrfMeta.getAttribute("content") : "";
  var SAFE_METHODS = /^(GET|HEAD|OPTIONS|TRACE)$/i;

  function isSameOrigin(url) {
    try {
      return new URL(url, window.location.href).origin === window.location.origin;
    } catch (e) {
      return false;
    }
  }

  /* ---- CSRF for fetch() ------------------------------------------------ */
  if (window.fetch && CSRF_TOKEN) {
    var nativeFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
      init = init || {};
      var method = (init.method || (input && input.method) || "GET").toUpperCase();
      var url = typeof input === "string" ? input : input && input.url;
      if (!SAFE_METHODS.test(method) && isSameOrigin(url)) {
        var headers = new Headers(init.headers || (input && input.headers) || {});
        headers.set("X-CSRFToken", CSRF_TOKEN);
        init.headers = headers;
        if (!init.credentials) init.credentials = "same-origin";
      }
      return nativeFetch(input, init);
    };
  }

  /* ---- CSRF for jQuery ------------------------------------------------- */
  if (window.jQuery && CSRF_TOKEN) {
    window.jQuery.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!SAFE_METHODS.test(settings.type) && isSameOrigin(settings.url)) {
          xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
        }
      }
    });
  }

  /* ---- HTML escaping helper for pages that build markup ---------------- */
  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function safeUrl(value) {
    try {
      var url = new URL(value, window.location.href);
      return /^https?:$/.test(url.protocol) ? url.href : "#";
    } catch (e) {
      return "#";
    }
  }

  /* ---- Toasts ---------------------------------------------------------- */
  var ICONS = { success: "fa-check-circle", error: "fa-exclamation-circle", info: "fa-info-circle" };

  function toastContainer() {
    var el = document.querySelector(".ih-toasts");
    if (!el) {
      el = document.createElement("div");
      el.className = "ih-toasts";
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    return el;
  }

  function dismiss(toast) {
    if (!toast || toast.classList.contains("is-leaving")) return;
    toast.classList.add("is-leaving");
    setTimeout(function () { toast.remove(); }, 260);
  }

  function wireToast(toast) {
    var close = toast.querySelector(".ih-toast-close");
    if (close) close.addEventListener("click", function () { dismiss(toast); });
    var timeout = toast.classList.contains("ih-toast--error") ? 9000 : 5000;
    var timer = setTimeout(function () { dismiss(toast); }, timeout);
    toast.addEventListener("mouseenter", function () { clearTimeout(timer); });
    toast.addEventListener("mouseleave", function () { timer = setTimeout(function () { dismiss(toast); }, 2500); });
  }

  function toast(message, type) {
    type = ICONS[type] ? type : "info";
    var el = document.createElement("div");
    el.className = "ih-toast ih-toast--" + type;
    el.setAttribute("role", type === "error" ? "alert" : "status");
    el.innerHTML =
      '<i class="fas ' + ICONS[type] + ' ih-toast-icon" aria-hidden="true"></i>' +
      '<div class="ih-toast-body">' + escapeHtml(message) + "</div>" +
      '<button type="button" class="ih-toast-close" aria-label="Dismiss">&times;</button>';
    toastContainer().appendChild(el);
    wireToast(el);
    return el;
  }

  /* ---- Missing images -------------------------------------------------- */
  function handleMissingImage(img) {
    // Map tiles and opted-out images manage their own failures.
    if (img.dataset.fallbackApplied || img.classList.contains("leaflet-tile") || img.hasAttribute("data-no-fallback")) return;
    img.dataset.fallbackApplied = "1";
    img.classList.add("img-missing");
    img.removeAttribute("srcset");
    img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
  }

  // Capture phase catches errors from images added later too.
  document.addEventListener("error", function (event) {
    var target = event.target;
    if (target && target.tagName === "IMG") handleMissingImage(target);
    if (target && (target.tagName === "VIDEO" || target.tagName === "SOURCE")) {
      var video = target.tagName === "VIDEO" ? target : target.parentElement;
      // A video with a poster keeps showing the poster image; only hide posterless ones.
      if (video && !video.getAttribute("poster")) video.classList.add("media-missing");
    }
  }, true);

  /* ---- Language switcher ----------------------------------------------- */
  function changeLanguage(lang, event) {
    if (event) event.preventDefault();
    fetch("/change-language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang: lang })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("language");
        window.location.reload();
      })
      .catch(function () { toast("Could not change language. Please try again.", "error"); });
  }

  document.addEventListener("click", function (event) {
    var langLink = event.target.closest("[data-lang]");
    if (langLink) changeLanguage(langLink.getAttribute("data-lang"), event);

    var toggle = event.target.closest(".ih-password-toggle");
    if (toggle) {
      var input = toggle.parentElement.querySelector("input");
      var showing = input.type === "text";
      input.type = showing ? "password" : "text";
      toggle.setAttribute("aria-pressed", String(!showing));
      toggle.setAttribute("aria-label", showing ? "Show password" : "Hide password");
      var icon = toggle.querySelector("i");
      if (icon) icon.className = showing ? "fas fa-eye" : "fas fa-eye-slash";
    }

    var step = event.target.closest("[data-qty-step]");
    if (step) {
      var field = step.closest(".ih-qty").querySelector("input");
      var next = (parseInt(field.value, 10) || 0) + parseInt(step.getAttribute("data-qty-step"), 10);
      var min = parseInt(field.min || "0", 10);
      var max = parseInt(field.max || "999", 10);
      field.value = Math.max(min, Math.min(max, next));
      field.dispatchEvent(new Event("change", { bubbles: true }));
    }
  });

  /* ---- Submit buttons show a loading state ----------------------------- */
  document.addEventListener("submit", function (event) {
    var form = event.target;
    if (event.defaultPrevented || !form.matches("form[data-loading]")) return;
    var button = form.querySelector('[type="submit"]');
    if (!button) return;
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.innerHTML = '<span class="spinner" aria-hidden="true"></span> ' + escapeHtml(form.getAttribute("data-loading") || "Please wait…");
  });

  /* ---- Boot ------------------------------------------------------------ */
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".ih-toast").forEach(wireToast);
    document.querySelectorAll("img").forEach(function (img) {
      if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) handleMissingImage(img);
    });
  });

  // Back/forward cache restores disabled buttons — re-enable them.
  window.addEventListener("pageshow", function (event) {
    if (!event.persisted) return;
    document.querySelectorAll('[aria-busy="true"]').forEach(function (button) {
      button.disabled = false;
      button.removeAttribute("aria-busy");
    });
  });

  window.Itihaas = { toast: toast, escapeHtml: escapeHtml, safeUrl: safeUrl, csrfToken: CSRF_TOKEN };
  // Backwards compatibility for inline handlers in older templates.
  window.changeLanguage = changeLanguage;
})();
