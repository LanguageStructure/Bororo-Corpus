(function () {
  "use strict";

  function initialize() {
    const panel = document.querySelector(".corbo-lex-pop");
    if (!panel) return;

    const desktop = window.matchMedia("(min-width: 900px)");

    function update() {
      if (desktop.matches) {
        panel.hidden = false;
      }
    }

    update();
    desktop.addEventListener("change", update);

    const observer = new MutationObserver(() => {
      if (desktop.matches && panel.hidden) {
        panel.hidden = false;
      }
    });

    observer.observe(panel, {
      attributes: true,
      attributeFilter: ["hidden"]
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }
})();
