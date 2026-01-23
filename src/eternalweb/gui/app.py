
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QStackedWidget, QListWidget, 
    QListWidgetItem, QFrame, QCheckBox, QGroupBox, QGridLayout
)
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QAction
from PySide6.QtCore import Qt, QSize
import json
from ..config import get_config, update_config

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
        self.add_nav_item("대시보드 (Dashboard)", "dashboard")
        self.add_nav_item("새 아카이브 (New Archive)", "add_box")
        self.add_nav_item("라이브러리 (Library)", "library_books")
        self.add_nav_item("설정 (Settings)", "settings")

    def add_nav_item(self, text, icon_name):
        item = QListWidgetItem(text)
        item.setSizeHint(QSize(0, 50))
        self.addItem(item)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel("EternalWeb 대시보드")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #fff;")
        
        stat_frame = QFrame()
        stat_frame.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 20px;")
        stat_layout = QHBoxLayout(stat_frame)
        
        self.stat_total = QLabel("총 아카이브: -")
        self.stat_engine = QLabel("엔진 상태: 준비됨")
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
        self.refresh_stats()

    def refresh_stats(self):
        index_file = Path(self.config['storage_path']) / "index.json"
        count = 0
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                count = len(data)
        self.stat_total.setText(f"총 아카이브: {count}")

class LibraryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        layout = QVBoxLayout()
        
        title = QLabel("아카이브 라이브러리 (Library)")
        title.setStyleSheet("font-size: 24px; color: #fff; margin-bottom: 5px;")
        layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #1a1a1a; border: 1px solid #333; border-radius: 4px; color: #eee; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #222; }
            QListWidget::item:selected { background-color: #333; color: #00bbff; }
        """)
        layout.addWidget(self.list_widget)
        
        self.btn_refresh = QPushButton("새로고침 (Refresh)")
        self.btn_refresh.clicked.connect(self.load_library)
        layout.addWidget(self.btn_refresh)
        
        self.setLayout(layout)
        self.load_library()

    def load_library(self):
        self.list_widget.clear()
        index_file = Path(self.config['storage_path']) / "index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in reversed(data):
                    display_text = f"[{item['timestamp']}] {item['url']}\n형식: {', '.join(item['formats'])}"
                    list_item = QListWidgetItem(display_text)
                    self.list_widget.addItem(list_item)

class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("웹페이지 아카이빙 / Archive Page")
        title.setStyleSheet("font-size: 24px; color: #fff; margin-bottom: 5px;")
        subtitle = QLabel("모든 유형의 웹사이트(SPA, React, 동적 웹)를 원본 그대로 영구 박제합니다.")
        subtitle.setStyleSheet("color: #aaa; font-size: 14px; margin-bottom: 20px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        # Input Container
        input_container = QFrame()
        input_container.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 20px;")
        input_layout = QVBoxLayout(input_container)
        
        # URL Input
        lbl_url = QLabel("대상 URL (Target URL)")
        lbl_url.setStyleSheet("color: #ddd; font-weight: bold;")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/저장할-페이지")
        self.url_input.setStyleSheet("padding: 10px; border: 1px solid #444; border-radius: 4px; background: #1a1a1a; color: white; font-size: 14px;")

        # Options Grid
        opts_lbl = QLabel("보존 강도 및 형식 (EternalWeb Levels)")
        opts_lbl.setStyleSheet("color: #00bbff; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")
        
        opts_container = QFrame()
        opts_layout = QHBoxLayout(opts_container)
        opts_layout.setContentsMargins(0, 0, 0, 0)

        # Level 1: SingleFile
        lv1_box = QGroupBox("Level 1: 신속 (Light)")
        lv1_box.setStyleSheet("QGroupBox { color: #00ff88; font-weight: bold; border: 1px solid #333; border-radius: 5px; margin-top: 10px; padding-top: 5px; }")
        lv1_layout = QVBoxLayout(lv1_box)
        self.chk_singlefile = QCheckBox("SingleFile HTML")
        self.chk_singlefile.setChecked(True)
        lv1_layout.addWidget(self.chk_singlefile)
        lv1_layout.addWidget(QLabel("단일 파일 완벽 보존", styleSheet="color: #666; font-size: 11px;"))

        # Level 2: Interactive
        lv2_box = QGroupBox("Level 2: 상호작용 (Interactive)")
        lv2_box.setStyleSheet("QGroupBox { color: #00bbff; font-weight: bold; border: 1px solid #333; border-radius: 5px; margin-top: 10px; padding-top: 5px; }")
        lv2_layout = QVBoxLayout(lv2_box)
        self.chk_wacz = QCheckBox("WACZ (SPA/동적)")
        self.chk_wacz.setChecked(True)
        lv2_layout.addWidget(self.chk_wacz)
        lv2_layout.addWidget(QLabel("React, 동적 웹 박제", styleSheet="color: #666; font-size: 11px;"))

        # Level 3: Deep
        lv3_box = QGroupBox("Level 3: 심층 (Deep)")
        lv3_box.setStyleSheet("QGroupBox { color: #ffcc00; font-weight: bold; border: 1px solid #333; border-radius: 5px; margin-top: 10px; padding-top: 5px; }")
        lv3_layout = QVBoxLayout(lv3_box)
        self.chk_warc = QCheckBox("WARC/Media")
        self.chk_pdf = QCheckBox("PDF 문서")
        self.chk_screenshot = QCheckBox("전체 스냅샷")
        lv3_layout.addWidget(self.chk_warc)
        lv3_layout.addWidget(self.chk_pdf)
        lv3_layout.addWidget(self.chk_screenshot)

        opts_layout.addWidget(lv1_box)
        opts_layout.addWidget(lv2_box)
        opts_layout.addWidget(lv3_box)


        # Action Button
        btn_layout = QHBoxLayout()
        self.btn_archive = QPushButton("아카이빙 시작 (Start Processing)")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setStyleSheet("""
            QPushButton {
                background-color: #0077cc;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                border: none;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #0088dd; }
            QPushButton:pressed { background-color: #0066aa; }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_archive)
        
        input_layout.addWidget(lbl_url)
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(opts_lbl)
        input_layout.addWidget(opts_container)
        input_layout.addLayout(btn_layout)
        
        # Log Output
        self.log_output = QLabel("시스템 대기 중... URL을 입력하세요.")
        self.log_output.setStyleSheet("color: #666; margin-top: 15px; font-family: monospace;")
        self.log_output.setWordWrap(True)
        
        layout.addLayout(header_layout)
        layout.addWidget(input_container)
        layout.addWidget(self.log_output)
        layout.addStretch()
        self.setLayout(layout)

        self.btn_archive.clicked.connect(self.start_archive)

    def start_archive(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_output.setText("⚠ URL을 입력해주세요.")
            self.log_output.setStyleSheet("color: #ff5555; margin-top: 15px; font-family: monospace;")
            return
            
        selected_modes = []
        if self.chk_wacz.isChecked(): selected_modes.append("WACZ")
        if self.chk_singlefile.isChecked(): selected_modes.append("SingleFile")
        if self.chk_pdf.isChecked(): selected_modes.append("PDF")
        if self.chk_screenshot.isChecked(): selected_modes.append("Screenshot")
        if self.chk_warc.isChecked(): selected_modes.append("WARC")
        if self.chk_media.isChecked(): selected_modes.append("Media")
        
        mode_str = ", ".join(selected_modes)
        self.log_output.setText(f"🚀 작업 시작됨: {url}\n[모드]: {mode_str}\n(백그라운드 엔진 가동 중... 잠시만 기다려주세요.)")
        self.log_output.setStyleSheet("color: #00ff88; margin-top: 15px; font-family: monospace;")
        
        # 필수 리프레시를 위해 이벤트 루프 처리
        QApplication.processEvents()

        # 실제 엔진 호출
        if Archiver:
            try:
                archiver = Archiver()
                archiver.archive_url(url, selected_modes)
                self.log_output.append("\n✅ 아카이빙이 성공적으로 완료되었습니다!")
            except Exception as e:
                self.log_output.append(f"\n❌ 오류 발생: {e}")
        else:
            self.log_output.append("\n❌ 엔진이 로드되지 않았습니다.")

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        layout = QVBoxLayout()
        
        title = QLabel("통합 설정 (Unified Settings)")
        title.setStyleSheet("font-size: 24px; color: #fff; margin-bottom: 5px;")
        desc = QLabel("EternalWeb의 핵심 동작 설정을 JSON 형태로 직접 관리합니다.")
        desc.setStyleSheet("color: #aaa; margin-bottom: 20px;")
        layout.addWidget(title)
        layout.addWidget(desc)
        
        from PySide6.QtWidgets import QTextEdit
        self.json_editor = QTextEdit()
        self.json_editor.setPlainText(json.dumps(self.config, indent=4, ensure_ascii=False))
        self.json_editor.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff88;
                font-family: 'Consolas', 'Monaco', monospace;
                border: 1px solid #333;
                border-radius: 4px;
                font-size: 13px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.json_editor)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("설정 저장 및 적용 (Save)")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #444; }
        """)
        self.btn_save.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)
        
        self.status_lbl = QLabel("")
        layout.addWidget(self.status_lbl)
        
        self.setLayout(layout)

    def save_settings(self):
        try:
            new_text = self.json_editor.toPlainText()
            new_config = json.loads(new_text)
            update_config(new_config)
            self.status_lbl.setText("✅ 설정이 성공적으로 저장되었습니다.")
            self.status_lbl.setStyleSheet("color: #00ff88;")
        except Exception as e:
            self.status_lbl.setText(f"❌ 오류: 유효하지 않은 JSON 형식입니다. ({e})")
            self.status_lbl.setStyleSheet("color: #ff5555;")

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
        
        self.dashboard = DashboardPage()
        self.archive_page = ArchivePage()
        self.library = LibraryPage()
        self.settings = SettingsPage()

        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.archive_page)
        self.pages.addWidget(self.library)
        self.pages.addWidget(self.settings)
        
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.pages)
        
        self.navbar.setCurrentRow(0)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)
        if index == 0:
            self.dashboard.refresh_stats()
        elif index == 2:
            self.library.load_library()

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
