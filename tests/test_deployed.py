"""
=============================================================================
 배포 후 검증 테스트 (Test Engineer 작성)
 - 대상: 배포된 webOS Subscription Operations Dashboard
 - 요구사항 3-C: Render 배포 후 최종 서비스 검증
 - 실행 방법:
     pytest tests/test_deployed.py -v --base-url https://YOUR-APP.onrender.com
 - 또는 환경변수로 BASE_URL 지정:
     BASE_URL=https://YOUR-APP.onrender.com pytest tests/test_deployed.py -v
=============================================================================
"""
import os
import pytest
import requests

# 배포 URL (환경변수 또는 pytest 옵션으로 설정)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="배포된 서비스의 URL (예: https://your-app.onrender.com)"
    )


@pytest.fixture(autouse=True)
def set_base_url(request):
    global BASE_URL
    url = request.config.getoption("--base-url", default=None)
    if url:
        BASE_URL = url.rstrip("/")


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEPLOY-01: 서비스 접근 가능성 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestServiceAccess:
    """배포된 서비스의 기본 접근 가능 여부 테스트"""

    def test_root_page_accessible(self):
        """TC-DEPLOY-01-01: 메인 페이지 접근 시 200 반환"""
        res = requests.get(f"{BASE_URL}/", timeout=30)
        assert res.status_code == 200, f"메인 페이지 접속 실패: {res.status_code}"

    def test_root_returns_html(self):
        """TC-DEPLOY-01-02: 메인 페이지가 HTML을 반환"""
        res = requests.get(f"{BASE_URL}/", timeout=30)
        assert "text/html" in res.headers.get("content-type", "")

    def test_root_contains_dashboard_title(self):
        """TC-DEPLOY-01-03: HTML에 대시보드 제목이 포함"""
        res = requests.get(f"{BASE_URL}/", timeout=30)
        assert "Subscription Management Dashboard" in res.text

    def test_health_endpoint(self):
        """TC-DEPLOY-01-04: /health 엔드포인트 200 OK"""
        res = requests.get(f"{BASE_URL}/health", timeout=10)
        assert res.status_code == 200
        assert res.json().get("status") == "ok"

    def test_static_css_served(self):
        """TC-DEPLOY-01-05: style.css 정적 파일이 제공됨"""
        res = requests.get(f"{BASE_URL}/static/style.css", timeout=10)
        assert res.status_code == 200
        assert "text/css" in res.headers.get("content-type", "")

    def test_static_js_served(self):
        """TC-DEPLOY-01-06: app.js 정적 파일이 제공됨"""
        res = requests.get(f"{BASE_URL}/static/app.js", timeout=10)
        assert res.status_code == 200
        assert "javascript" in res.headers.get("content-type", "").lower()


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEPLOY-02: 배포 환경에서 API 정상 동작
# ─────────────────────────────────────────────────────────────────────────────
class TestDeployedAPIs:
    """배포 환경의 API 정상 동작 테스트"""

    def test_get_subscribers(self):
        """TC-DEPLOY-02-01: GET /api/subscribers 정상 응답"""
        res = requests.get(f"{BASE_URL}/api/subscribers", timeout=10)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1, "구독자 데이터가 없습니다"

    def test_subscriber_has_required_fields(self):
        """TC-DEPLOY-02-02: 구독자 객체에 필수 필드 존재"""
        res = requests.get(f"{BASE_URL}/api/subscribers", timeout=10)
        data = res.json()
        required = {"userId", "name", "organization", "plan", "status", "deviceCount"}
        for s in data:
            missing = required - set(s.keys())
            assert not missing, f"누락된 필드: {missing}"

    def test_get_devices_by_user(self):
        """TC-DEPLOY-02-03: GET /api/subscribers/U001/devices 정상 응답"""
        res = requests.get(f"{BASE_URL}/api/subscribers/U001/devices", timeout=10)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_device_has_required_fields(self):
        """TC-DEPLOY-02-04: 디바이스 객체에 필수 필드 존재"""
        res = requests.get(f"{BASE_URL}/api/subscribers/U001/devices", timeout=10)
        data = res.json()
        required = {"deviceId", "type", "model", "location", "status", "lastSeen"}
        for d in data:
            missing = required - set(d.keys())
            assert not missing, f"누락된 필드: {missing}"

    def test_get_device_usage(self):
        """TC-DEPLOY-02-05: GET /api/devices/D001/usage 정상 응답"""
        res = requests.get(f"{BASE_URL}/api/devices/D001/usage", timeout=10)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, dict)

    def test_usage_has_required_fields(self):
        """TC-DEPLOY-02-06: usage 객체에 필수 필드 존재"""
        res = requests.get(f"{BASE_URL}/api/devices/D001/usage", timeout=10)
        data = res.json()
        required = {
            "deviceId", "deviceName", "powerStatus", "lastUsedAt",
            "totalUsageHours", "weeklyUsageCount", "healthStatus",
            "remark", "weeklyUsageTrend"
        }
        missing = required - set(data.keys())
        assert not missing, f"누락된 필드: {missing}"

    def test_weekly_usage_trend_7_days(self):
        """TC-DEPLOY-02-07: weeklyUsageTrend가 7개 요소를 포함"""
        res = requests.get(f"{BASE_URL}/api/devices/D001/usage", timeout=10)
        trend = res.json()["weeklyUsageTrend"]
        assert len(trend) == 7

    def test_nonexistent_user_404(self):
        """TC-DEPLOY-02-08: 존재하지 않는 userId에 404 반환"""
        res = requests.get(f"{BASE_URL}/api/subscribers/NOTEXIST/devices", timeout=10)
        assert res.status_code == 404

    def test_nonexistent_device_404(self):
        """TC-DEPLOY-02-09: 존재하지 않는 deviceId에 404 반환"""
        res = requests.get(f"{BASE_URL}/api/devices/NOTEXIST/usage", timeout=10)
        assert res.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEPLOY-03: 배포 환경에서 검색/필터 동작
# ─────────────────────────────────────────────────────────────────────────────
class TestDeployedSearchFilter:
    """배포 환경에서 검색/필터 기능 동작 테스트"""

    def test_search_by_name(self):
        """TC-DEPLOY-03-01: 이름 검색 동작"""
        res = requests.get(f"{BASE_URL}/api/subscribers", params={"search": "Kim"}, timeout=10)
        data = res.json()
        assert len(data) >= 1
        assert all("kim" in s["name"].lower() for s in data)

    def test_filter_by_status(self):
        """TC-DEPLOY-03-02: 상태 필터 동작"""
        res = requests.get(f"{BASE_URL}/api/subscribers", params={"status": "Active"}, timeout=10)
        data = res.json()
        assert len(data) >= 1
        assert all(s["status"] == "Active" for s in data)

    def test_empty_devices_user(self):
        """TC-DEPLOY-03-03: 가전 없는 사용자(U005)에 빈 리스트 반환"""
        res = requests.get(f"{BASE_URL}/api/subscribers/U005/devices", timeout=10)
        assert res.status_code == 200
        assert res.json() == []


# ─────────────────────────────────────────────────────────────────────────────
# TC-DEPLOY-04: 데이터 일관성 (배포 환경)
# ─────────────────────────────────────────────────────────────────────────────
class TestDeployedDataConsistency:
    """배포 환경에서 데이터 일관성 테스트"""

    def test_subscriber_count_matches_expected(self):
        """TC-DEPLOY-04-01: 구독자 수가 예상대로 5명"""
        res = requests.get(f"{BASE_URL}/api/subscribers", timeout=10)
        assert len(res.json()) == 5

    def test_device_count_matches_subscriber(self):
        """TC-DEPLOY-04-02: 구독자의 deviceCount와 실제 devices 수 일치"""
        subs = requests.get(f"{BASE_URL}/api/subscribers", timeout=10).json()
        for s in subs:
            devices = requests.get(
                f"{BASE_URL}/api/subscribers/{s['userId']}/devices", timeout=10
            ).json()
            assert s["deviceCount"] == len(devices), (
                f"userId={s['userId']}: deviceCount={s['deviceCount']}, actual={len(devices)}"
            )

    def test_all_devices_have_usage(self):
        """TC-DEPLOY-04-03: 모든 디바이스에 usage 데이터 존재"""
        subs = requests.get(f"{BASE_URL}/api/subscribers", timeout=10).json()
        for s in subs:
            devices = requests.get(
                f"{BASE_URL}/api/subscribers/{s['userId']}/devices", timeout=10
            ).json()
            for d in devices:
                usage_res = requests.get(
                    f"{BASE_URL}/api/devices/{d['deviceId']}/usage", timeout=10
                )
                assert usage_res.status_code == 200, (
                    f"deviceId={d['deviceId']}의 usage 없음"
                )
