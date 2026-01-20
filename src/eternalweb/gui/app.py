
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QStackedWidget, QListWidget, QListWidgetItem, QFrame
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QAction
from PySide6.QtCore import Qt, QSize

# Adjusted Imports for new structure
try:
    from ..engine.engine import init_engine, Archiver
except ImportError:
    init_engine = None
    Archiver = None

class ModernNavBar(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1a1a1a;
                border: none;
                outline: none;
            }
            QListWidget::item {
                color: #a0a0a0;
                padding: 15px;
                font-size: 14px;
                border-left: 3px solid transparent;
            }
            QListWidget::item:selected {
                color: #ffffff;
                background-color: #252525;
                border-left: 3px solid #00bbff;
            }
            QListWidget::item:hover {
                background-color: #222;
            }
        """)
        self.add_nav_item("대시보드 / Dashboard", "dashboard")
        self.add_nav_item("새 아카이브 / New", "add_box")
        self.add_nav_item("라이브러리 / Library", "library_books")
        self.add_nav_item("설정 / Settings", "settings")

    def add_nav_item(self, text, icon_name):
        item = QListWidgetItem(text)
        item.setSizeHint(QSize(0, 50))
        self.addItem(item)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        title = QLabel("EternalWeb Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff;")
        
        stat_frame = QFrame()
        stat_frame.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 20px;")
        stat_layout = QHBoxLayout(stat_frame)
        
        self.stat_total = QLabel("Total Archives: 0")
        self.stat_engine = QLabel("Engines: Ready")
        self.stat_total.setStyleSheet("font-size: 18px; color: #00bbff;")
        self.stat_engine.setStyleSheet("font-size: 18px; color: #ffcc00;")
        
        stat_layout.addWidget(self.stat_total)
        stat_layout.addStretch()
        stat_layout.addWidget(self.stat_engine)
        
        info = QLabel("통합 웹 아카이빙 시스템에 오신 것을 환영합니다.\nEternalWeb은 ArchiveBox, ArchiveWeb.page, SingleFile을 통합하여 영구적인 보존을 지원합니다.")
        info.setStyleSheet("color: #aaa; margin-top: 20px; font-size: 14px; line-height: 1.5;")
        
        layout.addWidget(title)
        layout.addWidget(stat_frame)
        layout.addWidget(info)
        layout.addStretch()
        self.setLayout(layout)

class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        title = QLabel("웹페이지 아카이빙 / Archive Page")
        title.setStyleSheet("font-size: 24px; color: #fff; margin-bottom: 20px;")
        
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 20px;")
        input_layout = QVBoxLayout(input_container)
        
        lbl_url = QLabel("Target URL")
        lbl_url.setStyleSheet("color: #ddd; font-weight: bold;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/page-to-save")
        self.url_input.setStyleSheet("padding: 10px; border: 1px solid #444; border-radius: 4px; background: #1a1a1a; color: white;")
        
        btn_layout = QHBoxLayout()
        self.btn_archive = QPushButton("아카이빙 시작 (Start)")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setStyleSheet("""
            QPushButton {
                background-color: #0077cc;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #0088dd; }
            QPushButton:pressed { background-color: #0066aa; }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_archive)
        
        input_layout.addWidget(lbl_url)
        input_layout.addWidget(self.url_input)
        input_layout.addLayout(btn_layout)
        
        self.log_output = QLabel("대기 중...")
        self.log_output.setStyleSheet("color: #666; margin-top: 10px;")
        
        layout.addWidget(title)
        layout.addWidget(input_container)
        layout.addWidget(self.log_output)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_archive.clicked.connect(self.start_archive)

    def start_archive(self):
        url = self.url_input.text()
        if not url:
            self.log_output.setText("URL을 입력해주세요.")
            self.log_output.setStyleSheet("color: #ff5555; margin-top: 10px;")
            return
            
        self.log_output.setText(f"작업 큐에 추가됨: {url}")
        self.log_output.setStyleSheet("color: #00cc00; margin-top: 10px;")

class EternalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EternalWeb - Super Archive App")
        self.resize(1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.navbar = ModernNavBar()
        self.navbar.currentRowChanged.connect(self.change_page)
        
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background-color: #121212;")
        
        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(ArchivePage())
        self.pages.addWidget(QLabel("Library (준비 중)", alignment=Qt.AlignCenter))
        self.pages.addWidget(QLabel("Settings (준비 중)", alignment=Qt.AlignCenter))
        
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.pages)
        
        self.navbar.setCurrentRow(0)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)

def set_dark_theme(app):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(18, 18, 18))
    palette.setColor(QPalette.AlternateBase, QColor(26, 26, 26))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(26, 26, 26))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

def main():
    if init_engine:
        init_engine()
        
    app = QApplication(sys.argv)
    set_dark_theme(app)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = EternalWindow()
    window.show()
    
    sys.exit(app.exec())
