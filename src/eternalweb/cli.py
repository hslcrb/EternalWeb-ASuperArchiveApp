import sys
import argparse
import json
from pathlib import Path
from eternalweb.engine.engine import init_engine, Archiver
from eternalweb.config import get_config

def main():
    parser = argparse.ArgumentParser(description="EternalWeb CLI - Super Archive App")
    parser.add_argument("url", help="아카이브할 대상 URL")
    parser.add_argument("--level", type=int, choices=[1, 2, 3], default=2, help="보존 레벨 (1: SingleFile, 2: WACZ, 3: Full)")
    parser.add_argument("--options", nargs="+", help="상세 검색 옵션 (WACZ, SingleFile, PDF, Screenshot, Media, WARC)")

    args = parser.parse_args()
    
    # 엔진 초기화
    init_engine()
    archiver = Archiver()
    
    # 레벨에 따른 기본 옵션 설정
    options = args.options if args.options else []
    if not options:
        if args.level >= 1: options.append("SingleFile")
        if args.level >= 2: options.append("WACZ")
        if args.level >= 3:
            options.extend(["PDF", "Screenshot", "WARC", "Media"])

    print(f"🚀 EternalWeb CLI 가동 중...")
    print(f"🔗 대상: {args.url}")
    print(f"📊 레벨: Level {args.level}")
    print(f"⚙️ 옵션: {options}")
    
    try:
        results = archiver.archive_url(args.url, options)
        print("\n✨ 아카이빙 완료!")
        print(f"📁 저장 위치: {results['path']}")
        print(f"✅ 생성된 포맷: {', '.join(results['formats'])}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
