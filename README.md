# 📂 Subculture Media Manager & Launcher (서브컬처 미디어 매니저 & 런처)

[![GitHub Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/dedexperiment1/Subculture-Media-Manager/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://www.python.org/)

로컬 디스크에 보관된 대용량 만화(동인지, 단행본, 웹툰)와 동영상을 **지능적으로 정리**하고, **최적의 뷰어 및 영상 플레이어로 편리하게 무작위 감상**할 수 있는 올인원 오픈소스 데스크탑 유틸리티입니다.

---

## 🌟 주요 기능 (Key Features)

### 1. 🎲 스마트 랜덤 미디어 런처 (Smart Random Launcher)
* **원클릭 & 전역 단축키**:
  * **만화 열기**: 기본 `F8` (F1~F12 자유 변경 지원)
  * **영상 열기**: 기본 `F7` (F1~F12 자유 변경 지원)
* **단일 인스턴스 연동**: 팟플레이어 및 반디뷰/꿀뷰의 기존 창에서 즉시 다음 파일로 교체 감상
* **대용량 드라이브 0.01초 초고속 로딩**: 인덱스 캐싱(`media_cache.json`)으로 재실행 지연 시간 제로
* **히스토리 지원**: 최근 감상 목록 더블클릭 다시 열기 및 탐색기 위치 열기 원클릭 지원

### 2. 📁 작가/서클/시리즈 스마트 자동 정리기 (Smart Author & Series Organizer)
* **모든 파일 형식 지원**: 압축파일(`.zip`, `.cbz` 등)뿐만 아니라 이미지, 영상 등 폴더 내 모든 파일 지원
* **위치 기반 괄호 분석 (Positional Bracket Tokenizer)**:
  * 초반 1~2번째 괄호 위치를 정밀 분석하여, 뒤쪽의 원작 장르명(`(Fate...)` 등)이나 언어 태그(`[Korean]`)를 작가명으로 오인하지 않음
* **단행본 권수·숫자 무시 및 시리즈 단일 폴더 통합**:
  * `공포학교01` ~ `공포학교15완결` $\rightarrow$ `공포학교` 단일 폴더로 자동 통합
  * `HyperPolice01` ~ `10` $\rightarrow$ `HyperPolice` 단일 폴더로 통합
  * `エイリアン9 01` ~ `03권` $\rightarrow$ 고유 숫자 9는 보존하고 권수만 분리하여 `エイリアン9` 단일 폴더로 통합
* **스마트 충돌 해결 & 안전 삭제**:
  * 동일 작품의 신규 판본(`(c24) aaa (2)`)이 들어올 경우 최신본을 유지하고 구버전은 **Windows 휴지통(Recycle Bin)**으로 안전 이동
* **파일명 100% 원본 보존**: 파일명을 일체 임의 수정하지 않고 원본 그대로 안전 분류

### 3. 🌐 다국어 지원 & 안전성 (i18n & Security)
* **3개 국어 실시간 전환**: 한국어(기본), 日本語, English
* **100% 오프라인 동작**: 외부 네트워크 통신이 전혀 없어 개인정보 및 소장 파일 목록 유출 위험 제로
* **클린 가상머신 빌드**: GitHub Actions 클라우드 환경에서 깨끗하게 소스코드를 컴파일하여 배포

---

## 🚀 다운로드 및 실행 방법 (Download & Run)

### 일반 사용자 (무설치 단일 파일)
1. 우측 상단의 **[Releases](https://github.com/dedexperiment1/Subculture-Media-Manager/releases)** 탭으로 이동합니다.
2. 최신 버전의 **`RandomMediaOpener.exe`**를 다운로드합니다.
3. 파이썬이나 별도 프로그램 설치 없이 더블 클릭하여 바로 실행합니다.

### 소스코드에서 직접 실행 (개발자용)
```bash
# 1. 저장소 클론
git clone https://github.com/dedexperiment1/Subculture-Media-Manager.git
cd Subculture-Media-Manager

# 2. 실행 (Python 3.10+ 권장)
python subculture_media_manager.py
```

---

## 📄 라이선스 (License)
본 프로젝트는 [MIT License](LICENSE)에 따라 자유롭게 사용, 수정, 배포할 수 있습니다.
Copyright (c) 2026 dedexperiment1
