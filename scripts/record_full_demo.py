#!/usr/bin/env python3
"""
Records a smooth, professional 46-second video demo (1280x720 @ 24fps) of Agy Helper in action.
Includes:
- Living mascot character resting on desktop
- Mouse cursor glides to Agy and clicks
- Assistant window opens smoothly
- Typing everyday questions in chat
- Jargon-free answers appearing
- Rolling through menus: 1-Click Fixes, App Installer, Scam Help, Safety & Health
- Senior Zoom text enlargement
- Unobtrusive, legible captions with NO emojis
"""

import os
import sys
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

WIDTH, HEIGHT = 1280, 720
FPS = 24
TOTAL_SECONDS = 46
TOTAL_FRAMES = FPS * TOTAL_SECONDS

try:
    FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    FONT_SUB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()

def render_gtk_window(win, w=840, h=590):
    """Renders the AssistantWindow to a PIL RGBA image."""
    win.queue_draw()
    for _ in range(15):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
    
    alloc = win.get_allocation()
    rw = max(alloc.width, w)
    rh = max(alloc.height, h)
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, rw, rh)
    cr = cairo.Context(surface)
    win.draw(cr)
    
    tmp = f"/tmp/gtktmp_{os.getpid()}.png"
    surface.write_to_png(tmp)
    img = Image.open(tmp).convert("RGBA")
    try:
        os.remove(tmp)
    except Exception:
        pass
    if img.size != (w, h):
        img = img.resize((w, h), Image.Resampling.LANCZOS)
    return img

def create_desktop_base():
    """Renders a clean, high-resolution desktop background."""
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (236, 242, 248, 255))
    d = ImageDraw.Draw(bg)
    
    # Soft background gradient
    for y in range(HEIGHT):
        alpha = y / HEIGHT
        r = int(238 * (1 - alpha * 0.05))
        g = int(244 * (1 - alpha * 0.05))
        b = int(250 * (1 - alpha * 0.02))
        d.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    
    # Top taskbar
    d.rectangle([(0, 0), (WIDTH, 32)], fill=(255, 255, 255, 240))
    d.line([(0, 32), (WIDTH, 32)], fill=(226, 232, 240, 255), width=1)
    d.text((18, 7), "Activities", fill=(71, 85, 105, 255), font=FONT_SUB)
    d.text((WIDTH // 2 - 35, 7), "Tuesday 3:30 PM", fill=(71, 85, 105, 255), font=FONT_SUB)
    d.text((WIDTH - 150, 7), "Wi-Fi  Sound  Battery", fill=(100, 116, 139, 255), font=FONT_SUB)
    return bg

def draw_cursor(img, x, y, clicking=False):
    """Draws a crisp desktop mouse pointer."""
    d = ImageDraw.Draw(img)
    pts = [(x, y), (x, y + 18), (x + 4, y + 14), (x + 8, y + 22), 
           (x + 11, y + 20), (x + 7, y + 13), (x + 13, y + 13)]
    
    if clicking:
        d.ellipse([(x - 8, y - 8), (x + 8, y + 8)], outline=(10, 132, 255, 220), width=2)
    
    shadow_pts = [(px + 1, py + 1) for px, py in pts]
    d.polygon(shadow_pts, fill=(0, 0, 0, 90))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(30, 41, 59, 255))

def draw_caption_bar(img, title, subtitle):
    """Renders a slim, elegant, non-obtrusive lower-third bar without emojis."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    
    bar_h = 56
    d.rectangle([(0, HEIGHT - bar_h), (WIDTH, HEIGHT)], fill=(15, 23, 42, 235))
    d.line([(0, HEIGHT - bar_h), (WIDTH, HEIGHT - bar_h)], fill=(51, 65, 85, 255), width=1)
    
    d.text((32, HEIGHT - bar_h + 8), title, fill=(255, 255, 255, 255), font=FONT_TITLE)
    d.text((32, HEIGHT - bar_h + 30), subtitle, fill=(203, 213, 225, 255), font=FONT_SUB)
    
    return Image.alpha_composite(img, overlay)

def ease_in_out(t):
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
    win.set_size_request(840, 590)
    win.show_all()

    # Load mascot image
    mascot_file = os.path.join(ROOT_DIR, "assets", "mascot.png")
    if not os.path.exists(mascot_file):
        mascot_file = os.path.join(ROOT_DIR, "assets", "mascot-160.png")
    raw_mascot = Image.open(mascot_file).convert("RGBA")
    mascot_img = raw_mascot.resize((120, 120), Image.Resampling.LANCZOS)

    # Pre-render window states
    print("Pre-rendering window states...")
    
    # State A: Chat Initial
    win.select_tab("chat")
    img_win_chat_init = render_gtk_window(win)

    # State B: Chat with First Question & Answer
    win._add_message_bubble("Why is my internet running slow today?", is_user=True)
    win._add_message_bubble(
        "Here are three simple things to try:\n\n"
        "1. **Restart your router**: Unplug the power cord for 30 seconds, then plug it back in.\n"
        "2. **Move closer to Wi-Fi**: Walls and appliances can weaken your wireless signal.\n"
        "3. **Check other household devices**: Another device might be downloading a large update.",
        is_user=False
    )
    img_win_chat_q1 = render_gtk_window(win)

    # State C: Chat with Second Question & Answer
    win._add_message_bubble("Explain what RAM does", is_user=True)
    win._add_message_bubble(
        "Think of RAM like your computer's kitchen countertop.\n\n"
        "The bigger the countertop, the more ingredients and cooking tools you can have "
        "laid out at the same time without things getting crowded and slowing you down.",
        is_user=False
    )
    img_win_chat_q2 = render_gtk_window(win)

    # State D: 1-Click Fixes
    win.select_tab("fixes")
    img_win_fixes = render_gtk_window(win)

    # State E: App Installer
    win.select_tab("apps")
    img_win_apps = render_gtk_window(win)

    # State F: Scam Help
    win.select_tab("scam")
    img_win_scam = render_gtk_window(win)

    # State G: Safety & Health
    win.select_tab("health")
    img_win_health = render_gtk_window(win)

    # State H: Zoom In (130%)
    win._on_zoom_in(None)
    win._on_zoom_in(None)
    win.select_tab("chat")
    img_win_zoom = render_gtk_window(win)

    desktop_base = create_desktop_base()
    
    # Window placement on desktop
    win_x = (WIDTH - 840) // 2
    win_y = 55
    
    mascot_x = WIDTH - 160
    mascot_y = HEIGHT - 180

    print(f"Rendering {TOTAL_FRAMES} frames (~{TOTAL_SECONDS}s at {FPS} fps)...")

    # Define Timeline Waypoints
    # (start_frame, end_frame, start_pos, end_pos, click_at_end, caption_title, caption_sub, win_state)
    timeline = [
        # 0 - 3.5s: Desktop with mascot waiting
        (0, 84, (640, 360), (mascot_x + 60, mascot_y + 40), False,
         "Meet Agy Desktop Helper",
         "A quiet, friendly desktop assistant designed for everyday computer tasks.",
         None),
        
        # 3.5 - 5.0s: Glide to mascot and click
        (84, 120, (mascot_x + 60, mascot_y + 40), (mascot_x + 60, mascot_y + 40), True,
         "One-Click Assistance",
         "Click Agy anytime you have a question or need computer help.",
         None),

        # 5.0 - 8.0s: Window opens smoothly
        (120, 192, (mascot_x + 60, mascot_y + 40), (win_x + 350, win_y + 535), False,
         "Assistant Window Opens",
         "A clean, simple window appears right on your screen without opening web browsers.",
         img_win_chat_init),

        # 8.0 - 13.0s: Typing first question & asking
        (192, 312, (win_x + 350, win_y + 535), (win_x + 750, win_y + 535), True,
         "Natural Language Support",
         "Type questions in plain everyday English. No technical jargon required.",
         img_win_chat_init),

        # 13.0 - 19.5s: Agy answers with simple practical steps
        (312, 468, (win_x + 750, win_y + 535), (win_x + 400, win_y + 350), False,
         "Jargon-Free Guidance",
         "Agy gives clear physical steps you can easily check yourself.",
         img_win_chat_q1),

        # 19.5 - 25.5s: Second question and answer (RAM explanation)
        (468, 612, (win_x + 400, win_y + 350), (win_x + 610, win_y + 140), True,
         "Clear Explanations",
         "Understand your computer concepts through simple, friendly everyday comparisons.",
         img_win_chat_q2),

        # 25.5 - 30.5s: 1-Click Fixes tab
        (612, 732, (win_x + 280, win_y + 105), (win_x + 730, win_y + 295), False,
         "1-Click Computer Fixes",
         "Easily fix sound hiccups, restart Wi-Fi, and safely free up gigabytes of disk space.",
         img_win_fixes),

        # 30.5 - 35.5s: Everyday App Installer
        (732, 852, (win_x + 410, win_y + 105), (win_x + 730, win_y + 240), False,
         "Everyday App Installer",
         "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice with no bundled adware.",
         img_win_apps),

        # 35.5 - 40.5s: Scam Help tab
        (852, 972, (win_x + 530, win_y + 105), (win_x + 380, win_y + 290), False,
         "Scam & Fraud Protection",
         "Clear, calm guidance on fake virus popups, delivery fees, and phone impersonations.",
         img_win_scam),

        # 40.5 - 44.5s: Safety & Health + Zoom Accessibility
        (972, 1068, (win_x + 660, win_y + 105), (win_x + 600, win_y + 55), True,
         "Guaranteed Safety & Text Zoom",
         "Personal Documents and Pictures are permanently protected. Text enlarges with one click.",
         img_win_health),

        # 44.5 - 46.0s: Final view at enlarged font
        (1068, TOTAL_FRAMES, (win_x + 600, win_y + 55), (win_x + 420, win_y + 300), False,
         "Agy Helper",
         "Free, private, and open-source desktop assistance for everyone.",
         img_win_zoom),
    ]

    print(f"Streaming {TOTAL_FRAMES} frames (~{TOTAL_SECONDS}s at {FPS} fps) directly to ffmpeg...")

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

    for frame_idx in range(TOTAL_FRAMES):
        # Find active segment in timeline
        seg = None
        for s in timeline:
            if s[0] <= frame_idx < s[1]:
                seg = s
                break
        if not seg:
            seg = timeline[-1]

        s_start, s_end, p_start, p_end, click_flag, cap_title, cap_sub, win_img = seg
        seg_progress = (frame_idx - s_start) / max(1, (s_end - s_start))
        
        # Base frame
        frame = desktop_base.copy()
        
        # Mascot floating bob
        bob_offset = int(4 * math.sin(frame_idx * 0.15))
        
        # If window is open, paste window
        if win_img:
            # Drop shadow
            shadow_box = Image.new("RGBA", (win_img.width + 20, win_img.height + 20), (0, 0, 0, 25))
            frame.paste(shadow_box, (win_x - 10, win_y - 8), shadow_box)
            frame.paste(win_img, (win_x, win_y), win_img)
            
            # Draw mascot in smaller dock corner
            frame.paste(mascot_img, (mascot_x + 30, mascot_y + bob_offset + 30), mascot_img)
        else:
            # Mascot with speech bubble on desktop
            frame.paste(mascot_img, (mascot_x, mascot_y + bob_offset), mascot_img)
            draw_d = ImageDraw.Draw(frame)
            b_box = [mascot_x - 120, mascot_y - 50 + bob_offset, mascot_x + 80, mascot_y + bob_offset]
            draw_d.rounded_rectangle(b_box, radius=10, fill=(255, 255, 255, 245), outline=(203, 213, 225, 255), width=1)
            draw_d.text((b_box[0] + 12, b_box[1] + 14), "Hi! Click me for IT help", fill=(30, 41, 59, 255), font=FONT_SUB)

        # Interpolate cursor position
        cur_x, cur_y = interpolate_pos(p_start, p_end, seg_progress)
        
        # Click indicator near end of click segments
        is_clicking = click_flag and (seg_progress > 0.8)
        draw_cursor(frame, int(cur_x), int(cur_y), clicking=is_clicking)

        # Overlay caption banner
        frame = draw_caption_bar(frame, cap_title, cap_sub)

        # Pipe raw frame RGBA bytes directly
        proc.stdin.write(frame.tobytes())

        if frame_idx % 240 == 0:
            pct = int((frame_idx / TOTAL_FRAMES) * 100)
            print(f"Progress: {frame_idx}/{TOTAL_FRAMES} frames ({pct}%)...")

    proc.stdin.close()
    proc.wait()
    print(f"MP4 created: {OUTPUT_MP4} ({os.path.getsize(OUTPUT_MP4) / (1024*1024):.2f} MB)")

    # Copy to Artifact directory
    dst_mp4 = os.path.join(ARTIFACT_DIR, "agy_helper_demo.mp4")
    shutil.copy2(OUTPUT_MP4, dst_mp4)

    # Generate an optimized companion GIF for markdown preview
    print("Generating animated GIF preview...")
    gif_cmd = [
        ffmpeg_bin,
        "-y",
        "-i", OUTPUT_MP4,
        "-vf", "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        OUTPUT_GIF
    ]
    subprocess.run(gif_cmd, check=True)
    print(f"GIF created: {OUTPUT_GIF} ({os.path.getsize(OUTPUT_GIF) / (1024*1024):.2f} MB)")
    
    dst_gif = os.path.join(ARTIFACT_DIR, "agy_helper_demo.gif")
    shutil.copy2(OUTPUT_GIF, dst_gif)

    print("Demo recording complete!")

if __name__ == "__main__":
    main()
