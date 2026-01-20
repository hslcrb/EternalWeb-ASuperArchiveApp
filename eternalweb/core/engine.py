
# EternalWeb Core Engine
# Orchestrates ArchiveBox, SingleFile, and ArchiveWeb.page

import os
import sys
import subprocess
from pathlib import Path

# Paths
CORE_DIR = Path(__file__).parent
ARCHIVEBOX_DIR = CORE_DIR / "archivebox"
VENDOR_DIR = CORE_DIR.parent / "vendor"

def init_engine():
    """Initialize the archiving engine and dependencies."""
    print(f"Initializing EternalWeb Engine from {CORE_DIR}")
    # Verify ArchiveBox integration
    try:
        import archivebox
        print(f"ArchiveBox integrated version: {archivebox.__version__ if hasattr(archivebox, '__version__') else 'Unknown'}")
    except ImportError:
        print("CRITICAL: ArchiveBox module not found in core.")

def run_archivebox_command(cmd_list):
    """Run an ArchiveBox CLI command via the integrated module."""
    # This simulates 'archivebox <cmd>'
    from archivebox.cli import main
    # We need to mock sys.argv
    old_argv = sys.argv
    sys.argv = ["archivebox"] + cmd_list
    try:
        main()
    except SystemExit:
        pass
    finally:
        sys.argv = old_argv

def run_singlefile(url, output_path):
    """Run SingleFile CLI to save a page."""
    # Assuming we have a node script entry point in vendor
    # detailed integration requires setting up the node environment
    print(f"SingleFile archiving {url} to {output_path}")
    pass

class Archiver:
    def __init__(self):
        self.active_jobs = []

    def archive_url(self, url, method="archivebox"):
        print(f"Archiving {url} using {method}")
        if method == "archivebox":
            # In a real app, run in background thread
            run_archivebox_command(["add", url])
        elif method == "singlefile":
            run_singlefile(url, "out.html")
