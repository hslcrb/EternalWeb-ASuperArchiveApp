# EternalWeb (이터널웹)

EternalWeb은 전설적인 웹 아카이빙 도구인 **ArchiveBox**, **ArchiveWeb.page**, **SingleFile**의 모든 장점을 하나의 강력한 데스크탑 애플리케이션으로 통합한 **초월적 아카이빙 솔루션**입니다.

복잡한 설정 없이, 클릭 한 번으로 웹의 역사를 당신의 컴퓨터에 영구적으로 박제하세요.

![GitHub License](https://img.shields.io/github/license/hslcrb/EternalWeb-ASuperArchiveApp)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

> **⚠️ 프로젝트 상태**: 본 소프트웨어는 현재 **초기 개발 단계 (Pre-Alpha)**입니다. 아직 정식 릴리즈가 이루어지지 않았습니다.
> 
> **🗓️ 최초 클론 및 개발 시작**: 20260120 한국표준시 KST 화요일

---

## 📖 프로젝트 철학 (Philosophy)

EternalWeb은 사라져가는 진실과 기록을 지키는 **디지털 타임캡슐**입니다. 현대의 복잡한 웹(SPA, React 등)을 박제하기 위해 상호보완적인 3단계 엔진을 통합했습니다.

더 자세한 철학과 기술적 배경은 **[사용자 가이드 (KR)](docs/manual/GUIDE_ko.md)** 또는 **[User Guide (EN)](docs/manual/GUIDE.md)**를 참조하세요.

---

## 🛠️ 통합 아키텍처 (Level 1~3 Architecture)

EternalWeb은 사용자의 목적에 따라 세 가지 레벨의 보존 방식을 제공합니다.

1. **Level 1: 신속 보존 (SingleFile)**
   - 개별 웹 페이지를 단 하나의 HTML 파일로 완벽하게 복제하여 개인 소장에 최적화합니다.

2. **Level 2: 상호작용 보존 (ArchiveWeb.page)**
   - 자바스크립트 기반 동적 웹사이트(SPA)의 세션 자체를 기록하여 '살아있는' 아카이브를 만듭니다.

3. **Level 3: 심층 아카이브 (ArchiveBox)**
   - 전체 자산, PDF, 스크린샷 등을 통째로 수집하는 강력한 관제 시스템입니다.

---

## 🚀 주요 기능 (Key Features)

- **현대적인 GUI**: PySide6 기반의 다크 테마 인터페이스로 누구나 쉽게 사용 가능.
- **강력한 CLI**: 서버 환경이나 자동화를 위한 명령줄 인터페이스 제공.
- **표준 포맷 지원**: WACZ, WARC, HAR, PDF, PNG 등 모든 범용 아카이브 포맷 지원.
- **영구 보존**: 모든 데이터는 로컬에 저장되어 외부 서버의 상태와 무관하게 영구 보전됩니다.
- **오픈 소스**: AGPL-3.0 라이선스를 따르는 투명한 무료 소프트웨어.

---

## 📂 프로젝트 구조 (Project Structure)

```
EternalWeb/
│
├── run_eternalweb.py       # GUI 실행 파일
├── eternalweb-cli.py       # CLI 실행 파일
├── requirements.txt        # 필수 라이브러리 목록
├── README.md               # 프로젝트 설명 (본 파일)
├── LICENSE                 # AGPL-3.0 라이선스
│
├── docs/                   # 문서화 (Documentation)
│   ├── licenses/           # 오픈소스 라이선스 고지
│   └── manual/             # 상세 가이드 (GUIDE_ko.md)
│
└── src/                    # 소스 코드 (Source Code)
    └── eternalweb/
        ├── cli.py          # CLI 구현부
        ├── gui/            # GUI 애플리케이션 (PySide6)
        ├── engine/         # 통합 아카이빙 엔진 로직
        └── config.py       # 전역 설정 매니저
```

---

## 🛠️ 설치 및 실행 (Installation & Usage)

### 전제 조건 (Prerequisites)
- **Python 3.8** 이상
- **Node.js** (외부 엔진 구동용)

### 1단계: 프로젝트 클론 및 설치
```bash
git clone https://github.com/hslcrb/EternalWeb-ASuperArchiveApp.git
cd EternalWeb-ASuperArchiveApp
pip install -r requirements.txt
```

### 2단계: 실행 (GUI)
```bash
python run_eternalweb.py
```

### 3단계: 실행 (CLI)
```bash
python eternalweb-cli.py https://example.com --level 2
```
- `--level`: 1 (신속), 2 (상호작용), 3 (심층)
- `--options`: 특정 포맷 지정 (WACZ, PDF, Screenshot, Media 등)

---

## 📜 라이선스 (License)

이 소프트웨어는 **AGPL-3.0** 라이선스 하에 배포됩니다.
EternalWeb에 포함된 각 컴포넌트(ArchiveBox, SingleFile 등)는 각 원작자의 라이선스를 준수하며, `docs/licenses` 디렉토리에서 확인할 수 있습니다.

**개발자: 이호세 (Rhee Hose)**
