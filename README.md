# 🛡️ Agy Helper

**The friendly, stress-free desktop assistant for everyday computer users, families, and seniors.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg)]()
[![Privacy](https://img.shields.io/badge/Privacy-Zero%20Data%20Selling-success.svg)](PRIVACY.md)

---

## 🌟 What is Agy Helper?

Computers can be confusing and overwhelming. When something stops working, most people are confronted with cryptic error messages, intimidating terminal commands, or deceptive internet popups.

**Agy Helper** is a free, open-source desktop companion powered by Google AGY and Gemini AI. It transforms complicated computer maintenance into **simple, safe, 1-click actions** explained in plain, caring English—like having a patient tech-savvy family member sitting right next to you.

---

## ✨ Key Features

### 💬 1. Ask Agy (Friendly AI Tech Support)
- Ask any question in everyday language: *"Why is my internet slow?"*, *"How do I print double-sided?"*, or *"What does RAM mean?"*
- Get warm, patient, jargon-free answers.
- Never gives confusing terminal commands; safe actions can be tested with a single click.

### ⚡ 2. 1-Click Computer Fixes
- Fix sound hiccups if audio stops working.
- Restart Wi-Fi and network adapters with one click.
- Free up gigabytes of disk space safely without touching your personal photos or documents.
- Clear temporary system and browser cache files.

### 🛡️ 3. Scam & Fraud Protection
- **The 3 Golden Rules**: Simple guidance to prevent fraud (e.g., real companies never put phone numbers on your screen or ask for gift cards).
- **Common Scam Scenarios**: Calm walkthroughs explaining full-screen fake virus popups, fake package delivery texts, and urgent bank transfer calls.
- **Message Checker**: Paste a suspicious email or text and ask Agy if it looks like a scam.
- **Close Trapped Browsers**: A single button to safely close stuck browser tabs if a scam website locks your screen.

### 📦 4. 1-Click Everyday App Installer
- Install essential, trusted everyday programs safely without accidentally downloading adware or search bar junk:
  - **Web Browsers**: Google Chrome, Mozilla Firefox, Brave
  - **Media & Entertainment**: VLC Media Player, Spotify
  - **Productivity & Office**: LibreOffice (Word & Excel compatible)
  - **Communication**: Zoom Video Meetings, Thunderbird Email
- Automatically detects which programs you already have installed.

### 👓 5. Senior-Friendly Accessibility
- Instant text zoom controls (**`A-`** and **`A+`**) right on the top bar.
- Effortlessly adjust text size (100%, 115%, 130%, 150%) for crystal-clear readability.
- High-contrast buttons and readable fonts that never turn unreadable gray when switching between windows.

---

## 🔒 Privacy & Safety First

We believe everyday tools must respect user privacy:

1. **Zero Data Selling**: Your personal information, browsing history, and searches are **never** sold, rented, or shared with third-party advertisers or data brokers.
2. **Your Files Stay Yours**: Personal files (`Documents`, `Pictures`, `Music`, `Desktop`) are permanently protected. The built-in safety engine strictly prohibits any automatic script from altering or deleting your personal files.
3. **Google Gemini Processing**: AI queries are transmitted securely via encrypted connections directly to Google Gemini solely to answer your technical questions.
4. **100% Open Source**: Every line of code is public and auditable by anyone under the permissive MIT License.

For more details, see [PRIVACY.md](PRIVACY.md) and [DISCLAIMER.md](DISCLAIMER.md).

---

## 📥 Download & Installation

Pre-built binaries and universal packages are available on the [Releases](https://github.com/SectorOneVentures/agy-helper/releases/latest) page:

- 🪟 **Windows**: Download [AgyHelper.exe](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/AgyHelper.exe) or [AgyHelper-Windows-x64.zip](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/AgyHelper-Windows-x64.zip)
- 🍎 **macOS**: Download [AgyHelper-macOS.dmg](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/AgyHelper-macOS.dmg) (compatible with Apple Silicon & Intel)
- 📦 **Flatpak**: Download [AgyHelper.flatpak](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/AgyHelper.flatpak) and install:
  ```bash
  flatpak install --user AgyHelper.flatpak
  ```
- 🐧 **Linux**:
  - Debian / Ubuntu / Mint: [agy-helper_1.0.0_amd64.deb](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/agy-helper_1.0.0_amd64.deb)
  - Snap: [agy-helper_1.0.0_amd64.snap](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/agy-helper_1.0.0_amd64.snap)
  - Standalone Binary: [AgyHelper-Linux-x86_64.tar.gz](https://github.com/SectorOneVentures/agy-helper/releases/latest/download/AgyHelper-Linux-x86_64.tar.gz)

---

## 💻 Running from Source (For Developers)

### Requirements
- Python 3.10 or higher
- GTK 3 (`python3-gi`, `gir1.2-gtk-3.0`)
- Google AGY CLI (`agy`)

### Quick Setup
```bash
# 1. Clone the repository
git clone https://github.com/SectorOneVentures/agy-helper.git
cd agy-helper

# 2. Install dependencies (Debian/Ubuntu/Mint)
sudo apt update && sudo apt install -y python3-gi gir1.2-gtk-3.0

# 3. Launch Agy Helper
python3 main.py --open-window
```

<details>
<summary><b>🛠️ Building Standalone Binaries</b></summary>

- **Linux**: `pyinstaller --clean agy_helper.spec` (Output in `dist/AgyHelper`)
- **Windows**: Run `scripts\build_windows.bat`
- **macOS**: Run `bash scripts/build_mac.sh`
</details>

---

## ⚖️ Legal & Trademarks

Agy Helper is an independent open-source project and is **not affiliated with, sponsored by, or endorsed by Google LLC, Microsoft Corporation, Apple Inc., Mozilla Corporation, Brave Software, VideoLAN, The Document Foundation, Spotify AB, or Zoom Video Communications**.

All brand names and logos are property of their respective owners and are referenced solely for nominative identification.

---

## 📄 License

Distributed under the open-source **MIT License**. See [LICENSE](LICENSE) for details.
