
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

    def archive_url(self, url, method="auto"):
        print(f"Engine Dispatch: {url} -> {method}")
        # Logic to dispatch to components
