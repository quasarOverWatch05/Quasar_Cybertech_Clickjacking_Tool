import os, json, csv, sys, time
import requests, validators, tldextract
from bs4 import BeautifulSoup
from argparse import ArgumentParser
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from rich.console import Console
from rich.table import Table
from datetime import datetime

init(autoreset=True)
console = Console()

SCREENSHOT_DIR = "results/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs("results", exist_ok=True)

def banner():
    console.rule("[bold magenta]Clickjacking Detector – Advanced CLI Tool")
    console.print("🔐 Developed by [bold]Quasar CyberTech[/bold]", style="cyan")
    console.rule()

def log(msg, style="white"):
    console.print(msg, style=style)

def validate_url(url):
    if not validators.url(url):
        log("[ERROR] Invalid URL format. Use http:// or https://", "bold red")
        sys.exit(1)

def get_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def check_headers(headers):
    secure = True
    findings = {}

    xfo = headers.get('X-Frame-Options')
    if xfo:
        findings['X-Frame-Options'] = xfo
        log(f"[X-Frame-Options] → {xfo}", "cyan")
        if xfo.upper() in ['DENY', 'SAMEORIGIN']:
            log("✅ Proper X-Frame-Options policy.", "green")
        else:
            log("⚠️ Weak X-Frame-Options policy!", "yellow")
            secure = False
    else:
        log("❌ X-Frame-Options header missing!", "yellow")
        findings['X-Frame-Options'] = "Missing"
        secure = False

    csp = headers.get('Content-Security-Policy')
    if csp:
        findings['Content-Security-Policy'] = csp
        log("[CSP] → Found", "cyan")
        if 'frame-ancestors' in csp:
            log("✅ frame-ancestors directive present.", "green")
        else:
            log("⚠️ CSP missing frame-ancestors!", "yellow")
            secure = False
    else:
        log("❌ CSP header missing!", "yellow")
        findings['Content-Security-Policy'] = "Missing"
        secure = False

    return secure, findings

def inspect_iframes(soup):
    iframes = soup.find_all('iframe')
    details = []
    if not iframes:
        log("✅ No iframe elements found.", "green")
        return details

    log(f"⚠️ Found {len(iframes)} iframe(s):", "yellow")
    table = Table(title="Iframe Details", style="cyan")
    table.add_column("Src"), table.add_column("Width"), table.add_column("Height"), table.add_column("Border")

    for iframe in iframes:
        data = {
            "src": iframe.get('src', 'N/A'),
            "width": iframe.get('width', 'N/A'),
            "height": iframe.get('height', 'N/A'),
            "border": iframe.get('frameborder', 'N/A'),
        }
        details.append(data)
        table.add_row(data["src"], data["width"], data["height"], data["border"])

    console.print(table)
    return details

def take_screenshot(url, domain):
    try:
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.set_window_size(1920, 1080)
        driver.get(url)
        time.sleep(2)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{domain}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        driver.quit()
        log(f"📸 Screenshot saved to {filepath}", "cyan")
        return filepath
    except Exception as e:
        log(f"[ERROR] Screenshot failed: {e}", "red")
        return None

def save_output(result, output_format):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_format == "json":
        path = f"results/report_{timestamp}.json"
        with open(path, "w") as f:
            json.dump(result, f, indent=4)
        log(f"📝 JSON saved: {path}", "green")
    elif output_format == "csv":
        path = f"results/report_{timestamp}.csv"
        with open(path, "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(result.keys())
            writer.writerow(result.values())
        log(f"📝 CSV saved: {path}", "green")

def analyze(url, output_format):
    log(f"[Analyzing] {url}\n", "bold white")
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        domain = get_domain(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        secure, headers_data = check_headers(response.headers)
        iframe_data = inspect_iframes(soup)

        screenshot_path = None
        if not secure:
            screenshot_path = take_screenshot(url, domain)

        result = {
            "url": url,
            "domain": domain,
            "secure": secure,
            "headers": headers_data,
            "iframes": iframe_data,
            "screenshot": screenshot_path,
            "scanned_at": datetime.now().isoformat()
        }

        if output_format:
            save_output(result, output_format)

        if secure:
            log(f"\n✅ {domain} is secure against Clickjacking.\n", "green")
        else:
            log(f"\n❌ {domain} is vulnerable to Clickjacking.\n", "red")

    except requests.RequestException as e:
        log(f"[ERROR] Failed to fetch page: {e}", "red")


def batch_analyze(file_path, output_format):
    if not os.path.isfile(file_path):
        log(f"[ERROR] File not found: {file_path}", "red")
        sys.exit(1)

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        log("[ERROR] No valid URLs found in the file.", "red")
        sys.exit(1)

    for url in urls:
        try:
            log(f"\n[Scanning] {url}", "bold blue")
            validate_url(url)
            analyze(url, output_format)
        except Exception as e:
            log(f"[ERROR] Scan failed for {url}: {e}", "red")

def main():
    parser = ArgumentParser(description="Advanced Clickjacking Detection Tool (Batch + Output + Screenshot)")
    parser.add_argument("-u", "--url", help="Scan a single URL")
    parser.add_argument("-l", "--list", help="File with list of URLs to scan")
    parser.add_argument("-o", "--output", choices=["json", "csv"], help="Output format")
    args = parser.parse_args()

    banner()

    if args.url:
        validate_url(args.url)
        analyze(args.url, args.output)
    elif args.list:
        batch_analyze(args.list, args.output)
    else:
        log("⚠️ Please provide either --url or --list to scan.", "yellow")
        sys.exit(1)

if __name__ == "__main__":
    main()
