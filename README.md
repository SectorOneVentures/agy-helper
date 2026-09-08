# 🚀 Agy Desktop Companion & IT Helper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()

**Agy Helper** is a friendly, accessible, open-source desktop companion and 1-click IT troubleshooter designed for everyday computer users, families, and seniors.

Powered by Google AGY and Gemini AI, Agy Helper turns scary computer error messages and technical maintenance into simple, safe, 1-click actions with zero technical jargon.

---

## ✨ Features

- **💬 Warm, Plain-English AI Tech Support**: Ask any computer question (e.g., *"Why is my internet slow?"*, *"What is RAM?"*). Agy answers like a patient, caring family member, avoiding confusing terminal commands and technical jargon.
- **🛡️ Scam & Fraud Protection**: Dedicated **Scam Help** tab educating users on common scams (fake virus popups, AnyDesk/TeamViewer remote caller traps, fake USPS texts, gift card fraud) with an interactive **Ask Agy to Check a Message** checker and an emergency **Close All Browsers** button.
- **👓 Senior Visibility Mode (Font Zoom `A-` / `A+`)**: Global font scaling (100%, 115%, 130%, 150%) so seniors and visually impaired users can comfortably read all content.
- **🔒 Zero-Deletion Safety Engine**: Hardcoded safety barriers guarantee that no script or fix can ever delete or alter files in `~/Documents`, `~/Pictures`, or `~/Music`. All proposed commands are verified before execution.
- **⚡ 1-Click IT Fixes**: Fix audio/sound hiccups, repair broken packages, free up disk space safely, restart Wi-Fi networking, and clear system caches with a single click.
- **📦 1-Click App Installer**: Curated catalog of essential everyday applications for families and seniors (Chrome, Firefox, Brave, VLC Media Player, LibreOffice, Spotify, Zoom, Thunderbird) with automatic detection of existing installations and authentic program icons.
- **🟢 Google AGY Status & Troubleshooter**: Real-time status indicator showing whether Google AGY is connected, complete with an interactive step-by-step troubleshooter for new computers.
- **🍏 Native iOS / macOS Light Aesthetic**: Modern clean design with backdrop stability ensuring readable white fonts on active tabs and buttons even when unfocused.

---

## 🚀 Quick Start (Running from Source)

### Prerequisites
- Python 3.10 or higher
- GTK 3 (`python3-gi`, `gir1.2-gtk-3.0`)
- Google AGY CLI (Antigravity)

### Linux (Ubuntu / Debian / Mint)
```bash
# 1. Install GTK3 dependencies
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 libgirepository1.0-dev

# 2. Clone repository
git clone https://github.com/your-username/agy-helper.git
cd agy-helper

# 3. Launch Agy Helper
python3 main.py --open-window
```

---

## 📦 Multi-Platform Packaging

### 🐧 Linux Snap Package
Agy Helper includes a full `snapcraft.yaml` configuration.
```bash
# Build the snap package
snapcraft

# Install locally
sudo snap install agy-helper_*.snap --dangerous
```
Or build a standalone Linux binary using PyInstaller:
```bash
bash scripts/build_linux.sh
```

### 🪟 Windows Executable (.exe)
Build a standalone single-file Windows executable:
```cmd
scripts\build_windows.bat
```
*(Requires Python for Windows and PyInstaller. Output executable will be in `dist/AgyHelper.exe`)*

### 🍎 macOS Application Bundle (.app & .dmg)
Build the macOS application bundle and DMG image:
```bash
bash scripts/build_mac.sh
```
*(Requires macOS and `create-dmg` or PyInstaller)*

---

## 🛡️ Privacy, Security & Google Gemini Integration

Agy Helper is built from the ground up with a strict privacy-first architecture:
- **Zero 3rd-Party Data Sharing**: No personal information, search queries, or browsing history is ever sold, tracked, or shared with third-party advertisers or data brokers.
- **How Google Gemini is Used**: When you type a question in the AI Chat tab, only the specific technical prompt and basic operating system context are sent to Google Gemini (Gemini 3.7 Flash) to formulate an answer.
- **Your Personal Files Never Leave Your Machine**: Private documents, family photos, passwords, and music are never uploaded or inspected.
- **Hardcoded Local Safety Engine**: Built-in rules in [safety_engine.py](safety_engine.py) permanently prohibit deleting files in personal directories (`~/Documents`, `~/Pictures`, `~/Music`).
- **Complete Privacy Statement**: Read our full [PRIVACY.md](PRIVACY.md) document for complete transparency.

---

## 🤝 Contributing

Contributions from the open-source community are welcome!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
