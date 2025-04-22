# 🔐 Quasar Clickjacker CLI – Advanced Clickjacking Detection Tool

A powerful, developer-friendly Python-based CLI utility that scans websites for potential **Clickjacking vulnerabilities** using security headers, iframe analysis, screenshots, and batch processing.

> ⚡ Developed by [Quasar CyberTech]

---

## 🚀 Features

- ✅ Detects missing or misconfigured `X-Frame-Options` and `Content-Security-Policy`
- ✅ Parses and inspects `<iframe>` elements for suspicious embeds
- 📸 Captures **headless screenshots** using Firefox + Selenium
- 🧪 Supports **single or batch scanning** (via `--list urls.txt`)
- 📝 Outputs results in **JSON or CSV**
- 💬 Beautiful CLI interface with colorized and structured results

---

## 📦 Installation

### Requirements

- Python 3.7+
- [Firefox](https://www.mozilla.org/en-US/firefox/new/)
- [GeckoDriver](https://github.com/mozilla/geckodriver/releases) in your system PATH

### Install Dependencies

```bash
pip install -r requirements.txt

```