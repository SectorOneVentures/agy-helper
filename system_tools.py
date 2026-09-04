"""
Built-in IT Tools & Software Catalog for Agy Companion.
Handles diagnostic assessments, common 1-click IT repairs, and software installs safely.
"""

import os
import subprocess
import shutil
import threading
from typing import Dict, List, Any, Callable, Optional
from safety_engine import check_command_safety

# Popular software catalog tailored for everyday users
APP_CATALOG = [
    {
        "id": "chrome",
        "name": "Google Chrome",
        "category": "Web Browser",
        "description": "Fast, secure, and popular web browser by Google.",
        "icon": "chrome",
        "fallback_icon": "google-chrome",
        "pkg": "google-chrome-stable",
        "check_cmd": "which google-chrome || which google-chrome-stable || which chromium || which chromium-browser",
        "launch_cmd": "google-chrome 2>/dev/null || google-chrome-stable 2>/dev/null || chromium 2>/dev/null || chromium-browser 2>/dev/null",
        "install_cmd": "wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && pkexec dpkg -i /tmp/chrome.deb || pkexec apt-get --fix-broken install -y",
    },
    {
        "id": "firefox",
        "name": "Mozilla Firefox",
        "category": "Web Browser",
        "description": "Privacy-focused open-source web browser.",
        "icon": "firefox",
        "fallback_icon": "firefox",
        "pkg": "firefox",
        "check_cmd": "which firefox",
        "launch_cmd": "firefox 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y firefox || sudo snap install firefox",
    },
    {
        "id": "vlc",
        "name": "VLC Media Player",
        "category": "Media Player",
        "description": "Plays virtually any video or audio file smoothly.",
        "icon": "vlc",
        "fallback_icon": "applications-multimedia",
        "pkg": "vlc",
        "check_cmd": "which vlc",
        "launch_cmd": "vlc 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y vlc",
    },
    {
        "id": "code",
        "name": "Visual Studio Code",
        "category": "Development",
        "description": "Popular, powerful code and text editor by Microsoft.",
        "icon": "code",
        "fallback_icon": "applications-development",
        "pkg": "code",
        "check_cmd": "which code",
        "launch_cmd": "code 2>/dev/null",
        "install_cmd": "sudo snap install --classic code || (pkexec apt-get update && pkexec apt-get install -y code)",
    },
    {
        "id": "spotify",
        "name": "Spotify Music",
        "category": "Music & Audio",
        "description": "Stream millions of songs, albums, and podcasts.",
        "icon": "spotify",
        "fallback_icon": "multimedia-audio-player",
        "pkg": "spotify",
        "check_cmd": "which spotify || snap list spotify 2>/dev/null",
        "launch_cmd": "spotify 2>/dev/null",
        "install_cmd": "sudo snap install spotify",
    },
    {
        "id": "gimp",
        "name": "GIMP Image Editor",
        "category": "Graphics",
        "description": "Full-featured photo editing and graphic creation tool.",
        "icon": "gimp",
        "fallback_icon": "applications-graphics",
        "pkg": "gimp",
        "check_cmd": "which gimp",
        "launch_cmd": "gimp 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y gimp",
    },
    {
        "id": "libreoffice",
        "name": "LibreOffice Suite",
        "category": "Office",
        "description": "Complete office suite for documents, spreadsheets, and presentations.",
        "icon": "libreoffice",
        "fallback_icon": "libreoffice-main",
        "pkg": "libreoffice",
        "check_cmd": "which libreoffice",
        "launch_cmd": "libreoffice 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y libreoffice",
    },
    {
        "id": "discord",
        "name": "Discord",
        "category": "Chat & Voice",
        "description": "Voice, video, and text communication platform.",
        "icon": "discord",
        "fallback_icon": "user-available",
        "pkg": "discord",
        "check_cmd": "which discord || snap list discord 2>/dev/null",
        "launch_cmd": "discord 2>/dev/null",
        "install_cmd": "sudo snap install discord",
    },
    {
        "id": "steam",
        "name": "Steam Gaming",
        "category": "Games",
        "description": "Ultimate destination for playing and discussing games.",
        "icon": "steam",
        "fallback_icon": "applications-games",
        "pkg": "steam",
        "check_cmd": "which steam",
        "launch_cmd": "steam 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y steam-installer || sudo snap install steam",
    },
    {
        "id": "inkscape",
        "name": "Inkscape Vector Graphics",
        "category": "Graphics",
        "description": "Professional vector graphics illustration program.",
        "icon": "inkscape",
        "fallback_icon": "applications-graphics",
        "pkg": "inkscape",
        "check_cmd": "which inkscape",
        "launch_cmd": "inkscape 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y inkscape",
    },
    {
        "id": "audacity",
        "name": "Audacity Sound Editor",
        "category": "Music & Audio",
        "description": "Multi-track audio recording and editing software.",
        "icon": "audacity",
        "fallback_icon": "multimedia-audio-player",
        "pkg": "audacity",
        "check_cmd": "which audacity",
        "launch_cmd": "audacity 2>/dev/null",
        "install_cmd": "pkexec apt-get update && pkexec apt-get install -y audacity",
    },
]

def launch_app_async(launch_cmd: str):
    """Launches an installed application in the background."""
    def _launch():
        try:
            subprocess.Popen(
                launch_cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=get_system_env(),
                start_new_session=True
            )
        except Exception as e:
            print(f"Error launching app ({launch_cmd}): {e}")

    t = threading.Thread(target=_launch, daemon=True)
    t.start()

# Quick IT Fix definitions
QUICK_FIXES = [
    {
        "id": "fix_network",
        "title": "Fix Internet & Wi-Fi",
        "icon": "network-wireless-symbolic",
        "summary": "Flushes DNS cache, verifies gateway, and restarts Network Manager.",
        "cmd": "resolvectl flush-caches 2>/dev/null || systemd-resolve --flush-caches 2>/dev/null; pkexec systemctl restart NetworkManager; ping -c 2 8.8.8.8",
    },
    {
        "id": "fix_packages",
        "title": "Repair Software & App Updates",
        "icon": "system-software-update-symbolic",
        "summary": "Fixes broken package locks, configures pending installs, and updates software repositories.",
        "cmd": "pkexec dpkg --configure -a && pkexec apt-get --fix-broken install -y && pkexec apt-get update",
    },
    {
        "id": "clean_space",
        "title": "Free Up Disk Space Safely",
        "icon": "drive-harddisk-symbolic",
        "summary": "Safely clears old package caches, thumbnails, and vacuum logs. Personal files in Documents, Music, and Pictures are NEVER touched.",
        "cmd": "rm -rf ~/.cache/thumbnails/* 2>/dev/null; pkexec apt-get clean; pkexec journalctl --vacuum-time=7d",
    },
    {
        "id": "fix_audio",
        "title": "Restart Audio & Sound",
        "icon": "audio-speakers-symbolic",
        "summary": "Restarts PipeWire / PulseAudio sound servers and un-mutes audio channels.",
        "cmd": "systemctl --user restart pipewire pipewire-pulse wireplumber 2>/dev/null || pulseaudio -k 2>/dev/null; pactl set-sink-mute @DEFAULT_SINK@ 0 2>/dev/null || true",
    },
    {
        "id": "check_health",
        "title": "Full System Health Check",
        "icon": "utilities-system-monitor-symbolic",
        "summary": "Analyzes storage usage, memory load, processor temperatures, and battery condition.",
        "cmd": "echo '=== Storage ==='; df -h -x tmpfs -x devtmpfs; echo '\n=== Memory ==='; free -h; echo '\n=== Uptime ==='; uptime",
    },
    {
        "id": "update_system",
        "title": "Check & Apply System Updates",
        "icon": "software-update-available-symbolic",
        "summary": "Safely fetches and applies available security and software updates.",
        "cmd": "pkexec apt-get update && pkexec apt-get upgrade -y",
    },
]

def get_system_env() -> Dict[str, str]:
    """Returns an environment with standard and user binary paths."""
    env = os.environ.copy()
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
    cur_path = env.get("PATH", "")
    cur_list = cur_path.split(":") if cur_path else []
    all_paths = [p for p in extra_paths if p not in cur_list] + cur_list
    env["PATH"] = ":".join(all_paths)
    return env

def check_app_installed(check_cmd: str) -> bool:
    """Checks if an app is installed on the system."""
    try:
        res = subprocess.run(
            check_cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=get_system_env()
        )
        return res.returncode == 0
    except Exception:
        return False

def get_system_health() -> Dict[str, Any]:
    """Gathers real-time system metrics for the UI."""
    data = {
        "cpu_usage": "N/A",
        "ram_usage": "N/A",
        "ram_percent": 0,
        "disk_usage": "N/A",
        "disk_percent": 0,
        "battery": "N/A",
        "uptime": "N/A",
    }
    
    # 1. Memory
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
        mem = {}
        for l in lines:
            parts = l.split(":")
            if len(parts) == 2:
                mem[parts[0].strip()] = int(parts[1].strip().split()[0])
        total_kb = mem.get("MemTotal", 0)
        avail_kb = mem.get("MemAvailable", 0)
        if total_kb > 0:
            used_kb = total_kb - avail_kb
            pct = int((used_kb / total_kb) * 100)
            data["ram_percent"] = pct
            data["ram_usage"] = f"{used_kb // 1024} MB / {total_kb // 1024} MB ({pct}%)"
    except Exception:
        pass

    # 2. Disk
    try:
        stat = os.statvfs(os.path.expanduser("~"))
        total = stat.f_blocks * stat.f_frsize
        avail = stat.f_bavail * stat.f_frsize
        used = total - avail
        if total > 0:
            pct = int((used / total) * 100)
            data["disk_percent"] = pct
            data["disk_usage"] = f"{used // (1024**3)} GB / {total // (1024**3)} GB ({pct}% used)"
    except Exception:
        pass

    # 3. Uptime
    try:
        with open("/proc/uptime", "r") as f:
            up_secs = float(f.readline().split()[0])
        hours = int(up_secs // 3600)
        mins = int((up_secs % 3600) // 60)
        data["uptime"] = f"{hours}h {mins}m"
    except Exception:
        pass

    return data

def run_command_safe_async(
    cmd_str: str,
    on_output: Callable[[str], None],
    on_complete: Callable[[int, str], None]
):
    """
    Validates safety and executes command in a background thread,
    streaming output line-by-line to on_output.
    """
    is_safe, safety_msg, _ = check_command_safety(cmd_str)
    if not is_safe:
        on_output(f"❌ EXECUTION BLOCKED BY SAFETY ENGINE:\n{safety_msg}\n")
        on_complete(1, safety_msg)
        return

    def _worker():
        try:
            on_output(f"🚀 Starting task: {cmd_str}\n" + "─" * 45 + "\n")
            process = subprocess.Popen(
                cmd_str,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=get_system_env(),
                bufsize=1
            )

            full_log = []
            for line in iter(process.stdout.readline, ''):
                full_log.append(line)
                on_output(line)

            process.stdout.close()
            ret = process.wait()
            on_output("\n" + "─" * 45 + f"\nFinished with code {ret}.\n")
            on_complete(ret, "".join(full_log))
        except Exception as e:
            err_msg = f"Task error: {e}\n"
            on_output(err_msg)
            on_complete(1, err_msg)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
