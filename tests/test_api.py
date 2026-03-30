"""
=============================================================================
 Backend API 테스트 코드 (Test Engineer 작성)
 - 대상: webOS Subscription Operations Dashboard
 - 테스트 프레임워크: pytest + httpx (FastAPI TestClient)
 - 실행 방법:
     cd CAS3141
     pip install pytest httpx
     pytest tests/ -v
=============================================================================
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.dummy_data import subscribers, devices_by_user, usage_by_device


client = TestClient(app)


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-01: GET /health — 서버 상태 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestHealth:
    """서버 헬스체크 관련 테스트"""

    def test_health_returns_200(self):
        """TC-BE-01-01: /health 엔드포인트가 200 OK를 반환한다"""
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_response_body(self):
        """TC-BE-01-02: /health 응답에 status: ok 가 포함된다"""
        res = client.get("/health")
        data = res.json()
        assert data["status"] == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-02: GET /api/subscribers — 전체 구독 사용자 목록 조회
# ─────────────────────────────────────────────────────────────────────────────
class TestGetSubscribers:
    """구독 사용자 목록 API 테스트"""

    def test_returns_200(self):
        """TC-BE-02-01: 정상 요청 시 200 OK를 반환한다"""
        res = client.get("/api/subscribers")
        assert res.status_code == 200

    def test_returns_list(self):
        """TC-BE-02-02: 응답이 리스트(배열) 형식이다"""
        res = client.get("/api/subscribers")
        data = res.json()
        assert isinstance(data, list)

    def test_returns_all_subscribers(self):
        """TC-BE-02-03: 필터 없이 호출 시 전체 구독자를 반환한다"""
        res = client.get("/api/subscribers")
        data = res.json()
        assert len(data) == len(subscribers)

    def test_subscriber_has_required_fields(self):
        """TC-BE-02-04: 각 구독자 객체에 필수 필드가 모두 존재한다"""
        res = client.get("/api/subscribers")
        data = res.json()
        required_fields = {"userId", "name", "organization", "plan", "status", "deviceCount"}
        for subscriber in data:
            missing = required_fields - set(subscriber.keys())
            assert not missing, f"누락된 필드: {missing} (userId: {subscriber.get('userId')})"

    def test_subscriber_field_types(self):
        """TC-BE-02-05: 각 필드의 데이터 타입이 명세와 일치한다"""
        res = client.get("/api/subscribers")
        data = res.json()
        for s in data:
            assert isinstance(s["userId"], str), f"userId 타입 오류: {type(s['userId'])}"
            assert isinstance(s["name"], str), f"name 타입 오류: {type(s['name'])}"
            assert isinstance(s["organization"], str), f"organization 타입 오류"
            assert isinstance(s["plan"], str), f"plan 타입 오류"
            assert isinstance(s["status"], str), f"status 타입 오류"
            assert isinstance(s["deviceCount"], (int, float)), f"deviceCount 타입 오류: {type(s['deviceCount'])}"

    def test_subscriber_plan_values(self):
        """TC-BE-02-06: plan 필드가 허용된 값만 포함한다 (Premium/Basic/Family)"""
        res = client.get("/api/subscribers")
        allowed_plans = {"Premium", "Basic", "Family"}
        for s in res.json():
            assert s["plan"] in allowed_plans, f"유효하지 않은 plan: {s['plan']} (userId: {s['userId']})"

    def test_subscriber_status_values(self):
        """TC-BE-02-07: status 필드가 허용된 값만 포함한다 (Active/Paused/Expired)"""
        res = client.get("/api/subscribers")
        allowed_statuses = {"Active", "Paused", "Expired"}
        for s in res.json():
            assert s["status"] in allowed_statuses, f"유효하지 않은 status: {s['status']} (userId: {s['userId']})"

    def test_device_count_non_negative(self):
        """TC-BE-02-08: deviceCount가 0 이상의 정수이다"""
        res = client.get("/api/subscribers")
        for s in res.json():
            assert s["deviceCount"] >= 0, f"deviceCount 음수: {s['deviceCount']} (userId: {s['userId']})"


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-02-S: GET /api/subscribers 검색/필터 테스트
# ─────────────────────────────────────────────────────────────────────────────
class TestSubscriberSearchFilter:
    """구독자 검색 및 필터 기능 테스트"""

    def test_search_by_name(self):
        """TC-BE-02-S01: name 검색이 정상 동작한다"""
        res = client.get("/api/subscribers", params={"search": "Kim"})
        data = res.json()
        assert len(data) >= 1
        assert all("kim" in s["name"].lower() for s in data)

    def test_search_by_user_id(self):
        """TC-BE-02-S02: userId 검색이 정상 동작한다"""
        res = client.get("/api/subscribers", params={"search": "U001"})
        data = res.json()
        assert len(data) >= 1
        assert any(s["userId"] == "U001" for s in data)

    def test_filter_by_status_active(self):
        """TC-BE-02-S03: status=Active 필터가 정상 동작한다"""
        res = client.get("/api/subscribers", params={"status": "Active"})
        data = res.json()
        assert len(data) >= 1
        assert all(s["status"] == "Active" for s in data)

    def test_filter_by_status_paused(self):
        """TC-BE-02-S04: status=Paused 필터가 정상 동작한다"""
        res = client.get("/api/subscribers", params={"status": "Paused"})
        data = res.json()
        assert len(data) >= 1
        assert all(s["status"] == "Paused" for s in data)

    def test_filter_by_status_expired(self):
        """TC-BE-02-S05: status=Expired 필터가 정상 동작한다"""
        res = client.get("/api/subscribers", params={"status": "Expired"})
        data = res.json()
        assert len(data) >= 1
        assert all(s["status"] == "Expired" for s in data)

    def test_filter_by_plan(self):
        """TC-BE-02-S06: plan 필터가 정상 동작한다"""
        res = client.get("/api/subscribers", params={"plan": "Premium"})
        data = res.json()
        assert len(data) >= 1
        assert all(s["plan"] == "Premium" for s in data)

    def test_search_no_results(self):
        """TC-BE-02-S07: 존재하지 않는 검색어에 빈 리스트를 반환한다"""
        res = client.get("/api/subscribers", params={"search": "ZZZZNOTEXIST"})
        data = res.json()
        assert res.status_code == 200
        assert data == []

    def test_search_case_insensitive(self):
        """TC-BE-02-S08: 검색이 대소문자를 구분하지 않는다"""
        res_lower = client.get("/api/subscribers", params={"search": "kim"})
        res_upper = client.get("/api/subscribers", params={"search": "KIM"})
        assert len(res_lower.json()) == len(res_upper.json())


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-03: GET /api/subscribers/{userId}/devices — 사용자별 가전 목록
# ─────────────────────────────────────────────────────────────────────────────
class TestGetDevicesByUser:
    """사용자별 가전 목록 API 테스트"""

    @pytest.mark.parametrize("user_id", ["U001", "U002", "U003", "U004"])
    def test_returns_200_for_existing_user(self, user_id):
        """TC-BE-03-01: 존재하는 userId에 대해 200을 반환한다"""
        res = client.get(f"/api/subscribers/{user_id}/devices")
        assert res.status_code == 200

    def test_returns_list(self):
        """TC-BE-03-02: 응답이 리스트 형식이다"""
        res = client.get("/api/subscribers/U001/devices")
        assert isinstance(res.json(), list)

    def test_device_count_matches(self):
        """TC-BE-03-03: 반환된 디바이스 수가 더미 데이터와 일치한다"""
        res = client.get("/api/subscribers/U001/devices")
        data = res.json()
        expected_count = len(devices_by_user.get("U001", []))
        assert len(data) == expected_count

    def test_device_has_required_fields(self):
        """TC-BE-03-04: 각 디바이스 객체에 필수 필드가 존재한다"""
        res = client.get("/api/subscribers/U001/devices")
        required_fields = {"deviceId", "type", "model", "location", "status", "lastSeen"}
        for device in res.json():
            missing = required_fields - set(device.keys())
            assert not missing, f"누락된 필드: {missing} (deviceId: {device.get('deviceId')})"

    def test_device_field_types(self):
        """TC-BE-03-05: 디바이스 필드 데이터 타입이 명세와 일치한다"""
        res = client.get("/api/subscribers/U001/devices")
        for d in res.json():
            assert isinstance(d["deviceId"], str)
            assert isinstance(d["type"], str)
            assert isinstance(d["model"], str)
            assert isinstance(d["location"], str)
            assert isinstance(d["status"], str)
            assert isinstance(d["lastSeen"], str)

    def test_device_status_values(self):
        """TC-BE-03-06: device status가 허용된 값이다 (Online/Offline/Standby/Error)"""
        allowed = {"Online", "Offline", "Standby", "Error"}
        for user_id in ["U001", "U002", "U003", "U004"]:
            res = client.get(f"/api/subscribers/{user_id}/devices")
            for d in res.json():
                assert d["status"] in allowed, f"유효하지 않은 status: {d['status']} (deviceId: {d['deviceId']})"

    def test_empty_devices_for_user_with_no_devices(self):
        """TC-BE-03-07: 가전이 없는 사용자(U005)에 대해 빈 리스트를 반환한다"""
        res = client.get("/api/subscribers/U005/devices")
        assert res.status_code == 200
        assert res.json() == []

    def test_404_for_nonexistent_user(self):
        """TC-BE-03-08: 존재하지 않는 userId 요청 시 404를 반환한다"""
        res = client.get("/api/subscribers/NONEXISTENT/devices")
        assert res.status_code == 404

    def test_404_response_has_detail(self):
        """TC-BE-03-09: 404 응답에 detail 메시지가 포함된다"""
        res = client.get("/api/subscribers/NONEXISTENT/devices")
        data = res.json()
        assert "detail" in data


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-04: GET /api/devices/{deviceId}/usage — 가전 사용 현황 조회
# ─────────────────────────────────────────────────────────────────────────────
class TestGetDeviceUsage:
    """가전 사용 현황 API 테스트"""

    @pytest.mark.parametrize("device_id", ["D001", "D002", "D003", "D004", "D005", "D006", "D007", "D008"])
    def test_returns_200_for_existing_device(self, device_id):
        """TC-BE-04-01: 존재하는 deviceId에 대해 200을 반환한다"""
        res = client.get(f"/api/devices/{device_id}/usage")
        assert res.status_code == 200

    def test_returns_object(self):
        """TC-BE-04-02: 응답이 객체(dict) 형식이다 (배열 아님)"""
        res = client.get("/api/devices/D001/usage")
        data = res.json()
        assert isinstance(data, dict)
        assert not isinstance(data, list)

    def test_usage_has_required_fields(self):
        """TC-BE-04-03: usage 객체에 필수 필드가 모두 존재한다"""
        res = client.get("/api/devices/D001/usage")
        data = res.json()
        required_fields = {
            "deviceId", "deviceName", "powerStatus", "lastUsedAt",
            "totalUsageHours", "weeklyUsageCount", "healthStatus",
            "remark", "weeklyUsageTrend"
        }
        missing = required_fields - set(data.keys())
        assert not missing, f"누락된 필드: {missing}"

    def test_usage_field_types(self):
        """TC-BE-04-04: usage 필드 데이터 타입이 명세와 일치한다"""
        res = client.get("/api/devices/D001/usage")
        d = res.json()
        assert isinstance(d["deviceId"], str)
        assert isinstance(d["deviceName"], str)
        assert isinstance(d["powerStatus"], str)
        assert isinstance(d["lastUsedAt"], str)
        assert isinstance(d["totalUsageHours"], (int, float))
        assert isinstance(d["weeklyUsageCount"], (int, float))
        assert isinstance(d["healthStatus"], str)
        assert isinstance(d["remark"], str)
        assert isinstance(d["weeklyUsageTrend"], list)

    def test_weekly_usage_trend_has_7_days(self):
        """TC-BE-04-05: weeklyUsageTrend가 정확히 7개(Mon~Sun) 요소를 포함한다"""
        res = client.get("/api/devices/D001/usage")
        trend = res.json()["weeklyUsageTrend"]
        assert len(trend) == 7, f"weeklyUsageTrend 길이: {len(trend)} (기대: 7)"

    def test_weekly_usage_trend_all_numbers(self):
        """TC-BE-04-06: weeklyUsageTrend의 각 요소가 숫자이다"""
        res = client.get("/api/devices/D001/usage")
        trend = res.json()["weeklyUsageTrend"]
        for i, val in enumerate(trend):
            assert isinstance(val, (int, float)), f"weeklyUsageTrend[{i}] 타입 오류: {type(val)}"

    def test_weekly_usage_trend_non_negative(self):
        """TC-BE-04-07: weeklyUsageTrend의 각 요소가 0 이상이다"""
        for device_id in usage_by_device:
            res = client.get(f"/api/devices/{device_id}/usage")
            trend = res.json()["weeklyUsageTrend"]
            for i, val in enumerate(trend):
                assert val >= 0, f"음수 사용량: device={device_id}, day={i}, value={val}"

    def test_total_usage_hours_non_negative(self):
        """TC-BE-04-08: totalUsageHours가 0 이상이다"""
        for device_id in usage_by_device:
            res = client.get(f"/api/devices/{device_id}/usage")
            assert res.json()["totalUsageHours"] >= 0

    def test_device_id_matches_request(self):
        """TC-BE-04-09: 응답의 deviceId가 요청한 deviceId와 일치한다"""
        for device_id in ["D001", "D002", "D003"]:
            res = client.get(f"/api/devices/{device_id}/usage")
            assert res.json()["deviceId"] == device_id

    def test_404_for_nonexistent_device(self):
        """TC-BE-04-10: 존재하지 않는 deviceId 요청 시 404를 반환한다"""
        res = client.get("/api/devices/NONEXISTENT/usage")
        assert res.status_code == 404

    def test_404_response_has_detail(self):
        """TC-BE-04-11: 404 응답에 detail 메시지가 포함된다"""
        res = client.get("/api/devices/NONEXISTENT/usage")
        data = res.json()
        assert "detail" in data

    def test_power_status_values(self):
        """TC-BE-04-12: powerStatus가 허용된 값이다"""
        allowed = {"On", "Off", "Standby", "Error", "Cleaning"}
        for device_id in usage_by_device:
            res = client.get(f"/api/devices/{device_id}/usage")
            ps = res.json()["powerStatus"]
            assert ps in allowed, f"유효하지 않은 powerStatus: {ps} (deviceId: {device_id})"

    def test_health_status_values(self):
        """TC-BE-04-13: healthStatus가 허용된 값이다 (Normal/Warning)"""
        allowed = {"Normal", "Warning"}
        for device_id in usage_by_device:
            res = client.get(f"/api/devices/{device_id}/usage")
            hs = res.json()["healthStatus"]
            assert hs in allowed, f"유효하지 않은 healthStatus: {hs} (deviceId: {device_id})"


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-05: 데이터 일관성 (Cross-API) 검증
# ─────────────────────────────────────────────────────────────────────────────
class TestDataConsistency:
    """API 간 데이터 일관성 테스트"""

    def test_subscriber_device_count_matches_devices_api(self):
        """TC-BE-05-01: subscriber의 deviceCount가 실제 devices API 결과 수와 일치한다"""
        subs = client.get("/api/subscribers").json()
        for s in subs:
            devices_res = client.get(f"/api/subscribers/{s['userId']}/devices")
            if devices_res.status_code == 200:
                actual_count = len(devices_res.json())
                assert s["deviceCount"] == actual_count, (
                    f"userId={s['userId']}: deviceCount={s['deviceCount']}, "
                    f"실제 devices 수={actual_count}"
                )

    def test_all_devices_have_usage_data(self):
        """TC-BE-05-02: 모든 디바이스에 대해 usage 데이터가 존재한다"""
        subs = client.get("/api/subscribers").json()
        for s in subs:
            devices_res = client.get(f"/api/subscribers/{s['userId']}/devices")
            if devices_res.status_code == 200:
                for d in devices_res.json():
                    usage_res = client.get(f"/api/devices/{d['deviceId']}/usage")
                    assert usage_res.status_code == 200, (
                        f"deviceId={d['deviceId']}의 usage 데이터가 없습니다"
                    )

    def test_device_name_consistent_with_model(self):
        """TC-BE-05-03: usage의 deviceName과 device의 model이 일치한다"""
        for user_id, devices in devices_by_user.items():
            for device in devices:
                usage_res = client.get(f"/api/devices/{device['deviceId']}/usage")
                if usage_res.status_code == 200:
                    usage = usage_res.json()
                    assert usage["deviceName"] == device["model"], (
                        f"deviceId={device['deviceId']}: "
                        f"usage.deviceName='{usage['deviceName']}' != "
                        f"device.model='{device['model']}'"
                    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-BE-06: 대시보드 메인 페이지 (HTML) 테스트
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardPage:
    """메인 대시보드 HTML 렌더링 테스트"""

    def test_root_returns_200(self):
        """TC-BE-06-01: GET / 요청 시 200을 반환한다"""
        res = client.get("/")
        assert res.status_code == 200

    def test_root_returns_html(self):
        """TC-BE-06-02: 응답 Content-Type이 HTML이다"""
        res = client.get("/")
        assert "text/html" in res.headers.get("content-type", "")

    def test_html_contains_title(self):
        """TC-BE-06-03: HTML에 대시보드 제목이 포함된다"""
        res = client.get("/")
        assert "Subscription Management Dashboard" in res.text

    def test_html_contains_subscriber_table(self):
        """TC-BE-06-04: HTML에 구독자 테이블 요소가 있다"""
        res = client.get("/")
        assert 'id="subscriber-table"' in res.text

    def test_html_contains_device_table(self):
        """TC-BE-06-05: HTML에 디바이스 테이블 요소가 있다"""
        res = client.get("/")
        assert 'id="device-table"' in res.text

    def test_html_contains_usage_chart(self):
        """TC-BE-06-06: HTML에 usage 차트 요소가 있다"""
        res = client.get("/")
        assert 'id="usage-chart"' in res.text

    def test_html_includes_app_js(self):
        """TC-BE-06-07: HTML에 app.js 스크립트가 포함된다"""
        res = client.get("/")
        assert "app.js" in res.text

    def test_html_includes_style_css(self):
        """TC-BE-06-08: HTML에 style.css 스타일시트가 포함된다"""
        res = client.get("/")
        assert "style.css" in res.text
