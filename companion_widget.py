"""
Floating Interactive Desktop Companion Mascot for Agy IT Helper.
Sits right on the desktop as a living, breathing companion character.
Built with native GTK widgets for hardware-accelerated rendering and reliable visibility.
"""

import os
import math
import json
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

CONFIG_DIR = os.path.expanduser("~/.config/agy-helper")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

class CompanionWidget(Gtk.Window):
    def __init__(self, app_controller, on_click_callback=None):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.app_controller = app_controller
        self.on_click_callback = on_click_callback

        self.set_title("Agy Desktop Companion")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(False)
        self.set_keep_below(True)
        self.stick()
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        self.get_style_context().add_class("companion-window")

        # RGBA transparency
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # Asset paths
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.mascot_160 = os.path.join(assets_dir, "mascot-160.png")
        self.mascot_192 = os.path.join(assets_dir, "mascot-192.png")
        if not os.path.exists(self.mascot_160):
            self.mascot_160 = os.path.join(assets_dir, "mascot.png")
        if not os.path.exists(self.mascot_192):
            self.mascot_192 = self.mascot_160

        # Event Box Container
        self.event_box = Gtk.EventBox()
        self.event_box.set_visible_window(False)
        self.add(self.event_box)

        # Content Box
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.vbox.set_halign(Gtk.Align.CENTER)
        self.vbox.set_valign(Gtk.Align.CENTER)
        self.event_box.add(self.vbox)

        # 1. Speech Bubble Label
        self.lbl_bubble = Gtk.Label(label="Hi! Click me for IT help! 🚀")
        self.lbl_bubble.get_style_context().add_class("companion-bubble")
        self.lbl_bubble.set_margin_bottom(2)
        self.vbox.pack_start(self.lbl_bubble, False, False, 0)

        # 2. Mascot Image Widget
        self.img_mascot = Gtk.Image.new_from_file(self.mascot_160)
        self.vbox.pack_start(self.img_mascot, False, False, 0)

        # Interaction & Animation state
        self._is_hovered = False
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._click_start_pos = (0, 0)

        self._anim_phase = 0.0
        self._base_margin = 8

        # Connect mouse events to EventBox
        self.event_box.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.ENTER_NOTIFY_MASK
            | Gdk.EventMask.LEAVE_NOTIFY_MASK
        )

        self.event_box.connect("button-press-event", self.on_button_press)
        self.event_box.connect("button-release-event", self.on_button_release)
        self.event_box.connect("motion-notify-event", self.on_motion_notify)
        self.event_box.connect("enter-notify-event", self.on_enter_notify)
        self.event_box.connect("leave-notify-event", self.on_leave_notify)

        self.set_default_size(240, 260)

        # Position on desktop
        GLib.idle_add(self._restore_position)

        # Animation timer (floating bob effect)
        GLib.timeout_add(50, self._animate_step)

        # Periodic tips rotation every 10 seconds
        GLib.timeout_add(10000, self._cycle_speech_tip)

    def _restore_position(self):
        screen = self.get_screen()
        w = screen.get_width()
        h = screen.get_height()
        default_x = max(50, w - 260)
        default_y = max(50, h - 320)

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
                pos_x = cfg.get("companion_x", default_x)
                pos_y = cfg.get("companion_y", default_y)
                pos_x = max(10, min(w - 240, pos_x))
                pos_y = max(10, min(h - 260, pos_y))
                self.move(pos_x, pos_y)
                return False
            except Exception:
                pass

        self.move(default_x, default_y)
        return False

    def _save_position(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        cur_x, cur_y = self.get_position()
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    cfg = json.load(f)
            except Exception:
                pass
        cfg["companion_x"] = cur_x
        cfg["companion_y"] = cur_y
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def _animate_step(self):
        self._anim_phase += 0.09
        if self._anim_phase > 2 * math.pi:
            self._anim_phase -= 2 * math.pi

        # Float modulation
        offset = int(math.sin(self._anim_phase) * 5)
        self.img_mascot.set_margin_top(max(0, self._base_margin + offset))
        self.img_mascot.set_margin_bottom(max(0, self._base_margin - offset))
        return True

    def _cycle_speech_tip(self):
        if self._dragging or self._is_hovered:
            return True
        tips = [
            "Hi! Need IT help or advice? 🤖",
            "Click me to install apps! 📦",
            "Your personal files are safe! 🛡️",
            "Want me to check computer health? 💻",
            "Internet slow? I can fix it! ⚡",
            "Ask me anything about Linux! 💬",
            "Always here on your desktop! ✨",
        ]
        import random
        self.lbl_bubble.set_text(random.choice(tips))
        return True

    def on_enter_notify(self, widget, event):
        self._is_hovered = True
        self.lbl_bubble.set_text("Click me to open Agy! ✨")
        self.img_mascot.set_from_file(self.mascot_192)

        # Set pointer cursor
        display = Gdk.Display.get_default()
        if display:
            cursor = Gdk.Cursor.new_from_name(display, "pointer") or Gdk.Cursor.new_from_name(display, "hand")
            window = self.get_window()
            if window and cursor:
                window.set_cursor(cursor)

    def on_leave_notify(self, widget, event):
        self._is_hovered = False
        self.img_mascot.set_from_file(self.mascot_160)
        display = Gdk.Display.get_default()
        if display:
            window = self.get_window()
            if window:
                window.set_cursor(None)

    def on_button_press(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self._dragging = True
            self._drag_start_x = int(event.x_root)
            self._drag_start_y = int(event.y_root)
            self._click_start_pos = (event.x_root, event.y_root)
        elif event.button == Gdk.BUTTON_SECONDARY:
            self._show_context_menu(event)

    def on_button_release(self, widget, event):
        if event.button == Gdk.BUTTON_PRIMARY:
            self._dragging = False
            self._save_position()
            dx = abs(event.x_root - self._click_start_pos[0])
            dy = abs(event.y_root - self._click_start_pos[1])
            if dx < 6 and dy < 6:
                # Cheerful click feedback and open assistant window
                self.lbl_bubble.set_text("Opening Helper! 🚀")
                if self.on_click_callback:
                    self.on_click_callback()

    def on_motion_notify(self, widget, event):
        if self._dragging:
            cur_x, cur_y = self.get_position()
            dx = int(event.x_root) - self._drag_start_x
            dy = int(event.y_root) - self._drag_start_y
            self.move(cur_x + dx, cur_y + dy)
            self._drag_start_x = int(event.x_root)
            self._drag_start_y = int(event.y_root)

    def _show_context_menu(self, event):
        menu = Gtk.Menu()

        item_open = Gtk.MenuItem(label="💬 Open IT Helper Chat")
        item_open.connect("activate", lambda w: self.on_click_callback() if self.on_click_callback else None)
        menu.append(item_open)

        menu.append(Gtk.SeparatorMenuItem())

        item_fixes = Gtk.MenuItem(label="⚡ 1 Click Fixes")
        item_fixes.connect("activate", lambda w: self.app_controller.open_tab("fixes"))
        menu.append(item_fixes)

        item_apps = Gtk.MenuItem(label="📦 Install Applications")
        item_apps.connect("activate", lambda w: self.app_controller.open_tab("apps"))
        menu.append(item_apps)

        item_scam = Gtk.MenuItem(label="🛡️ Scam Help & Protection")
        item_scam.connect("activate", lambda w: self.app_controller.open_tab("scam"))
        menu.append(item_scam)

        item_health = Gtk.MenuItem(label="⚙️ System Safety & Health")
        item_health.connect("activate", lambda w: self.app_controller.open_tab("health"))
        menu.append(item_health)

        menu.append(Gtk.SeparatorMenuItem())

        item_quit = Gtk.MenuItem(label="❌ Quit Agy Helper")
        item_quit.connect("activate", lambda w: Gtk.main_quit())
        menu.append(item_quit)

        menu.show_all()
        menu.popup_at_pointer(event)
