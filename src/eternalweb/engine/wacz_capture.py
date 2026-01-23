
import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess

async def capture_wacz_playwright(url, out_path):
    """
    Captures a WACZ file using Playwright HAR export and har2wacz.
    This is more reliable than browsertrix-crawler in constrained environments.
    """
    print(f"[*] Starting Playwright capture: {url}")
    
    # Create temp directory for HAR
    tmp_har = out_path.with_suffix(".har")
    
    try:
        async with async_playwright() as p:
            # Try to find a browser
            browser_type = p.chromium
            browser = await browser_type.launch(args=["--no-sandbox"])
            
            # Start recording HAR
            context = await browser.new_context(
                record_har_path=str(tmp_har),
                record_har_content="embed",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Navigate
            print(f"[*] Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Scroll to bottom to trigger lazy loading
            print("[*] Scrolling to trigger lazy loading...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
            await context.close()
            await browser.close()
            
        if not tmp_har.exists():
            print("[!] Error: HAR file was not created.")
            return False
            
        print(f"[*] HAR created ({tmp_har.stat().st_size} bytes). Converting to WACZ...")
        
        # Convert HAR to WACZ using the 'wacz' command line tool (installed via pip)
        # command: wacz create --har <har_file> -o <out_path>
        res = subprocess.run(["wacz", "create", "--har", str(tmp_har), "-o", str(out_path)], 
                             capture_output=True, text=True)
        
        if out_path.exists():
            print(f"[+] Success: WACZ created at {out_path}")
            return True
        else:
            print(f"[!] Error: WACZ conversion failed: {res.stderr}")
            return False
            
    except Exception as e:
        print(f"[!] Exception during capture: {e}")
        return False
    finally:
        if tmp_har.exists():
            os.remove(tmp_har)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python wacz_capture.py <url> <out_path>")
        sys.exit(1)
        
    url = sys.argv[1]
    out_path = Path(sys.argv[2])
    
    success = asyncio.run(capture_wacz_playwright(url, out_path))
    sys.exit(0 if success else 1)
