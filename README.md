# Quasar CyberTech Clickjacking Tool
<!-- Quasar CyberTech -->
<div align="center">
<img src="https://quasarcybertech.com/wp-content/uploads/2024/06/fulllogo_transparent_nobuffer.png" alt="Quasar CyberTech Logo" width="300"/>
</div>

A powerful, developer-friendly Python-based CLI utility that scans websites for potential **Clickjacking vulnerabilities** using security headers, iframe analysis, screenshots, and batch processing.

> ⚡ Developed and maintained by [Quasar CyberTech Research Team]

---

## 🚀 Features

- ✅ Detects missing or misconfigured `X-Frame-Options` and `Content-Security-Policy`.
- ✅ Parses and inspects `<iframe>` elements for suspicious embeds.
- 🧪 Supports **single or batch scanning** (via `--file url.txt`)
- 📝 Outputs results in **HTML**.
- 💬 Beautiful CLI interface with colorized and structured results.

---

## 📦 Installation

### Requirements

- Python 3.7+
- [Firefox](https://www.mozilla.org/en-US/firefox/new/)

### Clone The Repository

```bash
git clone "https://github.com/quasarOverWatch05/Quasar_Cybertech_Clickjacking_Tool"
cd Quasar_Cybertech_Clickjacking_Tool

```

### Create a virtual environment and activate it

```bash
python3 -m venv venv
source venv/bin/activate

```

### Install Dependencies

```bash
pip3 install -r requirements.txt

```

---

## Run the script 

For single URL

```bash
python3 clickjacker_pro.py -u https://evil.com/

```
For multiple URLs(use the url.txt file provided in the repository)

⚠️ Each URL should be on a new line for the script to function properly

```bash
python3 clickjacker_pro.py -f url.txt

```
For Interactive mode

```bash 
python3 clickjacker_pro.py

```
