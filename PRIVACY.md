# Privacy Statement & Data Protection Pledge

**Last Updated: September 2026**

Agy Helper is a free and open-source desktop IT companion designed to help everyday computer users, families, and seniors safely manage, diagnose, and troubleshoot their computers. 

We believe that computer help should be simple, transparent, and completely respectful of your personal privacy. This statement explains how your data is handled, why **no third-party data sharing occurs**, and how the connection to **Google Gemini AI** functions.

---

## 1. Zero Third-Party Information Sharing

- **No Sale or Sharing of Personal Data**: We do not sell, rent, monetize, or transmit your personal information, search queries, chat logs, or browsing activity to any third-party advertisers, data brokers, or marketing networks.
- **Zero Telemetry & Tracking**: Agy Helper contains **no background analytics frameworks, tracking cookies, advertising beacons, or telemetry probes**.
- **Local-Only Metrics**: All system health information (RAM usage, storage capacity, system uptime, and protected folder statuses) is read directly by your local operating system and is never uploaded anywhere.

---

## 2. How the Google Gemini AI Connection Works

To provide patient, warm, plain-English answers to your technical questions, Agy Helper connects to **Google Gemini** (specifically the Gemini 3.7 Flash model) through the official local Google AGY engine:

- **What is Sent**: When you ask a question in the "Ask Agy" chat tab, only the specific text prompt you enter and basic, non-sensitive environment metadata (such as your Linux OS distribution name) are transmitted to Google's Gemini API so it can formulate an accurate solution.
- **What is NEVER Sent**: Agy Helper **never** accesses, inspects, uploads, or shares your personal files, private documents, family photos, music library, saved passwords, web browsing cookies, or keyboard keystrokes.
- **Encrypted in Transit**: All API communications with Google's Gemini AI endpoints are encrypted using industry-standard TLS / HTTPS encryption.

---

## 3. Strict Safety Guardrails & Local Execution

- **Hardcoded Protection for Personal Folders**: Agy Helper contains built-in safety guardrails that permanently prohibit modifying or deleting files inside personal directories (`~/Documents`, `~/Pictures`, `~/Music`). Only safe read actions can be proposed.
- **Local Command Execution**: All 1-Click Fixes, cache cleaning, emergency browser terminations, and software installations execute strictly on your local machine.
- **Explicit User Consent**: Automated commands are never run covertly in the background. Every fix requires your direct click, and you can inspect the exact underlying shell command prior to execution.

---

## 4. 100% Free & Open Source

Agy Helper is licensed under the permissive **MIT License**. The entire source code is openly hosted on GitHub. Anyone in the security community, open-source community, or public can inspect, audit, and verify every single line of code to confirm that no hidden telemetry or surveillance exists.

---

## 5. Contact & Auditing

If you have any questions or would like to review the code yourself, visit the official repository:
- License: [MIT License](LICENSE)
