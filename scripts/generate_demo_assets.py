#!/usr/bin/env python3
"""
Generates high-resolution screenshots and an animated demo for Agy Helper.
Captures the companion mascot, the assistant window opening, chat questions,
1-click fixes, app installer, scam help, and safety features.
"""

import os
import sys
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from PIL import Image, ImageDraw, ImageFont

# Set up paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import styles
import assistant_window
import companion_widget

OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ARTIFACT_DIR = "/home/sectoroneventures/.gemini/antigravity/brain/b2b82baa-3f56-43fe-8ae8-1fb7e7dfd3aa"

# Typography for clean, unobtrusive captions
try:
    FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_SUB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()

def render_widget_to_image(widget, min_w=850, min_h=720):
    """Renders any GTK widget to a PIL Image using Cairo."""
    widget.queue_draw()
    for _ in range(15):
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
    
    alloc = widget.get_allocation()
    w = max(alloc.width, min_w)
    h = max(alloc.height, min_h)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(surface)
    widget.draw(cr)
    
    # Write to temporary png and load with PIL
    tmp_path = f"/tmp/widget_{os.getpid()}.png"
    surface.write_to_png(tmp_path)
    img = Image.open(tmp_path).convert("RGBA")
    try:
        os.remove(tmp_path)
    except Exception:
        pass
    return img

def create_desktop_canvas(width=1280, height=800):
    """Creates a modern, elegant desktop background canvas."""
    # Subtle soft slate-blue gradient background
    base = Image.new("RGBA", (width, height), (235, 240, 246, 255))
    draw = ImageDraw.Draw(base)
    
    # Top taskbar
    draw.rectangle([(0, 0), (width, 36)], fill=(255, 255, 255, 240))
    draw.line([(0, 36), (width, 36)], fill=(226, 232, 240, 255), width=1)
    draw.text((20, 9), "Activities", fill=(71, 85, 105, 255), font=FONT_SUB)
    draw.text((width // 2 - 40, 9), "Tue 3:30 PM", fill=(71, 85, 105, 255), font=FONT_SUB)
    draw.text((width - 140, 9), "Wi-Fi  Sound  Battery", fill=(100, 116, 139, 255), font=FONT_SUB)
    
    return base

def draw_caption_banner(img, title, subtitle):
    """Draws a clean, unobtrusive caption bar at the bottom with no emojis."""
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    
    # Elegant translucent dark pill/banner
    bar_h = 70
    d.rectangle([(0, h - bar_h), (w, h)], fill=(15, 23, 42, 230))
    d.line([(0, h - bar_h), (w, h - bar_h)], fill=(51, 65, 85, 255), width=1)
    
    # Title & Subtitle in crisp white and soft slate
    d.text((40, h - bar_h + 12), title, fill=(255, 255, 255, 255), font=FONT_TITLE)
    d.text((40, h - bar_h + 38), subtitle, fill=(203, 213, 225, 255), font=FONT_SUB)
    
    return Image.alpha_composite(img, overlay)

def main():
    print("Initializing GTK theme and windows...")
    styles.apply_theme(1.0)
    
    # Create assistant window
    win = assistant_window.AssistantWindow(None)
    win.set_size_request(860, 680)
    win.show_all()

    # Load mascot image
    mascot_path = os.path.join(ROOT_DIR, "assets", "mascot.png")
    if not os.path.exists(mascot_path):
        mascot_path = os.path.join(ROOT_DIR, "assets", "mascot-160.png")
    mascot_img = Image.open(mascot_path).convert("RGBA")
    mascot_w, mascot_h = 140, 140
    mascot_thumb = mascot_img.resize((mascot_w, mascot_h), Image.Resampling.LANCZOS)

    # Frame list for GIF
    demo_slides = []

    # -------------------------------------------------------------
    # SLIDE 1: Mascot on Desktop
    # -------------------------------------------------------------
    print("Capturing Slide 1: Companion on desktop...")
    bg1 = create_desktop_canvas()
    
    # Draw speech bubble for Agy
    draw1 = ImageDraw.Draw(bg1)
    bubble_box = [1280 - 240, 800 - 250, 1280 - 40, 800 - 190]
    draw1.rounded_rectangle(bubble_box, radius=12, fill=(255, 255, 255, 250), outline=(203, 213, 225, 255), width=1)
    draw1.text((bubble_box[0] + 16, bubble_box[1] + 16), "Hi! Click me for IT help", fill=(30, 41, 59, 255), font=FONT_SUB)
    bg1.paste(mascot_thumb, (1280 - 200, 800 - 180), mascot_thumb)
    
    frame1 = draw_caption_banner(
        bg1,
        "Meet Agy Desktop Helper",
        "A quiet, friendly desktop assistant designed for everyday computer tasks."
    )
    frame1.save(os.path.join(OUTPUT_DIR, "01_desktop_companion.png"))
    demo_slides.append((frame1, 4000))

    # -------------------------------------------------------------
    # SLIDE 2: Chat Welcome Screen
    # -------------------------------------------------------------
    print("Capturing Slide 2: Chat welcome...")
    win.select_tab("chat")
    img_chat_win = render_widget_to_image(win, 860, 640)
    
    bg2 = create_desktop_canvas()
    bg2.paste(img_chat_win, (120, 50), img_chat_win)
    bg2.paste(mascot_thumb, (1280 - 160, 800 - 160), mascot_thumb)
    
    frame2 = draw_caption_banner(
        bg2,
        "One-Click Assistant",
        "Click Agy anytime you have a question, need maintenance, or suspect an issue."
    )
    frame2.save(os.path.join(OUTPUT_DIR, "02_chat_welcome.png"))
    demo_slides.append((frame2, 3500))

    # -------------------------------------------------------------
    # SLIDE 3: Chat with Plain-English Questions & Answers
    # -------------------------------------------------------------
    print("Capturing Slide 3: Friendly Tech Support Q&A...")
    win._add_message_bubble("Why is my internet running slow today?", is_user=True)
    win._add_message_bubble(
        "Here are three simple things to try:\n\n"
        "1. **Restart your router**: Unplug the power cord for 30 seconds, then plug it back in.\n"
        "2. **Move closer to Wi-Fi**: Walls and appliances can weaken your wireless signal.\n"
        "3. **Check other household devices**: Another device might be downloading a large update.",
        is_user=False
    )
    img_chat_qa = render_widget_to_image(win, 860, 640)
    
    bg3 = create_desktop_canvas()
    bg3.paste(img_chat_qa, (120, 50), img_chat_qa)
    
    frame3 = draw_caption_banner(
        bg3,
        "Jargon-Free AI Support",
        "Ask questions naturally. Agy provides practical physical steps with no scary terminal commands."
    )
    frame3.save(os.path.join(OUTPUT_DIR, "03_chat_plain_english_advice.png"))
    demo_slides.append((frame3, 5000))

    # -------------------------------------------------------------
    # SLIDE 4: 1-Click IT Fixes Tab
    # -------------------------------------------------------------
    print("Capturing Slide 4: 1-Click IT Fixes...")
    win.select_tab("fixes")
    img_fixes = render_widget_to_image(win, 860, 640)
    
    bg4 = create_desktop_canvas()
    bg4.paste(img_fixes, (120, 50), img_fixes)
    
    frame4 = draw_caption_banner(
        bg4,
        "1-Click Computer Fixes",
        "Easily restore sound, restart network adapters, and safely reclaim gigabytes of disk space."
    )
    frame4.save(os.path.join(OUTPUT_DIR, "04_one_click_fixes.png"))
    demo_slides.append((frame4, 4500))

    # -------------------------------------------------------------
    # SLIDE 5: Everyday App Catalog Tab
    # -------------------------------------------------------------
    print("Capturing Slide 5: Everyday App Installer...")
    win.select_tab("apps")
    img_apps = render_widget_to_image(win, 860, 640)
    
    bg5 = create_desktop_canvas()
    bg5.paste(img_apps, (120, 50), img_apps)
    
    frame5 = draw_caption_banner(
        bg5,
        "Everyday App Installer",
        "Install trusted programs like Chrome, Firefox, VLC, and LibreOffice with zero bundled adware."
    )
    frame5.save(os.path.join(OUTPUT_DIR, "05_app_installer.png"))
    demo_slides.append((frame5, 4500))

    # -------------------------------------------------------------
    # SLIDE 6: Scam Help Tab
    # -------------------------------------------------------------
    print("Capturing Slide 6: Scam Help Tab...")
    win.select_tab("scam")
    img_scam = render_widget_to_image(win, 860, 640)
    
    bg6 = create_desktop_canvas()
    bg6.paste(img_scam, (120, 50), img_scam)
    
    frame6 = draw_caption_banner(
        bg6,
        "Scam & Fraud Protection",
        "Clear guidance on fake virus popups, phishing delivery texts, and urgent caller impersonations."
    )
    frame6.save(os.path.join(OUTPUT_DIR, "06_scam_help.png"))
    demo_slides.append((frame6, 4500))

    # -------------------------------------------------------------
    # SLIDE 7: Safety & System Health Tab
    # -------------------------------------------------------------
    print("Capturing Slide 7: Safety & System Health...")
    win.select_tab("health")
    img_health = render_widget_to_image(win, 860, 640)
    
    bg7 = create_desktop_canvas()
    bg7.paste(img_health, (120, 50), img_health)
    
    frame7 = draw_caption_banner(
        bg7,
        "Guaranteed Safety Engine",
        "Personal Documents, Pictures, and Music are permanently shielded and can never be deleted."
    )
    frame7.save(os.path.join(OUTPUT_DIR, "07_system_health.png"))
    demo_slides.append((frame7, 4500))

    # -------------------------------------------------------------
    # SLIDE 8: Senior Accessibility Mode (Zoom)
    # -------------------------------------------------------------
    print("Capturing Slide 8: Senior Zoom Accessibility...")
    win._on_zoom_in(None)
    win._on_zoom_in(None)
    win.select_tab("chat")
    img_zoom = render_widget_to_image(win, 860, 640)
    
    bg8 = create_desktop_canvas()
    bg8.paste(img_zoom, (120, 50), img_zoom)
    
    frame8 = draw_caption_banner(
        bg8,
        "Senior Accessibility Mode",
        "Enlarge text and buttons across the entire app with dedicated A- and A+ top-bar controls."
    )
    frame8.save(os.path.join(OUTPUT_DIR, "08_senior_zoom.png"))
    demo_slides.append((frame8, 4000))

    # -------------------------------------------------------------
    # Compile Looping Animated Demo GIF
    # -------------------------------------------------------------
    print("Assembling animated demo GIF...")
    gif_path = os.path.join(OUTPUT_DIR, "agy_helper_demo.gif")
    frames = [slide[0].convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT) for slide in demo_slides]
    durations = [slide[1] for slide in demo_slides]
    
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Demo GIF created: {gif_path}")

    # Copy files to Artifact Directory for UI viewing
    for f in os.listdir(OUTPUT_DIR):
        src = os.path.join(OUTPUT_DIR, f)
        dst = os.path.join(ARTIFACT_DIR, f)
        with open(src, "rb") as rf, open(dst, "wb") as wf:
            wf.write(rf.read())
    print(f"All demo screenshots and GIF copied to artifact directory: {ARTIFACT_DIR}")

if __name__ == "__main__":
    main()
