#!/usr/bin/env python3
"""
Agy Desktop Companion & IT Helper Application.
Main entry point, single-instance lifecycle controller, and theme coordinator.
"""

import sys
import os
import socket
import threading
import argparse
import json

os.environ["GDK_BACKEND"] = "x11"

# Enrich PATH so all child processes and subprocesses can find agy and system tools
extra_paths = [
    os.path.expanduser("~/.gemini/antigravity/bin"),
    os.path.expanduser("~/.config/Antigravity/bin"),
    os.path.expanduser("~/.local/bin"),
    "/usr/local/sbin",
    "/usr/local/bin",
    "/usr/sbin",
    "/usr/bin",
    "/sbin",
    "/bin",
    "/snap/bin",
]
cur_path = os.environ.get("PATH", "")
cur_list = cur_path.split(":") if cur_path else []
all_paths = [p for p in extra_paths if p not in cur_list] + cur_list
os.environ["PATH"] = ":".join(all_paths)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from styles import apply_theme, get_current_theme
from companion_widget import CompanionWidget
from assistant_window import AssistantWindow

SOCKET_PATH = f"/tmp/agy_helper_{os.getuid()}.sock"
CONFIG_DIR = os.path.expanduser("~/.config/agy-helper")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class AgyHelperApp:
    def __init__(self, start_open_window=False, target_tab="chat"):
        self.start_open_window = start_open_window
        self.target_tab = target_tab

        # Enforce Light Mode Only
        apply_theme("light")

        # Initialize windows
        self.companion = CompanionWidget(self, on_click_callback=self.toggle_assistant_window)
        self.assistant = AssistantWindow(self)

        # Show companion on desktop
        self.companion.show_all()

        if self.start_open_window:
            self.assistant.select_tab(self.target_tab)
            self.assistant.show_and_focus()

        # Start IPC Server for single-instance management
        self._start_ipc_server()

    def toggle_assistant_window(self):
        if self.assistant.is_visible():
            self.assistant.hide()
        else:
            self.assistant.show_and_focus()

    def show_all_windows(self):
        self.companion.show_all()
        self.assistant.show_and_focus()

    def open_tab(self, tab_name: str):
        self.companion.show_all()
        self.assistant.select_tab(tab_name)
        self.assistant.show_and_focus()

    def toggle_theme(self):
        apply_theme("light")
        return "light"

    def _start_ipc_server(self):
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except OSError:
                pass

        try:
            self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_sock.bind(SOCKET_PATH)
            self.server_sock.listen(5)

            t = threading.Thread(target=self._ipc_listener, daemon=True)
            t.start()
        except Exception as e:
            print(f"Warning: Could not start IPC socket: {e}", file=sys.stderr)

    def _ipc_listener(self):
        while True:
            try:
                conn, _ = self.server_sock.accept()
                data = conn.recv(1024).decode("utf-8").strip()
                if data:
                    GLib.idle_add(self._handle_ipc_command, data)
                conn.sendall(b"OK\n")
                conn.close()
            except Exception:
                break

    def _handle_ipc_command(self, cmd_str: str):
        if cmd_str == "TOGGLE":
            self.toggle_assistant_window()
        elif cmd_str == "SHOW":
            self.show_all_windows()
        elif cmd_str.startswith("TAB:"):
            tab = cmd_str.split(":", 1)[1]
            self.open_tab(tab)
        return False


def send_ipc_command(cmd_str: str) -> bool:
    """Send command to existing instance if running. Returns True if handled."""
    if not os.path.exists(SOCKET_PATH):
        return False
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(SOCKET_PATH)
        s.sendall(cmd_str.encode("utf-8"))
        res = s.recv(1024)
        s.close()
        return True
    except Exception:
        # Socket is stale or unconnectable, clean it up
        try:
            os.remove(SOCKET_PATH)
        except OSError:
            pass
        return False


def main():
    parser = argparse.ArgumentParser(description="Agy IT Companion Desktop Helper")
    parser.add_argument("--open-window", action="store_true", help="Open assistant window on launch")
    parser.add_argument("--toggle", action="store_true", help="Toggle window if already running")
    parser.add_argument("--tab", choices=["chat", "fixes", "apps", "scam", "health"], default="chat", help="Open specific tab")
    parser.add_argument("--autostart", action="store_true", help="Started by autostart (starts in companion mode)")

    args = parser.parse_args()

    # Determine command to dispatch
    ipc_cmd = "SHOW"
    if args.toggle:
        ipc_cmd = "TOGGLE"
    elif args.open_window and args.tab != "chat":
        ipc_cmd = f"TAB:{args.tab}"
    elif args.open_window:
        ipc_cmd = "SHOW"

    # If instance is already running, send IPC command
    if send_ipc_command(ipc_cmd):
        print("Sent command to running Agy Companion instance.")
        sys.exit(0)

    # Set process name / app name
    GLib.set_prgname("agy-helper")
    GLib.set_application_name("Agy IT Helper")

    open_window = args.open_window and not args.autostart
    app = AgyHelperApp(start_open_window=open_window, target_tab=args.tab)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    finally:
        if os.path.exists(SOCKET_PATH):
            try:
                os.remove(SOCKET_PATH)
            except OSError:
                pass


if __name__ == "__main__":
    main()
