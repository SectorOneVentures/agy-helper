"""
Main IT Helper Assistant Window for Agy Companion.
Features a modern iOS-styled interface, Dark/Light Mode, single native titlebar,
Gemini 3.7 Flash AI Chat, 1-Click IT Fixes, Software Installer, and Safety Monitor.
"""

import os
import re
import time
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango

from safety_engine import check_command_safety, get_protected_paths_summary
from agy_client import AgyClient, DEFAULT_MODEL, DEFAULT_EFFORT, check_agy_connection
from styles import apply_theme, zoom_in, zoom_out, get_scale_percentage
from system_tools import (
    APP_CATALOG,
    QUICK_FIXES,
    check_app_installed,
    get_system_health,
    run_command_safe_async,
    launch_app_async,
)

class AssistantWindow(Gtk.Window):
    def __init__(self, app_controller):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.app_controller = app_controller

        self.set_title("Agy IT Helper & Companion")
        self.set_default_size(800, 700)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.get_style_context().add_class("assistant-window")

        # Set Window Icon
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        icon_path = os.path.join(assets_dir, "icon-128.png")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)

        # AI Client & Query State
        self.ai_client = AgyClient(model=DEFAULT_MODEL, effort=DEFAULT_EFFORT)
        self._is_query_running = False
        self._typing_dots_count = 0
        self._typing_timer_id = None
        self._typing_bubble = None
        self._typing_label = None

        # 1. Single Native CSD Titlebar (Fixes duplicate close button!)
        header = self._create_header_bar(assets_dir)
        self.set_titlebar(header)

        # Main Layout
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # 2. Segmented Navigation Tab Bar
        nav_bar = self._create_nav_bar()
        main_vbox.pack_start(nav_bar, False, False, 0)

        # 3. Notebook Stack (Tabs) wrapped in Overlay for Floating Scroll Arrows
        self.notebook_overlay = Gtk.Overlay()

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.notebook.set_show_border(False)
        self.notebook_overlay.add(self.notebook)

        # Create Tab Pages
        self.page_chat = self._build_chat_tab(assets_dir)
        self.page_fixes = self._build_fixes_tab()
        self.page_apps = self._build_apps_tab()
        self.page_scam = self._build_scam_tab()
        self.page_health = self._build_health_tab()

        self.notebook.append_page(self.page_chat, Gtk.Label(label="Chat"))
        self.notebook.append_page(self.page_fixes, Gtk.Label(label="Fixes"))
        self.notebook.append_page(self.page_apps, Gtk.Label(label="Apps"))
        self.notebook.append_page(self.page_scam, Gtk.Label(label="Scam Help"))
        self.notebook.append_page(self.page_health, Gtk.Label(label="Health"))

        self.scroll_pages = [self.chat_scroll, self.fixes_scroll, self.apps_scroll, self.scam_scroll, self.health_scroll]

        # Floating Up Arrow (Top-Right of Tab Window)
        self.up_revealer = Gtk.Revealer()
        self.up_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.up_revealer.set_halign(Gtk.Align.END)
        self.up_revealer.set_valign(Gtk.Align.START)
        self.up_revealer.set_margin_end(20)
        self.up_revealer.set_margin_top(12)
        self.btn_scroll_up = Gtk.Button(label="⬆")
        self.btn_scroll_up.get_style_context().add_class("floating-scroll-btn")
        self.btn_scroll_up.set_tooltip_text("Scroll to Top")
        self.btn_scroll_up.connect("clicked", lambda b: self._scroll_current_tab_to_top())
        self.up_revealer.add(self.btn_scroll_up)
        self.notebook_overlay.add_overlay(self.up_revealer)

        # Floating Down Arrow (Bottom-Right of Tab Window)
        self.down_revealer = Gtk.Revealer()
        self.down_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.down_revealer.set_halign(Gtk.Align.END)
        self.down_revealer.set_valign(Gtk.Align.END)
        self.down_revealer.set_margin_end(20)
        self.down_revealer.set_margin_bottom(16)
        self.btn_scroll_down = Gtk.Button(label="⬇")
        self.btn_scroll_down.get_style_context().add_class("floating-scroll-btn")
        self.btn_scroll_down.set_tooltip_text("Scroll to Bottom")
        self.btn_scroll_down.connect("clicked", lambda b: self._scroll_current_tab_to_bottom())
        self.down_revealer.add(self.btn_scroll_down)
        self.notebook_overlay.add_overlay(self.down_revealer)

        for sw in self.scroll_pages:
            adj = sw.get_vadjustment()
            adj.connect("value-changed", lambda a: self._update_floating_scroll_arrows())
            adj.connect("changed", lambda a: self._update_floating_scroll_arrows())

        main_vbox.pack_start(self.notebook_overlay, True, True, 0)

        # 4. Terminal Log Drawer at Bottom
        self.log_revealer, self.log_text_view = self._create_terminal_drawer()
        main_vbox.pack_end(self.log_revealer, False, False, 0)

        # Hide on close instead of destroying
        self.connect("delete-event", self._on_delete_event)

        # Welcome message, initial connection check, and initial scroll arrow check
        GLib.idle_add(self._add_welcome_chat)
        GLib.idle_add(self._check_initial_connection)
        GLib.timeout_add(200, self._update_floating_scroll_arrows)

    def show_and_focus(self):
        """Cleanly raise and focus the assistant window."""
        self.show_all()
        self.deiconify()
        t = int(time.time())
        self.present_with_time(t)

    def _on_delete_event(self, widget, event):
        self.hide()
        return True

    def _create_header_bar(self, assets_dir):
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.get_style_context().add_class("ios-header")

        # App Icon & Title
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        icon_path = os.path.join(assets_dir, "icon-48.png")
        if os.path.exists(icon_path):
            img = Gtk.Image.new_from_file(icon_path)
            title_box.pack_start(img, False, False, 0)

        label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_title = Gtk.Label(label="Agy IT Companion")
        lbl_title.get_style_context().add_class("header-title")
        lbl_title.set_xalign(0)
        lbl_sub = Gtk.Label(label="Gemini 3.7 Flash • Friendly IT Tech Support")
        lbl_sub.get_style_context().add_class("header-subtitle")
        lbl_sub.set_xalign(0)
        label_box.pack_start(lbl_title, False, False, 0)
        label_box.pack_start(lbl_sub, False, False, 0)
        title_box.pack_start(label_box, False, False, 0)

        header.set_custom_title(title_box)

        # Left side control: Google AGY Connection Status Pill
        self.btn_conn_status = Gtk.Button(label="🟢 AGY Connected")
        self.btn_conn_status.get_style_context().add_class("status-pill-green")
        self.btn_conn_status.connect("clicked", lambda b: self._show_agy_troubleshooter_dialog())
        header.pack_start(self.btn_conn_status)

        # Right side controls
        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Zoom Accessibility Controls (Senior Friendly Font Scaling)
        zoom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        btn_zoom_out = Gtk.Button(label="A-")
        btn_zoom_out.get_style_context().add_class("zoom-btn")
        btn_zoom_out.set_tooltip_text("Make text smaller")
        btn_zoom_out.connect("clicked", self._on_zoom_out)

        self.lbl_zoom = Gtk.Label(label=get_scale_percentage())
        self.lbl_zoom.get_style_context().add_class("zoom-label")

        btn_zoom_in = Gtk.Button(label="A+")
        btn_zoom_in.get_style_context().add_class("zoom-btn")
        btn_zoom_in.set_tooltip_text("Make text larger (Senior Visibility Mode)")
        btn_zoom_in.connect("clicked", self._on_zoom_in)

        zoom_box.pack_start(btn_zoom_out, False, False, 0)
        zoom_box.pack_start(self.lbl_zoom, False, False, 0)
        zoom_box.pack_start(btn_zoom_in, False, False, 0)
        right_box.pack_start(zoom_box, False, False, 0)

        # Shield badge
        lbl_shield = Gtk.Label(label="🛡️ Files Safe")
        lbl_shield.get_style_context().add_class("shield-pill-green")
        right_box.pack_start(lbl_shield, False, False, 0)

        # Model badge
        lbl_model = Gtk.Label(label="⚡ Gemini 3.7 Flash")
        lbl_model.get_style_context().add_class("shield-pill-blue")
        right_box.pack_start(lbl_model, False, False, 0)

        header.pack_end(right_box)
        return header

    def _create_nav_bar(self):
        box_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        box_wrapper.set_halign(Gtk.Align.CENTER)
        box_wrapper.set_margin_top(8)
        box_wrapper.set_margin_bottom(8)

        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        tab_box.get_style_context().add_class("ios-tab-bar")

        self.tab_buttons = []
        tabs = [
            ("💬 Ask Agy (AI Chat)", 0),
            ("⚡ 1 Click Fixes", 1),
            ("📦 App Installer", 2),
            ("🛡️ Scam Help", 3),
            ("⚙️ Safety & Health", 4),
        ]

        group = None
        for label, idx in tabs:
            btn = Gtk.RadioButton.new_with_label_from_widget(group, label)
            btn.set_mode(False)
            btn.get_style_context().add_class("ios-tab-btn")
            btn.connect("toggled", self._on_tab_toggled, idx)
            tab_box.pack_start(btn, False, False, 0)
            self.tab_buttons.append(btn)
            if group is None:
                group = btn
                btn.set_active(True)

        box_wrapper.pack_start(tab_box, False, False, 0)
        return box_wrapper

    def _on_tab_toggled(self, btn, page_idx):
        if btn.get_active():
            self.notebook.set_current_page(page_idx)
            if page_idx == 4:
                self._refresh_health_tab()
            GLib.idle_add(self._update_floating_scroll_arrows)
            GLib.timeout_add(100, self._update_floating_scroll_arrows)

    def select_tab(self, tab_name: str):
        mapping = {"chat": 0, "fixes": 1, "apps": 2, "scam": 3, "health": 4}
        idx = mapping.get(tab_name, 0)
        if idx < len(self.tab_buttons):
            self.tab_buttons[idx].set_active(True)

    def _get_current_scrolled_window(self):
        page_idx = self.notebook.get_current_page()
        if 0 <= page_idx < len(self.scroll_pages):
            return self.scroll_pages[page_idx]
        return None

    def _update_floating_scroll_arrows(self):
        """Monitors scroll position of active tab and reveals down/up arrows gracefully."""
        sw = self._get_current_scrolled_window()
        if not sw or not hasattr(self, 'down_revealer') or not hasattr(self, 'up_revealer'):
            return False

        adj = sw.get_vadjustment()
        val = adj.get_value()
        upper = adj.get_upper()
        page_size = adj.get_page_size()
        max_scroll = max(0, upper - page_size)

        if max_scroll > 20:
            show_down = (val < max_scroll - 20)
            show_up = (val > 25)
        else:
            show_down = False
            show_up = False

        self.down_revealer.set_reveal_child(show_down)
        self.up_revealer.set_reveal_child(show_up)
        return False

    def _scroll_current_tab_to_bottom(self):
        sw = self._get_current_scrolled_window()
        if sw:
            adj = sw.get_vadjustment()
            target = max(0, adj.get_upper() - adj.get_page_size())
            adj.set_value(target)
            GLib.idle_add(self._update_floating_scroll_arrows)

    def _scroll_current_tab_to_top(self):
        sw = self._get_current_scrolled_window()
        if sw:
            adj = sw.get_vadjustment()
            adj.set_value(adj.get_lower())
            GLib.idle_add(self._update_floating_scroll_arrows)

    # -------------------------------------------------------------
    # TAB 1: Chat Assistant
    # -------------------------------------------------------------
    def _build_chat_tab(self, assets_dir):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)
        vbox.set_margin_bottom(12)

        # Suggestions Bar
        suggestions_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        suggestions_box.set_margin_bottom(4)
        quick_questions = [
            "Why is my internet slow?",
            "Fix my audio/sound",
            "Free up disk space safely",
            "Explain what RAM does",
            "Check computer health",
        ]
        for q in quick_questions:
            chip = Gtk.Button(label=q)
            chip.get_style_context().add_class("suggestion-chip")
            chip.connect("clicked", lambda b, query=q: self._send_user_query(query))
            suggestions_box.pack_start(chip, False, False, 0)

        sugg_scroll = Gtk.ScrolledWindow()
        sugg_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        sugg_scroll.set_min_content_height(38)
        sugg_scroll.add(suggestions_box)
        vbox.pack_start(sugg_scroll, False, False, 0)

        # Chat History Scroll Window
        self.chat_scroll = Gtk.ScrolledWindow()
        self.chat_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.chat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.chat_box.set_margin_top(8)
        self.chat_box.set_margin_bottom(8)
        self.chat_box.connect("size-allocate", self._on_chat_size_allocate)
        self.chat_scroll.add(self.chat_box)
        vbox.pack_start(self.chat_scroll, True, True, 0)

        # Input Bar Area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.entry_chat = Gtk.Entry()
        self.entry_chat.set_placeholder_text("Ask any computer question or give me an IT task...")
        self.entry_chat.get_style_context().add_class("chat-entry")
        self.entry_chat.connect("activate", lambda e: self._send_user_query(self.entry_chat.get_text()))
        input_box.pack_start(self.entry_chat, True, True, 0)

        self.btn_send = Gtk.Button(label="Ask Agy 🚀")
        self.btn_send.get_style_context().add_class("ios-btn-primary")
        self.btn_send.set_valign(Gtk.Align.CENTER)
        self.btn_send.set_size_request(130, 38)
        self.btn_send.connect("clicked", lambda b: self._send_user_query(self.entry_chat.get_text()))
        input_box.pack_start(self.btn_send, False, False, 0)

        vbox.pack_start(input_box, False, False, 0)
        return vbox

    def _add_welcome_chat(self):
        welcome_text = (
            "👋 **Hi there! I'm Agy, your friendly desktop companion.**\n\n"
            "I'm here to make using your computer easy, stress-free, and fun!\n\n"
            "• You don't need to know anything about Linux or technical commands.\n"
            "• Just type what you'd like to do or ask a question in plain English.\n"
            "• **Safety Promise:** Your personal **Documents, Music, and Pictures** are 100% shielded and will **never** be deleted.\n\n"
            "How can I help you today?"
        )
        self._add_message_bubble(welcome_text, is_user=False)
        return False

    def _add_message_bubble(self, text: str, is_user: bool = False, actions: list = None):
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        bubble_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        if is_user:
            bubble_box.get_style_context().add_class("chat-bubble-user")
            bubble_box.set_halign(Gtk.Align.END)
        else:
            bubble_box.get_style_context().add_class("chat-bubble-assistant")
            bubble_box.set_halign(Gtk.Align.START)

        # Label with markup
        lbl = Gtk.Label()
        lbl.set_line_wrap(True)
        lbl.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        lbl.set_max_width_chars(60)
        lbl.set_xalign(0)

        formatted = self._format_markdown_for_pango(text)
        lbl.set_markup(formatted)
        bubble_box.pack_start(lbl, False, False, 0)

        # Action Cards
        if actions:
            for act in actions:
                card = self._create_action_card(act)
                bubble_box.pack_start(card, False, False, 4)

        row_box.pack_start(bubble_box, False, False, 0)
        self.chat_box.pack_start(row_box, False, False, 0)
        self.chat_box.show_all()

        self._scroll_to_bottom()

    def _on_chat_size_allocate(self, widget, allocation):
        """Automatically called whenever chat items change size or are added."""
        adj = self.chat_scroll.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def _scroll_chat_bottom(self):
        adj = self.chat_scroll.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        return False

    def _scroll_to_bottom(self):
        """Ensures the scroll bar pushes immediately and accurately to the latest chat response."""
        adj = self.chat_scroll.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())
        GLib.idle_add(self._scroll_chat_bottom)
        GLib.timeout_add(30, self._scroll_chat_bottom)
        GLib.timeout_add(100, self._scroll_chat_bottom)

    def _format_markdown_for_pango(self, text: str) -> str:
        t = GLib.markup_escape_text(text)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"`([^`]+)`", r"<tt>\1</tt>", t)
        t = re.sub(r"^• (.+)$", r"  • \1", t, flags=re.MULTILINE)
        return t

    def _create_action_card(self, act_info: dict):
        cmd = act_info.get("command", "")
        is_safe, safety_msg, _ = check_command_safety(cmd)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.get_style_context().add_class("ios-card-inner")

        lbl_head = Gtk.Label()
        if is_safe:
            lbl_head.set_markup("<b>⚡ Recommended Automated Action</b> (Verified Safe)")
        else:
            lbl_head.set_markup("<span color='#FF453A'><b>🚫 Blocked Unsafe Action</b></span>")
        lbl_head.set_xalign(0)
        card.pack_start(lbl_head, False, False, 0)

        # Friendly explanation for everyday users
        lbl_desc = Gtk.Label(label="Agy can safely carry out this computer task for you in 1 click.")
        lbl_desc.set_line_wrap(True)
        lbl_desc.set_xalign(0)
        lbl_desc.get_style_context().add_class("header-subtitle")
        card.pack_start(lbl_desc, False, False, 0)

        if is_safe:
            btn_exec = Gtk.Button(label="▶️ Run Safe Action Now")
            btn_exec.set_valign(Gtk.Align.CENTER)
            btn_exec.set_size_request(180, 38)
            btn_exec.get_style_context().add_class("ios-btn-primary")
            btn_exec.connect("clicked", lambda b, c=cmd: self._execute_safe_task(c, btn_exec))
            card.pack_start(btn_exec, False, False, 0)
        else:
            lbl_warn = Gtk.Label()
            lbl_warn.set_markup(f"<small color='#FF453A'>{safety_msg}</small>")
            lbl_warn.set_line_wrap(True)
            lbl_warn.set_xalign(0)
            card.pack_start(lbl_warn, False, False, 0)

        # Technical details disclosure (hidden by default so seniors & everyday users are not intimidated)
        expander = Gtk.Expander(label="🔍 Show Technical Command Details")
        lbl_cmd = Gtk.Label(label=f"$ {cmd}")
        lbl_cmd.set_line_wrap(True)
        lbl_cmd.set_xalign(0)
        lbl_cmd.get_style_context().add_class("terminal-box")
        expander.add(lbl_cmd)
        card.pack_start(expander, False, False, 0)

        return card

    def _start_typing_indicator(self):
        """Shows typing animation and sets Ask Agy button to 'Replying...' in white font."""
        self._is_query_running = True
        self._typing_dots_count = 1

        # Keep Ask Agy button exactly in place, fixed size, white font
        self.btn_send.set_label("Replying...")
        self.btn_send.set_sensitive(False)

        # 1. Animated typing bubble in chat
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bubble_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bubble_box.get_style_context().add_class("chat-bubble-typing")
        bubble_box.set_halign(Gtk.Align.START)

        self._typing_label = Gtk.Label(label="Agy is replying.")
        self._typing_label.set_xalign(0)
        bubble_box.pack_start(self._typing_label, False, False, 0)
        row_box.pack_start(bubble_box, False, False, 0)

        self._typing_bubble = row_box
        self.chat_box.pack_start(row_box, False, False, 0)
        self.chat_box.show_all()
        self._scroll_to_bottom()

        if self._typing_timer_id is not None:
            GLib.source_remove(self._typing_timer_id)
        self._typing_timer_id = GLib.timeout_add(350, self._tick_typing_animation)

    def _tick_typing_animation(self):
        if not self._is_query_running:
            return False
        self._typing_dots_count = (self._typing_dots_count % 3) + 1
        dots = "." * self._typing_dots_count
        text = f"Agy is replying{dots}"
        if self._typing_label:
            self._typing_label.set_text(text)
        return True

    def _stop_typing_indicator(self):
        """Stops animation, removes typing bubble, and restores 'Ask Agy 🚀'."""
        self._is_query_running = False
        if self._typing_timer_id is not None:
            GLib.source_remove(self._typing_timer_id)
            self._typing_timer_id = None

        if self._typing_bubble and self._typing_bubble.get_parent():
            self.chat_box.remove(self._typing_bubble)
            self._typing_bubble = None
            self._typing_label = None

        # Restore Ask Agy button
        self.btn_send.set_label("Ask Agy 🚀")
        self.btn_send.set_sensitive(True)

    def _send_user_query(self, query: str):
        if not query or not query.strip():
            return
        if self._is_query_running:
            return
        query = query.strip()
        self.entry_chat.set_text("")
        self._add_message_bubble(query, is_user=True)

        self._start_typing_indicator()

        def on_success(response_text: str):
            GLib.idle_add(self._handle_ai_response, response_text)

        def on_error(err_text: str):
            GLib.idle_add(self._handle_ai_error, err_text)

        self.ai_client.send_message_async(query, on_success, on_error)

    def _handle_ai_response(self, response_text: str):
        self._stop_typing_indicator()

        actions = AgyClient.extract_action_commands(response_text)
        clean_text = re.sub(r"```(fix_command|inspect_command)[\s\S]*?```", "", response_text).strip()
        if not clean_text:
            clean_text = "Here is the recommended action to solve this:"

        self._add_message_bubble(clean_text, is_user=False, actions=actions)
        self._scroll_to_bottom()
        return False

    def _handle_ai_error(self, err_text: str):
        self._stop_typing_indicator()
        self._add_message_bubble(f"⚠️ {err_text}", is_user=False)
        self._scroll_to_bottom()
        return False

    # -------------------------------------------------------------
    # TAB 2: 1 Click Fixes
    # -------------------------------------------------------------
    def _build_fixes_tab(self):
        self.fixes_scroll = Gtk.ScrolledWindow()
        self.fixes_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)

        lbl_desc = Gtk.Label(label="Common 1-click repairs and optimizations. All actions are verified safe.")
        lbl_desc.get_style_context().add_class("header-subtitle")
        lbl_desc.set_xalign(0)
        vbox.pack_start(lbl_desc, False, False, 0)

        for item in QUICK_FIXES:
            card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            card.get_style_context().add_class("ios-card")

            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            
            icon = Gtk.Image.new_from_icon_name(item["icon"], Gtk.IconSize.DND)
            icon.set_valign(Gtk.Align.CENTER)
            header_box.pack_start(icon, False, False, 0)

            t_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            lbl_title = Gtk.Label(label=item["title"])
            lbl_title.get_style_context().add_class("header-title")
            lbl_title.set_xalign(0)
            lbl_sum = Gtk.Label(label=item["summary"])
            lbl_sum.set_line_wrap(True)
            lbl_sum.set_xalign(0)
            lbl_sum.get_style_context().add_class("header-subtitle")
            t_box.pack_start(lbl_title, False, False, 0)
            t_box.pack_start(lbl_sum, False, False, 0)
            header_box.pack_start(t_box, True, True, 0)

            btn_run = Gtk.Button(label="Run Fix ⚡")
            btn_run.get_style_context().add_class("ios-btn-primary")
            btn_run.set_valign(Gtk.Align.CENTER)
            btn_run.set_size_request(130, 38)
            btn_run.connect("clicked", lambda b, c=item["cmd"]: self._execute_safe_task(c, b))
            header_box.pack_end(btn_run, False, False, 0)

            card.pack_start(header_box, True, True, 0)
            vbox.pack_start(card, False, False, 0)

        self.fixes_scroll.add(vbox)
        return self.fixes_scroll

    # -------------------------------------------------------------
    # TAB 3: Easy Software Installer & App Launcher
    # -------------------------------------------------------------
    def _get_app_icon_widget(self, app_info: dict) -> Gtk.Widget:
        """Returns a high-quality rendered icon widget from bundled SVGs or system theme."""
        assets_apps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "apps")
        app_id = app_info.get("id", "")
        icon_name = app_info.get("icon", "")

        # 1. Check bundled SVGs in assets/apps/
        for name in [app_id, icon_name]:
            svg_path = os.path.join(assets_apps_dir, f"{name}.svg")
            if os.path.exists(svg_path):
                try:
                    pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(svg_path, 44, 44, True)
                    if pix:
                        return Gtk.Image.new_from_pixbuf(pix)
                except Exception:
                    pass

        # 2. Check system IconTheme
        theme = Gtk.IconTheme.get_default()
        if theme:
            if icon_name and theme.has_icon(icon_name):
                return Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
            fallback = app_info.get("fallback_icon", "")
            if fallback and theme.has_icon(fallback):
                return Gtk.Image.new_from_icon_name(fallback, Gtk.IconSize.DND)

        # 3. Fallback generic executable icon
        return Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DND)

    def _open_app(self, app_info: dict):
        """Launches an installed application smoothly."""
        launch_cmd = app_info.get("launch_cmd", app_info.get("id", ""))
        launch_app_async(launch_cmd)
        self._add_message_bubble(f"🚀 **Opening {app_info['name']}...**", is_user=False)

    def _build_apps_tab(self):
        self.apps_scroll = Gtk.ScrolledWindow()
        self.apps_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)

        lbl_desc = Gtk.Label(label="Manage and launch applications with a single click. Verified safe and easy.")
        lbl_desc.get_style_context().add_class("header-subtitle")
        lbl_desc.set_xalign(0)
        vbox.pack_start(lbl_desc, False, False, 0)

        self.app_buttons = {}

        for app in APP_CATALOG:
            card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
            card.get_style_context().add_class("ios-card")

            # High-res / SVG app icon
            icon_widget = self._get_app_icon_widget(app)
            card.pack_start(icon_widget, False, False, 0)

            info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            lbl_name = Gtk.Label(label=app["name"])
            lbl_name.get_style_context().add_class("header-title")
            lbl_name.set_xalign(0)
            lbl_desc_app = Gtk.Label(label=f"[{app['category']}] {app['description']}")
            lbl_desc_app.set_line_wrap(True)
            lbl_desc_app.set_xalign(0)
            lbl_desc_app.get_style_context().add_class("header-subtitle")
            info_box.pack_start(lbl_name, False, False, 0)
            info_box.pack_start(lbl_desc_app, False, False, 0)
            card.pack_start(info_box, True, True, 0)

            is_installed = check_app_installed(app["check_cmd"])
            btn_app = Gtk.Button()
            btn_app.set_valign(Gtk.Align.CENTER)
            btn_app.set_size_request(110, 38)
            
            if is_installed:
                btn_app.set_label("🚀 Open")
                btn_app.get_style_context().add_class("ios-btn-open-green")
                btn_app.connect("clicked", lambda b, a=app: self._open_app(a))
            else:
                btn_app.set_label("⬇️ Install")
                btn_app.get_style_context().add_class("ios-btn-primary")
                btn_app.connect("clicked", lambda b, a=app: self._install_app(a, b))

            self.app_buttons[app["id"]] = (btn_app, app)
            card.pack_end(btn_app, False, False, 0)
            vbox.pack_start(card, False, False, 0)

        self.apps_scroll.add(vbox)
        return self.apps_scroll

    def _install_app(self, app_info: dict, btn_widget: Gtk.Button):
        btn_widget.set_sensitive(False)
        btn_widget.set_label("Installing...")
        self._execute_safe_task(
            app_info["install_cmd"],
            btn_widget,
            on_finish_callback=lambda success: self._on_app_installed_finish(app_info["id"], success)
        )

    def _on_app_installed_finish(self, app_id: str, success: bool):
        if app_id in self.app_buttons:
            btn, app = self.app_buttons[app_id]
            if success or check_app_installed(app["check_cmd"]):
                btn.set_label("🚀 Open")
                btn.get_style_context().remove_class("ios-btn-primary")
                btn.get_style_context().add_class("ios-btn-open-green")
                btn.set_sensitive(True)
                btn.connect("clicked", lambda b, a=app: self._open_app(a))
            else:
                btn.set_label("⬇️ Install")
                btn.get_style_context().remove_class("ios-btn-open-green")
                btn.get_style_context().add_class("ios-btn-primary")
                btn.set_sensitive(True)

    # -------------------------------------------------------------
    # Zoom Controls (Senior Accessibility)
    # -------------------------------------------------------------
    def _on_zoom_in(self, btn):
        pct = zoom_in()
        self.lbl_zoom.set_text(pct)
        GLib.timeout_add(100, self._update_floating_scroll_arrows)

    def _on_zoom_out(self, btn):
        pct = zoom_out()
        self.lbl_zoom.set_text(pct)
        GLib.timeout_add(100, self._update_floating_scroll_arrows)

    # -------------------------------------------------------------
    # Google AGY Connection & Setup Troubleshooter
    # -------------------------------------------------------------
    def _check_initial_connection(self):
        """Runs initial health check on Google AGY binary and updates status indicator."""
        is_conn, _ = check_agy_connection()
        self._update_connection_ui()
        if not is_conn:
            self._show_agy_troubleshooter_dialog()

    def _update_connection_ui(self):
        """Updates the header connection pill."""
        is_conn, msg = check_agy_connection()
        if hasattr(self, 'btn_conn_status'):
            ctx = self.btn_conn_status.get_style_context()
            if is_conn:
                ctx.remove_class("status-pill-red")
                ctx.add_class("status-pill-green")
                self.btn_conn_status.set_label("🟢 AGY Connected")
                self.btn_conn_status.set_tooltip_text("Connected to Google AGY AI engine. Click to view status.")
            else:
                ctx.remove_class("status-pill-green")
                ctx.add_class("status-pill-red")
                self.btn_conn_status.set_label("🔴 Setup AGY")
                self.btn_conn_status.set_tooltip_text("Google AGY is disconnected. Click for easy step-by-step setup.")

    def _show_agy_troubleshooter_dialog(self):
        """Displays a simple, step-by-step onboarding and troubleshooter modal for Google AGY."""
        dialog = Gtk.Dialog(
            title="Google AGY Setup & Troubleshooter",
            parent=self,
            flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        dialog.set_default_size(520, 440)
        content_area = dialog.get_content_area()
        content_area.set_spacing(14)
        content_area.set_margin_start(20)
        content_area.set_margin_end(20)
        content_area.set_margin_top(18)
        content_area.set_margin_bottom(18)

        is_connected, msg = check_agy_connection()

        # Status Header
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl_status_icon = Gtk.Label()
        lbl_status_icon.set_markup("<span font='24'>" + ("🟢" if is_connected else "🔴") + "</span>")
        status_box.pack_start(lbl_status_icon, False, False, 0)

        status_text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_s_title = Gtk.Label()
        lbl_s_title.set_markup("<b>Google AGY AI Status: " + ("Connected & Ready" if is_connected else "Setup Required / Disconnected") + "</b>")
        lbl_s_title.set_xalign(0)
        lbl_s_sub = Gtk.Label(label=msg)
        lbl_s_sub.get_style_context().add_class("header-subtitle")
        lbl_s_sub.set_xalign(0)
        status_text_box.pack_start(lbl_s_title, False, False, 0)
        status_text_box.pack_start(lbl_s_sub, False, False, 0)
        status_box.pack_start(status_text_box, True, True, 0)
        content_area.pack_start(status_box, False, False, 0)

        # Step-by-Step Guide Card
        guide_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        guide_box.get_style_context().add_class("ios-card")

        lbl_guide_title = Gtk.Label(label="<b>Simple Step-by-Step Guide to Connect:</b>")
        lbl_guide_title.set_use_markup(True)
        lbl_guide_title.set_xalign(0)
        guide_box.pack_start(lbl_guide_title, False, False, 0)

        steps = [
            ("Step 1: Download & Install AGY from Google",
             "Google AGY is the free agentic AI engine that powers Agy Helper. It installs into ~/.local/bin/agy automatically when you install Antigravity."),
            ("Step 2: Sign In or Set Gemini API Key",
             "Run 'agy login' in your terminal or ensure your Google Antigravity account is signed in."),
            ("Step 3: Test Connection",
             "Click 'Test Connection' below. When the green light turns on, Agy Helper is fully ready to assist you!")
        ]

        for s_title, s_desc in steps:
            s_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            st = Gtk.Label(label=f"<b>{s_title}</b>")
            st.set_use_markup(True)
            st.set_xalign(0)
            sd = Gtk.Label(label=s_desc)
            sd.set_line_wrap(True)
            sd.set_xalign(0)
            sd.get_style_context().add_class("header-subtitle")
            s_row.pack_start(st, False, False, 0)
            s_row.pack_start(sd, False, False, 0)
            guide_box.pack_start(s_row, False, False, 0)

        content_area.pack_start(guide_box, True, True, 0)

        # Action Buttons
        btn_area = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_area.set_halign(Gtk.Align.END)

        btn_test = Gtk.Button(label="⚡ Test Connection Now")
        btn_test.get_style_context().add_class("ios-btn-primary")

        def on_test_click(b):
            conn, m = check_agy_connection()
            self._update_connection_ui()
            if conn:
                lbl_s_title.set_markup("<b>Google AGY AI Status: Connected & Ready 🎉</b>")
                lbl_s_sub.set_text("Successfully connected to Google AGY AI engine.")
                lbl_status_icon.set_markup("<span font='24'>🟢</span>")
                btn_test.set_label("Connected! ✓")
                btn_test.set_sensitive(False)
            else:
                lbl_s_title.set_markup("<b>Google AGY AI Status: Disconnected</b>")
                lbl_s_sub.set_text(m)
                lbl_status_icon.set_markup("<span font='24'>🔴</span>")

        btn_test.connect("clicked", on_test_click)
        btn_area.pack_start(btn_test, False, False, 0)

        btn_close = Gtk.Button(label="Close")
        btn_close.get_style_context().add_class("ios-btn-secondary")
        btn_close.connect("clicked", lambda b: dialog.destroy())
        btn_area.pack_start(btn_close, False, False, 0)

        content_area.pack_start(btn_area, False, False, 0)
        dialog.show_all()

    # -------------------------------------------------------------
    # TAB 4: Scam Help & Fraud Prevention
    # -------------------------------------------------------------
    def _build_scam_tab(self):
        self.scam_scroll = Gtk.ScrolledWindow()
        self.scam_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        vbox.set_margin_top(16)
        vbox.set_margin_bottom(16)

        # 1. Top Reassurance Banner
        banner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        banner.get_style_context().add_class("scam-banner")

        lbl_b_title = Gtk.Label(label="🛡️ Scam & Fraud Protection Helper")
        lbl_b_title.get_style_context().add_class("header-title")
        lbl_b_title.set_xalign(0)
        banner.pack_start(lbl_b_title, False, False, 0)

        lbl_b_desc = Gtk.Label(
            label="Scammers use fake warnings, loud sirens, and urgency to trick people into giving away money or remote computer access. "
                  "Remember: real tech companies will NEVER lock your screen or ask for gift cards. You are completely safe here."
        )
        lbl_b_desc.set_line_wrap(True)
        lbl_b_desc.set_xalign(0)
        banner.pack_start(lbl_b_desc, False, False, 0)

        # Quick Action Buttons Row
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_margin_top(6)

        btn_ask_scam = Gtk.Button(label="🔍 Ask Agy to Check a Suspicious Message")
        btn_ask_scam.get_style_context().add_class("ios-btn-primary")
        btn_ask_scam.connect("clicked", lambda b: self._start_scam_check())
        btn_box.pack_start(btn_ask_scam, False, False, 0)

        btn_kill_browsers = Gtk.Button(label="🛑 Emergency: Close All Web Browsers")
        btn_kill_browsers.get_style_context().add_class("btn-emergency")
        btn_kill_browsers.set_tooltip_text("Use this if a scary fake virus webpage won't let you close the window.")
        btn_kill_browsers.connect("clicked", lambda b: self._emergency_close_browsers())
        btn_box.pack_start(btn_kill_browsers, False, False, 0)

        banner.pack_start(btn_box, False, False, 0)
        vbox.pack_start(banner, False, False, 0)

        # 2. Golden Safety Rules Card
        rules_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        rules_card.get_style_context().add_class("ios-card")

        lbl_r_head = Gtk.Label(label="⭐ The 3 Golden Rules To Never Get Scammed")
        lbl_r_head.get_style_context().add_class("header-title")
        lbl_r_head.set_xalign(0)
        rules_card.pack_start(lbl_r_head, False, False, 0)

        rules = [
            ("1. No Real Company Puts a Phone Number on Your Screen",
             "If your screen flashes red saying 'Call Microsoft at 1-800-XXX-XXXX', it is 100% a fake website! Real error messages never ask you to phone an 800 number."),
            ("2. Never Allow Anyone Who Called You to Control Your Computer",
             "If someone calls claiming to be from Amazon, your bank, or tech support asking you to install AnyDesk, TeamViewer, or QuickAssist, HANG UP. They want to get into your online banking."),
            ("3. Gift Cards = 100% Scam (Always)",
             "No legitimate company, bank, police department, or the IRS ever accepts Target, Apple, Google Play, or Walmart gift cards as payment. Anyone asking for gift cards is a scammer.")
        ]
        for title, detail in rules:
            r_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            r_row.get_style_context().add_class("ios-card-inner")
            lt = Gtk.Label(label=f"<b>{title}</b>")
            lt.set_use_markup(True)
            lt.set_xalign(0)
            ld = Gtk.Label(label=detail)
            ld.set_line_wrap(True)
            ld.set_xalign(0)
            ld.get_style_context().add_class("header-subtitle")
            r_row.pack_start(lt, False, False, 0)
            r_row.pack_start(ld, False, False, 0)
            rules_card.pack_start(r_row, False, False, 0)

        vbox.pack_start(rules_card, False, False, 0)

        # 3. Common Scam Tactics Card
        tactics_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tactics_card.get_style_context().add_class("ios-card")

        lbl_t_head = Gtk.Label(label="🚨 Common Scams & What To Do")
        lbl_t_head.get_style_context().add_class("header-title")
        lbl_t_head.set_xalign(0)
        tactics_card.pack_start(lbl_t_head, False, False, 0)

        tactics = [
            {
                "name": "Fake Tech Support / Virus Alarm Popup",
                "danger": "A loud siren plays and a webpage says your computer is infected with 5 viruses.",
                "safe": "It's just an annoying webpage! Click 'Emergency Close Browsers' above or press Alt+F4. Your files are completely safe."
            },
            {
                "name": "The Fake USPS / Delivery Fee Text Message",
                "danger": "A text message claims 'Package cannot be delivered, click here to pay $0.30 redelivery fee'.",
                "safe": "Delete the text immediately! The link leads to a fake clone site designed to steal your debit card."
            },
            {
                "name": "Bank Fraud Alert / Account Frozen Call",
                "danger": "A caller claims your bank account has a suspicious $1,500 wire and asks for your password or PIN.",
                "safe": "Hang up! Never give PINs or passwords. Look at the back of your physical bank card and call that official number yourself."
            },
            {
                "name": "Family Member Emergency Impersonation",
                "danger": "A caller sounds like a grandchild claiming they are in an accident or jail and need money sent right now.",
                "safe": "Hang up and call that family member or their parents directly on their known phone number before sending any money."
            }
        ]

        for t in tactics:
            t_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            t_box.get_style_context().add_class("ios-card-inner")

            t_name = Gtk.Label(label=f"<b>{t['name']}</b>")
            t_name.set_use_markup(True)
            t_name.set_xalign(0)
            t_box.pack_start(t_name, False, False, 0)

            d_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            d_box.get_style_context().add_class("scam-danger-box")
            ld = Gtk.Label(label=f"⚠️ <b>What Scammers Do:</b> {t['danger']}")
            ld.set_use_markup(True)
            ld.set_line_wrap(True)
            ld.set_xalign(0)
            d_box.pack_start(ld, False, False, 0)
            t_box.pack_start(d_box, False, False, 0)

            s_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            s_box.get_style_context().add_class("scam-safe-box")
            ls = Gtk.Label(label=f"✅ <b>What You Should Do:</b> {t['safe']}")
            ls.set_use_markup(True)
            ls.set_line_wrap(True)
            ls.set_xalign(0)
            s_box.pack_start(ls, False, False, 0)
            t_box.pack_start(s_box, False, False, 0)

            tactics_card.pack_start(t_box, False, False, 0)

        vbox.pack_start(tactics_card, False, False, 0)

        self.scam_scroll.add(vbox)
        return self.scam_scroll

    def _start_scam_check(self):
        """Switches to the AI Chat tab and prepares a suspicious message check."""
        self.select_tab("chat")
        self.entry_chat.set_text("Someone sent me a message saying: '[paste message here]'. Is this a scam or is it safe?")
        self.entry_chat.grab_focus()

    def _emergency_close_browsers(self):
        """Safely closes all active web browsers in case of a locked scam popup."""
        cmd = "killall chrome chrome-sandbox firefox brave-browser msedge 2>/dev/null || true"
        self._execute_safe_task(cmd, None)
        self._add_message_bubble("🛑 **Closed all web browser windows.** Any fake scam popups have been safely dismissed.", is_user=False)
        self.select_tab("chat")

    # -------------------------------------------------------------
    # TAB 5: Safety & System Health
    # -------------------------------------------------------------
    def _build_health_tab(self):
        self.health_scroll = Gtk.ScrolledWindow()
        self.health_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.health_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.health_vbox.set_margin_start(20)
        self.health_vbox.set_margin_end(20)
        self.health_vbox.set_margin_top(16)
        self.health_vbox.set_margin_bottom(16)

        # 1. Protected Personal Folders Card
        prot_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        prot_card.get_style_context().add_class("ios-card")

        lbl_prot_head = Gtk.Label()
        lbl_prot_head.set_markup("<b>🛡️ Active Safety Guardrails (Personal Folders)</b>")
        lbl_prot_head.set_xalign(0)
        prot_card.pack_start(lbl_prot_head, False, False, 0)

        lbl_prot_sub = Gtk.Label(
            label="Agy Helper has hardcoded safety rules that strictly prevent deletion "
                  "in your personal media and document directories. Only reading is allowed."
        )
        lbl_prot_sub.set_line_wrap(True)
        lbl_prot_sub.set_xalign(0)
        lbl_prot_sub.get_style_context().add_class("header-subtitle")
        prot_card.pack_start(lbl_prot_sub, False, False, 0)

        for p_info in get_protected_paths_summary():
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            row.get_style_context().add_class("ios-card-inner")

            icon_sh = Gtk.Image.new_from_icon_name("security-high-symbolic", Gtk.IconSize.MENU)
            row.pack_start(icon_sh, False, False, 0)

            l_name = Gtk.Label(label=f"📁 ~/{p_info['name']}")
            l_name.get_style_context().add_class("header-title")
            row.pack_start(l_name, False, False, 0)

            l_status = Gtk.Label(label="🔒 Read-Only Protected (Deletion Prohibited)")
            l_status.get_style_context().add_class("shield-pill-green")
            row.pack_end(l_status, False, False, 0)
            prot_card.pack_start(row, False, False, 0)

        self.health_vbox.pack_start(prot_card, False, False, 0)

        # 2. System Resources Card
        self.res_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.res_card.get_style_context().add_class("ios-card")

        lbl_res_head = Gtk.Label()
        lbl_res_head.set_markup("<b>💻 Live System Diagnostics</b>")
        lbl_res_head.set_xalign(0)
        self.res_card.pack_start(lbl_res_head, False, False, 0)

        self.lbl_ram_stat = Gtk.Label(label="Memory (RAM): Checking...")
        self.lbl_ram_stat.set_xalign(0)
        self.res_card.pack_start(self.lbl_ram_stat, False, False, 0)

        self.lbl_disk_stat = Gtk.Label(label="Storage: Checking...")
        self.lbl_disk_stat.set_xalign(0)
        self.res_card.pack_start(self.lbl_disk_stat, False, False, 0)

        self.lbl_uptime_stat = Gtk.Label(label="Uptime: Checking...")
        self.lbl_uptime_stat.set_xalign(0)
        self.res_card.pack_start(self.lbl_uptime_stat, False, False, 0)

        btn_refresh = Gtk.Button(label="🔄 Refresh Metrics")
        btn_refresh.get_style_context().add_class("ios-btn-secondary")
        btn_refresh.set_valign(Gtk.Align.CENTER)
        btn_refresh.set_size_request(160, 38)
        btn_refresh.connect("clicked", lambda b: self._refresh_health_tab())
        self.res_card.pack_start(btn_refresh, False, False, 0)

        self.health_vbox.pack_start(self.res_card, False, False, 0)

        # 3. Model & Settings Card
        settings_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        settings_card.get_style_context().add_class("ios-card")

        lbl_set_head = Gtk.Label()
        lbl_set_head.set_markup("<b>⚙️ AI Model &amp; Startup Settings</b>")
        lbl_set_head.set_xalign(0)
        settings_card.pack_start(lbl_set_head, False, False, 0)

        lbl_set_info = Gtk.Label(
            label=f"• Model: {DEFAULT_MODEL} (Effort: {DEFAULT_EFFORT})\n"
                  f"• Token Saver: Active (History pruning enabled to prevent overages)\n"
                  f"• Autostart: Enabled on startup (~/.config/autostart)\n"
                  f"• Dock Icon: Installed &amp; pinned in GNOME Favorites"
        )
        lbl_set_info.set_line_wrap(True)
        lbl_set_info.set_xalign(0)
        lbl_set_info.get_style_context().add_class("header-subtitle")
        settings_card.pack_start(lbl_set_info, False, False, 0)

        self.health_vbox.pack_start(settings_card, False, False, 0)

        self.health_scroll.add(self.health_vbox)
        return self.health_scroll

    def _refresh_health_tab(self):
        h = get_system_health()
        self.lbl_ram_stat.set_text(f"Memory (RAM): {h['ram_usage']}")
        self.lbl_disk_stat.set_text(f"Storage (Home): {h['disk_usage']}")
        self.lbl_uptime_stat.set_text(f"System Uptime: {h['uptime']}")

    # -------------------------------------------------------------
    # Terminal Log Drawer
    # -------------------------------------------------------------
    def _create_terminal_drawer(self):
        revealer = Gtk.Revealer()
        revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        revealer.set_reveal_child(False)

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        frame.get_style_context().add_class("terminal-box")
        frame.set_margin_start(16)
        frame.set_margin_end(16)
        frame.set_margin_bottom(12)

        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl = Gtk.Label()
        lbl.set_markup("<b>Activity Terminal Log</b>")
        header_row.pack_start(lbl, False, False, 0)

        btn_close = Gtk.Button(label="Hide Log ✕")
        btn_close.get_style_context().add_class("ios-btn-secondary")
        btn_close.connect("clicked", lambda b: revealer.set_reveal_child(False))
        header_row.pack_end(btn_close, False, False, 0)
        frame.pack_start(header_row, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(140)

        text_view = Gtk.TextView()
        text_view.set_editable(False)
        text_view.set_cursor_visible(False)
        text_view.get_style_context().add_class("terminal-box")
        scroll.add(text_view)
        frame.pack_start(scroll, True, True, 0)

        revealer.add(frame)
        return revealer, text_view

    def _append_log(self, text: str):
        buf = self.log_text_view.get_buffer()
        end_iter = buf.get_end_iter()
        buf.insert(end_iter, text)
        mark = buf.create_mark(None, buf.get_end_iter(), False)
        self.log_text_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def _execute_safe_task(self, cmd_str: str, trigger_btn=None, on_finish_callback=None):
        self.log_revealer.set_reveal_child(True)
        buf = self.log_text_view.get_buffer()
        buf.set_text("")

        if trigger_btn:
            trigger_btn.set_sensitive(False)

        def on_output(line: str):
            GLib.idle_add(self._append_log, line)

        def on_complete(ret_code: int, full_log: str):
            def _finish():
                if trigger_btn:
                    trigger_btn.set_sensitive(True)
                if on_finish_callback:
                    on_finish_callback(ret_code == 0)
                if ret_code == 0:
                    self._add_message_bubble(f"✅ **Task finished successfully!**\n`{cmd_str}`", is_user=False)
                else:
                    self._add_message_bubble(f"⚠️ **Task completed with status code {ret_code}**.\nCheck the activity log for details.", is_user=False)
            GLib.idle_add(_finish)

        run_command_safe_async(cmd_str, on_output, on_complete)
