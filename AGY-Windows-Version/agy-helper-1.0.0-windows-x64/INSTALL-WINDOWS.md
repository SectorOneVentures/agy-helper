# 🪟 Agy Helper — Windows Installation & Security Guide

Welcome to **Agy Helper**! This guide explains how to install Agy Helper on Windows 10 and 11, install the code signing certificate package so Windows trusts the application without warnings, and use the built-in Microsoft Store / Windows App Installer features.

---

## 🚀 Option 1: 1-Click Fast Setup (Recommended)

1. Extract the downloaded zip folder (`agy-helper-1.0.0-windows-x64.zip`) to a location on your computer (such as `C:\Program Files\Agy Helper` or your user folder).
2. Right-click **`Setup-AgyHelper.bat`** and choose **Run as administrator**.
3. When Windows asks *"Do you want to allow this app to make changes to your device?"*, click **Yes**.
4. That's it! 
   - The security certificate is automatically imported into your Windows certificate store.
   - Convenient shortcuts are created on your Desktop and Start Menu.
   - Agy Helper will open automatically.

---

## 🛡️ Option 2: Install Certificate Only

If you prefer to install only the signing certificate:

1. Right-click **`Install-Certificate.bat`** and choose **Run as administrator**.
2. Click **Yes** at the prompt.
3. Once the green `SUCCESS` message appears, double-click **`AgyHelper.exe`** to start using Agy Helper anytime.

*(Alternatively, run `Install-Certificate.ps1` in PowerShell with Administrator rights).*

---

## 🔍 Option 3: Manual Certificate Installation (Windows GUI)

If your system administrator restricts batch files:

1. Right-click **`AgyHelper-Certificate.cer`** and choose **Install Certificate**.
2. Under *Store Location*, select **Local Machine** and click **Next** (Click *Yes* on the Windows security prompt).
3. Select **Place all certificates in the following store** and click **Browse**.
4. Choose **Trusted Root Certification Authorities** and click **OK**, then click **Next** and **Finish**.
5. Repeat steps 1–4, this time selecting **Trusted Publishers** in step 4.
6. Agy Helper is now fully trusted on your Windows PC!

---

## 📦 Windows Apps & Microsoft Store Integration

Agy Helper includes a **1-Click Everyday App Installer** (Google Chrome, Firefox, VLC, Spotify, LibreOffice, Zoom, Brave, and Thunderbird).

- **Verified Safe**: Every application is retrieved directly from the official **Microsoft Store** and Windows Package Manager (`winget`) catalog. No adware, search bar junk, or third-party download traps.
- **App Installer Status**: 
  - Windows 10 and 11 come with Microsoft's official **App Installer** pre-installed.
  - If your PC reports that App Installer or `winget` is missing or out of date, simply open the Microsoft Store and search for **App Installer** (published by Microsoft Corporation), or visit:
    [Microsoft Store: App Installer](https://apps.microsoft.com/detail/9nblggh4nns1)
  - You can also click the **"ℹ️ Help with App Installer"** button directly inside Agy Helper under the *App Installer* tab to verify your status with 1 click.

---

## 💬 Support & Help

Need assistance or have questions?
- Visit our GitHub repository: [SectorOneVentures/agy-helper](https://github.com/SectorOneVentures/agy-helper)
- View our [DISCLAIMER.md](DISCLAIMER.md) and [LICENSE](LICENSE).
