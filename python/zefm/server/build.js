/* Launch a guarded ZEFM document build from its own browser tab. */
(() => {
  "use strict";
  const form = document.getElementById("zefm-build-form");
  const status = document.getElementById("zefm-build-status");
  const log = document.getElementById("zefm-build-log");
  const go = document.getElementById("zefm-build-button");
  if (!form || !status || !log || !go) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (go.disabled) return;
    go.disabled = true;
    status.textContent = "Compiling document…";
    log.textContent = "";
    try {
      const response = await fetch("/build", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        body: new URLSearchParams(new FormData(form)),
        headers: {"Content-Type": "application/x-www-form-urlencoded"}
      });
      const raw = await response.text();
      let result;
      try { result = JSON.parse(raw); }
      catch (_) { throw new Error("Build server error (HTTP " + response.status + ")"); }
      log.textContent = result.log || result.error || "";
      if (response.ok && result.ok && result.pdf) {
        status.textContent = "Compilation succeeded. Opening generated PDF…";
        // Do not use arbitrary URLs: the server returns a confined root-relative path.
        location.href = "/pdf?" + new URLSearchParams({path: result.pdf});
      } else {
        status.textContent = "Compilation failed; review the diagnostics below.";
      }
    } catch (error) {
      status.textContent = "Build request failed: " + String(error.message || error);
    } finally {
      go.disabled = false;
    }
  });
})();
