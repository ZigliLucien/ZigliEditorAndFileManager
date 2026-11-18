"""Open ZEFM URLs with a real browser, not a desktop text-editor association.

On Linux, Python's webbrowser default can follow BROWSER=emacs (or an
xdg-open association to Emacs). Prefer installed graphical browsers
directly. Never shell-evaluate a URL, program name, or configuration.
"""
import os
import shutil
import subprocess
import sys
from urllib.parse import urlsplit


BROWSERS = (
    "firefox", "qutebrowser", "chromium", "chromium-browser",
    "google-chrome", "brave-browser", "vivaldi", "epiphany",
)


def browser_command(url, platform=None, which=None, environ=None):
    """Return argv for an available browser, without invoking a shell."""
    platform = sys.platform if platform is None else platform
    which = shutil.which if which is None else which
    environ = os.environ if environ is None else environ
    if not isinstance(url, str) or urlsplit(url).scheme not in ("http", "https", "file"):
        raise ValueError("Only local-file and HTTP(S) browser URLs are supported")
    # Explicit opt-in: a bare executable name/path, not a shell command.
    preferred = environ.get("ZEFM_BROWSER", "").strip()
    if preferred:
        if any(c.isspace() for c in preferred):
            raise ValueError("ZEFM_BROWSER must be a browser executable, not a command line")
        executable = which(preferred)
        if not executable:
            raise ValueError(f"ZEFM_BROWSER executable not found: {preferred}")
        return [executable, url]
    if platform == "darwin":
        # Safari is explicitly selected; the default handler for local HTML
        # may have been configured as an editor.
        opener = which("open") or "/usr/bin/open"
        return [opener, "-a", "Safari", url]
    if platform.startswith("linux") or platform.startswith("freebsd"):
        for name in BROWSERS:
            executable = which(name)
            if executable:
                return [executable, url]
        raise ValueError(
            "No graphical browser found. Install Firefox or qutebrowser, "
            "or set ZEFM_BROWSER to an installed browser executable.")
    # Other platforms rely on a registered browser rather than a local
    # document's file association.
    raise ValueError("No browser launcher configured for this platform")


def open_browser(url):
    """Start a browser without blocking Tk; raise when launch fails."""
    argv = browser_command(url)
    try:
        subprocess.Popen(
            argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as exc:
        raise ValueError(f"Unable to launch browser {argv[0]}: {exc}") from exc
    return True
