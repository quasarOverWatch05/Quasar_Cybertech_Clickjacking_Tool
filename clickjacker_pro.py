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
    """Generate polished split-view Clickjacking PoC HTML."""
    from urllib.parse import urlparse
    url = urlparse(url).netloc
    filename = f"{output_dir}/{url}_clickjacking_poc.html"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Clickjacking PoC - {url}</title>
    <link rel="icon" href="/Quasar.png" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Basic reset */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html, body {{
            height: 100%;
            width: 100%;
            overflow: hidden; /* No scrolling */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #480020;
            color: #f3d5b5;
        }}

        .container {{
            display: flex;
            height: 100%;
        }}

        .left-panel {{
            flex: 2;
            background-color: #480020;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow: hidden;
        }}

        .iframe-wrapper {{
            position: relative;
            width: 80%;
            height: 95%;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.2);
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
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: bold;
            color: #000;
            font-size: 1.5rem;
            pointer-events: none;
            display: none;
            z-index: 10;
        }}

        .right-panel {{
            flex: 1;
            background-color: #480020;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 30px;
            margin-right: 80px;
        }}

        h1 {{
            margin-bottom: 30px;
            font-size: 2rem;
            text-align: center;
        }}

        .url-box {{
            width: 100%;
            display: flex;
            margin-bottom: 20px;
        }}

        .url-box input {{
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px 0 0 8px;
            font-size: 1rem;
            color: #333;
        }}

        .url-box button {{
            background-color: #2979ff;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 0 8px 8px 0;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
        }}

        .info {{
            width: 100%;
            background-color: #fff0f0;
            color: #000;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: left;
            font-size: 0.95rem;
        }}

        .alert {{
            width: 100%;
            background-color: #d32f2f;
            color: white;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }}

        .toggle-btn {{
            background-color: #2196f3;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: background-color 0.3s;
        }}

        .toggle-btn:hover {{
            background-color: #1976d2;
        }}

        footer {{
            margin-top: 20px;
            font-size: 0.8rem;
            color: #bbb;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="left-panel">
            <div class="iframe-wrapper">
                <div class="overlay" id="overlay">Click Me!</div>
                <iframe src="https://{url}" sandbox="allow-forms allow-scripts"></iframe>
            </div>
        </div>
        <div class="right-panel">
            <img src="https://quasarcybertech.com/wp-content/uploads/2024/06/fulllogo_transparent_nobuffer.png" alt="Quasar CyberTech Logo" style="width: 75%; max-width: 130px; margin-bottom: 20px;">
            <h1>Clickjacking Test</h1>
            <div class="url-box">
                <input type="text" value="https://{url}" readonly>
                <button disabled>Tested</button>
            </div>
            <div class="info">
                <strong>Site:</strong> https://{url}<br>
                <strong>IP Address:</strong> Auto-Detected<br>
                <strong>Time:</strong> Auto-Generated
            </div>
            <div class="alert">
                🚨 Vulnerable to Clickjacking
            </div>
            <button class="toggle-btn" onclick="toggleOverlay()">Toggle Overlay</button>
            <footer>PoC generated by Quasar CyberTech</footer>
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

    with open(filename, 'w', encoding="utf-8") as f:
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
            box=ROUNDED
        ))
        return result  # Return the result even in case of error
    
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
    
    return result  # Return the result for summary table

def main():
    """Main function"""
    console.print(
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n"
        "[bright_green]     |Q|u|a|s|a|r| |C|y|b|e|r|T|e|c|h|\n"
        "[bright_green]     +-+-+-+-+-+-+ +-+-+-+-+-+-+-+-+-+\n\n"
    )
    console.print(
        "[bright_green]     Clickjacking Detection & Exploitation Tool[/bright_green]\n"
        "[bright_green]     Developed and Maintained by Quasar CyberTech Research Team[/bright_green]\n\n"
        
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
            table = Table(title="[bold bright_green]Clickjacking Test Results", style="bright_green")
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
        "[bright_green]     Clickjacking Detection & Exploitation Tool[/bright_green]\n"
        "[bright_green]     Developed and Maintained by Quasar CyberTech Research Team[/bright_green]\n\n"
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
        file_name = input(f"{Fore.CYAN}Enter the file name containing URLs: {Style.RESET_ALL}")
        try:
            with open(file_name, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]

            if not urls:
                console.print(f"[bold red]No URLs found in {file_name}.")
                return

            console.print(f"[bold blue]Loaded {len(urls)} URLs from '{file_name}'.")

            # Create a table for results summary
            table = Table(title="[bold bright_green]Clickjacking Test Results (Interactive Mode)", style="bright_green")
            table.add_column("URL", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Vulnerable", style="red")

            # Process URLs sequentially and collect results
            for url in urls:
                result = process_url(url, output_dir)
                if result:
                    status = str(result['status_code'])
                    vulnerable = "YES" if result.get('vulnerable', False) else "NO"
                    table.add_row(url, status, vulnerable)
                else:
                    table.add_row(url, "Error", "N/A")

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
