#!/usr/bin/env python3
"""
Records a smooth, pixel-perfect 55-second video demo (1920x1080 @ 24fps) of Agy Helper in action.
Features:
- Exact widget coordinate targeting (all cursor destinations queried dynamically from GTK).
- Discrete interaction phases: Move -> Hover & Click -> State Transition -> Hold & Read.
- In-place text typing simulation in the chat entry box.
- Plain-English Q&A (Slow Wi-Fi checks, RAM kitchen countertop analogy).
- Full tour across all 5 tabs: Chat -> Fixes -> Apps -> Scam Help -> Health -> Senior Zoom (130%).
- Unobtrusive lower-third subtitle bar with generous 4-6s reading time.
- STRICTLY ZERO EMOJIS in all overlay captions.
"""

import os
import sys
import time
import math
import shutil
import subprocess
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import styles
import assistant_window

ARTIFACT_DIR = "/home/sectoroneventures/.gemini/antigravity/brain/b2b82baa-3f56-43fe-8ae8-1fb7e7dfd3aa"
OUTPUT_MP4 = os.path.join(ROOT_DIR, "assets", "agy_helper_demo.mp4")
OUTPUT_GIF = os.path.join(ROOT_DIR, "assets", "screenshots", "agy_helper_demo.gif")

WIDTH, HEIGHT = 1920, 1080
FPS = 24

try:
    FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_SUB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    FONT_DESKTOP = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    FONT_SPEECH = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()
    FONT_DESKTOP = ImageFont.load_default()
    FONT_SPEECH = ImageFont.load_default()

def pump_gtk(win):
    """Pumps the GTK main iteration loop with frame clock ticks so all CSS transitions complete."""
    win.check_resize()
    win.queue_draw()
    for _ in range(50):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        time.sleep(0.01)

def render_gtk_window(win):
    """Renders the AssistantWindow to an unscaled, pixel-perfect PIL RGBA image."""
    pump_gtk(win)
    alloc = win.get_allocation()
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, alloc.width, alloc.height)
    cr = cairo.Context(surface)
    win.draw(cr)
    
    tmp = f"/tmp/gtktmp_{os.getpid()}.png"
    surface.write_to_png(tmp)
    img = Image.open(tmp).convert("RGBA")
    try:
        os.remove(tmp)
    except Exception:
        pass
    return img

def get_widget_center(w, win):
    """Returns the exact (cx, cy) pixel center of a GTK widget relative to the window."""
    alloc = w.get_allocation()
    res = w.translate_coordinates(win, 0, 0)
    if res:
        return res[0] + alloc.width // 2, res[1] + alloc.height // 2
    return alloc.x + alloc.width // 2, alloc.y + alloc.height // 2

def create_desktop_base():
    """Renders a clean, high-resolution desktop background at 1920x1080."""
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (236, 242, 248, 255))
    d = ImageDraw.Draw(bg)
    
    # Soft background gradient
    for y in range(HEIGHT):
        alpha = y / HEIGHT
        r = int(236 * (1 - alpha * 0.04))
        g = int(242 * (1 - alpha * 0.04))
        b = int(248 * (1 - alpha * 0.02))
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    
    # Top taskbar (height 36px)
    d.rectangle([(0, 0), (WIDTH, 36)], fill=(255, 255, 255, 245))
    d.line([(0, 36), (WIDTH, 36)], fill=(226, 232, 240, 255), width=1)
    d.text((24, 9), "Activities", fill=(71, 85, 105, 255), font=FONT_DESKTOP)
    d.text((WIDTH // 2 - 45, 9), "Tuesday 3:30 PM", fill=(71, 85, 105, 255), font=FONT_DESKTOP)
    d.text((WIDTH - 180, 9), "Wi-Fi  Sound  Battery", fill=(100, 116, 139, 255), font=FONT_DESKTOP)
    return bg

def draw_cursor(img, x, y, clicking=False):
    """Draws a crisp desktop mouse pointer whose sharp tip is exactly at (x, y)."""
    d = ImageDraw.Draw(img)
    pts = [
        (x, y),
        (x, y + 20),
        (x + 5, y + 15),
        (x + 10, y + 25),
        (x + 13, y + 23),
        (x + 8, y + 14),
        (x + 16, y + 14)
    ]
    
    if clicking:
        # Concentric ripple ring centered at the exact pointer tip
        d.ellipse([(x - 12, y - 12), (x + 12, y + 12)], outline=(14, 165, 233, 200), width=2)
        d.ellipse([(x - 6, y - 6), (x + 6, y + 6)], outline=(2, 132, 199, 240), width=2)
    
    shadow_pts = [(px + 2, py + 2) for px, py in pts]
    d.polygon(shadow_pts, fill=(0, 0, 0, 70))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(15, 23, 42, 255))

def draw_caption_bar(img, title, subtitle):
    """Renders a slim, elegant, non-obtrusive lower-third bar without emojis."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    
    bar_h = 66
    d.rectangle([(0, HEIGHT - bar_h), (WIDTH, HEIGHT)], fill=(15, 23, 42, 240))
    d.line([(0, HEIGHT - bar_h), (WIDTH, HEIGHT - bar_h)], fill=(51, 65, 85, 255), width=1)
    
    d.text((40, HEIGHT - bar_h + 10), title, fill=(255, 255, 255, 255), font=FONT_TITLE)
    d.text((40, HEIGHT - bar_h + 36), subtitle, fill=(203, 213, 225, 255), font=FONT_SUB)
    
    return Image.alpha_composite(img, overlay)

def ease_in_out(t):
    """Smooth cosine ease-in-out easing function."""
    return (1 - math.cos(t * math.pi)) / 2

def interpolate_pos(p1, p2, t):
    t_eased = ease_in_out(max(0.0, min(1.0, t)))
    return (
        p1[0] + (p2[0] - p1[0]) * t_eased,
        p1[1] + (p2[1] - p1[1]) * t_eased
    )

def main():
    print("Initializing GTK assistant window...")
    styles.apply_theme(1.0)
    win = assistant_window.AssistantWindow(None)
    win.set_default_size(960, 600)
    win.show_all()
    pump_gtk(win)

    alloc = win.get_allocation()
    win_w, win_h = alloc.width, alloc.height
    print(f"Window dimensions: {win_w}x{win_h}")

    # Center window horizontally, placed cleanly below top taskbar
    win_x = (WIDTH - win_w) // 2
    win_y = 68

    # Mascot on desktop
    mascot_w, mascot_h = 160, 160
    mascot_x = WIDTH - 260
    mascot_y = HEIGHT - 280
    pos_mascot_center = (mascot_x + mascot_w // 2, mascot_y + mascot_h // 2)

    # Load mascot image
    mascot_file = os.path.join(ROOT_DIR, "assets", "mascot.png")
    if not os.path.exists(mascot_file):
        mascot_file = os.path.join(ROOT_DIR, "assets", "mascot-256.png")
    raw_mascot = Image.open(mascot_file).convert("RGBA")
    mascot_img = raw_mascot.resize((mascot_w, mascot_h), Image.Resampling.LANCZOS)
    mascot_corner_img = raw_mascot.resize((120, 120), Image.Resampling.LANCZOS)

    print("Querying exact widget coordinates from GTK...")
    coords = {}
    coords["tab_chat"] = get_widget_center(win.tab_buttons[0], win)
    coords["tab_fixes"] = get_widget_center(win.tab_buttons[1], win)
    coords["tab_apps"] = get_widget_center(win.tab_buttons[2], win)
    coords["tab_scam"] = get_widget_center(win.tab_buttons[3], win)
    coords["tab_health"] = get_widget_center(win.tab_buttons[4], win)

    coords["chat_entry"] = get_widget_center(win.entry_chat, win)
    coords["send_btn"] = get_widget_center(win.btn_send, win)
    coords["zoom_in"] = get_widget_center(win.btn_zoom_in, win)
    coords["zoom_out"] = get_widget_center(win.btn_zoom_out, win)

    # Sub-tab buttons
    win.select_tab("fixes")
    pump_gtk(win)
    coords["run_fix_0"] = get_widget_center(win.fixes_buttons[0][0], win)

    win.select_tab("apps")
    pump_gtk(win)
    if "firefox" in win.app_buttons:
        coords["app_btn"] = get_widget_center(win.app_buttons["firefox"][0], win)
    else:
        coords["app_btn"] = get_widget_center(list(win.app_buttons.values())[0][0], win)

    win.select_tab("scam")
    pump_gtk(win)
    coords["scam_btn"] = get_widget_center(win.btn_ask_scam, win)

    win.select_tab("health")
    pump_gtk(win)
    coords["health_btn"] = get_widget_center(win.btn_refresh_health, win)

    # Convert window-relative coordinates to absolute desktop screen positions
    def to_screen(w_coord):
        return (win_x + w_coord[0], win_y + w_coord[1])

    pos_tab_chat = to_screen(coords["tab_chat"])
    pos_tab_fixes = to_screen(coords["tab_fixes"])
    pos_tab_apps = to_screen(coords["tab_apps"])
    pos_tab_scam = to_screen(coords["tab_scam"])
    pos_tab_health = to_screen(coords["tab_health"])

    pos_chat_entry = to_screen(coords["chat_entry"])
    pos_send_btn = to_screen(coords["send_btn"])
    pos_run_fix = to_screen(coords["run_fix_0"])
    pos_app_btn = to_screen(coords["app_btn"])
    pos_scam_btn = to_screen(coords["scam_btn"])
    pos_health_btn = to_screen(coords["health_btn"])
    pos_zoom_in = to_screen(coords["zoom_in"])

    print("Absolute Screen Coordinates:")
    print(f"  Mascot: {pos_mascot_center}")
    print(f"  Chat Entry: {pos_chat_entry}")
    print(f"  Send Button: {pos_send_btn}")
    print(f"  Tab Chat: {pos_tab_chat}")
    print(f"  Tab Fixes: {pos_tab_fixes} -> Run Fix: {pos_run_fix}")
    print(f"  Tab Apps: {pos_tab_apps} -> App Action: {pos_app_btn}")
    print(f"  Tab Scam: {pos_tab_scam} -> Scam Action: {pos_scam_btn}")
    print(f"  Tab Health: {pos_tab_health} -> Health Action: {pos_health_btn}")
    print(f"  Zoom In (A+): {pos_zoom_in}")

    print("Pre-rendering visual UI states...")
    
    # State 1: Chat Welcome (Empty)
    win.select_tab("chat")
    win.entry_chat.set_text("")
    img_win_welcome = render_gtk_window(win)

    # State 2: Chat Entry with Question 1 Typed
    win.entry_chat.set_text("Why is my internet running slow today?")
    img_win_typing1 = render_gtk_window(win)

    # State 3: Chat Q1 Answered
    win.entry_chat.set_text("")
    win._add_message_bubble("Why is my internet running slow today?", is_user=True)
    win._add_message_bubble(
        "Here are three simple things to try:\n\n"
        "1. **Restart your router**: Unplug the power cord for 30 seconds, then plug it back in.\n"
        "2. **Move closer to Wi-Fi**: Walls and appliances can weaken your wireless signal.\n"
        "3. **Check other household devices**: Another device might be downloading a large update.",
        is_user=False
    )
    img_win_chat_q1 = render_gtk_window(win)

    # State 4: Chat Entry with Question 2 Typed
    win.entry_chat.set_text("Explain what RAM does")
    img_win_typing2 = render_gtk_window(win)

    # State 5: Chat Q2 Answered
    win.entry_chat.set_text("")
    win._add_message_bubble("Explain what RAM does", is_user=True)
    win._add_message_bubble(
        "Think of RAM like your computer's kitchen countertop.\n\n"
        "The bigger the countertop, the more ingredients and cooking tools you can have "
        "laid out at the same time without things getting crowded and slowing you down.",
        is_user=False
    )
    img_win_chat_q2 = render_gtk_window(win)

    # State 6: 1-Click Fixes Tab
    win.select_tab("fixes")
    img_win_fixes = render_gtk_window(win)

    # State 7: Everyday App Installer Tab
    win.select_tab("apps")
    img_win_apps = render_gtk_window(win)

    # State 8: Scam Help Tab
    win.select_tab("scam")
    img_win_scam = render_gtk_window(win)

    # State 9: Safety & Health Tab
    win.select_tab("health")
    img_win_health = render_gtk_window(win)

    # State 10: Senior Zoom (130%)
    win._on_zoom_in(None)
    win._on_zoom_in(None)
    win.select_tab("chat")
    img_win_zoom = render_gtk_window(win)

    desktop_base = create_desktop_base()

    # Pre-render drop shadow for window
    shadow_pad = 16
    shadow_box = Image.new("RGBA", (win_w + shadow_pad * 2, win_h + shadow_pad * 2), (0, 0, 0, 30))

    # Construct clean, discrete timeline segments
    # (start_frame, end_frame, p_start, p_end, click_at_end, title, subtitle, win_img)
    timeline = []
    current_frame = 0

    def add_move(p_start, p_end, num_frames, title, sub, win_img):
        nonlocal current_frame
        timeline.append((current_frame, current_frame + num_frames, p_start, p_end, False, title, sub, win_img))
        current_frame += num_frames

    def add_hover_click(pos, num_frames, title, sub, win_img):
        nonlocal current_frame
        timeline.append((current_frame, current_frame + num_frames, pos, pos, True, title, sub, win_img))
        current_frame += num_frames

    def add_hold(pos, num_frames, title, sub, win_img):
        nonlocal current_frame
        timeline.append((current_frame, current_frame + num_frames, pos, pos, False, title, sub, win_img))
        current_frame += num_frames

    # --- 1. Desktop & Mascot ---
    add_move((960, 540), pos_mascot_center, 48, "Meet Agy Desktop Helper", "A quiet, friendly companion designed for everyday computer tasks.", None)
    add_hover_click(pos_mascot_center, 24, "One-Click Assistance", "Click Agy anytime you have a question or need computer help.", None)

    # --- 2. Assistant Window Opens & Question 1 ---
    add_move(pos_mascot_center, pos_chat_entry, 36, "Assistant Window Opens", "A clean, simple window appears right on your screen without opening web browsers.", img_win_welcome)
    add_hover_click(pos_chat_entry, 18, "Natural Language Support", "Type questions in plain everyday English. No technical jargon required.", img_win_welcome)
    add_hold(pos_chat_entry, 18, "Natural Language Support", "Type questions in plain everyday English. No technical jargon required.", img_win_typing1)
    add_move(pos_chat_entry, pos_send_btn, 30, "Natural Language Support", "Type questions in plain everyday English. No technical jargon required.", img_win_typing1)
    add_hover_click(pos_send_btn, 18, "Instant AI Response", "Sending your question directly to Google AI assistance.", img_win_typing1)

    # Q1 Answer (Reading time: 4.0s)
    q1_read_pos = (win_x + 650, win_y + 420)
    add_move(pos_send_btn, q1_read_pos, 18, "Jargon-Free Guidance", "Agy gives clear physical steps you can easily check yourself.", img_win_chat_q1)
    add_hold(q1_read_pos, 96, "Jargon-Free Guidance", "Agy gives clear physical steps you can easily check yourself.", img_win_chat_q1)

    # --- 3. Question 2 (RAM Analogy) ---
    add_move(q1_read_pos, pos_chat_entry, 30, "Clear Explanations", "Ask any computer concept and receive friendly, relatable answers.", img_win_chat_q1)
    add_hover_click(pos_chat_entry, 18, "Clear Explanations", "Ask any computer concept and receive friendly, relatable answers.", img_win_chat_q1)
    add_hold(pos_chat_entry, 18, "Clear Explanations", "Ask any computer concept and receive friendly, relatable answers.", img_win_typing2)
    add_move(pos_chat_entry, pos_send_btn, 30, "Clear Explanations", "Ask any computer concept and receive friendly, relatable answers.", img_win_typing2)
    add_hover_click(pos_send_btn, 18, "Instant AI Response", "Sending your question directly to Google AI assistance.", img_win_typing2)

    # Q2 Answer (Reading time: 4.0s)
    q2_read_pos = (win_x + 650, win_y + 480)
    add_move(pos_send_btn, q2_read_pos, 18, "Relatable Analogies", "Understand your computer concepts through simple, friendly comparisons.", img_win_chat_q2)
    add_hold(q2_read_pos, 96, "Relatable Analogies", "Understand your computer concepts through simple, friendly comparisons.", img_win_chat_q2)

    # --- 4. Tab 1: 1-Click Fixes ---
    add_move(q2_read_pos, pos_tab_fixes, 30, "1-Click Computer Fixes", "Easily fix sound hiccups, restart Wi-Fi, and safely free up disk space.", img_win_chat_q2)
    add_hover_click(pos_tab_fixes, 18, "1-Click Computer Fixes", "Easily fix sound hiccups, restart Wi-Fi, and safely free up disk space.", img_win_chat_q2)
    add_hold(pos_tab_fixes, 12, "1-Click Computer Fixes", "Easily fix sound hiccups, restart Wi-Fi, and safely free up disk space.", img_win_fixes)
    add_move(pos_tab_fixes, pos_run_fix, 30, "1-Click Computer Fixes", "Easily fix sound hiccups, restart Wi-Fi, and safely free up disk space.", img_win_fixes)
    add_hover_click(pos_run_fix, 18, "Verified Safe Repairs", "One click resolves common system glitches without dangerous terminal commands.", img_win_fixes)
    add_hold(pos_run_fix, 48, "Verified Safe Repairs", "One click resolves common system glitches without dangerous terminal commands.", img_win_fixes)

    # --- 5. Tab 2: Everyday App Installer ---
    add_move(pos_run_fix, pos_tab_apps, 30, "Everyday App Installer", "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice.", img_win_fixes)
    add_hover_click(pos_tab_apps, 18, "Everyday App Installer", "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice.", img_win_fixes)
    add_hold(pos_tab_apps, 12, "Everyday App Installer", "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice.", img_win_apps)
    add_move(pos_tab_apps, pos_app_btn, 30, "Everyday App Installer", "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice with no bundled adware.", img_win_apps)
    add_hold(pos_app_btn, 48, "Zero Adware or Bundles", "Direct, official downloads for your favorite browsers and media players.", img_win_apps)

    # --- 6. Tab 3: Scam Help ---
    add_move(pos_app_btn, pos_tab_scam, 30, "Scam & Fraud Protection", "Clear, calm guidance on fake virus popups, delivery fees, and phone calls.", img_win_apps)
    add_hover_click(pos_tab_scam, 18, "Scam & Fraud Protection", "Clear, calm guidance on fake virus popups, delivery fees, and phone calls.", img_win_apps)
    add_hold(pos_tab_scam, 12, "Scam & Fraud Protection", "Clear, calm guidance on fake virus popups, delivery fees, and phone calls.", img_win_scam)
    add_move(pos_tab_scam, pos_scam_btn, 30, "Scam & Fraud Protection", "Clear, calm guidance on fake virus popups, delivery fees, and phone impersonations.", img_win_scam)
    add_hold(pos_scam_btn, 48, "Peace of Mind", "Never panic when an unexpected popup or warning appears on your screen.", img_win_scam)

    # --- 7. Tab 4: Safety & Health ---
    add_move(pos_scam_btn, pos_tab_health, 30, "Guaranteed Safety Guardrails", "Personal Documents and Pictures are permanently protected against deletion.", img_win_scam)
    add_hover_click(pos_tab_health, 18, "Guaranteed Safety Guardrails", "Personal Documents and Pictures are permanently protected against deletion.", img_win_scam)
    add_hold(pos_tab_health, 12, "Guaranteed Safety Guardrails", "Personal Documents and Pictures are permanently protected against deletion.", img_win_health)
    add_move(pos_tab_health, pos_health_btn, 30, "Guaranteed Safety Guardrails", "Personal Documents and Pictures are permanently protected against deletion.", img_win_health)
    add_hold(pos_health_btn, 48, "System Diagnostics", "Monitor real-time storage, memory, and safety status at a glance.", img_win_health)

    # --- 8. Senior Zoom & Accessibility ---
    add_move(pos_health_btn, pos_zoom_in, 30, "Senior Accessibility Mode", "One click instantly enlarges text across the entire application for effortless reading.", img_win_health)
    add_hover_click(pos_zoom_in, 18, "Senior Accessibility Mode", "One click instantly enlarges text across the entire application for effortless reading.", img_win_health)
    add_hold(pos_zoom_in, 12, "Senior Accessibility Mode", "One click instantly enlarges text across the entire application for effortless reading.", img_win_zoom)
    add_move(pos_zoom_in, pos_tab_chat, 24, "Agy Helper", "Free, private, and open-source desktop assistance for everyone.", img_win_zoom)
    add_hover_click(pos_tab_chat, 18, "Agy Helper", "Free, private, and open-source desktop assistance for everyone.", img_win_zoom)
    add_hold(pos_tab_chat, 48, "Agy Helper", "Free, private, and open-source desktop assistance for everyone.", img_win_zoom)

    total_frames = current_frame
    total_seconds = total_frames / FPS
    print(f"Master Timeline: {total_frames} frames ({total_seconds:.1f}s @ {FPS} fps)...")

    print(f"Streaming {total_frames} frames directly to ffmpeg (1920x1080 @ {FPS} fps)...")

    ffmpeg_bin = os.path.expanduser("~/.local/bin/ffmpeg")
    ffmpeg_cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgba",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "19",
        "-movflags", "+faststart",
        OUTPUT_MP4
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    for frame_idx in range(total_frames):
        # Find active segment in timeline
        seg = None
        for s in timeline:
            if s[0] <= frame_idx < s[1]:
                seg = s
                break
        if not seg:
            seg = timeline[-1]

        s_start, s_end, p_start, p_end, is_hover_click, cap_title, cap_sub, win_img = seg
        seg_len = max(1, s_end - s_start)
        seg_progress = (frame_idx - s_start) / seg_len

        # Base desktop
        frame = desktop_base.copy()

        # Mascot bobbing offset
        bob_offset = int(5 * math.sin(frame_idx * 0.12))

        # Render window or standalone mascot
        if win_img:
            # Soft drop shadow under window
            frame.paste(shadow_box, (win_x - shadow_pad, win_y - shadow_pad), shadow_box)
            frame.paste(win_img, (win_x, win_y), win_img)

            # Mascot in dock corner
            frame.paste(mascot_corner_img, (WIDTH - 180, HEIGHT - 180 + bob_offset), mascot_corner_img)
        else:
            # Full mascot on desktop with greeting bubble
            frame.paste(mascot_img, (mascot_x, mascot_y + bob_offset), mascot_img)
            draw_d = ImageDraw.Draw(frame)
            b_box = [mascot_x - 170, mascot_y - 50 + bob_offset, mascot_x + 90, mascot_y + 10 + bob_offset]
            draw_d.rounded_rectangle(b_box, radius=12, fill=(255, 255, 255, 250), outline=(203, 213, 225, 255), width=2)
            draw_d.text((b_box[0] + 16, b_box[1] + 18), "Hi! Click me for IT help", fill=(15, 23, 42, 255), font=FONT_SPEECH)

        # Interpolate cursor position with smooth cosine easing
        cur_x, cur_y = interpolate_pos(p_start, p_end, seg_progress)

        # Show click ripple during second half of hover-click segments
        is_clicking = is_hover_click and (seg_progress > 0.4)
        draw_cursor(frame, int(cur_x), int(cur_y), clicking=is_clicking)

        # Overlay slim caption banner
        frame = draw_caption_bar(frame, cap_title, cap_sub)

        # Stream raw RGBA bytes directly into ffmpeg pipe
        proc.stdin.write(frame.tobytes())

        if frame_idx % 240 == 0:
            pct = int((frame_idx / total_frames) * 100)
            print(f"Progress: {frame_idx}/{total_frames} frames ({pct}%)...")

    proc.stdin.close()
    proc.wait()
    print(f"MP4 created: {OUTPUT_MP4} ({os.path.getsize(OUTPUT_MP4) / (1024*1024):.2f} MB)")

    # Copy to Artifact directory
    dst_mp4 = os.path.join(ARTIFACT_DIR, "agy_helper_demo.mp4")
    shutil.copy2(OUTPUT_MP4, dst_mp4)

    # Generate an optimized companion animated GIF for markdown embed
    print("Generating animated GIF preview (960x540 @ 12fps)...")
    gif_cmd = [
        ffmpeg_bin,
        "-y",
        "-i", OUTPUT_MP4,
        "-vf", "fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        OUTPUT_GIF
    ]
    subprocess.run(gif_cmd, check=True)
    print(f"GIF created: {OUTPUT_GIF} ({os.path.getsize(OUTPUT_GIF) / (1024*1024):.2f} MB)")

    dst_gif = os.path.join(ARTIFACT_DIR, "agy_helper_demo.gif")
    shutil.copy2(OUTPUT_GIF, dst_gif)

    print("Demo recording successfully completed!")

if __name__ == "__main__":
    main()
