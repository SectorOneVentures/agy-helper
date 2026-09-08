"""
AI Agent Client for Agy Companion.
Communicates with `agy` CLI using Gemini 3.7 Flash Medium.
Handles token-efficient conversations, system prompt injection, and command proposals.
"""

import os
import shutil
import subprocess
import threading
import json
import re
from typing import List, Dict, Callable, Optional

DEFAULT_MODEL = "gemini-3.7-flash-medium"
DEFAULT_EFFORT = "medium"

SYSTEM_PROMPT = """You are Agy Companion, a warm, caring, patient, and friendly desktop helper designed for everyday computer users and seniors.
The user may be completely unfamiliar with computers, technical jargon, or Linux. Always treat them with kindness, respect, and zero condescension.

COMMUNICATION GUIDELINES:
1. Warm, Simple & Plain English:
   - Speak like a helpful, reassuring friend or family member.
   - NEVER use intimidating jargon like "packet loss", "DNS resolution", "latency", "TTL", "routing tables", "inodes", or "daemons".
   - If a technical concept is necessary, translate it into everyday language (e.g. "connection hiccups" instead of "packet loss", "website address directory" instead of "DNS", "storage space" instead of "disk partition").

2. Conversational Questions (e.g., "Why is my internet slow?", "What is RAM?"):
   - Answer in 2 to 4 clear, friendly sentences or bullet points.
   - Give practical, physical real-world tips the user can easily check themselves (e.g. "1. Restart your Wi-Fi router by unplugging it for 30 seconds. 2. Move your computer closer to the Wi-Fi box. 3. Check if someone else in the house is downloading large files.").
   - DO NOT suggest terminal commands (like ping, traceroute, netstat) for general conversational questions. Never overwhelm the user with code or scary terminal text.

3. Executing Automated Tasks (ONLY when specifically requested or genuinely needed):
   - Only propose a command if the user asked you to fix a system issue, install an app, or free up disk space.
   - If proposing a command, ALWAYS precede it with a friendly 1-line plain-English explanation of what it will accomplish.
   - Propose commands using:
     ```fix_command
     <safe command to execute>
     ```
     or
     ```inspect_command
     <safe read-only command>
     ```

4. Privacy and User Trust:
   - If the user asks about privacy, data sharing, or security, reassure them warmly:
     * We NEVER sell, share, or monetize their personal data or browsing history with ANY third parties or advertisers.
     * Explain that you are powered by Google Gemini AI (Gemini 3.7 Flash) to answer tech questions, but only the question they type is sent to Google—their personal computer files, photos, passwords, and private documents never leave their computer.
     * Agy Helper is 100% free and open-source software with strict local safety guardrails.

STRICT SAFETY RULES:
- NEVER delete or destroy files in ~/Documents, ~/Music, or ~/Pictures. Only reading/viewing them is permitted.
- NEVER tamper with or delete critical system files (/etc/passwd, /boot, /dev, root partition wipe).
- Keep answers concise, clear, and reassuring.
"""

def check_agy_connection() -> tuple:
    """Checks whether the Google AGY binary is installed and executable. Returns (is_connected, message)."""
    agy_bin = find_agy_binary()
    if not agy_bin:
        return False, "AGY binary not found in standard paths."
    try:
        res = subprocess.run(
            [agy_bin, "--help"],
            capture_output=True,
            text=True,
            env=get_augmented_env(),
            timeout=5
        )
        if res.returncode == 0:
            return True, "Connected to Google AGY"
        return False, f"AGY returned status code {res.returncode}"
    except Exception as e:
        return False, f"Connection test failed: {e}"

def auto_connect_agy() -> tuple:
    """
    Attempts to automatically find, configure, and connect to Google AGY without requiring the user
    to understand terminals, directories, or technical configurations.
    Returns (is_connected, message).
    """
    conn, msg = check_agy_connection()
    if conn:
        return True, "Google AI is connected and ready to assist you!"

    agy_path = find_agy_binary()
    if not agy_path:
        search_dirs = [
            os.path.expanduser("~/.gemini"),
            os.path.expanduser("~/.config/Antigravity"),
            os.path.expanduser("~/.local/share"),
            "/opt",
            "/snap"
        ]
        for sdir in search_dirs:
            if os.path.isdir(sdir):
                for root, dirs, files in os.walk(sdir):
                    if "agy" in files:
                        p = os.path.join(root, "agy")
                        if os.access(p, os.X_OK):
                            agy_path = p
                            break
                    if agy_path:
                        break
            if agy_path:
                break

    if agy_path and os.path.exists(agy_path):
        target_dir = os.path.expanduser("~/.local/bin")
        try:
            os.makedirs(target_dir, exist_ok=True)
            target_sym = os.path.join(target_dir, "agy")
            if not os.path.exists(target_sym):
                os.symlink(agy_path, target_sym)
        except Exception:
            pass

    conn, msg = check_agy_connection()
    if conn:
        return True, "Successfully connected to Google AI!"

    return False, "Google Antigravity was not found on this computer yet. Please click 'Open Free Download Page' below."

def find_agy_binary() -> Optional[str]:
    """Finds the agy CLI binary across system and user-local directories."""
    # 1. Check standard PATH
    found = shutil.which("agy")
    if found and os.path.isfile(found) and os.access(found, os.X_OK):
        return found

    # 2. Check known candidate install locations
    candidates = [
        os.path.expanduser("~/.local/bin/agy"),
        os.path.expanduser("~/.gemini/antigravity/bin/agy"),
        os.path.expanduser("~/.config/Antigravity/bin/agy"),
        "/usr/local/bin/agy",
        "/usr/bin/agy",
        "/snap/bin/agy",
        "/var/lib/snapd/snap/bin/agy",
        os.path.expanduser("~/.local/bin/antigravity"),
        os.path.expanduser("~/.gemini/antigravity/bin/antigravity"),
    ]

    for cand in candidates:
        if cand and os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand

    return None

def get_augmented_env() -> Dict[str, str]:
    """Returns an environment dictionary with standard user and system binary paths included in PATH."""
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

class AgyClient:
    def __init__(self, model: str = DEFAULT_MODEL, effort: str = DEFAULT_EFFORT):
        self.model = model
        self.effort = effort
        self.history: List[Dict[str, str]] = []
        self._max_history = 6  # Keeps token footprint minimal

    def clear_history(self):
        self.history.clear()

    def send_message_async(self, user_text: str, on_success: Callable[[str], None], on_error: Callable[[str], None]):
        """Runs the query in a background thread to prevent UI freezing."""
        t = threading.Thread(target=self._run_query, args=(user_text, on_success, on_error), daemon=True)
        t.start()

    def _run_query(self, user_text: str, on_success: Callable[[str], None], on_error: Callable[[str], None]):
        try:
            agy_bin = find_agy_binary()
            if not agy_bin:
                on_error(
                    "Could not locate the 'agy' binary. "
                    "Please verify that agy is installed in ~/.local/bin or ~/.gemini/antigravity/bin."
                )
                return

            # Build conversation context
            conversation_context = f"{SYSTEM_PROMPT}\n\n"
            for item in self.history[-self._max_history:]:
                role = "User" if item["role"] == "user" else "Agy"
                conversation_context += f"{role}: {item['content']}\n"

            conversation_context += f"User: {user_text}\nAgy:"

            # Execute agy CLI with Gemini 3.7 Flash
            cmd = [
                agy_bin,
                "-p",
                conversation_context,
                "--model",
                self.model,
                "--effort",
                self.effort,
                "--disable-slash-commands"
            ]

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=get_augmented_env(),
                timeout=60
            )

            if process.returncode != 0:
                err_msg = process.stderr.strip() or "Process returned error"
                on_error(f"Could not reach Agy AI: {err_msg}")
                return

            response_text = process.stdout.strip()
            if not response_text:
                response_text = "I processed your request, but received an empty response. How else can I help?"

            # Record history
            self.history.append({"role": "user", "content": user_text})
            self.history.append({"role": "assistant", "content": response_text})

            # Trim history to avoid exceeding token usage
            if len(self.history) > self._max_history * 2:
                self.history = self.history[- (self._max_history * 2):]

            on_success(response_text)

        except subprocess.TimeoutExpired:
            on_error("The AI request timed out. Please check your internet connection and try again.")
        except Exception as e:
            on_error(f"Error communicating with AI helper: {e}")

    @staticmethod
    def extract_action_commands(response_text: str) -> List[Dict[str, str]]:
        """Extracts proposed fix_command or inspect_command blocks."""
        actions = []
        fix_matches = re.findall(r"```fix_command\s*([\s\S]*?)\s*```", response_text)
        for cmd in fix_matches:
            actions.append({"type": "fix", "command": cmd.strip()})

        inspect_matches = re.findall(r"```inspect_command\s*([\s\S]*?)\s*```", response_text)
        for cmd in inspect_matches:
            actions.append({"type": "inspect", "command": cmd.strip()})

        return actions

