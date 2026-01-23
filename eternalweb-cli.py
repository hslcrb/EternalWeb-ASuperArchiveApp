#!/usr/bin/env python3
import sys
import os

# src 디렉토리를 path에 추가하여 내부 모듈 임포트 가능하게 함
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from eternalweb.cli import main

if __name__ == "__main__":
    main()
