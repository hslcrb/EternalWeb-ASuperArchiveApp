
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
        
        # 1. SingleFile (Level 1)
        if "SingleFile" in options:
            out_path = job_dir / "snapshot.html"
            self.run_singlefile(url, out_path)
            if out_path.exists(): results["formats"].append("HTML")
            
        # 2. Playing + WACZ (Level 2)
        if "WACZ" in options:
            out_path = job_dir / "interactive.wacz"
            self.run_interactive_archiver(url, out_path)
            if out_path.exists(): results["formats"].append("WACZ")
            
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

    def run_interactive_archiver(self, url, out_path):
        self.log(f"🚀 [Level 2] 고 fidelity 아카이빙 시작 (Playwright + WACZ)...")
        try:
            capture_script = CORE_DIR / "wacz_capture.py"
            self.log("ℹ Playwright 엔진 및 브라우저 세션 가동...")
            
            # .venv/bin/python 경로를 명확히 하여 독립성 확보
            venv_python = sys.executable 
            
            result = subprocess.run([venv_python, str(capture_script), url, str(out_path)], 
                                    capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000:
                self.log("✔ Level 2 WACZ 아카이브 완료 (고화질)")
            else:
                self.log(f"⚠ Playwright 캡처 결과물 없음 (코드: {result.returncode}). 상세 로그:\n{result.stdout}\n{result.stderr}")
                self.log("ℹ Browsertrix Crawler 대체 엔진 시도 중...")
                save_dir = out_path.parent / "wacz_tmp"
                save_dir.mkdir(exist_ok=True)
                # Browsertrix Crawler는 npx로 실행
                cmd = ["npx", "-y", "@webrecorder/browsertrix-crawler", "crawl", 
                       "--url", url, "--generateWACZ", "--output", str(save_dir), "--workers", "1"]
                
                alt_result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                wacz_files = list(save_dir.glob("**/*.wacz"))
                if wacz_files:
                    import shutil
                    shutil.move(str(wacz_files[0]), str(out_path))
                    self.log("✔ Level 2 WACZ 아카이브 완료 (Browsertrix)")
                else:
                    self.log(f"❌ Level 2 결국 실패. Browsertrix 로그:\n{alt_result.stderr[-300:]}")
        except Exception as e:
            self.log(f"❌ Level 2 예외 발생: {e}")

    def run_singlefile(self, url, out_path):
        self.log(f"📸 [Level 1] 스냅샷 추출 중 (single-file-cli)...")
        try:
            # single-file-cli 옵션 교정: --browser-wait-until 사용
            cmd = [
                "npx", "-y", "single-file-cli", 
                url, str(out_path), 
                "--browser-args", '["--no-sandbox", "--ignore-certificate-errors", "--disable-web-security"]',
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "--load-deferred-images-dispatch-scroll-event", "true",
                "--browser-wait-until", "networkIdle"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if out_path.exists() and out_path.stat().st_size > 500:
                self.log("✔ Level 1 HTML 스냅샷 저장 완료")
            else:
                self.log(f"❌ Level 1 실패 (코드: {result.returncode}). 로그:\n{result.stdout}\n{result.stderr[-400:]}")
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

