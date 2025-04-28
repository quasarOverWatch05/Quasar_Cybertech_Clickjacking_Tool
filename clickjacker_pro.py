# Quasar CyberTech
import os
import sys
import argparse
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED 
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Clickjacking Test</title>
    <link rel="icon" href="https://drive.google.com/file/d/1ngUK9EbvK_DGSiFBvQm1nqmTWzxPFAO1/view?usp=drive_link">
    <style>
        body {{
            margin: 0;
            font-family: 'Segoe UI', sans-serif;
            background-color: #3d0b1c;
            color: #f3d5b5;
        }}
        .header {{
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2em;
        }}
        .container {{
            max-width: 1000px;
            margin: auto;
            background: #500c20;
            padding: 20px;
            border-radius: 10px;
        }}
        .url-box {{
            margin-bottom: 20px;
            display: flex;
        }}
        .url-box input {{
            flex: 1;
            padding: 10px;
            font-size: 16px;
            border: none;
            border-radius: 5px 0 0 5px;
        }}
        .url-box button {{
            background-color: #2979ff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 0 5px 5px 0;
            cursor: pointer;
        }}
        .info {{
            background-color: #fff0f0;
            padding: 15px;
            border-radius: 10px;
            color: #000;
            margin-bottom: 20px;
        }}
        .alert {{
            background-color: #d32f2f;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
        }}
        .iframe-wrapper {{
            position: relative;
            width: 100%;
            height: 600px;
            border: 2px solid #900;
            border-radius: 10px;
            overflow: hidden;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
            opacity: 0.95;
        }}
        .overlay {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(255, 255, 0, 0.4);
            color: #000;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: bold;
            z-index: 10;
            pointer-events: none;
            display: none;
        }}
        .toggle-btn {{
            margin: 10px auto 20px;
            display: block;
            padding: 10px 20px;
            background-color: #2196f3;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Clickjacking Test</h1>
    </div>
    <div class="container">
        <div class="url-box">
            <input type="text" value="{url}" readonly>
            <button>Test</button>
        </div>
        <div class="info">
            <strong>Site:</strong> {url}<br>
            <strong>IP Address:</strong> Auto-Detected<br>
            <strong>Time:</strong> Auto-Generated<br>
            <strong>Missing Headers:</strong> <span style="color: red;">X-Frame-Options, CSP frame-ancestors</span>
        </div>
        <div class="alert">Site is vulnerable to Clickjacking</div>
        <button class="toggle-btn" onclick="toggleOverlay()">Toggle Overlay</button>
        <div class="iframe-wrapper">
            <div class="overlay" id="overlay">Click Me!</div>
            <iframe src="{url}"></iframe>
        </div>
    </div>
    <script>
        function toggleOverlay() {{
            const overlay = document.getElementById('overlay');
            overlay.style.display = (overlay.style.display === 'block') ? 'none' : 'block';
        }}
    </script>
</body>
</html>
    """
    
    with open(filename, 'w') as f:
        f.write(html_content)
    
    return filename

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
            border_style="red",
            box="ROUNDED"
        ))
        return
    
    if result['vulnerable']:
        console.print(Panel(
            f"[bold green]URL: {url}\n"
            f"[bold red]Status: VULNERABLE\n"
            f"[bold yellow]X-Frame-Options: {result['x_frame_options']}\n"
            f"[bold yellow]CSP Frame-Ancestors: {result['csp_frame_ancestors']}\n"
            f"[bold cyan]Clickjacking Mitigation Guide: https://quasarclickjacker.netlify.app/defensecj.html",
            title="Clickjacking Vulnerability Found",
            border_style="red",
            box=ROUNDED
        ))
        
        # Generate PoC HTML file
        html_file = generate_poc_html(url, output_dir)
        console.print(f"[bold green]PoC HTML file generated: {html_file}")
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
    console.print(
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n"
        "[bright_green]     |Q|u|a|s|a|r| |C|y|b|e|r|T|e|c|h|\n"
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n\n"
    )
    console.print(
        "[bold cyan]Clickjacking Detection & Exploitation Tool[/bold cyan]\n"
        "[yellow]Developed and Maintained by Quasar CyberTech Research Team[/yellow]\n\n"
        
    )
    
    parser = argparse.ArgumentParser(description="Clickjacking Detection & Exploitation Tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='Test a single URL for clickjacking vulnerability')
    group.add_argument('-f', '--file', help='Provide a file with multiple URLs to test (one URL per line)')
    parser.add_argument('-o', '--output', default='output', help='Directory to save results (default: output)')
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
    console.print(
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n"
        "[bright_green]     |Q|u|a|s|a|r| |C|y|b|e|r|T|e|c|h|\n"
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n\n"
    )
    console.print(
        "[bold cyan]Clickjacking Detection & Exploitation Tool[/bold cyan]\n"
        "[yellow]Developed and Maintained by Quasar CyberTech Research Team[/yellow]\n\n"
    )
    
    output_dir = 'output'
    create_directory(output_dir)
    
    console.print("[bold blue]Choose an option:")
    console.print("[1] Test a single URL")
    console.print("[2] Test multiple URLs")
    
    choice = input(f"{Fore.CYAN}Enter your choice (1/2): {Style.RESET_ALL}")
    
    if choice == '1':
        url = input(f"{Fore.CYAN}Enter URL to test: {Style.RESET_ALL}")
        process_url(url, output_dir)

    elif choice == '2':
        urls = []
        file_name = input(f"{Fore.CYAN}Enter the file name containing URLs: {Style.RESET_ALL}")
        try:
            with open(file_name, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            if not urls:
                console.print(f"[bold red]No URLs found in {file_name}.")
                return

            console.print(f"[bold blue]Loaded {len(urls)} URLs from '{file_name}'.")

            # Create a table for results summary
            table = Table(title="Clickjacking Test Results (Interactive Mode)")
            table.add_column("URL", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Vulnerable", style="red")

            # Process URLs in parallel
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for url in urls:
                    futures.append(executor.submit(process_url, url, output_dir))

                for i, future in enumerate(futures):
                    try:
                        # Assuming process_url also internally calls check_clickjacking
                        url = urls[i]
                        result = check_clickjacking(check_url_format(url))
                        status = str(result['status_code'])
                        vulnerable = "YES" if result.get('vulnerable', False) else "NO"
                        table.add_row(url, status, vulnerable)
                    except Exception as e:
                        console.print(f"[bold red]Error processing {urls[i]}: {str(e)}")
            console.print(table)

        except FileNotFoundError:
            console.print(f"[bold red]'{file_name}' not found. Please create '{file_name}' with URLs inside it.")
        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}")
    else:
        console.print("[bold red]Invalid choice.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        interactive_mode()
