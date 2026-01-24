
import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess

async def capture_playwright_all(url, wacz_path, html_path=None):
    """
    Captures WACZ (Level 2) and optionally HTML (Level 1) using a single Playwright session.
    """
    print(f"[*] Starting Consolidated Playwright capture: {url}")
    
    tmp_har = wacz_path.with_suffix(".har")
    
    try:
        async with async_playwright() as p:
            # 브라우저 실행 (보안/샌드박스 설정 강화)
            browser = await p.chromium.launch(args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--ignore-certificate-errors",
                "--disable-web-security"
            ])
            
            # HAR 기록 및 최신 브라우저 스타일 설정
            version = "120.0.0.0"
            context = await browser.new_context(
                record_har_path=str(tmp_har),
                record_har_content="embed",
                ignore_https_errors=True,
                viewport={'width': 1920, 'height': 1080},
                user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
            )
            
            page = await context.new_page()
            
            # 페이지 이동 및 대기
            print(f"[*] Navigating to {url}...")
            # 교육청 사이트 등은 로딩이 느릴 수 있으므로 90초 대기
            await page.goto(url, wait_until="networkidle", timeout=90000)
            
            # 레이지 로딩 트리거 (스크롤)
            print("[*] Scrolling to trigger lazy loading...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
            # Level 1 Snapshot용 HTML 명시적 저장
            if html_path:
                print(f"[*] Saving HTML snapshot to {html_path}...")
                content = await page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(content)

            await context.close()
            await browser.close()
            
        if not tmp_har.exists():
            print("[!] Error: HAR file was not created.")
            return False
            
        print(f"[*] HAR created ({tmp_har.stat().st_size} bytes). Converting to WACZ...")
        
        # venv 내의 wacz 도구 사용하여 패키징
        venv_bin = Path(sys.executable).parent
        wacz_cmd = venv_bin / "wacz"
        if not wacz_cmd.exists(): wacz_cmd = venv_bin / "wacz.exe"
            
        print(f"[*] Running: {wacz_cmd} create -o {wacz_path} {tmp_har}")
        res = subprocess.run([str(wacz_cmd), "create", "-o", str(wacz_path), str(tmp_har)], 
                             capture_output=True, text=True)
        
        if wacz_path.exists():
            print(f"[+] Success: WACZ created at {wacz_path}")
            return True
        else:
            print(f"[!] Error: WACZ conversion failed: {res.stderr}")
            return False
            
    except Exception as e:
        print(f"[!] Exception during capture: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if tmp_har.exists():
            try: os.remove(tmp_har)
            except: pass

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python wacz_capture.py <url> <wacz_path> [html_path]")
        sys.exit(1)
        
    url = sys.argv[1]
    wacz_path = Path(sys.argv[2])
    html_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    success = asyncio.run(capture_playwright_all(url, wacz_path, html_path))
    sys.exit(0 if success else 1)
