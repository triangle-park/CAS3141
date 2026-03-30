"""
=============================================================================
 Frontend UI 테스트 코드 (Test Engineer 작성)
 - 대상: webOS Subscription Operations Dashboard 프론트엔드
 - 테스트 프레임워크: pytest + Selenium
 - 실행 방법:
     1. 서버 실행: cd CAS3141 && uvicorn app.main:app --reload
     2. 테스트 실행: pytest tests/test_frontend.py -v
 - 사전 요구사항:
     pip install selenium
     Chrome + ChromeDriver 설치 필요
=============================================================================
"""
import pytest
import time

# ── Selenium 의존성 체크 ──
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

pytestmark = pytest.mark.skipif(
    not HAS_SELENIUM,
    reason="Selenium이 설치되어 있지 않습니다. pip install selenium"
)

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def browser():
    """Chrome 브라우저 인스턴스 (모듈 단위 공유)"""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(autouse=True)
def load_page(browser):
    """각 테스트 전 메인 페이지 로딩"""
    browser.get(BASE_URL)
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "subscriber-body"))
    )
    # 데이터 로딩 대기
    time.sleep(1)


# ─────────────────────────────────────────────────────────────────────────────
# TC-FE-01: 메인 대시보드 접근 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardAccess:
    """메인 대시보드 접근 및 기본 렌더링 테스트"""

    def test_page_title(self, browser):
        """TC-FE-01-01: 페이지 제목이 올바르게 표시된다"""
        assert "Subscription Management Dashboard" in browser.title

    def test_hero_section_visible(self, browser):
        """TC-FE-01-02: 히어로 섹션이 표시된다"""
        hero = browser.find_element(By.CLASS_NAME, "hero")
        assert hero.is_displayed()

    def test_subscriber_panel_visible(self, browser):
        """TC-FE-01-03: 구독자 패널이 표시된다"""
        panels = browser.find_elements(By.CLASS_NAME, "panel")
        assert len(panels) >= 1

    def test_three_panels_exist(self, browser):
        """TC-FE-01-04: 3개의 패널(Subscriber, Device, Usage)이 존재한다"""
        panels = browser.find_elements(By.CLASS_NAME, "panel")
        assert len(panels) == 3


# ─────────────────────────────────────────────────────────────────────────────
# TC-FE-02: Table 데이터 렌더링 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestTableRendering:
    """테이블 데이터 렌더링 테스트"""

    def test_subscriber_table_has_rows(self, browser):
        """TC-FE-02-01: 구독자 테이블에 데이터 행이 존재한다"""
        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        assert len(rows) >= 1, "구독자 테이블에 데이터가 없습니다"

    def test_subscriber_table_has_5_columns(self, browser):
        """TC-FE-02-02: 구독자 테이블이 5개 컬럼(ID, Name, Plan, Status, Devices)을 갖는다"""
        headers = browser.find_elements(By.CSS_SELECTOR, "#subscriber-table thead th")
        assert len(headers) == 5

    def test_subscriber_table_column_names(self, browser):
        """TC-FE-02-03: 구독자 테이블의 컬럼명이 올바르다"""
        headers = browser.find_elements(By.CSS_SELECTOR, "#subscriber-table thead th")
        expected = ["User ID", "Name", "Plan", "Status", "Devices"]
        actual = [h.text for h in headers]
        assert actual == expected, f"컬럼명 불일치: {actual}"

    def test_subscriber_data_content(self, browser):
        """TC-FE-02-04: 첫 번째 구독자 데이터가 올바르게 렌더링된다"""
        first_row_cells = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr:first-child td")
        assert len(first_row_cells) == 5
        assert first_row_cells[0].text == "U001"  # userId
        assert first_row_cells[1].text == "Kim Minsoo"  # name

    def test_subscriber_row_count(self, browser):
        """TC-FE-02-05: 전체 더미 데이터 수만큼 행이 렌더링된다 (5명)"""
        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        assert len(rows) == 5

    def test_click_subscriber_shows_devices(self, browser):
        """TC-FE-02-06: 구독자 클릭 시 해당 사용자의 가전 목록이 표시된다"""
        first_row = browser.find_element(By.CSS_SELECTOR, "#subscriber-body tr:first-child")
        first_row.click()
        time.sleep(1)

        device_table = browser.find_element(By.ID, "device-table")
        assert device_table.is_displayed(), "디바이스 테이블이 표시되지 않습니다"

        device_rows = browser.find_elements(By.CSS_SELECTOR, "#device-body tr")
        assert len(device_rows) >= 1, "디바이스 테이블에 데이터가 없습니다"

    def test_device_table_has_5_columns(self, browser):
        """TC-FE-02-07: 디바이스 테이블이 5개 컬럼을 갖는다"""
        headers = browser.find_elements(By.CSS_SELECTOR, "#device-table thead th")
        assert len(headers) == 5

    def test_device_table_column_names(self, browser):
        """TC-FE-02-08: 디바이스 테이블의 컬럼명이 올바르다"""
        headers = browser.find_elements(By.CSS_SELECTOR, "#device-table thead th")
        expected = ["Device ID", "Type", "Model", "Location", "Status"]
        actual = [h.text for h in headers]
        assert actual == expected, f"컬럼명 불일치: {actual}"


# ─────────────────────────────────────────────────────────────────────────────
# TC-FE-03: 검색(Search) 및 필터(Filter) 동작
# ─────────────────────────────────────────────────────────────────────────────
class TestSearchAndFilter:
    """검색 및 필터 기능 UI 테스트"""

    def test_subscriber_search_exists(self, browser):
        """TC-FE-03-01: 구독자 검색 입력 필드가 존재한다"""
        search_input = browser.find_element(By.ID, "subscriber-search")
        assert search_input.is_displayed()

    def test_subscriber_status_filter_exists(self, browser):
        """TC-FE-03-02: 구독자 상태 필터 드롭다운이 존재한다"""
        status_filter = browser.find_element(By.ID, "subscriber-status-filter")
        assert status_filter.is_displayed()

    def test_search_filters_realtime(self, browser):
        """TC-FE-03-03: 검색어 입력 시 실시간으로 테이블이 필터링된다"""
        search_input = browser.find_element(By.ID, "subscriber-search")
        search_input.clear()
        search_input.send_keys("Kim")
        time.sleep(0.5)

        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        assert len(rows) >= 1
        # 검색 결과에 "Kim"이 포함되어야 함
        for row in rows:
            text = row.text.lower()
            assert "kim" in text, f"검색 결과에 'Kim'이 없습니다: {row.text}"

    def test_status_filter_active(self, browser):
        """TC-FE-03-04: Active 상태 필터 적용 시 Active만 표시된다"""
        search_input = browser.find_element(By.ID, "subscriber-search")
        search_input.clear()

        select = Select(browser.find_element(By.ID, "subscriber-status-filter"))
        select.select_by_value("Active")
        time.sleep(0.5)

        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        assert len(rows) >= 1
        for row in rows:
            badge = row.find_element(By.CLASS_NAME, "badge")
            assert badge.text == "Active", f"Active 필터 적용 후 다른 상태 발견: {badge.text}"

    def test_status_filter_all(self, browser):
        """TC-FE-03-05: All Status 필터 선택 시 전체 구독자가 표시된다"""
        search_input = browser.find_element(By.ID, "subscriber-search")
        search_input.clear()

        select = Select(browser.find_element(By.ID, "subscriber-status-filter"))
        select.select_by_value("")  # All Status
        time.sleep(0.5)

        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        assert len(rows) == 5

    def test_no_results_message(self, browser):
        """TC-FE-03-06: 검색 결과가 없을 때 안내 메시지가 표시된다"""
        select = Select(browser.find_element(By.ID, "subscriber-status-filter"))
        select.select_by_value("")

        search_input = browser.find_element(By.ID, "subscriber-search")
        search_input.clear()
        search_input.send_keys("ZZZZNOTEXISTUSER")
        time.sleep(0.5)

        empty_state = browser.find_element(By.ID, "subscriber-empty")
        assert empty_state.is_displayed(), "빈 상태 메시지가 표시되지 않습니다"

    def test_device_search_exists(self, browser):
        """TC-FE-03-07: 디바이스 검색 입력 필드가 존재한다"""
        search_input = browser.find_element(By.ID, "device-search")
        assert search_input.is_displayed()

    def test_device_status_filter_exists(self, browser):
        """TC-FE-03-08: 디바이스 상태 필터 드롭다운이 존재한다"""
        status_filter = browser.find_element(By.ID, "device-status-filter")
        assert status_filter.is_displayed()


# ─────────────────────────────────────────────────────────────────────────────
# TC-FE-04: 상태 색상 배지(Status Badge) 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestStatusBadges:
    """상태 색상 배지 렌더링 테스트"""

    def test_badges_exist_in_subscriber_table(self, browser):
        """TC-FE-04-01: 구독자 테이블에 배지가 존재한다"""
        badges = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body .badge")
        assert len(badges) >= 1

    def test_active_badge_green(self, browser):
        """TC-FE-04-02: Active 상태 배지가 초록색(status-active) 클래스를 갖는다"""
        badges = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body .badge")
        active_badges = [b for b in badges if b.text == "Active"]
        assert len(active_badges) >= 1, "Active 배지를 찾을 수 없습니다"
        for badge in active_badges:
            assert "status-active" in badge.get_attribute("class"), \
                "Active 배지에 status-active 클래스가 없습니다"

    def test_paused_badge_blue(self, browser):
        """TC-FE-04-03: Paused 상태 배지가 파란색(status-paused) 클래스를 갖는다"""
        badges = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body .badge")
        paused_badges = [b for b in badges if b.text == "Paused"]
        assert len(paused_badges) >= 1, "Paused 배지를 찾을 수 없습니다"
        for badge in paused_badges:
            assert "status-paused" in badge.get_attribute("class"), \
                "Paused 배지에 status-paused 클래스가 없습니다"

    def test_expired_badge_red(self, browser):
        """TC-FE-04-04: Expired 상태 배지가 빨간색(status-expired) 클래스를 갖는다"""
        badges = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body .badge")
        expired_badges = [b for b in badges if b.text == "Expired"]
        assert len(expired_badges) >= 1, "Expired 배지를 찾을 수 없습니다"
        for badge in expired_badges:
            assert "status-expired" in badge.get_attribute("class"), \
                "Expired 배지에 status-expired 클래스가 없습니다"

    def test_device_status_badges_after_click(self, browser):
        """TC-FE-04-05: 디바이스 테이블에서도 상태 배지가 올바르게 렌더링된다"""
        # U001 클릭 (Online + Offline 디바이스 보유)
        first_row = browser.find_element(By.CSS_SELECTOR, "#subscriber-body tr:first-child")
        first_row.click()
        time.sleep(1)

        badges = browser.find_elements(By.CSS_SELECTOR, "#device-body .badge")
        assert len(badges) >= 1

        for badge in badges:
            text = badge.text
            cls = badge.get_attribute("class")
            if text == "Online":
                assert "status-active" in cls, "Online 배지에 status-active 없음"
            elif text == "Offline":
                assert "status-offline" in cls, "Offline 배지에 status-offline 없음"
            elif text == "Standby":
                assert "status-paused" in cls, "Standby 배지에 status-paused 없음"
            elif text == "Error":
                assert "status-expired" in cls, "Error 배지에 status-expired 없음"


# ─────────────────────────────────────────────────────────────────────────────
# TC-FE-05: Bar Chart 렌더링 확인
# ─────────────────────────────────────────────────────────────────────────────
class TestBarChart:
    """주간 사용량 Bar Chart 렌더링 테스트"""

    def _navigate_to_usage(self, browser):
        """U001 > D001 선택하여 usage 데이터 로딩"""
        first_row = browser.find_element(By.CSS_SELECTOR, "#subscriber-body tr:first-child")
        first_row.click()
        time.sleep(1)

        device_row = browser.find_element(By.CSS_SELECTOR, "#device-body tr:first-child")
        device_row.click()
        time.sleep(1)

    def test_usage_detail_shown_after_device_click(self, browser):
        """TC-FE-05-01: 디바이스 클릭 후 usage 상세 정보가 표시된다"""
        self._navigate_to_usage(browser)
        detail = browser.find_element(By.ID, "usage-detail")
        assert detail.is_displayed(), "Usage detail 패널이 표시되지 않습니다"

    def test_chart_container_visible(self, browser):
        """TC-FE-05-02: Bar Chart 컨테이너가 표시된다"""
        self._navigate_to_usage(browser)
        chart = browser.find_element(By.ID, "usage-chart")
        assert chart.is_displayed(), "Chart가 표시되지 않습니다"

    def test_chart_has_7_columns(self, browser):
        """TC-FE-05-03: Bar Chart에 7개의 요일 컬럼이 존재한다"""
        self._navigate_to_usage(browser)
        columns = browser.find_elements(By.CSS_SELECTOR, "#usage-chart .chart-column")
        assert len(columns) == 7, f"차트 컬럼 수: {len(columns)} (기대: 7)"

    def test_chart_day_labels(self, browser):
        """TC-FE-05-04: Bar Chart의 요일 라벨이 Mon~Sun이다"""
        self._navigate_to_usage(browser)
        day_labels = browser.find_elements(By.CSS_SELECTOR, "#usage-chart .chart-day")
        expected = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        actual = [label.text for label in day_labels]
        assert actual == expected, f"요일 라벨 불일치: {actual}"

    def test_chart_bars_exist(self, browser):
        """TC-FE-05-05: 각 컬럼에 Bar 요소가 존재한다"""
        self._navigate_to_usage(browser)
        bars = browser.find_elements(By.CSS_SELECTOR, "#usage-chart .chart-bar")
        assert len(bars) == 7

    def test_chart_values_displayed(self, browser):
        """TC-FE-05-06: 각 Bar 위에 사용량 숫자가 표시된다"""
        self._navigate_to_usage(browser)
        values = browser.find_elements(By.CSS_SELECTOR, "#usage-chart .chart-value")
        assert len(values) == 7
        # D001의 weeklyUsageTrend: [2, 3, 1, 4, 2, 3, 3]
        expected_values = ["2", "3", "1", "4", "2", "3", "3"]
        actual_values = [v.text for v in values]
        assert actual_values == expected_values, f"차트 값 불일치: {actual_values}"

    def test_usage_detail_cards(self, browser):
        """TC-FE-05-07: Usage 상세 카드에 필수 정보가 표시된다"""
        self._navigate_to_usage(browser)
        info_cards = browser.find_elements(By.CSS_SELECTOR, "#usage-info .detail-card")
        assert len(info_cards) == 8, f"Detail 카드 수: {len(info_cards)} (기대: 8)"

        labels = [card.find_element(By.CLASS_NAME, "detail-label").text for card in info_cards]
        expected_labels = [
            "DEVICE ID", "DEVICE NAME", "POWER STATUS", "LAST USED",
            "TOTAL USAGE", "WEEKLY COUNT", "HEALTH STATUS", "REMARK"
        ]
        assert labels == expected_labels, f"카드 라벨 불일치: {labels}"

    def test_no_devices_message(self, browser):
        """TC-FE-05-08: 가전이 없는 사용자(U005) 선택 시 안내 메시지가 표시된다"""
        # U005 (Expired, deviceCount=0) 행 클릭
        rows = browser.find_elements(By.CSS_SELECTOR, "#subscriber-body tr")
        u005_row = None
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells and cells[0].text == "U005":
                u005_row = row
                break

        assert u005_row is not None, "U005 행을 찾을 수 없습니다"
        u005_row.click()
        time.sleep(1)

        device_empty = browser.find_element(By.ID, "device-empty")
        assert device_empty.is_displayed(), "빈 디바이스 안내 메시지가 표시되지 않습니다"
