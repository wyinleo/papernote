(() => {
  "use strict";

  const config = window.PAPERNOTE_ANALYTICS || {};
  const endpoint = String(config.goatcounterEndpoint || "");
  const allowedHosts = Array.isArray(config.allowedHosts) ? config.allowedHosts : [];
  const doNotTrack = navigator.doNotTrack === "1" || window.doNotTrack === "1";

  if (!endpoint || !allowedHosts.includes(window.location.hostname) || doNotTrack) {
    return;
  }

  const script = document.createElement("script");
  script.async = true;
  script.src = "https://gc.zgo.at/count.js";
  script.dataset.goatcounter = endpoint;
  script.referrerPolicy = "strict-origin-when-cross-origin";
  document.head.append(script);
})();
