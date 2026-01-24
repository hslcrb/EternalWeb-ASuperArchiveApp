
# EternalWeb Core Engine
# Orchestrates ArchiveBox, SingleFile, and ArchiveWeb.page

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from ..config import get_config

# 통합 설정 로드
config = get_config()

# Paths adjustment for new structure
# This file is in src/eternalweb/engine/engine.py
# Components are in src/eternalweb/components/

CORE_DIR = Path(__file__).parent
COMPONENTS_DIR = CORE_DIR.parent / "components"
ARCHIVEBOX_DIR = CORE_DIR / "archivebox" # Moved here earlier

# Legacy Support: Add core dir to sys.path so 'import archivebox' works
sys.path.append(str(CORE_DIR))

def init_engine():
    """설정을 기반으로 엔진을 초기화합니다."""
    print(f"EternalWeb 엔진 코어 초기화 중... (저장경로: {config['storage_path']})")
    print(f"구성 요소 경로: {COMPONENTS_DIR}")
    
    # Check Components
    if (COMPONENTS_DIR / "singlefile").exists():
        print("✔ 구성 요소 로드됨: SingleFile (고해상도)")
    else:
        print("✘ 구성 요소 누락: SingleFile")

    if (COMPONENTS_DIR / "webpage").exists():
        print("✔ 구성 요소 로드됨: ArchiveWeb.page (대화형 아카이브)")
    else:
        print("✘ 구성 요소 누락: ArchiveWeb.page")

    # Verify ArchiveBox
    try:
        # Since we moved archivebox to src/eternalweb/engine/archivebox,
        # we need to make sure it's importable.
        # It's a subdirectory here, so it should be fine if __init__.py exists.
        from . import archivebox
        print(f"✔ 코어 로드됨: ArchiveBox 레거시 엔진")
    except ImportError as e:
        print(f"⚠ ArchiveBox 임포트 문제 발생: {e}")

class Archiver:
    def __init__(self, log_fn=None):
        self.active_jobs = []
        self.log_fn = log_fn if log_fn else print

    def archive_url(self, url, options=None):
        if options is None:
            options = ["WACZ", "SingleFile"]

        storage_path = Path(config['storage_path'])
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # 아카이브 결과 데이터 (Library 연동용)
        archive_id = Path(url.replace("://", "_").replace("/", "_")).name[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_dir = storage_path / f"{timestamp}_{archive_id}"
        job_dir.mkdir(parents=True, exist_ok=True)
 
        return self.run_archiving(url, options, job_dir)

    def run_archiving(self, url, options, job_dir):
        self.log(f"⚡ [이터널웹] 엔진 가동: {url}")
        self.log(f"📂 저장 경로: {job_dir}")
        
        # timestamp는 폴더명에서 직접 파싱 (YYYYMMDD_HHMMSS 형식 유지)
        ts_part = job_dir.name.split('_')[0] + "_" + job_dir.name.split('_')[1]
        results = {"url": url, "timestamp": ts_part, "path": str(job_dir), "formats": []}
        
        # 통합 아카이빙 엔진 (Playwright 기반)
        # Level 1 (HTML)과 Level 2 (WACZ)를 한 번의 브라우저 세션으로 처리합니다.
        wacz_path = job_dir / "interactive.wacz"
        html_path = job_dir / "snapshot.html"
        
        needed_wacz = "WACZ" in options
        needed_html = "SingleFile" in options or "HTML" in options
        
        if needed_wacz or needed_html:
            self.log(f"🚀 [통합 엔진] Playwright 고성능 캡처 시작...")
            capture_script = CORE_DIR / "wacz_capture.py"
            
            # 파라미터 구성
            cmd = [sys.executable, str(capture_script), url, str(wacz_path)]
            if needed_html:
                cmd.append(str(html_path))
            
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if html_path.exists():
                self.log("✔ [Level 1] HTML 스냅샷 저장 완료")
                results["formats"].append("HTML")
            
            if wacz_path.exists():
                self.log("✔ [Level 2] WACZ 인터랙티브 아카이브 완료")
                results["formats"].append("WACZ")
            else:
                self.log(f"⚠ Playwright 캡처 실패 (코드: {res.returncode})")
                if res.stderr: self.log(f"상세 로그:\n{res.stderr[-500:]}")
                
                # Fallback: Browsertrix Crawler (WACZ용)
                if needed_wacz:
                    self.log("ℹ 대체 엔진 (Browsertrix) 시도 중...")
                    save_dir = job_dir / "wacz_tmp"
                    save_dir.mkdir(exist_ok=True)
                    # npx @webrecorder/browsertrix-crawler 가 404나면 browsertrix-crawler 도 시도
                    bt_cmd = ["npx", "-y", "@webrecorder/browsertrix-crawler", "crawl", 
                           "--url", url, "--generateWACZ", "--output", str(save_dir), "--workers", "1"]
                    
                    alt_res = subprocess.run(bt_cmd, capture_output=True, text=True, check=False)
                    wacz_files = list(save_dir.glob("**/*.wacz"))
                    if wacz_files:
                        import shutil
                        shutil.move(str(wacz_files[0]), str(wacz_path))
                        self.log("✔ [Level 2] WACZ 완료 (Browsertrix)")
                        results["formats"].append("WACZ")
                
                # Fallback: SingleFile (HTML 전용)
                if needed_html and not html_path.exists():
                    self.run_singlefile(url, html_path)
                    if html_path.exists(): results["formats"].append("HTML")

        # 3. ArchiveBox (Level 3)
        if any(opt in options for opt in ["WARC", "Media", "PDF", "Screenshot"]):
            self.run_archivebox(url, options, job_dir)
            results["formats"].append("ArchiveBox")
        
        self.save_to_library(results)
        return results

    def log(self, message):
        """커맨드 및 GUI 로그 동시 출력"""
        t = datetime.now().strftime('%H:%M:%S')
        msg = f"[{t}] {message}"
        print(msg)
        if self.log_fn:
            self.log_fn(message)

    def run_singlefile(self, url, out_path):
        self.log(f"📸 [Level 1] 스냅샷 추출 중 (single-file-cli)...")
        try:
            # single-file-cli 옵션 최적화: 브라우저 인자 강화 및 대기 시간 조정
            cmd = [
                "npx", "-y", "single-file-cli", 
                url, str(out_path), 
                "--browser-args", '["--no-sandbox", "--disable-setuid-sandbox", "--ignore-certificate-errors", "--disable-web-security", "--disable-features=IsolateOrigins,site-per-process"]',
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--load-deferred-images-dispatch-scroll-event", "true",
                "--browser-wait-until", "networkIdle",
                "--browser-load-max-time", "120000",
                "--browser-wait-delay", "3000"
            ]
            
            # 실행 시 환경 변수에서 NODE_OPTIONS 등을 제거하여 순수 npx 실행 시도
            env = os.environ.copy()
            # npm 인증 경고 방지
            env["NPM_CONFIG_REGISTRY"] = "https://registry.npmjs.org/"
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
            
            if out_path.exists() and out_path.stat().st_size > 500:
                self.log("✔ Level 1 HTML 스냅샷 저장 완료")
            else:
                self.log(f"❌ Level 1 실패 (코드: {result.returncode})")
                if result.stderr: self.log(f"상세 에러:\n{result.stderr[-500:]}")
                if result.stdout: self.log(f"표준 출력:\n{result.stdout[-200:]}")
        except Exception as e:
            self.log(f"❌ SingleFile 예외 발생: {e}")

    def run_archivebox(self, url, options, job_dir):
        self.log(f"📦 [Level 3] 내장 ArchiveBox 엔진 가동 중...")
        # 0.8.x 버전에서는 --extract 대신 --plugins를 사용함
        plugins = []
        if "WARC" in options: plugins.append("wget")
        if "PDF" in options: plugins.append("pdf")
        if "Media" in options: plugins.append("media")
        if "Screenshot" in options: plugins.append("screenshot")
        
        try:
            engine_root = str(CORE_DIR.resolve())
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{engine_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
            
            # 1. 초기화
            self.log("ℹ ArchiveBox 데이터베이스 초기화 중...")
            init_res = subprocess.run([sys.executable, "-m", "archivebox", "init", "--force"], 
                                      cwd=job_dir, env=env, capture_output=True, text=True, check=False)
            
            if not (job_dir / "index.sqlite3").exists():
                self.log(f"⚠ Level 3 초기화 실패. 로그:\n{init_res.stderr[-300:]}")
                return
            
            # 2. 추가 및 추출
            self.log(f"ℹ ArchiveBox 플러그인 실행: {', '.join(plugins) if plugins else 'all'}")
            cmd = [sys.executable, "-m", "archivebox", "add", url]
            if plugins:
                cmd.append(f"--plugins={','.join(plugins)}")
            
            result = subprocess.run(cmd, cwd=job_dir, env=env, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                self.log(f"❌ Level 3 실패. 로그:\n{result.stderr[-400:]}")
            else:
                self.log("✔ Level 3 심층 아카이브 완료")
        except Exception as e:
            self.log(f"❌ ArchiveBox 예외 발생: {e}")

    def save_to_library(self, data):
        """아카이브 결과를 중앙 인덱스 파일에 기록합니다."""
        index_file = Path(config['storage_path']) / "index.json"
        library = []
        if index_file.exists() and index_file.stat().st_size > 0:
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    library = json.load(f)
            except json.JSONDecodeError:
                self.log_fn("⚠ 라이브러리 파일이 손상되었습니다. 새로 생성합니다.")
                library = []
        
        library.append(data)
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(library, f, indent=4, ensure_ascii=False)
        self.log_fn(f"📚 라이브러리에 저장 완료: {data['url']}")

