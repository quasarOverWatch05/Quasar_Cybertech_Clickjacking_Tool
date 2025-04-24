# 🔐 Quasar Clickjacker CLI – Advanced Clickjacking Detection Tool

<img src="https://quasarcybertech.com/wp-content/uploads/2024/06/fulllogo_transparent_nobuffer.png" alt="Quasar CyberTech Logo" width="400"/>

A powerful, developer-friendly Python-based CLI utility that scans websites for potential **Clickjacking vulnerabilities** using security headers, iframe analysis, screenshots, and batch processing.

> ⚡ Developed and maintained by [Quasar CyberTech Research Team]

---

## 🚀 Features

- ✅ Detects missing or misconfigured `X-Frame-Options` and `Content-Security-Policy`
- ✅ Parses and inspects `<iframe>` elements for suspicious embeds
- 📸 Captures **headless screenshots** using Firefox + Selenium
- 🧪 Supports **single or batch scanning** (via `--list urls.txt`)
- 📝 Outputs results in **HTML & Screenshot**
- 💬 Beautiful CLI interface with colorized and structured results

---

## 📦 Installation

### Requirements

- Python 3.7+
- [Firefox](https://www.mozilla.org/en-US/firefox/new/)
- [GeckoDriver](https://github.com/mozilla/geckodriver/releases) in your system PATH

### Clone The Repository

```bash
git clone "https://github.com/quasarOverWatch05/quasar-clickjacker-cli"
cd quasar-clickjacker-cli

```

### Create a virtual environment and activate it

```bash
python3 -m venv venv
source venv/bin/activate

```

### Install Dependencies

```bash
pip3 install -r requirements.txt
python -m playwright install firefox

```
### Run the script 

For single URL

```bash
python3 clickjacker_pro.py -u https://evil.com/

```
For multiple URLs(use the url.txt file provided in the repository)

⚠️ Each URL should be on a new line for the script to function properly

```bash
python3 clickjacker_pro.py -l url.txt

```
