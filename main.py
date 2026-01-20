
import sys
import os
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit
from PyQt6.QtCore import Qt, QTimer

# 1. Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR) # Allow importing eternalweb
sys.path.append(os.path.join(BASE_DIR, 'eternalweb', 'core')) # Allow importing archivebox legacy

# 2. Configure Django Environment (Essential for ArchiveBox)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "archivebox.core.settings")

# 3. Import Core
# We import inside main or try block to handle missing deps
try:
    from eternalweb.core.engine import init_engine, Archiver
except ImportError as e:
    print(f"Setup Error: {e}")
    init_engine = None

class EternalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EternalWeb - Integrated Archiving Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        self.archiver = Archiver() if init_engine else None
        
        # UI
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.setup_styles()
        self.create_dashboard()
        self.create_capture_ui()
        self.create_console()

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            QTabWidget::pane { border: 1px solid #333; }
            QTabBar::tab { background: #2a2a2a; color: #aaa; padding: 12px 20px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background: #3a3a3a; color: #ffffff; border-bottom: 2px solid #00bbff; }
            QLineEdit { padding: 8px; border-radius: 4px; border: 1px solid #444; background: #252525; color: white; }
            QPushButton { padding: 8px 16px; border-radius: 4px; background: #0077cc; color: white; border: none; }
            QPushButton:hover { background: #0088dd; }
            QTextEdit { background: #111; color: #0f0; font-family: monospace; border: 1px solid #333; }
        """)

    def create_dashboard(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("EternalWeb")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #00bbff;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("The Super Archive App")
        subtitle.setStyleSheet("font-size: 16px; color: #888;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Dashboard")

    def create_capture_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        input_layout = QVBoxLayout()
        lbl = QLabel("Target URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        
        btn = QPushButton("Archive Now")
        btn.clicked.connect(self.start_archive)
        
        input_layout.addWidget(lbl)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(btn)
        
        layout.addLayout(input_layout)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Capture")

    def create_console(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.console_out = QTextEdit()
        self.console_out.setReadOnly(True)
        layout.addWidget(self.console_out)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Log")

    def log(self, text):
        self.console_out.append(text)

    def start_archive(self):
        url = self.url_input.text()
        if not url:
            self.log("Error: No URL provided")
            return
            
        self.log(f"Starting archive for: {url}")
        
        # Run in thread to not freeze UI
        t = threading.Thread(target=self._run_archive_thread, args=(url,))
        t.start()
        
    def _run_archive_thread(self, url):
        # This is a demo integration
        try:
            if self.archiver:
                self.archiver.archive_url(url)
                # We can't update GUI directly from thread in strict Qt, but append is usually safe-ish or use signals.
                # For safety/simple demo:
                print(f"Archived {url}")
        except Exception as e:
            print(f"Archive failed: {e}")

def main():
    if init_engine:
        init_engine()
    
    # Init Django
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"Django Setup Warning: {e}")

    app = QApplication(sys.argv)
    window = EternalWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
