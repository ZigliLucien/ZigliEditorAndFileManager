/* Local-only iCalendar file picker. No third-party scripts or network calls. */
(function () {
  "use strict";
  const input = document.getElementById("ical-file");
  const source = document.getElementById("ical-source");
  if (!input || !source) return;
  input.addEventListener("change", async function () {
    const file = input.files && input.files[0];
    if (!file) return;
    if (file.size > 128 * 1024) {
      source.setCustomValidity("iCalendar file exceeds 128 KiB");
      source.reportValidity();
      return;
    }
    try {
      const contents = await file.text();
      if (contents.includes("\u0000")) {
        source.setCustomValidity("Not a valid text-based iCalendar file");
        source.reportValidity();
        return;
      }
      source.value = contents;
      source.setCustomValidity("");
    } catch (_) {
      source.setCustomValidity("Cannot read selected iCalendar file");
      source.reportValidity();
    }
  });
  source.addEventListener("input", function () { source.setCustomValidity(""); });
})();
