# EternalWeb (이터널웹)

EternalWeb은 전설적인 웹 아카이빙 도구인 **ArchiveBox**, **ArchiveWeb.page**, **SingleFile**의 모든 장점을 하나의 강력한 데스크탑 애플리케이션으로 통합한 **초월적 아카이빙 솔루션**입니다.

복잡한 설정 없이, 클릭 한 번으로 웹의 역사를 당신의 컴퓨터에 영구적으로 박제하세요.

![GitHub License](https://img.shields.io/github/license/hslcrb/EternalWeb-ASuperArchiveApp)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

## 🚀 주요 기능 (Key Features)

### 1. 통합 아카이빙 엔진 (Unified Engine)
EternalWeb은 다음과 같은 강력한 엔진들을 내부 부품(Components)으로 탑재하여 상황에 맞는 최적의 보존 방식을 제공합니다.

- **ArchiveBox Core**: 강력한 백엔드 아카이빙 관리. HTML, PDF, 스크린샷 등 다양한 포맷 동시 저장.
- **High-Fidelity Mode (SingleFile)**: 페이지를 단 하나의 HTML 파일로 완벽하게 압축 저장.
- **Interactive Mode (ArchiveWeb.page)**: 단순 스크린샷이 아닌, 클릭하고 스크롤할 수 있는 '살아있는' 웹페이지를 보존 (WARC).

### 2. 현대적인 GUI (Modern GUI)
- **PySide6** 기반의 세련된 다크 테마 인터페이스.
- 터미널 명령어를 몰라도 누구나 쉽게 사용 가능.
- 실시간 대시보드 및 작업 큐 시각화.

### 3. 영구 보존 (Permanent Preservation)
- 모든 데이터는 로컬 스토리지에 저장되어 인터넷이 끊겨도 언제든 열람 가능.
- 표준 포맷(WARC, HTML, PDF) 준수로 높은 호환성 보장.

## 📂 프로젝트 구조 (Project Structure)

이 프로젝트는 더 이상 단순한 저장소의 집합이 아닙니다. 모든 코드는 `src` 내부로 통합되어 체계적으로 관리됩니다.

```
EternalWeb/
│
├── run_eternalweb.py       # 애플리케이션 실행 파일 (Entry Point)
├── requirements.txt        # 필수 라이브러리 목록
├── README.md               # 프로젝트 설명 (본 파일)
├── LICENSE                 # AGPL-3.0 라이선스
│
├── docs/                   # 문서화 (Documentation)
│   ├── licenses/           # 오픈소스 라이선스 고지
│   └── manual/             # 사용자 매뉴얼
│
└── src/                    # 소스 코드 (Source Code)
    └── eternalweb/
        ├── gui/            # GUI 애플리케이션 (PySide6)
        ├── engine/         # 통합 아카이빙 엔진 로직
        │   └── archivebox/ # [Core] ArchiveBox 백엔드 로직
        └── components/     # 외부 엔진 구성요소
            ├── singlefile/ # [Component] SingleFile CLI/Lib
            └── webpage/    # [Component] ArchiveWeb.page Tools
```

## 🛠️ 설치 및 실행 (Installation & Usage)

### 전제 조건 (Prerequisites)
- **Python 3.8** 이상
- **Node.js** (SingleFile 및 일부 컴포넌트 구동용)
- **Git**

### 1단계: 프로젝트 클론
```bash
git clone https://github.com/hslcrb/EternalWeb-ASuperArchiveApp.git
cd EternalWeb-ASuperArchiveApp
```

### 2단계: 의존성 설치
```bash
pip install -r requirements.txt
```

### 3단계: 실행
```bash
python run_eternalweb.py
```
앱이 실행되면 대시보드에서 아카이브할 URL을 입력하고 **'아카이빙 시작'** 버튼을 누르세요.

## 🤝 기여 (Contributing)
EternalWeb은 오픈 소스 프로젝트입니다. 버그 제보, 기능 제안, PR은 언제나 환영합니다.
모든 기여는 AGPL-3.0 라이선스 하에 배포되어야 합니다.

## 📜 라이선스 (License)
이 소프트웨어는 **AGPL-3.0** 라이선스 하에 배포됩니다.
EternalWeb에 포함된 각 컴포넌트(ArchiveBox, SingleFile 등)는 각 원작자의 라이선스를 준수하며, `docs/licenses` 디렉토리에서 확인할 수 있습니다.
