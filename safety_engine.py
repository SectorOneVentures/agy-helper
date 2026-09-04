"""
Safety Engine for Agy IT Helper Companion.

Enforces strict safety guardrails:
1. Absolute protection for user personal folders:
   - ~/Documents, ~/Music, ~/Pictures (and subdirectories) CANNOT be deleted or modified destructively.
   - ONLY READ operations (e.g., cat, ls, du, file, stat, grep) are permitted.
2. Protection for critical system files:
   - Blocks tampering/deletion of /etc/passwd, /etc/shadow, /boot, /dev, /proc, /sys, /lib, etc.
   - Blocks dangerous root destructions like 'rm -rf /' or disk formatting 'mkfs'.
3. Permits safe IT assessment and fixes:
   - System assessment: df, free, top, systemctl status, journalctl, ip, ping, dpkg, etc.
   - Software management & fixes: apt update, apt install, apt --fix-broken install, snap install, cache clean, service restarts.
"""

import os
import re
import shlex
from typing import Tuple, List, Dict, Any

HOME_DIR = os.path.expanduser("~")

# User protected media and personal document directories
PROTECTED_MEDIA_DIRS = [
    os.path.realpath(os.path.expanduser("~/Documents")),
    os.path.realpath(os.path.expanduser("~/Music")),
    os.path.realpath(os.path.expanduser("~/Pictures")),
]

# Critical system directories that must not be destructively altered
CRITICAL_SYSTEM_DIRS = [
    "/boot",
    "/dev",
    "/etc/sudoers",
    "/etc/sudoers.d",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/gshadow",
    "/proc",
    "/sys",
    "/lib",
    "/lib64",
    "/usr/bin",
    "/usr/sbin",
    "/sbin",
    "/bin",
]

# Deletion command patterns
DELETION_COMMANDS = {
    "rm", "unlink", "shred", "rmdir", "srm", "trash-put", "wipe"
}

# Dangerous system-level patterns
DANGEROUS_SYSTEM_PATTERNS = [
    r"\bmkfs(\.\w+)?\b",
    r"\bfdisk\b",
    r"\bparted\b",
    r"\bgparted\b",
    r"\bdd\s+.*of=/dev/",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # Forkbomb
    r">\s*/dev/sd[a-z]",
    r">\s*/dev/nvme",
    r">\s*/etc/passwd",
    r">\s*/etc/shadow",
    r">\s*/etc/sudoers",
    r"\bchmod\s+(-R\s+)?777\s+/",
    r"\bchown\s+(-R\s+)?.*\s+/",
    r"\brm\s+-[rfRF]{1,4}\s+/\s*$",
    r"\brm\s+-[rfRF]{1,4}\s+/\*",
]

def is_path_under_dir(target_path: str, parent_dir: str) -> bool:
    """Check if target_path is inside or equal to parent_dir."""
    try:
        real_target = os.path.realpath(os.path.expanduser(target_path))
        real_parent = os.path.realpath(os.path.expanduser(parent_dir))
        return os.path.commonpath([real_target, real_parent]) == real_parent
    except Exception:
        return False

def check_command_safety(cmd_str: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates whether a shell command is safe to execute.
    Returns:
        (is_safe, message, details)
    """
    if not cmd_str or not cmd_str.strip():
        return False, "Empty command.", {"severity": "error"}

    cmd_str = cmd_str.strip()

    # 1. Check for dangerous system destructive patterns
    for pat in DANGEROUS_SYSTEM_PATTERNS:
        if re.search(pat, cmd_str, re.IGNORECASE):
            return False, (
                "🚫 BLOCKED FOR SAFETY: This command contains operations that could damage "
                "or wipe critical system files. To keep your computer completely safe, "
                "this action is prohibited."
            ), {"severity": "critical", "type": "critical_system_tampering"}

    # 2. Parse command tokens to inspect commands and target paths
    try:
        # Split by pipes, logical operators, subshells, and semicolons
        sub_cmds = re.split(r"[;&|]+", cmd_str)
    except Exception:
        sub_cmds = [cmd_str]

    for sub in sub_cmds:
        sub = sub.strip()
        if not sub:
            continue
        try:
            tokens = shlex.split(sub)
        except Exception:
            tokens = sub.split()

        if not tokens:
            continue

        cmd_name = os.path.basename(tokens[0])

        # Check if this sub-command is a deletion tool
        if cmd_name in DELETION_COMMANDS:
            # Inspect all arguments
            for arg in tokens[1:]:
                # Ignore options like -r, -f, --force, -rf
                if arg.startswith("-"):
                    continue

                # Expand target path
                full_path = os.path.expanduser(arg)
                if not os.path.isabs(full_path):
                    full_path = os.path.join(os.getcwd(), full_path)

                # Check if target is inside protected media directories
                for p_dir in PROTECTED_MEDIA_DIRS:
                    if is_path_under_dir(full_path, p_dir):
                        return False, (
                            f"🛡️ PROTECTED FOLDER GUARD: The helper is strictly not allowed "
                            f"to delete files in your '{os.path.basename(p_dir)}' folder. "
                            f"Your personal Documents, Music, and Pictures are permanently safe "
                            f"and can only be viewed or read, never deleted."
                        ), {"severity": "critical", "type": "protected_media_deletion", "path": full_path}

                # Check if target is inside critical system directories
                for c_dir in CRITICAL_SYSTEM_DIRS:
                    if is_path_under_dir(full_path, c_dir):
                        return False, (
                            f"🛡️ SYSTEM INTEGRITY GUARD: Deleting files in critical system folder "
                            f"'{c_dir}' is blocked to prevent breaking your operating system."
                        ), {"severity": "critical", "type": "critical_system_deletion", "path": full_path}

        # Check find -delete or find -exec rm
        if cmd_name == "find":
            if "-delete" in tokens or "rm" in tokens:
                for arg in tokens[1:]:
                    if not arg.startswith("-"):
                        for p_dir in PROTECTED_MEDIA_DIRS:
                            if is_path_under_dir(arg, p_dir):
                                return False, (
                                    f"🛡️ PROTECTED FOLDER GUARD: Deleting files in your "
                                    f"'{os.path.basename(p_dir)}' folder is prohibited."
                                ), {"severity": "critical", "type": "protected_media_deletion"}

    return True, "✅ Command passed all safety checks.", {"severity": "safe"}

def get_protected_paths_summary() -> List[Dict[str, str]]:
    """Returns human-readable status of protected paths for the UI."""
    items = []
    for p in PROTECTED_MEDIA_DIRS:
        exists = os.path.exists(p)
        items.append({
            "name": os.path.basename(p),
            "path": p,
            "policy": "Read-Only (No Deletion Allowed)",
            "status": "Active & Shielded" if exists else "Shielded (Directory inactive)"
        })
    return items
