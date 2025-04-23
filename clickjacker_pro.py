#!/usr/bin/env python3
"""
Clickjacking Detection & Exploitation Tool
Checks websites for clickjacking vulnerabilities and generates proof-of-concept HTML files
"""

import os
import sys
import time
import argparse
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Initialize colorama
init(autoreset=True)

# Initialize rich console
console = Console()

def create_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def check_url_format(url):
    """Check if URL has proper format and add http:// if missing"""
    if not url.startswith(('http://', 'https://')):
        return f'http://{url}'
    return url

def check_clickjacking(url):
    """Check if website is vulnerable to clickjacking"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check X-Frame-Options header
        x_frame_options = response.headers.get('X-Frame-Options', '').upper()
        
        # Check Content-Security-Policy header for frame-ancestors directive
        csp = response.headers.get('Content-Security-Policy', '')
        frame_ancestors = False
        if 'frame-ancestors' in csp:
            frame_ancestors = True
            
        # Site is vulnerable if both protections are missing
        is_vulnerable = not (x_frame_options in ['DENY', 'SAMEORIGIN'] or frame_ancestors)
        
        return {
            'url': url,
            'status_code': response.status_code,
            'vulnerable': is_vulnerable,
            'x_frame_options': x_frame_options if x_frame_options else 'Not Set',
            'csp_frame_ancestors': 'Set' if frame_ancestors else 'Not Set'
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'status_code': 'Error',
            'vulnerable': False,
            'x_frame_options': 'N/A',
            'csp_frame_ancestors': 'N/A',
            'error': str(e)
        }

def generate_poc_html(url, output_dir):
    """Generate HTML PoC file with iframe"""
    domain = urlparse(url).netloc
    filename = f"{output_dir}/{domain}_clickjacking_poc.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clickjacking PoC for {domain}</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }}
            .container {{
                width: 100%;
                height: 100vh;
                position: relative;
            }}
            .target-website {{
                width: 100%;
                height: 100%;
                border: none;
                position: absolute;
                top: 0;
                left: 0;
                z-index: 1;
                opacity: 0.8;
            }}
            .overlay {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 2;
                background-color: rgba(255, 0, 0, 0.3);
                padding: 20px;
                border-radius: 5px;
                pointer-events: none;
            }}
            h1 {{
                color: #333;
                text-align: center;
                padding: 10px;
                background-color: #fff;
                border-radius: 5px;
                margin-top: 0;
            }}
        </style>
    </head>
    <body>
        <h1>Clickjacking Proof of Concept for {domain}</h1>
        <div class="container">
            <div class="overlay">Clickable Area (Demonstration)</div>
            <iframe class="target-website" src="{url}"></iframe>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_content)
    
    return filename

def take_screenshot(url, html_file, output_dir):
    """Take screenshot of the vulnerable page with iframe using Playwright and Firefox"""
    try:
        domain = urlparse(url).netloc
        screenshot_path = f"{output_dir}/{domain}_screenshot.png"
        
        with sync_playwright() as p:
            # Launch Firefox browser
            browser = p.firefox.launch()
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            
            # Load the HTML file
            file_url = f"file://{os.path.abspath(html_file)}"
            page.goto(file_url)
            
            # Wait for iframe to load
            page.wait_for_timeout(3000)
            
            # Take screenshot
            page.screenshot(path=screenshot_path)
            browser.close()
        
        return screenshot_path
    except Exception as e:
        console.print(f"[bold red]Error taking screenshot: {str(e)}")
        return None

def process_url(url, output_dir):
    """Process a single URL"""
    url = check_url_format(url)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Testing {task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(url, total=1)
        result = check_clickjacking(url)
        progress.update(task, advance=1)
    
    if result['status_code'] == 'Error':
        console.print(Panel(
            f"[bold red]Error testing {url}: {result.get('error', 'Unknown error')}",
            title="Error",
            border_style="red"
        ))
        return
    
    if result['vulnerable']:
        console.print(Panel(
            f"[bold green]URL: {url}\n"
            f"[bold red]Status: VULNERABLE\n"
            f"[bold yellow]X-Frame-Options: {result['x_frame_options']}\n"
            f"[bold yellow]CSP Frame-Ancestors: {result['csp_frame_ancestors']}",
            title="Clickjacking Vulnerability Found",
            border_style="red"
        ))
        
        # Generate PoC HTML file
        html_file = generate_poc_html(url, output_dir)
        console.print(f"[bold green]PoC HTML file generated: {html_file}")
        
        # Take screenshot
        with console.status("[bold yellow]Taking screenshot..."):
            screenshot = take_screenshot(url, html_file, output_dir)
        
        if screenshot:
            console.print(f"[bold green]Screenshot saved: {screenshot}")
    else:
        console.print(Panel(
            f"[bold green]URL: {url}\n"
            f"[bold green]Status: PROTECTED\n"
            f"[bold yellow]X-Frame-Options: {result['x_frame_options']}\n"
            f"[bold yellow]CSP Frame-Ancestors: {result['csp_frame_ancestors']}",
            title="Site Protected Against Clickjacking",
            border_style="green"
        ))

def main():
    """Main function"""
    console.print(Panel.fit(
        "[bold cyan]Clickjacking Detection & Exploitation Tool[/bold cyan]\n"
        "[yellow]Detects clickjacking vulnerabilities and generates PoC[/yellow]",
        border_style="blue"
    ))
    
    parser = argparse.ArgumentParser(description="Clickjacking Detection & Exploitation Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='Single URL to test')
    group.add_argument('-f', '--file', help='File containing URLs to test (one per line)')
    parser.add_argument('-o', '--output', default='output', help='Output directory for results (default: output)')
    args = parser.parse_args()
    
    # Create output directory
    create_directory(args.output)
    
    if args.url:
        # Process single URL
        process_url(args.url, args.output)
    elif args.file:
        # Process multiple URLs from file
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                console.print("[bold red]No URLs found in the file.")
                return
            
            console.print(f"[bold blue]Testing {len(urls)} URLs for clickjacking vulnerabilities...")
            
            # Create a table for results summary
            table = Table(title="Clickjacking Test Results")
            table.add_column("URL", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Vulnerable", style="red")
            
            # Process URLs in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                for url in urls:
                    process_url(url, args.output)
                    
                    # Add to summary table
                    result = check_clickjacking(check_url_format(url))
                    status = str(result['status_code'])
                    vulnerable = "YES" if result.get('vulnerable', False) else "NO"
                    table.add_row(url, status, vulnerable)
            
            console.print(table)
            
        except FileNotFoundError:
            console.print(f"[bold red]File not found: {args.file}")
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}")

def interactive_mode():
    """Interactive mode for the tool"""
    console.print(Panel.fit(
        "[bold cyan]Clickjacking Detection & Exploitation Tool[/bold cyan]\n"
        "[yellow]Detects clickjacking vulnerabilities and generates PoC[/yellow]",
        border_style="blue"
    ))
    
    output_dir = 'output'
    create_directory(output_dir)
    
    console.print("[bold cyan]Choose an option:")
    console.print("[1] Test a single URL")
    console.print("[2] Test multiple URLs")
    
    choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}")
    
    if choice == '1':
        url = input(f"{Fore.GREEN}Enter URL to test: {Style.RESET_ALL}")
        process_url(url, output_dir)
    elif choice == '2':
        urls = []
        console.print("[bold yellow]Enter URLs (one per line, enter empty line to finish):")
        while True:
            url = input(f"{Fore.GREEN}URL: {Style.RESET_ALL}")
            if not url:
                break
            urls.append(url)
        
        if not urls:
            console.print("[bold red]No URLs provided.")
            return
        
        for url in urls:
            process_url(url, output_dir)
    else:
        console.print("[bold red]Invalid choice.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()
