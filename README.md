# webOS Subscription Management Dashboard 📺

webOS 구독자 및 가전 기기 사용 현황을 한눈에 파악하고 관리할 수 있는 통합 대시보드 웹 애플리케이션입니다.

## ✨ 주요 기능 (Key Features)

- **구독자 관리**: 전체 구독자 목록 조회 및 이름, ID, 구독 플랜, 상태 기반 검색 및 필터링 기능
- **디바이스 관리**: 구독자별 보유 가전 기기 목록 확인, 기기 타입 및 상태에 따른 실시간 필터링
- **사용량 통계**: 선택한 기기의 주간 사용량 추이를 시각적인 바 차트(Bar Chart)로 제공
- **상태 모니터링**: 기기 및 구독자 상태를 직관적인 색상 배지(Badge)로 다이나믹하게 표시 (🟢 Active/Online, 🔵 Paused/Standby, 🔴 Expired/Error, ⚪️ Offline)
- **반응형 UI**: 데스크톱 및 모바일 환경에 최적화된 모던하고 미려한 디자인

## 🛠 기술 스택 (Tech Stack)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn
- **Template Engine**: Jinja2

### Frontend
- **HTML/CSS/JS**: Vanilla (프레임워크 없이 순수 언어로 동적 UI 구현)
- **Styling**: Custom CSS (Glassmorphism, CSS Variables, Flexbox/Grid)

### QA (Testing) & DevOps
- **Test Framework**: `pytest`, `httpx` (API), `requests` (Deploy)
- **UI Testing**: `Selenium WebDriver`
- **CI/CD**: GitHub Actions
- **Deployment**: Render

## 📂 프로젝트 구조 (Project Structure)

```text
CAS3141/
├── app/
│   ├── api/             # FastAPI 라우터 모듈 (subscribers.py, devices.py)
│   ├── data/            # 더미 데이터 분리 (dummy_data.py)
│   ├── static/          # 정적 파일 (style.css, app.js 등)
│   ├── templates/       # HTML 템플릿 (index.html)
│   └── main.py          # 엔트리포인트 및 앱 설정
├── tests/               # 테스트 코드 폴더
│   ├── test_api.py      # 백엔드 API 유닛 테스트 (FastAPI TestClient)
│   ├── test_frontend.py # 프론트엔드 UI 자동화 테스트 (Selenium)
│   └── test_deployed.py # 배포 서버 E2E 테스트 (Requests)
├── .github/workflows/
│   └── ci.yml           # GitHub Actions 자동 테스트 파이프라인
├── requirements.txt     # Python 패키지 의존성
├── test_report.md       # 종합 테스트 검증 보고서
└── README.md            # 현재 프로젝트 설명
```

## 🚀 로컬 실행 방법 (How to Run Locally)

### 1. 환경 설정 및 의존성 설치
```bash
# 레포지토리 클론 후 프로젝트 폴더로 이동
cd CAS3141

# Python 가상 환경(권장) 및 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
# Uvicorn을 통해 FastAPI 서버 실행 (개발 모드)
uvicorn app.main:app --reload
```
서버가 정상적으로 실행되면 브라우저에서 `http://localhost:8000` 으로 접속하여 대시보드를 확인할 수 있습니다.

## 🧪 자동화 테스트 (Automated Testing)

본 프로젝트는 코드의 신뢰성을 보장하기 위해 API부터 UI, 배포 환경까지 다각도로 검증하는 자동화 테스트 스위트를 포함하고 있습니다.

- **Backend API 테스트**: `FastAPI TestClient`를 활용하여 서버를 띄우지 않고 API 정합성 및 데이터 무결성을 빠르게 검증합니다.
  ```bash
  pytest tests/test_api.py -v
  ```
- **Frontend UI 테스트**: `Selenium WebDriver`를 통해 렌더링, 컴포넌트 상호작용 및 디바이스 상태 배지 동작 등을 브라우저 환경에서 자동 측정합니다.
  ```bash
  pytest tests/test_frontend.py -v
  ```
- **배포 환경 테스트**: 운영망에 배포된 URL 환경을 대상으로 실제 API Endpoint 접근성 등 End-to-End 검증을 수행합니다.
  ```bash
  BASE_URL=https://YOUR-APP.onrender.com pytest tests/test_deployed.py -v
  ```

> 💡 **참고**: 상세한 테스트 검증 결과 및 품질 리포트는 📊 [test_report.md](./test_report.md)에서 확인하실 수 있습니다.

## 🌐 지속적 통합/배포 파이프라인 (CI / CD)

현대적인 DevOps 방법론에 따라, 코드 통합부터 배포까지의 과정을 자동화하여 일관성 있는 배포 환경을 무중단으로 유지하고 있습니다.

- **CI (Continuous Integration)**: GitHub Actions (`ci.yml`) 기반으로, 코드가 수시로 Push 및 PR 될 때마다 Python 구문 검사와 Health Check가 자동으로 수행되어 코드 품질을 일관성있게 관리합니다.
- **CD (Continuous Deployment)**: CI 과정을 통과한 안정된 `main` 브랜치의 코드는 **Render** 클라우드 인프라와 즉시 연동되어, 개발자의 추가 수동 개입 없이 안전하고 신속하게 운영 서버로 업데이트 배포됩니다.
