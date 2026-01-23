
import asyncio
import sys
from pathlib import Path
from warcio.capture import capture_requests
from warcio.warcwriter import WARCWriter
from playwright.async_api import async_playwright
import requests

async def capture_wacz(url, out_path):
    print(f"Capturing {url} to {out_path}...")
    
    warc_path = out_path.with_suffix(".warc.gz")
    
    with open(warc_path, 'wb') as output:
        writer = WARCWriter(output, gzip=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=["--no-sandbox"])
            context = await browser.new_context()
            page = await context.new_page()
            
            # Setup request capturing if needed, but playwright-warc is better
            # For now, let's just use the page.content() and save as WARC record
            await page.goto(url, wait_until="networkidle")
            content = await page.content()
            
            # Write a basic WARC record for the main page
            import datetime
            record = writer.create_warc_record(
                url, 'response',
                payload=sys.stdin.buffer, # Placeholder
                http_headers=None # Placeholder
            )
            # Actually, using playwright-warc would be complex.
            # Let's use the 'wacz' CLI to package.
            
            await browser.close()

    # Convert to WACZ using the tool we just installed
    subprocess.run(["wacz", "create", "-o", str(out_path), str(warc_path)])
    print("Done")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        asyncio.run(capture_wacz(sys.argv[1], Path(sys.argv[2])))
