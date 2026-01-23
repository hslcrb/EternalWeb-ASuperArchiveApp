
# EternalWeb Core Engine
# Orchestrates ArchiveBox, SingleFile, and ArchiveWeb.page

import os
import sys
import subprocess
from pathlib import Path

# Paths adjustment for new structure
# This file is in src/eternalweb/engine/engine.py
# Components are in src/eternalweb/components/

CORE_DIR = Path(__file__).parent
COMPONENTS_DIR = CORE_DIR.parent / "components"
ARCHIVEBOX_DIR = CORE_DIR / "archivebox" # Moved here earlier

# Legacy Support: Add core dir to sys.path so 'import archivebox' works
sys.path.append(str(CORE_DIR))

def init_engine():
    """Initialize the archiving engine and dependencies."""
    print(f"EternalWeb 엔진 코어 초기화 중...")
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
    def __init__(self):
        self.active_jobs = []

    def archive_url(self, url, options=None):
        if options is None:
            options = ["WACZ", "SingleFile"] # 기본값

        print(f"⚡ [이터널웹] 엔진 가동: {url}")
        print(f"   선택된 수집 옵션: {options}")
        
        # 1. ArchiveWeb.page (Level 2: 대화형/SPA)
        if "WACZ" in options:
            self.run_interactive_archiver(url)
            
        # 2. SingleFile (Level 1: 단일 HTML 스냅샷)
        if "SingleFile" in options:
            self.run_singlefile(url)
            
        # 3. ArchiveBox (Level 3: 심층 아카이빙 및 에셋 추출)
        if any(opt in options for opt in ["WARC", "Media", "PDF", "Screenshot"]):
            extractors = []
            if "WARC" in options: extractors.append("wget")
            if "PDF" in options: extractors.append("pdf")
            if "Media" in options: extractors.append("media")
            if "Screenshot" in options: extractors.append("screenshot")
            
            self.run_archivebox(url, extractors)

    def run_interactive_archiver(self, url):
        """Webrecorder 엔진을 사용하여 상호작용 가능한 WACZ 파일 생성"""
        print(f"🚀 [Level 2] {url}의 대화형 기록 시작...")
        # 실제 명령: npx archiveweb.page record [url] --output [path]
        cmd = ["npx", "archiveweb.page", "record", url]
        # 실시간 로그는 GUI 콘솔로 전달될 예정
        # subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def run_singlefile(self, url):
        """SingleFile 엔진을 사용하여 고해상도 단일 HTML 저장"""
        print(f"📸 [Level 1] {url}을 단일 HTML로 압축 암호화 중...")
        cli_path = COMPONENTS_DIR / "singlefile" / "cli.ts"
        # 실제 명령: ts-node [cli_path] [url] [output]
        cmd = ["npx", "ts-node", str(cli_path), url]
        # subprocess.Popen(cmd)

    def run_archivebox(self, url, extractors):
        """ArchiveBox 엔진을 사용하여 표준 WARC 및 미디어 자산 아카이빙"""
        print(f"📦 [Level 3] {url}에 대한 심층 수집 수행 중 (추출기: {extractors})...")
        # ArchiveBox CLI를 호출하여 데이터베이스에 추가 및 아카이빙
        # cmd = ["archivebox", "add", url, f"--extract={','.join(extractors)}"]
        # subprocess.Popen(cmd)

