import json
import os
from pathlib import Path

# 설정 파일 경로 (사용자 홈 디렉토리 또는 현재 디렉토리)
CONFIG_DIR = Path.home() / ".eternalweb"
CONFIG_FILE = CONFIG_DIR / "settings.json"

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "storage_path": str(Path.home() / "EternalWebArchives"),
    "ui": {
        "theme": "dark",
        "language": "ko"
    },
    "engines": {
        "singlefile": {
            "enabled": True,
            "binary_path": "npx",
            "args": ["ts-node"]
        },
        "webrecorder": {
            "enabled": True,
            "binary_path": "npx",
            "args": ["archiveweb.page"]
        },
        "archivebox": {
            "enabled": True,
            "binary_path": "archivebox"
        }
    },
    "archiving": {
        "default_levels": [1, 2],
        "auto_extract_media": True
    }
}

def get_config():
    """설정을 불러오거나 없을 경우 기본값으로 생성합니다."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✨ 설정 디렉토리 생성됨: {CONFIG_DIR}")

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        print(f"⚙️ 기본 설정 파일이 생성되었습니다: {CONFIG_FILE}")
        return DEFAULT_CONFIG

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 새로운 필드가 추가되었을 수 있으므로 기본값과 병합 (Optional)
            return config
    except Exception as e:
        print(f"⚠ 설정 파일을 읽는 중 오류 발생: {e}. 기본값을 사용합니다.")
        return DEFAULT_CONFIG

def update_config(new_config):
    """설정을 업데이트하고 파일에 저장합니다."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=4, ensure_ascii=False)
    print("✅ 설정이 업데이트되었습니다.")
