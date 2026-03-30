# 📊 Test Verification Report (테스트 검증 보고서)

## 1. 개요 (Overview)

| 항목 | 내용 |
|---|---|
| **프로젝트** | webOS Subscription Management Dashboard |
| **작성자 (Test Engineer)** | _______________ |
| **테스트 일자** | 2026-03-30 |
| **대상 시스템** | 구독자 가전 관리 대시보드 (Backend API & Frontend UI) |
| **테스트 환경** | Local macOS — Python 3.13.12, pytest 9.0.2 |
| **테스트 프레임워크** | pytest + FastAPI TestClient (Backend), Selenium (Frontend), requests (Deployed) |
| **소스 위치** | `CAS3141/tests/` |

---

## 2. 요구사항 매핑 (Requirement Traceability)

본 테스트는 아래 요구사항을 기반으로 설계되었습니다.

| 요구사항 | 설명 | 테스트 범위 |
|---|---|---|
| **요구사항 #1** | `GET /api/subscribers` — 전체 구독 사용자 목록 반환 | TC-BE-02 |
| **요구사항 #2** | `GET /api/subscribers/{userId}/devices` — 사용자별 가전 목록 반환 | TC-BE-03 |
| **요구사항 #2** | `GET /api/devices/{deviceId}/usage` — 가전 상세 사용 현황 반환 | TC-BE-04 |
| **요구사항 3-A** | 상태 기반 UI 표현 — Badge 색상 규칙 | TC-FE-04, TC-BE-02-06~07, TC-BE-03-06 |
| **요구사항 3-B** | GitHub Actions CI 자동 검증 | CI workflow 검증 |
| **요구사항 3-C** | Render 연동 배포 | TC-DEPLOY-01~04 |

### 요구사항 3-A: 상태 기반 UI 표현 (Status Badge Color Rules)

| 상태 값 | 색상 | CSS 클래스 | 검증 TC |
|---|---|---|---|
| Active / Online | 초록 (Green) | `status-active`, `status-online` | TC-FE-04-02, TC-FE-04-05 |
| Paused / Standby | 파랑 (Blue) | `status-paused`, `status-standby` | TC-FE-04-03, TC-FE-04-05 |
| Expired / Error | 빨강 (Red) | `status-expired`, `status-error` | TC-FE-04-04, TC-FE-04-05 |
| Offline | 회색 (Gray) | `status-offline` | TC-FE-04-05 |

### 요구사항 3-B: GitHub Actions CI (자동 검증)

| CI 단계 | 설명 | ci.yml 반영 |
|---|---|---|
| push/PR 트리거 | push 또는 pull_request 발생 시 자동 실행 | ✅ `on: push/pull_request` |
| Python 환경 구성 | Python 3.11 설치 | ✅ `actions/setup-python@v5` |
| 의존성 설치 | `pip install -r requirements.txt` | ✅ |
| 정적 분석 (Syntax Check) | `py_compile`로 주요 파일 검증 | ✅ `main.py`, `subscribers.py`, `devices.py` |
| 서버 실행 후 Health Check | uvicorn 서버 시작 → `/health` curl | ✅ |
| 주요 API endpoint 검증 | `/api/subscribers`, `/devices`, `/usage` curl | ✅ |

### 요구사항 3-C: Render 연동 배포

| 설정 항목 | 값 |
|---|---|
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |
| Build Command | `pip install -r requirements.txt` |
| Language | Python 3 |
| Branch | main |

---

## 3. 테스트 요약 (Test Summary)

| 구분 | 테스트 파일 | 전체 | Pass ✅ | Fail ❌ | N/A ⏸️ |
|---|---|:---:|:---:|:---:|:---:|
| **Backend — Health** | `test_api.py` | 2 | 2 | 0 | 0 |
| **Backend — Subscribers** | `test_api.py` | 8 | 8 | 0 | 0 |
| **Backend — Search/Filter** | `test_api.py` | 8 | 8 | 0 | 0 |
| **Backend — Devices** | `test_api.py` | 9 | 9 | 0 | 0 |
| **Backend — Usage** | `test_api.py` | 13 | 13 | 0 | 0 |
| **Backend — Data Consistency** | `test_api.py` | 3 | 3 | 0 | 0 |
| **Backend — Dashboard HTML** | `test_api.py` | 8 | 8 | 0 | 0 |
| **Frontend — Dashboard Access** | `test_frontend.py` | 4 | — | — | 4 |
| **Frontend — Table Rendering** | `test_frontend.py` | 8 | — | — | 8 |
| **Frontend — Search & Filter** | `test_frontend.py` | 8 | — | — | 8 |
| **Frontend — Status Badge** | `test_frontend.py` | 5 | — | — | 5 |
| **Frontend — Bar Chart** | `test_frontend.py` | 8 | — | — | 8 |
| **Deployed — 서비스 접근** | `test_deployed.py` | 6 | — | — | 6 |
| **Deployed — API 동작** | `test_deployed.py` | 9 | — | — | 9 |
| **Deployed — 검색/필터** | `test_deployed.py` | 3 | — | — | 3 |
| **Deployed — 데이터 일관성** | `test_deployed.py` | 3 | — | — | 3 |
| **총합** | — | **97** | **61** | **0** | **36** |

> **Backend API 테스트 (test_api.py):** 61개 전체 **PASS** (통과율 100%)
> Frontend / Deployed 테스트는 서버 실행 및 배포 환경 필요 → N/A 처리

---

## 4. 테스트 시나리오 및 결과 (Test Scenarios & Results)

### 🔧 [Backend / API] 검증 시나리오

#### TC-BE-01: `GET /health` — 서버 상태 확인

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-01-01 | `/health` 호출 시 200 반환 | 상태 코드 200 | 200 OK | ✅ Pass |
| TC-BE-01-02 | 응답에 `status: ok` 포함 | `{"status": "ok"}` | `{"status": "ok"}` | ✅ Pass |

#### TC-BE-02: `GET /api/subscribers` — 전체 구독 사용자 목록 조회

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-02-01 | 정상 요청 시 200 반환 | 상태 코드 200 | 200 OK | ✅ Pass |
| TC-BE-02-02 | 응답이 리스트 형식 | `Array` 타입 | `list` 확인 | ✅ Pass |
| TC-BE-02-03 | 전체 구독자 반환 (5명) | `len(data) == 5` | 5명 반환 | ✅ Pass |
| TC-BE-02-04 | 필수 필드 존재 확인 | 6개 필드 모두 존재 | 모든 필드 존재 | ✅ Pass |
| TC-BE-02-05 | 필드 타입 검증 | string/number 타입 | 타입 일치 | ✅ Pass |
| TC-BE-02-06 | plan 값 검증 | Premium / Basic / Family | 허용값만 확인 | ✅ Pass |
| TC-BE-02-07 | status 값 검증 | Active / Paused / Expired | 허용값만 확인 | ✅ Pass |
| TC-BE-02-08 | deviceCount ≥ 0 | 0 이상 정수 | 모두 0 이상 | ✅ Pass |

#### TC-BE-02-S: `GET /api/subscribers` — 검색/필터 테스트

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-02-S01 | name 검색 (`Kim`) | Kim 포함 결과 반환 | 정상 필터링 | ✅ Pass |
| TC-BE-02-S02 | userId 검색 (`U001`) | U001 포함 결과 반환 | U001 포함 확인 | ✅ Pass |
| TC-BE-02-S03 | status=Active 필터 | Active만 반환 | Active만 반환 | ✅ Pass |
| TC-BE-02-S04 | status=Paused 필터 | Paused만 반환 | Paused만 반환 | ✅ Pass |
| TC-BE-02-S05 | status=Expired 필터 | Expired만 반환 | Expired만 반환 | ✅ Pass |
| TC-BE-02-S06 | plan=Premium 필터 | Premium만 반환 | Premium만 반환 | ✅ Pass |
| TC-BE-02-S07 | 존재하지 않는 검색어 | 빈 리스트 반환 | `[]` 반환 | ✅ Pass |
| TC-BE-02-S08 | 대소문자 무시 검색 | 동일 결과 반환 | 동일 결과 | ✅ Pass |

#### TC-BE-03: `GET /api/subscribers/{userId}/devices` — 가전 목록 조회

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-03-01 | 존재하는 userId에 200 반환 | U001~U004 각각 200 | 모두 200 OK | ✅ Pass |
| TC-BE-03-02 | 응답이 리스트 형식 | `Array` 타입 | `list` 확인 | ✅ Pass |
| TC-BE-03-03 | 디바이스 수 일치 | 더미 데이터 수와 동일 | 일치 확인 | ✅ Pass |
| TC-BE-03-04 | 필수 필드 존재 확인 | 6개 필드 존재 | 모든 필드 존재 | ✅ Pass |
| TC-BE-03-05 | 필드 타입 검증 | 모두 string 타입 | 타입 일치 | ✅ Pass |
| TC-BE-03-06 | status 값 검증 | Online/Offline/Standby/Error | 허용값만 확인 | ✅ Pass |
| TC-BE-03-07 | 가전 0개인 사용자 (U005) | 빈 리스트 `[]` 반환 | `[]` 확인 | ✅ Pass |
| TC-BE-03-08 | 존재하지 않는 userId → 404 | `status_code == 404` | 404 반환 | ✅ Pass |
| TC-BE-03-09 | 404 응답에 detail 포함 | `detail` 키 존재 | `detail` 확인 | ✅ Pass |

#### TC-BE-04: `GET /api/devices/{deviceId}/usage` — 가전 사용 현황 조회

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-04-01 | D001~D008 각각 200 반환 | `status_code == 200` | 모두 200 OK | ✅ Pass |
| TC-BE-04-02 | 응답이 객체(dict) 형식 | `dict` 타입 | `dict` 확인 | ✅ Pass |
| TC-BE-04-03 | 필수 필드 존재 확인 | 9개 필드 전부 존재 | 모든 필드 존재 | ✅ Pass |
| TC-BE-04-04 | 필드 타입 검증 | 명세 기준 타입 일치 | 타입 일치 | ✅ Pass |
| TC-BE-04-05 | weeklyUsageTrend 7개 요소 | `len(trend) == 7` | 7개 확인 | ✅ Pass |
| TC-BE-04-06 | weeklyUsageTrend 숫자 타입 | 각 요소 int/float | 숫자 타입 | ✅ Pass |
| TC-BE-04-07 | weeklyUsageTrend ≥ 0 | 모든 요소 0 이상 | 0 이상 확인 | ✅ Pass |
| TC-BE-04-08 | totalUsageHours ≥ 0 | 0 이상 | 0 이상 확인 | ✅ Pass |
| TC-BE-04-09 | deviceId 일치 검증 | 요청 ID == 응답 ID | 일치 확인 | ✅ Pass |
| TC-BE-04-10 | 존재하지 않는 deviceId → 404 | `status_code == 404` | 404 반환 | ✅ Pass |
| TC-BE-04-11 | 404 응답에 detail 포함 | `detail` 키 존재 | `detail` 확인 | ✅ Pass |
| TC-BE-04-12 | powerStatus 값 검증 | On/Off/Standby/Error/Cleaning | 허용값만 확인 | ✅ Pass |
| TC-BE-04-13 | healthStatus 값 검증 | Normal / Warning | 허용값만 확인 | ✅ Pass |

#### TC-BE-05: 데이터 일관성 (Cross-API) 검증

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-05-01 | subscriber.deviceCount == 실제 devices 수 | 동일 | 전체 사용자 일치 | ✅ Pass |
| TC-BE-05-02 | 모든 디바이스에 usage 데이터 존재 | 200 응답 | 모두 200 확인 | ✅ Pass |
| TC-BE-05-03 | usage.deviceName == device.model | 동일 | 일치 확인 | ✅ Pass |

#### TC-BE-06: 대시보드 HTML 렌더링

| TC ID | 테스트 항목 | 예상 결과 | 실제 결과 | Pass/Fail |
|---|---|---|---|:---:|
| TC-BE-06-01 | `GET /` → 200 반환 | 상태 코드 200 | 200 OK | ✅ Pass |
| TC-BE-06-02 | Content-Type HTML 확인 | `text/html` | `text/html` 확인 | ✅ Pass |
| TC-BE-06-03 | 대시보드 제목 포함 | "Subscription Management Dashboard" | 제목 일치 | ✅ Pass |
| TC-BE-06-04 | subscriber-table 요소 존재 | HTML에 ID 존재 | ID 존재 확인 | ✅ Pass |
| TC-BE-06-05 | device-table 요소 존재 | HTML에 ID 존재 | ID 존재 확인 | ✅ Pass |
| TC-BE-06-06 | usage-chart 요소 존재 | HTML에 ID 존재 | ID 존재 확인 | ✅ Pass |
| TC-BE-06-07 | app.js 포함 확인 | `<script>` 포함 | 포함 확인 | ✅ Pass |
| TC-BE-06-08 | style.css 포함 확인 | `<link>` 포함 | 포함 확인 | ✅ Pass |

---

### 🎨 [Frontend / UI] 검증 시나리오

> Frontend UI 테스트는 `Selenium + Chrome/ChromeDriver` 환경이 필요하며, 로컬 서버(`uvicorn`)가 실행 중이어야 합니다.

#### TC-FE-01: 메인 대시보드 접근 확인

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-FE-01-01 | 페이지 제목 확인 | "Subscription Management Dashboard" | ⏸️ N/A |
| TC-FE-01-02 | 히어로 섹션 표시 | `.hero` 요소 visible | ⏸️ N/A |
| TC-FE-01-03 | 구독자 패널 표시 | `.panel` 요소 존재 | ⏸️ N/A |
| TC-FE-01-04 | 3개 패널 존재 | Subscriber + Device + Usage | ⏸️ N/A |

#### TC-FE-02: Table 데이터 렌더링 확인

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-FE-02-01 | 구독자 테이블 데이터 행 존재 | 1개 이상 `<tr>` | ⏸️ N/A |
| TC-FE-02-02 | 구독자 테이블 5개 컬럼 | `<th>` 5개 | ⏸️ N/A |
| TC-FE-02-03 | 컬럼명 확인 | User ID, Name, Plan, Status, Devices | ⏸️ N/A |
| TC-FE-02-04 | 첫 번째 행 데이터 검증 | U001, Kim Minsoo | ⏸️ N/A |
| TC-FE-02-05 | 전체 행 수 확인 | 5개 행 | ⏸️ N/A |
| TC-FE-02-06 | 구독자 클릭 → 가전 표시 | 테이블 전환 + 데이터 로딩 | ⏸️ N/A |
| TC-FE-02-07 | 디바이스 테이블 5개 컬럼 | `<th>` 5개 | ⏸️ N/A |
| TC-FE-02-08 | 디바이스 컬럼명 확인 | Device ID, Type, Model, Location, Status | ⏸️ N/A |

#### TC-FE-03: 검색(Search) 및 필터(Filter) 동작

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-FE-03-01 | 검색 입력 필드 존재 | `#subscriber-search` visible | ⏸️ N/A |
| TC-FE-03-02 | 상태 필터 드롭다운 존재 | `#subscriber-status-filter` visible | ⏸️ N/A |
| TC-FE-03-03 | "Kim" 검색 시 실시간 필터링 | Kim 포함 행만 표시 | ⏸️ N/A |
| TC-FE-03-04 | Active 필터 적용 | Active 상태만 표시 | ⏸️ N/A |
| TC-FE-03-05 | All Status 선택 시 전체 복원 | 5개 행 표시 | ⏸️ N/A |
| TC-FE-03-06 | 검색 결과 없을 때 안내 메시지 | empty-state 표시 | ⏸️ N/A |
| TC-FE-03-07 | 디바이스 검색 필드 존재 | `#device-search` visible | ⏸️ N/A |
| TC-FE-03-08 | 디바이스 상태 필터 존재 | `#device-status-filter` visible | ⏸️ N/A |

#### TC-FE-04: 상태 색상 배지(Status Badge) 확인 — 요구사항 3-A

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail | 비고 |
|---|---|---|:---:|---|
| TC-FE-04-01 | 구독자 테이블에 배지 존재 | `.badge` 요소 1개 이상 | ⏸️ N/A | |
| TC-FE-04-02 | Active → 초록 (Green) | `status-active` 클래스 | ⏸️ N/A | `#dcfce7` |
| TC-FE-04-03 | Paused → 파랑 (Blue) | `status-paused` 클래스 | ⏸️ N/A | `#dbeafe` |
| TC-FE-04-04 | Expired → 빨강 (Red) | `status-expired` 클래스 | ⏸️ N/A | `#fee2e2` |
| TC-FE-04-05 | 디바이스 상태 배지 검증 | Online=초록, Offline=회색, Standby=파랑, Error=빨강 | ⏸️ N/A | 요구사항 3-A |

> **상태 색상(Color) 규칙 — CSS 구현 확인:**
> - [x] **초록 (Green):** Active / Online / Normal → `status-active` / `status-online` / `status-normal` → `background: #dcfce7`
> - [x] **파랑 (Blue):** Paused / Standby → `status-paused` / `status-standby` → `background: #dbeafe`
> - [x] **빨강 (Red):** Expired / Error / Warning → `status-expired` / `status-error` / `status-warning` → `background: #fee2e2`
> - [x] **회색 (Gray):** Offline → `status-offline` → `background: #e5e7eb`
>
> ✅ CSS 파일(`style.css`)에서 위 규칙이 올바르게 구현되었음을 코드 리뷰로 확인

#### TC-FE-05: Bar Chart 렌더링 확인

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-FE-05-01 | 디바이스 클릭 → usage 표시 | `#usage-detail` visible | ⏸️ N/A |
| TC-FE-05-02 | Chart 컨테이너 표시 | `#usage-chart` visible | ⏸️ N/A |
| TC-FE-05-03 | 7개 요일 컬럼 존재 | `.chart-column` 7개 | ⏸️ N/A |
| TC-FE-05-04 | 요일 라벨: Mon~Sun | 순서대로 표시 | ⏸️ N/A |
| TC-FE-05-05 | Bar 요소 7개 존재 | `.chart-bar` 7개 | ⏸️ N/A |
| TC-FE-05-06 | 사용량 숫자 표시 (D001) | 2,3,1,4,2,3,3 | ⏸️ N/A |
| TC-FE-05-07 | Detail 카드 8개 표시 | 각 필드별 카드 | ⏸️ N/A |
| TC-FE-05-08 | 가전 없는 사용자(U005) 안내 | empty message 표시 | ⏸️ N/A |

---

### 🚀 [Deployed] 배포 환경 검증 시나리오 — 요구사항 3-C

> 배포 테스트는 Render 배포 URL이 필요합니다.
> `pytest tests/test_deployed.py -v --base-url https://YOUR-APP.onrender.com`

#### TC-DEPLOY-01: 서비스 접근 가능성 확인

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-DEPLOY-01-01 | 메인 페이지 접근 시 200 | 200 OK | ⏸️ N/A |
| TC-DEPLOY-01-02 | 메인 페이지 HTML 반환 | `text/html` | ⏸️ N/A |
| TC-DEPLOY-01-03 | 대시보드 제목 포함 | 제목 문자열 존재 | ⏸️ N/A |
| TC-DEPLOY-01-04 | `/health` 엔드포인트 200 | `{"status":"ok"}` | ⏸️ N/A |
| TC-DEPLOY-01-05 | style.css 정적 파일 제공 | 200 + `text/css` | ⏸️ N/A |
| TC-DEPLOY-01-06 | app.js 정적 파일 제공 | 200 + `javascript` | ⏸️ N/A |

#### TC-DEPLOY-02: 배포 환경 API 동작

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-DEPLOY-02-01 | `GET /api/subscribers` 정상 | 200 + list | ⏸️ N/A |
| TC-DEPLOY-02-02 | 구독자 필수 필드 존재 | 6개 필드 | ⏸️ N/A |
| TC-DEPLOY-02-03 | `GET /api/subscribers/U001/devices` 정상 | 200 + list | ⏸️ N/A |
| TC-DEPLOY-02-04 | 디바이스 필수 필드 존재 | 6개 필드 | ⏸️ N/A |
| TC-DEPLOY-02-05 | `GET /api/devices/D001/usage` 정상 | 200 + dict | ⏸️ N/A |
| TC-DEPLOY-02-06 | usage 필수 필드 존재 | 9개 필드 | ⏸️ N/A |
| TC-DEPLOY-02-07 | weeklyUsageTrend 7개 요소 | len == 7 | ⏸️ N/A |
| TC-DEPLOY-02-08 | 존재하지 않는 userId → 404 | 404 | ⏸️ N/A |
| TC-DEPLOY-02-09 | 존재하지 않는 deviceId → 404 | 404 | ⏸️ N/A |

#### TC-DEPLOY-03: 배포 환경 검색/필터

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-DEPLOY-03-01 | 이름 검색 동작 | Kim 검색 정상 | ⏸️ N/A |
| TC-DEPLOY-03-02 | 상태 필터 동작 | Active 필터 정상 | ⏸️ N/A |
| TC-DEPLOY-03-03 | 가전 없는 사용자 빈 리스트 | U005 → `[]` | ⏸️ N/A |

#### TC-DEPLOY-04: 배포 환경 데이터 일관성

| TC ID | 테스트 항목 | 예상 결과 | Pass/Fail |
|---|---|---|:---:|
| TC-DEPLOY-04-01 | 구독자 수 5명 | len == 5 | ⏸️ N/A |
| TC-DEPLOY-04-02 | deviceCount와 실제 devices 수 일치 | 동일 | ⏸️ N/A |
| TC-DEPLOY-04-03 | 모든 디바이스에 usage 존재 | 200 응답 | ⏸️ N/A |

---

## 5. 결함 리포트 (Defect Report)

> 현재 Backend API 테스트 전체 통과 — 발견된 결함 없음.

| TC ID | 결함 내용 / 재현 경로 | 심각도 | 등록일 | 담당자(개발) | 진행 상태 |
|---|---|:---:|---|---|:---:|
| — | — | — | — | — | — |

> 심각도: Critical / Major / Minor / Trivial

---

## 6. CI/CD 파이프라인 검증 (요구사항 3-B, 3-C)

### GitHub Actions CI 워크플로우

파일 위치: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run syntax check
        run: |
          python -m py_compile app/main.py
          python -m py_compile app/api/subscribers.py
          python -m py_compile app/api/devices.py

      - name: Start server and test health endpoint
        run: |
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 3
          curl -f http://localhost:8000/health

      - name: Test API endpoints
        run: |
          curl -f http://localhost:8000/api/subscribers
          curl -f http://localhost:8000/api/subscribers/U001/devices
          curl -f http://localhost:8000/api/devices/D001/usage
```

### GitHub에서 CI 확인 방법

1. GitHub 리포지토리 → **Actions** 탭 이동
2. 워크플로우 실행 로그 확인
3. 모든 Step이 초록색(통과)인지 확인

### Render 배포 설정

| 항목 | 값 |
|---|---|
| Service Type | Web Services |
| Language | Python 3 |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

---

## 7. 테스트 실행 방법

### Backend API 테스트 (서버 없이 실행 가능)
```bash
cd CAS3141
pip install pytest httpx
pytest tests/test_api.py -v
```

### Frontend UI 테스트 (서버 실행 필요)
```bash
# 터미널 1: 서버 실행
cd CAS3141
pip install -r requirements.txt
uvicorn app.main:app --reload

# 터미널 2: UI 테스트 실행
pip install selenium
pytest tests/test_frontend.py -v
```

### 배포 환경 테스트 (배포 URL 필요)
```bash
BASE_URL=https://YOUR-APP.onrender.com pytest tests/test_deployed.py -v
# 또는
pytest tests/test_deployed.py -v --base-url https://YOUR-APP.onrender.com
```

> **참고:**
> - Backend 테스트는 FastAPI TestClient를 사용하므로 **서버 실행 없이** 단독 실행 가능합니다.
> - Frontend 테스트는 **Chrome + ChromeDriver**가 설치되어 있어야 합니다.
> - Deployed 테스트는 **Render 배포 서비스 URL**이 필요합니다.

---

## 8. pytest 실행 로그 (Raw Output)

```
============================= test session starts ==============================
platform darwin -- Python 3.13.12, pytest-9.0.2, pluggy-1.5.0
rootdir: /Users/june/yonsei/connected/lab/CAS3141
plugins: anyio-4.10.0

tests/test_api.py::TestHealth::test_health_returns_200                    PASSED [  1%]
tests/test_api.py::TestHealth::test_health_response_body                  PASSED [  3%]
tests/test_api.py::TestGetSubscribers::test_returns_200                   PASSED [  4%]
tests/test_api.py::TestGetSubscribers::test_returns_list                  PASSED [  6%]
tests/test_api.py::TestGetSubscribers::test_returns_all_subscribers       PASSED [  8%]
tests/test_api.py::TestGetSubscribers::test_subscriber_has_required_fields PASSED [  9%]
tests/test_api.py::TestGetSubscribers::test_subscriber_field_types        PASSED [ 11%]
tests/test_api.py::TestGetSubscribers::test_subscriber_plan_values        PASSED [ 13%]
tests/test_api.py::TestGetSubscribers::test_subscriber_status_values      PASSED [ 14%]
tests/test_api.py::TestGetSubscribers::test_device_count_non_negative     PASSED [ 16%]
tests/test_api.py::TestSubscriberSearchFilter::test_search_by_name        PASSED [ 18%]
tests/test_api.py::TestSubscriberSearchFilter::test_search_by_user_id     PASSED [ 19%]
tests/test_api.py::TestSubscriberSearchFilter::test_filter_by_status_active PASSED [ 21%]
tests/test_api.py::TestSubscriberSearchFilter::test_filter_by_status_paused PASSED [ 22%]
tests/test_api.py::TestSubscriberSearchFilter::test_filter_by_status_expired PASSED [ 24%]
tests/test_api.py::TestSubscriberSearchFilter::test_filter_by_plan        PASSED [ 26%]
tests/test_api.py::TestSubscriberSearchFilter::test_search_no_results     PASSED [ 27%]
tests/test_api.py::TestSubscriberSearchFilter::test_search_case_insensitive PASSED [ 29%]
tests/test_api.py::TestGetDevicesByUser::test_returns_200_for_existing_user[U001] PASSED [ 31%]
tests/test_api.py::TestGetDevicesByUser::test_returns_200_for_existing_user[U002] PASSED [ 32%]
tests/test_api.py::TestGetDevicesByUser::test_returns_200_for_existing_user[U003] PASSED [ 34%]
tests/test_api.py::TestGetDevicesByUser::test_returns_200_for_existing_user[U004] PASSED [ 36%]
tests/test_api.py::TestGetDevicesByUser::test_returns_list                PASSED [ 37%]
tests/test_api.py::TestGetDevicesByUser::test_device_count_matches        PASSED [ 39%]
tests/test_api.py::TestGetDevicesByUser::test_device_has_required_fields  PASSED [ 40%]
tests/test_api.py::TestGetDevicesByUser::test_device_field_types          PASSED [ 42%]
tests/test_api.py::TestGetDevicesByUser::test_device_status_values        PASSED [ 44%]
tests/test_api.py::TestGetDevicesByUser::test_empty_devices_for_user_with_no_devices PASSED [ 45%]
tests/test_api.py::TestGetDevicesByUser::test_404_for_nonexistent_user    PASSED [ 47%]
tests/test_api.py::TestGetDevicesByUser::test_404_response_has_detail     PASSED [ 49%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D001] PASSED [ 50%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D002] PASSED [ 52%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D003] PASSED [ 54%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D004] PASSED [ 55%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D005] PASSED [ 57%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D006] PASSED [ 59%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D007] PASSED [ 60%]
tests/test_api.py::TestGetDeviceUsage::test_returns_200_for_existing_device[D008] PASSED [ 62%]
tests/test_api.py::TestGetDeviceUsage::test_returns_object                PASSED [ 63%]
tests/test_api.py::TestGetDeviceUsage::test_usage_has_required_fields     PASSED [ 65%]
tests/test_api.py::TestGetDeviceUsage::test_usage_field_types             PASSED [ 67%]
tests/test_api.py::TestGetDeviceUsage::test_weekly_usage_trend_has_7_days PASSED [ 68%]
tests/test_api.py::TestGetDeviceUsage::test_weekly_usage_trend_all_numbers PASSED [ 70%]
tests/test_api.py::TestGetDeviceUsage::test_weekly_usage_trend_non_negative PASSED [ 72%]
tests/test_api.py::TestGetDeviceUsage::test_total_usage_hours_non_negative PASSED [ 73%]
tests/test_api.py::TestGetDeviceUsage::test_device_id_matches_request     PASSED [ 75%]
tests/test_api.py::TestGetDeviceUsage::test_404_for_nonexistent_device    PASSED [ 77%]
tests/test_api.py::TestGetDeviceUsage::test_404_response_has_detail       PASSED [ 78%]
tests/test_api.py::TestGetDeviceUsage::test_power_status_values           PASSED [ 80%]
tests/test_api.py::TestGetDeviceUsage::test_health_status_values          PASSED [ 81%]
tests/test_api.py::TestDataConsistency::test_subscriber_device_count_matches_devices_api PASSED [ 83%]
tests/test_api.py::TestDataConsistency::test_all_devices_have_usage_data  PASSED [ 85%]
tests/test_api.py::TestDataConsistency::test_device_name_consistent_with_model PASSED [ 86%]
tests/test_api.py::TestDashboardPage::test_root_returns_200               PASSED [ 88%]
tests/test_api.py::TestDashboardPage::test_root_returns_html              PASSED [ 90%]
tests/test_api.py::TestDashboardPage::test_html_contains_title            PASSED [ 91%]
tests/test_api.py::TestDashboardPage::test_html_contains_subscriber_table PASSED [ 93%]
tests/test_api.py::TestDashboardPage::test_html_contains_device_table     PASSED [ 95%]
tests/test_api.py::TestDashboardPage::test_html_contains_usage_chart      PASSED [ 96%]
tests/test_api.py::TestDashboardPage::test_html_includes_app_js           PASSED [ 98%]
tests/test_api.py::TestDashboardPage::test_html_includes_style_css        PASSED [100%]

========================= 61 passed in 0.54s ==================================
```

---

## 9. 최종 배포 판단 (Deployment Decision)

| 항목 | 내용 |
|---|---|
| **테스트 완료일** | 2026-03-30 |
| **총 테스트** | 97건 |
| **실행된 테스트** | 61건 (Backend API) |
| **Pass** | 61건 |
| **Fail** | 0건 |
| **N/A** | 36건 (Frontend/Deployed — 환경 미구성) |
| **통과율 (실행 기준)** | **100%** |

### 의견 (Comments)

1. **Backend API 안정성:** 전체 61/61 통과 — API 계약(Contract)이 안정적으로 구현됨
2. **요구사항 3-A (Status Badge):** CSS 코드 리뷰로 색상 규칙(초록/파랑/빨강/회색) 올바르게 구현 확인
3. **요구사항 3-B (GitHub Actions CI):** `.github/workflows/ci.yml` 요구사항 대로 구성 완료
4. **요구사항 3-C (Render 배포):** 배포 설정 준비 완료, Render 연동 후 `test_deployed.py` 실행 필요
5. **Cross-API 일관성:** Subscriber → Device → Usage 간 데이터 정합성 검증 통과
6. **미실행 테스트:** Frontend(33건) + Deployed(16건) = 36건은 해당 환경 구성 후 별도 실행 필요

### 결정 (Decision)

> **승인 (Go)** — Backend API 전체 통과, CI/CD 파이프라인 구성 완료, Frontend/Deployed는 배포 후 추가 검증

| 검증자 | 서명 | 일자 |
|---|---|---|
| Test Engineer | _______________ | 2026-03-30 |
| PM | _______________ | |
