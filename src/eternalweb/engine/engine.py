
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
        self.log_fn(f"🚀 [Level 2] {url} 기록 시작...")
        # archiveweb.page는 npx로 실행하는 것이 가장 안정적입니다.
        try:
            subprocess.run(["npx", "-y", "archiveweb.page", "record", url, "--output", str(out_path)], check=False)
        except Exception as e:
            self.log_fn(f"❌ Webrecorder 오류: {e}")

    def run_singlefile(self, url, out_path):
        self.log_fn(f"📸 [Level 1] {url} 스냅샷 추출 중...")
        try:
            # single-file-cli 사용
            subprocess.run(["npx", "-y", "single-file-cli", url, str(out_path)], check=False)
        except Exception as e:
            self.log_fn(f"❌ SingleFile 오류: {e}")

    def run_archivebox(self, url, options, job_dir):
        self.log_fn(f"📦 [Level 3] ArchiveBox 엔진 가동 중...")
        extractors = []
        if "WARC" in options: extractors.append("wget")
        if "PDF" in options: extractors.append("pdf")
        if "Media" in options: extractors.append("media")
        if "Screenshot" in options: extractors.append("screenshot")
        
        # ArchiveBox CLI 또는 통합 모듈 호출
        # 현재는 독립 실행 환경 구축을 위해 subprocess 권장
        os.environ["OUTPUT_DIR"] = str(job_dir)
        try:
            subprocess.run(["archivebox", "add", url, f"--extract={','.join(extractors)}"], cwd=job_dir, check=False)
        except Exception as e:
            self.log_fn(f"❌ ArchiveBox 오류: {e}")

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

