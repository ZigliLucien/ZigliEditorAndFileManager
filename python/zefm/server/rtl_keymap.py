"""Original ZEFM Yiddish Alt keymap for browser RTL editing.

The mapping is read from the existing legacy keymap; the browser inserts
Unicode in logical order and handles bidirectional rendering.
"""
import json
from pathlib import Path

from ..editor.legacy_keymaps import read_keymap


def yiddish_keymap_json():
    source = Path(__file__).resolve().parents[2] / "legacy_keymaps" / "Yiddish.keymap"
    keymap = read_keymap(source)
    pairs = {f"{code}{suffix}": mapping.characters
             for (code, suffix), mapping in keymap.items() if suffix in ("", "S")}
    return json.dumps(pairs, ensure_ascii=False, sort_keys=True)


RTL_KEYMAP_JS = r"""
/* Original ZEFM Yiddish Alt mappings; never reverse the text itself. */
(() => {
  "use strict";
  const textarea = document.getElementById("zefm-rtl-content");
  const enabled = document.getElementById("zefm-yiddish-keymap");
  if (!textarea || !enabled) return;
  let map;
  try {
    map = JSON.parse(textarea.dataset.zefmKeymap || "{}");
  } catch (_) {
    return;
  }
  const punctuation = {
    BracketLeft: 91, BracketRight: 93, Semicolon: 59,
    Comma: 44, Period: 46, Slash: 47, Backslash: 92,
    Quote: 222, Minus: 45, Equal: 61
  };
  function javaKeyCode(code) {
    if (/^Key[A-Z]$/.test(code)) return code.charCodeAt(3);
    return Object.prototype.hasOwnProperty.call(punctuation, code)
      ? punctuation[code] : null;
  }
  textarea.addEventListener("keydown", (event) => {
    if (!enabled.checked || !event.altKey || event.ctrlKey ||
        event.metaKey || event.isComposing) return;
    const code = javaKeyCode(event.code || "");
    if (code === null) return;
    const key = String(code) + (event.shiftKey ? "S" : "");
    if (!Object.prototype.hasOwnProperty.call(map, key)) return;
    event.preventDefault();
    const insertion = map[key];
    textarea.setRangeText(insertion, textarea.selectionStart,
                          textarea.selectionEnd, "end");
    textarea.dispatchEvent(new Event("input", {bubbles: true}));
  });
})();
"""
