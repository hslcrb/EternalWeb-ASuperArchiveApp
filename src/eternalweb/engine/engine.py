
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

def init_engine():
    """Initialize the archiving engine and dependencies."""
    print(f"Initializing EternalWeb Engine Core...")
    print(f"Components Path: {COMPONENTS_DIR}")
    
    # Check Components
    if (COMPONENTS_DIR / "singlefile").exists():
        print("✔ Component Loaded: SingleFile (High Fidelity)")
    else:
        print("✘ Component Missing: SingleFile")

    if (COMPONENTS_DIR / "webpage").exists():
        print("✔ Component Loaded: ArchiveWeb.page (Interactive)")
    else:
        print("✘ Component Missing: ArchiveWeb.page")

    # Verify ArchiveBox
    try:
        # Since we moved archivebox to src/eternalweb/engine/archivebox,
        # we need to make sure it's importable.
        # It's a subdirectory here, so it should be fine if __init__.py exists.
        from . import archivebox
        print(f"✔ Core Loaded: ArchiveBox Legacy Engine")
    except ImportError as e:
        print(f"⚠ ArchiveBox Import Issue: {e}")

class Archiver:
    def __init__(self):
        self.active_jobs = []

    def archive_url(self, url, options=None):
        if options is None:
            options = ["WACZ", "SingleFile"] # Defaults

        print(f"⚡ Engine Dispatch: {url}")
        print(f"   Options: {options}")
        
        # 1. ArchiveWeb.page (WACZ) - Best for SPA/Dynamic
        if "WACZ" in options:
            self.run_interactive_archiver(url)
            
        # 2. SingleFile - Best for DOM Snapshot
        if "SingleFile" in options:
            self.run_singlefile(url)
            
        # 3. ArchiveBox - Best for Static/Assets/PDF
        if "WARC" in options or "Media" in options or "PDF" in options:
            extractors = []
            if "WARC" in options: extractors.append("wget")
            if "PDF" in options: extractors.append("pdf")
            if "Media" in options: extractors.append("media")
            if "Screenshot" in options: extractors.append("screenshot")
            
            self.run_archivebox(url, extractors)

    def run_interactive_archiver(self, url):
        # Requires aw-page CLI or embedding
        print(f"[ArchiveWeb] Capturing interactive session for {url} (WACZ)...")
        # subprocess.run(["npx", "archiveweb.page", "record", url, ...]) 
        # Placeholder for actual command execution logic
        
    def run_singlefile(self, url):
        # Requires Node.js
        print(f"[SingleFile] Freezing DOM state for {url}...")
        # out_path = ...
        # subprocess.run(["./src/eternalweb/components/singlefile/cli.js", url, ...])
        
    def run_archivebox(self, url, extractors):
        print(f"[ArchiveBox] Deep archiving {url} with {extractors}...")
        try:
            from .archivebox.cli import main
            # In-process call might need environment setup, or better use subprocess for isolation
            # subprocess.run(["archivebox", "add", url, "--extract=" + ",".join(extractors)])
        except ImportError:
            print("ArchiveBox module not loaded.")
