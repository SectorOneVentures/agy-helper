"""
Modern iOS / macOS-inspired Light Stylesheet for Agy Companion & IT Helper.
Strictly Light Mode only with Senior Font Zooming and Backdrop Stability.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

def generate_css(scale: float = 1.0) -> str:
    """Generates CSS with dynamically scaled font sizes and proportional padding."""
    f_xs = max(10, int(round(11 * scale)))
    f_sm = max(11, int(round(12 * scale)))
    f_base = max(12, int(round(13 * scale)))
    f_md = max(13, int(round(14 * scale)))
    f_lg = max(14, int(round(15 * scale)))
    f_xl = max(16, int(round(17 * scale)))
    f_title = max(17, int(round(19 * scale)))

    btn_h = max(36, int(round(38 * scale)))
    btn_pad_v = max(6, int(round(8 * scale)))
    btn_pad_h = max(12, int(round(18 * scale)))
    tab_pad_v = max(4, int(round(6 * scale)))
    tab_pad_h = max(10, int(round(14 * scale)))
    float_size = max(36, int(round(38 * scale)))

    return f"""
/* === LIGHT THEME ONLY === */
window.companion-window {{
    background-color: transparent;
    background: transparent;
}}

.companion-bubble {{
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1.5px solid #0A84FF;
    border-radius: 16px;
    padding: 6px 14px;
    font-weight: bold;
    font-size: {f_sm}px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}}

window.assistant-window {{
    background-color: #F8FAFC;
    color: #1E293B;
}}

headerbar.ios-header {{
    background-color: #FFFFFF;
    background-image: none;
    border-bottom: 1px solid #E2E8F0;
    min-height: 52px;
    padding: 0 14px;
}}

.header-title {{
    font-weight: bold;
    font-size: {f_lg}px;
    color: #0F172A;
}}

.header-subtitle {{
    font-size: {f_xs}px;
    color: #64748B;
}}

/* Header Connection Status Pill */
button.status-pill-green,
.status-pill-green {{
    background-image: none;
    background-color: #ECFDF5;
    color: #047857;
    border: 1px solid #A7F3D0;
    border-radius: 14px;
    padding: 4px 10px;
    font-size: {f_xs}px;
    font-weight: bold;
}}

button.status-pill-green label,
.status-pill-green label {{
    color: #047857;
    font-weight: bold;
}}

button.status-pill-red,
.status-pill-red {{
    background-image: none;
    background-color: #FEF2F2;
    color: #B91C1C;
    border: 1.5px solid #FCA5A5;
    border-radius: 14px;
    padding: 4px 10px;
    font-size: {f_xs}px;
    font-weight: bold;
}}

button.status-pill-red:hover,
.status-pill-red:hover {{
    background-color: #FEE2E2;
    border-color: #F87171;
}}

button.status-pill-red label,
.status-pill-red label {{
    color: #B91C1C;
    font-weight: bold;
}}

/* Header Zoom Accessibility Controls */
button.zoom-btn,
.zoom-btn {{
    background-image: none;
    background-color: #F1F5F9;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    color: #334155;
    font-weight: bold;
    font-size: {f_base}px;
    padding: 2px 8px;
    min-width: 28px;
    min-height: 28px;
}}

button.zoom-btn:hover,
.zoom-btn:hover {{
    background-color: #E2E8F0;
    color: #0F172A;
}}

.zoom-label {{
    font-size: {f_xs}px;
    font-weight: bold;
    color: #475569;
    padding: 0 4px;
}}

/* iOS Tab Bar */
.ios-tab-bar {{
    background-color: #EFF6FF;
    border: 1px solid #DBEAFE;
    border-radius: 12px;
    padding: 3px;
    margin: 8px 14px;
}}

button.ios-tab-btn,
.ios-tab-btn {{
    background-image: none;
    background-color: transparent;
    border: none;
    border-radius: 9px;
    padding: {tab_pad_v}px {tab_pad_h}px;
    font-weight: bold;
    font-size: {f_base}px;
    color: #1D4ED8;
    box-shadow: none;
}}

button.ios-tab-btn:hover:not(:checked),
.ios-tab-btn:hover:not(:checked) {{
    background-image: none;
    background-color: #DBEAFE;
    color: #1E40AF;
}}

/* CRITICAL FIX: Active Tab Highlight - Keeps crisp white text even when unfocused/in background (:backdrop) */
button.ios-tab-btn:checked,
button.ios-tab-btn:checked:backdrop,
.ios-tab-btn:checked,
.ios-tab-btn:checked:backdrop {{
    background-image: none;
    background-color: #0A84FF;
    color: #FFFFFF;
    box-shadow: 0 2px 5px rgba(10, 132, 255, 0.35);
}}

button.ios-tab-btn:checked label,
button.ios-tab-btn:checked:backdrop label,
.ios-tab-btn:checked label,
.ios-tab-btn:checked:backdrop label {{
    color: #FFFFFF;
    text-shadow: none;
}}

/* Cards */
.ios-card {{
    background-color: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    padding: 16px;
    margin-bottom: 12px;
    color: #1E293B;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}}

.ios-card-inner {{
    background-color: #F1F5F9;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 12px;
    color: #1E293B;
}}

/* ========================================================= */
/* BUTTON STYLING - Guaranteed White Font on Blue and Green  */
/* Keeps white font in all states including :disabled and :backdrop */
/* ========================================================= */
button.ios-btn-primary,
button.ios-btn-primary:backdrop,
.ios-btn-primary,
.ios-btn-primary:backdrop,
button.ios-btn-primary:disabled,
button.ios-btn-primary:disabled:backdrop,
.ios-btn-primary:disabled,
.ios-btn-primary:disabled:backdrop,
button.ios-btn-installed,
.ios-btn-installed {{
    background-image: none;
    background-color: #0A84FF;
    color: #FFFFFF;
    font-weight: bold;
    font-size: {f_base}px;
    border-radius: 12px;
    border: none;
    min-height: {btn_h}px;
    padding: {btn_pad_v}px {btn_pad_h}px;
    box-shadow: 0 2px 6px rgba(10, 132, 255, 0.3);
    opacity: 1.0;
    -gtk-icon-effect: none;
}}

button.ios-btn-primary label,
button.ios-btn-primary:backdrop label,
.ios-btn-primary label,
.ios-btn-primary:backdrop label,
button.ios-btn-primary:disabled label,
button.ios-btn-primary:disabled:backdrop label,
.ios-btn-primary:disabled label,
.ios-btn-primary:disabled:backdrop label {{
    color: #FFFFFF;
    opacity: 1.0;
    text-shadow: none;
}}

button.ios-btn-primary:hover,
.ios-btn-primary:hover {{
    background-image: none;
    background-color: #3B99FF;
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(10, 132, 255, 0.4);
}}

button.ios-btn-primary:active,
.ios-btn-primary:active {{
    background-image: none;
    background-color: #0070E0;
    color: #FFFFFF;
}}

/* Green Open Button for already installed apps */
button.ios-btn-open-green,
button.ios-btn-open-green:backdrop,
.ios-btn-open-green,
.ios-btn-open-green:backdrop,
button.ios-btn-open-green:disabled,
button.ios-btn-open-green:disabled:backdrop {{
    background-image: none;
    background-color: #34C759;
    color: #FFFFFF;
    font-weight: bold;
    font-size: {f_base}px;
    border-radius: 12px;
    border: none;
    min-height: {btn_h}px;
    padding: {btn_pad_v}px {btn_pad_h}px;
    box-shadow: 0 2px 6px rgba(52, 199, 89, 0.35);
    opacity: 1.0;
    -gtk-icon-effect: none;
}}

button.ios-btn-open-green label,
button.ios-btn-open-green:backdrop label,
.ios-btn-open-green label,
.ios-btn-open-green:backdrop label,
button.ios-btn-open-green:disabled label,
button.ios-btn-open-green:disabled:backdrop label {{
    color: #FFFFFF;
    opacity: 1.0;
    text-shadow: none;
}}

button.ios-btn-open-green:hover,
.ios-btn-open-green:hover {{
    background-image: none;
    background-color: #2ECC71;
    color: #FFFFFF;
    box-shadow: 0 4px 10px rgba(52, 199, 89, 0.45);
}}

button.ios-btn-open-green:active,
.ios-btn-open-green:active {{
    background-image: none;
    background-color: #24A148;
    color: #FFFFFF;
}}

/* Floating Navigation Scroll Buttons (Down/Up Arrows) */
button.floating-scroll-btn,
button.floating-scroll-btn:backdrop,
.floating-scroll-btn,
.floating-scroll-btn:backdrop {{
    background-image: none;
    background-color: #0A84FF;
    color: #FFFFFF;
    border-radius: {float_size // 2}px;
    border: 2px solid #FFFFFF;
    min-width: {float_size}px;
    min-height: {float_size}px;
    padding: 0;
    font-size: {f_lg}px;
    font-weight: bold;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
}}

button.floating-scroll-btn:hover,
.floating-scroll-btn:hover {{
    background-image: none;
    background-color: #3B99FF;
    box-shadow: 0 6px 18px rgba(10, 132, 255, 0.45);
}}

button.floating-scroll-btn:active,
.floating-scroll-btn:active {{
    background-image: none;
    background-color: #0070E0;
}}

button.floating-scroll-btn label,
button.floating-scroll-btn:backdrop label,
.floating-scroll-btn label,
.floating-scroll-btn:backdrop label {{
    color: #FFFFFF;
    font-size: {f_lg}px;
    font-weight: bold;
}}

/* Secondary Buttons - Lighter Blue Accent */
button.ios-btn-secondary,
.ios-btn-secondary {{
    background-image: none;
    background-color: #EFF6FF;
    color: #0A84FF;
    font-weight: bold;
    font-size: {f_base}px;
    border-radius: 12px;
    border: 1.5px solid #BFDBFE;
    min-height: {btn_h}px;
    padding: {btn_pad_v}px {btn_pad_h}px;
    box-shadow: 0 1px 3px rgba(10, 132, 255, 0.15);
}}

button.ios-btn-secondary:hover,
.ios-btn-secondary:hover {{
    background-image: none;
    background-color: #DBEAFE;
    color: #0062CC;
    border-color: #93C5FD;
}}

button.ios-btn-secondary:active,
.ios-btn-secondary:active {{
    background-image: none;
    background-color: #BFDBFE;
    color: #0051A8;
}}

/* Suggestion Chips */
button.suggestion-chip,
.suggestion-chip {{
    background-image: none;
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 14px;
    color: #1D4ED8;
    font-size: {f_sm}px;
    font-weight: bold;
    padding: 6px 12px;
}}

button.suggestion-chip:hover,
.suggestion-chip:hover {{
    background-image: none;
    background-color: #DBEAFE;
    border-color: #93C5FD;
    color: #1E40AF;
}}

/* Status Badges */
.shield-pill-green {{
    background-color: #ECFDF5;
    color: #065F46;
    font-weight: bold;
    font-size: {f_xs}px;
    border-radius: 20px;
    border: 1px solid #A7F3D0;
    padding: 4px 10px;
}}

.shield-pill-blue {{
    background-color: #EFF6FF;
    color: #1E40AF;
    font-weight: bold;
    font-size: {f_xs}px;
    border-radius: 20px;
    border: 1px solid #BFDBFE;
    padding: 4px 10px;
}}

/* Chat Bubbles */
.chat-bubble-user {{
    background-color: #0A84FF;
    color: #FFFFFF;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 14px;
    margin: 4px 0 4px 50px;
    box-shadow: 0 1px 4px rgba(10, 132, 255, 0.2);
    font-size: {f_base}px;
}}

.chat-bubble-assistant {{
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1px solid #E2E8F0;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 4px 50px 4px 0;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    font-size: {f_base}px;
}}

/* Typing Indicator Bubble */
.chat-bubble-typing {{
    background-color: #EFF6FF;
    color: #0A84FF;
    border: 1.5px solid #BFDBFE;
    border-radius: 18px 18px 18px 4px;
    padding: 10px 16px;
    margin: 4px 50px 4px 0;
    font-weight: bold;
    font-size: {f_base}px;
    box-shadow: 0 1px 3px rgba(10, 132, 255, 0.1);
}}

/* Chat Entry */
.chat-entry {{
    background-color: #FFFFFF;
    color: #1E293B;
    border: 1.5px solid #BFDBFE;
    border-radius: 20px;
    padding: 10px 14px;
    font-size: {f_md}px;
}}

.chat-entry:focus {{
    border-color: #0A84FF;
}}

/* Terminal Log */
.terminal-box {{
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: monospace;
    font-size: {f_sm}px;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    padding: 10px;
}}

/* ========================================================= */
/* SCAM HELP TAB STYLES                                      */
/* ========================================================= */
.scam-banner {{
    background-color: #EFF6FF;
    border: 1.5px solid #93C5FD;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
}}

.scam-card {{
    background-color: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    padding: 16px;
    margin-bottom: 12px;
}}

.scam-danger-box {{
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 10px;
    padding: 8px 12px;
    color: #991B1B;
    font-size: {f_sm}px;
}}

.scam-safe-box {{
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    border-radius: 10px;
    padding: 8px 12px;
    color: #166534;
    font-size: {f_sm}px;
}}

button.btn-emergency,
.btn-emergency {{
    background-image: none;
    background-color: #DC2626;
    color: #FFFFFF;
    font-weight: bold;
    font-size: {f_base}px;
    border-radius: 12px;
    border: none;
    min-height: {btn_h}px;
    padding: {btn_pad_v}px {btn_pad_h}px;
    box-shadow: 0 2px 6px rgba(220, 38, 38, 0.35);
}}

button.btn-emergency:hover,
.btn-emergency:hover {{
    background-image: none;
    background-color: #EF4444;
}}

button.btn-emergency label,
.btn-emergency label {{
    color: #FFFFFF;
    font-weight: bold;
}}
"""

_current_provider = None
_current_theme = "light"
_current_scale = 1.0

SCALE_STEPS = [1.0, 1.15, 1.30, 1.50]

def get_current_scale() -> float:
    global _current_scale
    return _current_scale

def get_scale_percentage() -> str:
    global _current_scale
    return f"{int(round(_current_scale * 100))}%"

def get_current_theme() -> str:
    return "light"

def apply_theme(scale: float = 1.0):
    global _current_provider, _current_theme, _current_scale
    _current_theme = "light"
    _current_scale = scale

    settings = Gtk.Settings.get_default()
    if settings:
        settings.set_property("gtk-application-prefer-dark-theme", False)
    
    screen = Gdk.Screen.get_default()
    if not screen:
        return

    if _current_provider:
        Gtk.StyleContext.remove_provider_for_screen(screen, _current_provider)

    css_text = generate_css(_current_scale)
    _current_provider = Gtk.CssProvider()
    _current_provider.load_from_data(css_text.encode('utf-8'))
    Gtk.StyleContext.add_provider_for_screen(
        screen,
        _current_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_USER
    )

def zoom_in() -> str:
    """Steps up font size scale for senior visibility."""
    global _current_scale
    for s in SCALE_STEPS:
        if s > _current_scale + 0.05:
            apply_theme(s)
            return get_scale_percentage()
    apply_theme(SCALE_STEPS[-1])
    return get_scale_percentage()

def zoom_out() -> str:
    """Steps down font size scale."""
    global _current_scale
    for s in reversed(SCALE_STEPS):
        if s < _current_scale - 0.05:
            apply_theme(s)
            return get_scale_percentage()
    apply_theme(SCALE_STEPS[0])
    return get_scale_percentage()

def toggle_theme() -> str:
    # Always stay in light mode
    apply_theme(_current_scale)
    return "light"

# Legacy alias
LIGHT_THEME_CSS = generate_css(1.0)
DARK_THEME_CSS = LIGHT_THEME_CSS
