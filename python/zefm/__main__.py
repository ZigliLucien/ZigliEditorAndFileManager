"""Unified ZEFM launcher.

    python3 -m zefm --mode editor
    python3 -m zefm --mode files [--root DIR] [--port PORT]
    python3 -m zefm --mode both [--root DIR] [--port PORT]

Existing module entry points remain supported.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import threading
import webbrowser


def build_parser():
    parser = argparse.ArgumentParser(
        prog="python3 -m zefm",
        description="Launch the ZEFM editor, browser file manager, or both.")
    parser.add_argument(
        "--mode", "-m", choices=("editor", "files", "both"), default="editor",
        help="editor only (default), browser file manager only, or both")
    parser.add_argument(
        "--root", type=Path, default=None,
        help="file manager's root directory (default: home in files mode; "
             "editor's working directory in both mode)")
    parser.add_argument(
        "--port", type=int, default=0,
        help="loopback HTTP port for file manager (0: automatic)")
    parser.add_argument(
        "--no-browser", action="store_true",
        help="start file manager without automatically opening a browser tab")
    return parser


def launch_editor(*, root=None, port=0, with_files=False, open_browser=True):
    """Tk owns the main thread; HTTP workers communicate through its queue."""
    from .editor.gui.tk_editor import Window

    window = Window()
    window.root.protocol("WM_DELETE_WINDOW", window.quit)
    if with_files:
        window.open_local_file_manager(directory=root, port=port,
                                       open_browser=open_browser)
    window.root.mainloop()


def launch_files(*, root=None, port=0, open_browser=True):
    """Standalone HTTP manager: no tkinter import, no editor process."""
    from .server.http import BrowserServer

    directory = root if root is not None else Path.home()
    browser = BrowserServer(str(directory), port=port)
    try:
        address = browser.start() + "listing"
        print(f"ZEFM file manager: {address}", flush=True)
        if open_browser:
            webbrowser.open(address)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
    finally:
        browser.close()


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not 0 <= args.port <= 65535:
        build_parser().error("--port must be between 0 and 65535")
    if args.mode == "editor":
        if args.root is not None or args.port != 0 or args.no_browser:
            build_parser().error(
                "--root, --port and --no-browser apply only to files/both modes")
        launch_editor()
    elif args.mode == "files":
        launch_files(root=args.root, port=args.port,
                     open_browser=not args.no_browser)
    else:
        launch_editor(root=args.root, port=args.port, with_files=True,
                      open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
