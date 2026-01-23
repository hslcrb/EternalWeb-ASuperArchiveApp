
# EternalWeb Core Engine
# Orchestrates ArchiveBox, SingleFile, and ArchiveWeb.page

import os
import sys
import subprocess
import json
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
        timestamp = Path(os.popen("date +%Y%m%d_%H%M%S").read().strip()).name
        job_dir = storage_path / f"{timestamp}_{archive_id}"
        job_dir.mkdir(parents=True, exist_ok=True)
 
        self.log_fn(f"⚡ [이터널웹] 엔진 가동: {url}")
        self.log_fn(f"📂 저장 경로: {job_dir}")
        
        results = {"url": url, "timestamp": timestamp, "path": str(job_dir), "formats": []}

        # 1. Level 1: SingleFile
        if "SingleFile" in options:
            out_file = job_dir / "snapshot.html"
            self.run_singlefile(url, out_file)
            results["formats"].append("HTML")

        # 2. Level 2: ArchiveWeb.page (WACZ)
        if "WACZ" in options:
            out_wacz = job_dir / "interactive.wacz"
            self.run_interactive_archiver(url, out_wacz)
            results["formats"].append("WACZ")

        # 3. Level 3: ArchiveBox
        if any(opt in options for opt in ["WARC", "Media", "PDF", "Screenshot"]):
            self.run_archivebox(url, options, job_dir)
            results["formats"].append("ArchiveBox")

        self.save_to_library(results)
        return results

    def run_interactive_archiver(self, url, out_path):
        self.log_fn(f"🚀 [Level 2] 고 fidelity 아카이빙 시작 (Playwright + WACZ)...")
        try:
            # src/eternalweb/engine/wacz_capture.py 스크립트 위치 확인
            capture_script = CORE_DIR / "wacz_capture.py"
            
            # Playwright 브라우저가 설치되어 있는지 확인 (자동 설치 시도 생략하고 실행)
            # .venv/bin/python 을 사용하여 동일한 환경에서 실행
            self.log_fn("ℹ Playwright 엔진 및 브라우저 세션 가동...")
            
            result = subprocess.run([sys.executable, str(capture_script), url, str(out_path)], 
                                    capture_output=True, text=True, check=False)
            
            if out_path.exists() and out_path.stat().st_size > 1000:
                self.log_fn("✔ Level 2 WACZ 아카이브 완료 (고화질)")
            else:
                self.log_fn("ℹ Browsertrix Crawler 대체 엔진 시도 중...")
                # Fallback to browsertrix-crawler if Playwright fails
                save_dir = out_path.parent / "wacz_tmp"
                save_dir.mkdir(exist_ok=True)
                cmd = ["npx", "-y", "@webrecorder/browsertrix-crawler", "crawl", 
                       "--url", url, "--generateWACZ", "--output", str(save_dir), "--workers", "1"]
                
                alt_result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                wacz_files = list(save_dir.glob("**/*.wacz"))
                if wacz_files:
                    import shutil
                    shutil.move(str(wacz_files[0]), str(out_path))
                    self.log_fn("✔ Level 2 WACZ 아카이브 완료 (Browsertrix)")
                else:
                    self.log_fn(f"❌ Level 2 실패: {result.stderr[-200:]}")
        except Exception as e:
            self.log_fn(f"❌ Level 2 예외: {e}")

    def run_singlefile(self, url, out_path):
        self.log_fn(f"📸 [Level 1] 스냅샷 추출 중 (single-file-cli)...")
        try:
            # single-file-cli 실행
            # Warning 메시지(stdout/stderr)에 상관없이 파일이 생성되면 성공으로 판단
            result = subprocess.run(["npx", "-y", "single-file-cli", url, str(out_path), "--browser-args", '["--no-sandbox"]'], 
                                    capture_output=True, text=True, check=False)
            
            if out_path.exists() and out_path.stat().st_size > 1000:
                self.log_fn("✔ Level 1 HTML 스냅샷 저장 완료")
            else:
                # 에러 메시지가 너무 길면 마지막 부분만 출력
                err = result.stderr[-200:] if result.stderr else "알 수 없는 오류"
                self.log_fn(f"❌ Level 1 실패: {err}")
        except Exception as e:
            self.log_fn(f"❌ SingleFile 예외: {e}")

    def run_archivebox(self, url, options, job_dir):
        self.log_fn(f"📦 [Level 3] 내장 ArchiveBox 엔진 가동 중...")
        extractors = []
        if "WARC" in options: extractors.append("wget")
        if "PDF" in options: extractors.append("pdf")
        if "Media" in options: extractors.append("media")
        if "Screenshot" in options: extractors.append("screenshot")
        
        try:
            # CORE_DIR는 src/eternalweb/engine 임.
            # 이 디렉토리가 PYTHONPATH에 있어야 'import archivebox'가 가능함.
            engine_root = str(CORE_DIR.resolve())
            
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{engine_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
            
            # 1. 초기화
            init_res = subprocess.run([sys.executable, "-m", "archivebox", "init", "--force"], 
                                      cwd=job_dir, env=env, capture_output=True, text=True, check=False)
            
            if not (job_dir / "index.sqlite3").exists():
                self.log_fn(f"⚠ Level 3 초기화 실패: {init_res.stderr[-200:]}")
                return
            
            # 2. 추가 및 추출
            cmd = [sys.executable, "-m", "archivebox", "add", url]
            if extractors:
                cmd.append(f"--extract={','.join(extractors)}")
            
            result = subprocess.run(cmd, cwd=job_dir, env=env, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                self.log_fn(f"❌ Level 3 실패: {result.stderr[-200:]}")
            else:
                self.log_fn("✔ Level 3 심층 아카이브 완료")
        except Exception as e:
            self.log_fn(f"❌ ArchiveBox 예외: {e}")

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

