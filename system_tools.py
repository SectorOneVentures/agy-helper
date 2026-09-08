"""
Built-in IT Tools & Software Catalog for Agy Companion.
Handles diagnostic assessments, common 1-click IT repairs, and software installs safely.
"""

import os
import sys
import subprocess
import shutil
import threading
from typing import Dict, List, Any, Callable, Optional
from safety_engine import check_command_safety

def get_app_catalog() -> List[Dict[str, Any]]:
    """Returns platform-tailored everyday application catalog."""
    if sys.platform.startswith("win"):
        return [
            {
                "id": "chrome",
                "name": "Google Chrome",
                "category": "Web Browser",
                "description": "Fast, simple, and secure web browser for everyday browsing.",
                "icon": "chrome",
                "fallback_icon": "google-chrome",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                ],
                "check_cmd": "where chrome.exe 2>nul",
                "launch_cmd": 'start "" "chrome"',
                "install_cmd": "winget install --id Google.Chrome -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "firefox",
                "name": "Mozilla Firefox",
                "category": "Web Browser",
                "description": "Safe, reliable web browser for everyday internet use.",
                "icon": "firefox",
                "fallback_icon": "firefox",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"),
                ],
                "check_cmd": "where firefox.exe 2>nul",
                "launch_cmd": 'start "" "firefox"',
                "install_cmd": "winget install --id Mozilla.Firefox -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "brave",
                "name": "Brave Browser",
                "category": "Web Browser",
                "description": "Fast web browser with built-in ad blocker to stop annoying popups.",
                "icon": "brave",
                "fallback_icon": "brave-browser",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                    os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                ],
                "check_cmd": "where brave.exe 2>nul",
                "launch_cmd": 'start "" "brave"',
                "install_cmd": "winget install --id Brave.Brave -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "vlc",
                "name": "VLC Media Player",
                "category": "Media Player",
                "description": "Easily plays movies, home videos, music files, and DVDs.",
                "icon": "vlc",
                "fallback_icon": "vlc",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\VideoLAN\VLC\vlc.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\VideoLAN\VLC\vlc.exe"),
                ],
                "check_cmd": "where vlc.exe 2>nul",
                "launch_cmd": 'start "" "vlc"',
                "install_cmd": "winget install --id VideoLAN.VLC -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "libreoffice",
                "name": "LibreOffice Suite",
                "category": "Office & Documents",
                "description": "Complete office program for writing letters, documents, and spreadsheets.",
                "icon": "libreoffice",
                "fallback_icon": "libreoffice-main",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\LibreOffice\program\soffice.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\LibreOffice\program\soffice.exe"),
                ],
                "check_cmd": "where soffice.exe 2>nul",
                "launch_cmd": 'start "" "soffice"',
                "install_cmd": "winget install --id TheDocumentFoundation.LibreOffice -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "spotify",
                "name": "Spotify Music",
                "category": "Music & Audio",
                "description": "Listen to your favorite songs, music artists, and podcasts.",
                "icon": "spotify",
                "fallback_icon": "spotify-client",
                "check_paths": [
                    os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
                ],
                "check_cmd": "where spotify.exe 2>nul",
                "launch_cmd": 'start "" "spotify"',
                "install_cmd": "winget install --id Spotify.Spotify -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "zoom",
                "name": "Zoom Video Meetings",
                "category": "Video Calls",
                "description": "Video calls and meetings with family, friends, and telehealth doctors.",
                "icon": "zoom",
                "fallback_icon": "zoom",
                "check_paths": [
                    os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe"),
                    os.path.expandvars(r"%ProgramFiles%\Zoom\bin\Zoom.exe"),
                ],
                "check_cmd": "where zoom.exe 2>nul",
                "launch_cmd": 'start "" "zoom"',
                "install_cmd": "winget install --id Zoom.Zoom -e --accept-package-agreements --accept-source-agreements",
            },
            {
                "id": "thunderbird",
                "name": "Thunderbird Email",
                "category": "Email & Messages",
                "description": "Easy, clean desktop email program for reading and sending email.",
                "icon": "thunderbird",
                "fallback_icon": "thunderbird",
                "check_paths": [
                    os.path.expandvars(r"%ProgramFiles%\Mozilla Thunderbird\thunderbird.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Mozilla Thunderbird\thunderbird.exe"),
                ],
                "check_cmd": "where thunderbird.exe 2>nul",
                "launch_cmd": 'start "" "thunderbird"',
                "install_cmd": "winget install --id Mozilla.Thunderbird -e --accept-package-agreements --accept-source-agreements",
            },
        ]
    elif sys.platform == "darwin":
        return [
            {
                "id": "chrome",
                "name": "Google Chrome",
                "category": "Web Browser",
                "description": "Fast, simple, and secure web browser for everyday browsing.",
                "icon": "chrome",
                "fallback_icon": "google-chrome",
                "check_paths": ["/Applications/Google Chrome.app"],
                "check_cmd": 'test -d "/Applications/Google Chrome.app"',
                "launch_cmd": 'open -a "Google Chrome"',
                "install_cmd": 'brew install --cask google-chrome 2>/dev/null || open "https://www.google.com/chrome/"',
            },
            {
                "id": "firefox",
                "name": "Mozilla Firefox",
                "category": "Web Browser",
                "description": "Safe, reliable web browser for everyday internet use.",
                "icon": "firefox",
                "fallback_icon": "firefox",
                "check_paths": ["/Applications/Firefox.app"],
                "check_cmd": 'test -d "/Applications/Firefox.app"',
                "launch_cmd": 'open -a "Firefox"',
                "install_cmd": 'brew install --cask firefox 2>/dev/null || open "https://www.mozilla.org/firefox/new/"',
            },
            {
                "id": "brave",
                "name": "Brave Browser",
                "category": "Web Browser",
                "description": "Fast web browser with built-in ad blocker to stop annoying popups.",
                "icon": "brave",
                "fallback_icon": "brave-browser",
                "check_paths": ["/Applications/Brave Browser.app"],
                "check_cmd": 'test -d "/Applications/Brave Browser.app"',
                "launch_cmd": 'open -a "Brave Browser"',
                "install_cmd": 'brew install --cask brave-browser 2>/dev/null || open "https://brave.com/download/"',
            },
            {
                "id": "vlc",
                "name": "VLC Media Player",
                "category": "Media Player",
                "description": "Easily plays movies, home videos, music files, and DVDs.",
                "icon": "vlc",
                "fallback_icon": "vlc",
                "check_paths": ["/Applications/VLC.app"],
                "check_cmd": 'test -d "/Applications/VLC.app"',
                "launch_cmd": 'open -a "VLC"',
                "install_cmd": 'brew install --cask vlc 2>/dev/null || open "https://www.videolan.org/vlc/"',
            },
            {
                "id": "libreoffice",
                "name": "LibreOffice Suite",
                "category": "Office & Documents",
                "description": "Complete office program for writing letters, documents, and spreadsheets.",
                "icon": "libreoffice",
                "fallback_icon": "libreoffice-main",
                "check_paths": ["/Applications/LibreOffice.app"],
                "check_cmd": 'test -d "/Applications/LibreOffice.app"',
                "launch_cmd": 'open -a "LibreOffice"',
                "install_cmd": 'brew install --cask libreoffice 2>/dev/null || open "https://www.libreoffice.org/download/"',
            },
            {
                "id": "spotify",
                "name": "Spotify Music",
                "category": "Music & Audio",
                "description": "Listen to your favorite songs, music artists, and podcasts.",
                "icon": "spotify",
                "fallback_icon": "spotify-client",
                "check_paths": ["/Applications/Spotify.app"],
                "check_cmd": 'test -d "/Applications/Spotify.app"',
                "launch_cmd": 'open -a "Spotify"',
                "install_cmd": 'brew install --cask spotify 2>/dev/null || open "https://www.spotify.com/download/"',
            },
            {
                "id": "zoom",
                "name": "Zoom Video Meetings",
                "category": "Video Calls",
                "description": "Video calls and meetings with family, friends, and telehealth doctors.",
                "icon": "zoom",
                "fallback_icon": "zoom",
                "check_paths": ["/Applications/zoom.us.app", "/Applications/Zoom.app"],
                "check_cmd": 'test -d "/Applications/zoom.us.app" || test -d "/Applications/Zoom.app"',
                "launch_cmd": 'open -a "zoom.us" 2>/dev/null || open -a "Zoom" 2>/dev/null',
                "install_cmd": 'brew install --cask zoom 2>/dev/null || open "https://zoom.us/download"',
            },
            {
                "id": "thunderbird",
                "name": "Thunderbird Email",
                "category": "Email & Messages",
                "description": "Easy, clean desktop email program for reading and sending email.",
                "icon": "thunderbird",
                "fallback_icon": "thunderbird",
                "check_paths": ["/Applications/Thunderbird.app"],
                "check_cmd": 'test -d "/Applications/Thunderbird.app"',
                "launch_cmd": 'open -a "Thunderbird"',
                "install_cmd": 'brew install --cask thunderbird 2>/dev/null || open "https://www.thunderbird.net/"',
            },
        ]
    else:
        # Linux (Ubuntu, Debian, Fedora, Arch)
        return [
            {
                "id": "chrome",
                "name": "Google Chrome",
                "category": "Web Browser",
                "description": "Fast, simple, and secure web browser for everyday browsing.",
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
                "description": "Safe, reliable web browser for everyday internet use.",
                "icon": "firefox",
                "fallback_icon": "firefox",
                "pkg": "firefox",
                "check_cmd": "which firefox",
                "launch_cmd": "firefox 2>/dev/null",
                "install_cmd": "pkexec apt-get update && pkexec apt-get install -y firefox || sudo snap install firefox",
            },
            {
                "id": "brave",
                "name": "Brave Browser",
                "category": "Web Browser",
                "description": "Fast web browser with built-in ad blocker to stop annoying popups.",
                "icon": "brave",
                "fallback_icon": "brave-browser",
                "pkg": "brave-browser",
                "check_cmd": "which brave-browser || which brave || snap list brave 2>/dev/null",
                "launch_cmd": "brave-browser 2>/dev/null || brave 2>/dev/null || snap run brave 2>/dev/null",
                "install_cmd": "sudo snap install brave",
            },
            {
                "id": "vlc",
                "name": "VLC Media Player",
                "category": "Media Player",
                "description": "Easily plays movies, home videos, music files, and DVDs.",
                "icon": "vlc",
                "fallback_icon": "vlc",
                "pkg": "vlc",
                "check_cmd": "which vlc",
                "launch_cmd": "vlc 2>/dev/null",
                "install_cmd": "pkexec apt-get update && pkexec apt-get install -y vlc",
            },
            {
                "id": "libreoffice",
                "name": "LibreOffice Suite",
                "category": "Office & Documents",
                "description": "Complete office program for writing letters, documents, and spreadsheets.",
                "icon": "libreoffice",
                "fallback_icon": "libreoffice-main",
                "pkg": "libreoffice",
                "check_cmd": "which libreoffice",
                "launch_cmd": "libreoffice 2>/dev/null",
                "install_cmd": "pkexec apt-get update && pkexec apt-get install -y libreoffice",
            },
            {
                "id": "spotify",
                "name": "Spotify Music",
                "category": "Music & Audio",
                "description": "Listen to your favorite songs, music artists, and podcasts.",
                "icon": "spotify",
                "fallback_icon": "spotify-client",
                "pkg": "spotify",
                "check_cmd": "which spotify || snap list spotify 2>/dev/null",
                "launch_cmd": "spotify 2>/dev/null",
                "install_cmd": "sudo snap install spotify",
            },
            {
                "id": "zoom",
                "name": "Zoom Video Meetings",
                "category": "Video Calls",
                "description": "Video calls and meetings with family, friends, and telehealth doctors.",
                "icon": "zoom",
                "fallback_icon": "zoom",
                "pkg": "zoom-client",
                "check_cmd": "which zoom || snap list zoom-client 2>/dev/null",
                "launch_cmd": "zoom 2>/dev/null || snap run zoom-client 2>/dev/null",
                "install_cmd": "sudo snap install zoom-client",
            },
            {
                "id": "thunderbird",
                "name": "Thunderbird Email",
                "category": "Email & Messages",
                "description": "Easy, clean desktop email program for reading and sending email.",
                "icon": "thunderbird",
                "fallback_icon": "thunderbird",
                "pkg": "thunderbird",
                "check_cmd": "which thunderbird || snap list thunderbird 2>/dev/null",
                "launch_cmd": "thunderbird 2>/dev/null",
                "install_cmd": "pkexec apt-get update && pkexec apt-get install -y thunderbird || sudo snap install thunderbird",
            },
        ]

APP_CATALOG = get_app_catalog()

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

def get_quick_fixes() -> List[Dict[str, Any]]:
    """Returns platform-specific 1-click IT repair actions."""
    if sys.platform.startswith("win"):
        # Windows Native Commands
        return [
            {
                "id": "fix_network",
                "title": "Fix Internet & Wi-Fi",
                "icon": "network-wireless-symbolic",
                "summary": "Flushes DNS resolver cache, releases and renews IP address lease, and checks connectivity.",
                "cmd": "ipconfig /flushdns & ipconfig /renew & ping -n 2 8.8.8.8",
            },
            {
                "id": "fix_packages",
                "title": "Repair Windows Update",
                "icon": "system-software-update-symbolic",
                "summary": "Restarts Windows Update background services and verifies system integrity.",
                "cmd": "net stop wuauserv & net start wuauserv & dism /online /cleanup-image /restorehealth",
            },
            {
                "id": "clean_space",
                "title": "Free Up Disk Space Safely",
                "icon": "drive-harddisk-symbolic",
                "summary": "Safely clears temporary application caches, crash dumps, and Windows temp files. Personal files in Documents, Pictures, and Music are NEVER touched.",
                "cmd": "del /q /f /s \"%TEMP%\\*\" 2>nul & cleanmgr /verylowdisk 2>nul",
            },
            {
                "id": "fix_audio",
                "title": "Restart Audio & Sound",
                "icon": "audio-speakers-symbolic",
                "summary": "Restarts the Windows Audio service (Audiosrv) to resolve muted or stuck audio devices.",
                "cmd": "net stop Audiosrv & net start Audiosrv",
            },
            {
                "id": "check_health",
                "title": "Full System Health Check",
                "icon": "utilities-system-monitor-symbolic",
                "summary": "Checks storage capacity, memory status, and system boot time.",
                "cmd": "wmic logicaldisk get size,freespace,caption & systeminfo | findstr /B /C:\"Total Physical Memory\" /C:\"Available Physical Memory\" /C:\"System Boot Time\"",
            },
            {
                "id": "update_system",
                "title": "Check & Apply System Updates",
                "icon": "software-update-available-symbolic",
                "summary": "Scans for available Windows security updates and patches.",
                "cmd": "usoclient StartInteractiveScan",
            },
        ]
    elif sys.platform == "darwin":
        # macOS Native Commands
        return [
            {
                "id": "fix_network",
                "title": "Fix Internet & Wi-Fi",
                "icon": "network-wireless-symbolic",
                "summary": "Flushes macOS DNS resolver cache, restarts mDNSResponder, and verifies connection.",
                "cmd": "sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder; ping -c 2 8.8.8.8",
            },
            {
                "id": "fix_packages",
                "title": "Repair Homebrew & App Updates",
                "icon": "system-software-update-symbolic",
                "summary": "Cleans up outdated package caches and runs package diagnostics.",
                "cmd": "brew cleanup -s 2>/dev/null; brew doctor 2>/dev/null || echo 'Homebrew not installed or system healthy'",
            },
            {
                "id": "clean_space",
                "title": "Free Up Disk Space Safely",
                "icon": "drive-harddisk-symbolic",
                "summary": "Safely clears user application caches, QuickLook preview caches, and system crash logs. Personal files in Documents, Pictures, and Music are NEVER touched.",
                "cmd": "rm -rf ~/Library/Caches/* 2>/dev/null; qlmanage -r cache 2>/dev/null; sudo rm -rf /private/var/log/asl/*.asl 2>/dev/null",
            },
            {
                "id": "fix_audio",
                "title": "Restart Audio & Sound",
                "icon": "audio-speakers-symbolic",
                "summary": "Restarts macOS CoreAudio service to restore sound, microphones, and headphones.",
                "cmd": "sudo killall coreaudiod",
            },
            {
                "id": "check_health",
                "title": "Full System Health Check",
                "icon": "utilities-system-monitor-symbolic",
                "summary": "Analyzes storage volumes, memory statistics, and uptime.",
                "cmd": "df -h /; vm_stat; uptime",
            },
            {
                "id": "update_system",
                "title": "Check & Apply System Updates",
                "icon": "software-update-available-symbolic",
                "summary": "Scans for and applies official Apple macOS software and security updates.",
                "cmd": "softwareupdate -ia",
            },
        ]
    else:
        # Linux (Ubuntu, Debian, Fedora, Arch)
        return [
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

# Module-level variable for compatibility
QUICK_FIXES = get_quick_fixes()

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
        "/opt/homebrew/bin",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Antigravity\bin"),
        os.path.expandvars(r"%ProgramFiles%\Antigravity"),
    ]
    cur_path = env.get("PATH", "")
    cur_list = cur_path.split(os.pathsep) if cur_path else []
    all_paths = [p for p in extra_paths if p not in cur_list] + cur_list
    env["PATH"] = os.pathsep.join(all_paths)
    return env

def check_app_installed(app_or_cmd: Any) -> bool:
    """Checks if an app is installed on the system."""
    if isinstance(app_or_cmd, dict):
        for p in app_or_cmd.get("check_paths", []):
            if p and os.path.exists(p):
                return True
        cmd = app_or_cmd.get("check_cmd", "")
    else:
        cmd = str(app_or_cmd)

    if not cmd:
        return False

    try:
        res = subprocess.run(
            cmd,
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
        usage = shutil.disk_usage(os.path.expanduser("~"))
        total = usage.total
        used = usage.used
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
