"""Small Unicode click-pad for mathematical and multilingual editing.

The palette inserts through the live Tk Text widget, preserving its native
Undo stack. It does not change the system keyboard layout or read files.
"""

PALETTES = {
    "Math": ("α", "β", "γ", "δ", "θ", "λ", "μ", "π", "σ", "φ",
             "∑", "∏", "∫", "∂", "∇", "∞", "√", "≤", "≥", "≠",
             "∈", "∉", "⊂", "⊆", "→", "↦", "⇒", "∀", "∃", "ℝ"),
    "LaTeX": (r"\alpha", r"\beta", r"\gamma", r"\delta", r"\theta",
               r"\lambda", r"\mu", r"\pi", r"\sigma", r"\phi",
               r"\sum", r"\prod", r"\int", r"\partial", r"\nabla",
               r"\infty", r"\sqrt{}", r"\leq", r"\geq", r"\neq",
               r"\in", r"\subset", r"\subseteq", r"\to",
               r"\mapsto", r"\Rightarrow", r"\forall", r"\exists"),
    "Yiddish": ("א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י",
                "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר",
                "ש", "ת", "ך", "ם", "ן", "ף", "ץ", "װ", "ױ", "ײ"),
}


def palette_for(mode_name: str, language_name: str = "") -> str:
    """Select a sensible default without mutating the user's keymap."""
    if language_name.lower() in ("yiddish", "yi"):
        return "Yiddish"
    if mode_name.lower() in ("latex", "tex"):
        return "LaTeX"
    return "Math"
