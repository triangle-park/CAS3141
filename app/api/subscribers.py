from fastapi import APIRouter, HTTPException, Query
from app.data.dummy_data import subscribers, devices_by_user

router = APIRouter()
SEARCHABLE_FIELDS = ("userId", "name", "plan", "status")
DEVICE_SEARCHABLE_FIELDS = ("deviceId", "type", "model", "location", "status")


def _contains(value: str, keyword: str) -> bool:
    return keyword in value.lower()


def _subscriber_exists(user_id: str) -> bool:
    return any(subscriber["userId"] == user_id for subscriber in subscribers)


# =============================================================================
# TODO [요구사항 #1]: GET /api/subscribers
# =============================================================================
# 전체 구독 사용자 목록을 반환하는 엔드포인트를 구현하세요.
#
# - HTTP Method: GET
# - Path: /subscribers
# - 응답: subscribers 리스트 전체를 JSON으로 반환
# - 참고: dummy_data.py의 subscribers 변수를 활용하세요.
# =============================================================================
@router.get("/subscribers")
def get_subscribers(
    search: str | None = Query(default=None),
    q: str | None = Query(default=None),
    userId: str | None = Query(default=None),
    name: str | None = Query(default=None),
    plan: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    # subscribers 리스트 전체를 반환
    filtered_subscribers = subscribers
    search_keyword = (search or q or "").strip().lower()

    if search_keyword:
        filtered_subscribers = [
            subscriber
            for subscriber in filtered_subscribers
            if any(
                _contains(str(subscriber[field]), search_keyword)
                for field in SEARCHABLE_FIELDS
            )
        ]

    if userId:
        keyword = userId.strip().lower()
        filtered_subscribers = [
            subscriber
            for subscriber in filtered_subscribers
            if _contains(subscriber["userId"], keyword)
        ]

    if name:
        keyword = name.strip().lower()
        filtered_subscribers = [
            subscriber
            for subscriber in filtered_subscribers
            if _contains(subscriber["name"], keyword)
        ]

    if plan:
        keyword = plan.strip().lower()
        filtered_subscribers = [
            subscriber
            for subscriber in filtered_subscribers
            if subscriber["plan"].lower() == keyword
        ]

    if status:
        keyword = status.strip().lower()
        filtered_subscribers = [
            subscriber
            for subscriber in filtered_subscribers
            if subscriber["status"].lower() == keyword
        ]

    return filtered_subscribers

# =============================================================================
# TODO [요구사항 #2]: GET /api/subscribers/{user_id}/devices
# =============================================================================
# 특정 사용자의 가전 목록을 반환하는 엔드포인트를 구현하세요.
#
# - HTTP Method: GET
# - Path: /subscribers/{user_id}/devices
# - Path Parameter: user_id (str)
# - 정상 응답: 해당 사용자의 디바이스 리스트 반환
# - 사용자가 존재하지 않는 경우: HTTPException(status_code=404) 반환
# - 가전이 없는 경우: 빈 리스트([]) 반환
# - 참고: devices_by_user 딕셔너리를 활용하세요.
# =============================================================================
@router.get("/subscribers/{user_id}/devices")
def get_devices_by_user(
    user_id: str,
    search: str | None = Query(default=None),
    q: str | None = Query(default=None),
    deviceId: str | None = Query(default=None),
    type: str | None = Query(default=None),
    model: str | None = Query(default=None),
    location: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    # 1. subscribers 리스트에서 user_id가 존재하는지 확인
    # 2. 존재하면 devices_by_user에서 해당 사용자의 디바이스 목록 반환
    # 3. 존재하지 않으면 HTTPException(status_code=404) 발생
    if not _subscriber_exists(user_id):
        raise HTTPException(status_code=404, detail="Subscriber not found")

    filtered_devices = devices_by_user.get(user_id, [])
    search_keyword = (search or q or "").strip().lower()

    if search_keyword:
        filtered_devices = [
            device
            for device in filtered_devices
            if any(
                _contains(str(device[field]), search_keyword)
                for field in DEVICE_SEARCHABLE_FIELDS
            )
        ]

    if deviceId:
        keyword = deviceId.strip().lower()
        filtered_devices = [
            device
            for device in filtered_devices
            if _contains(device["deviceId"], keyword)
        ]

    if type:
        keyword = type.strip().lower()
        filtered_devices = [
            device
            for device in filtered_devices
            if _contains(device["type"], keyword)
        ]

    if model:
        keyword = model.strip().lower()
        filtered_devices = [
            device
            for device in filtered_devices
            if _contains(device["model"], keyword)
        ]

    if location:
        keyword = location.strip().lower()
        filtered_devices = [
            device
            for device in filtered_devices
            if _contains(device["location"], keyword)
        ]

    if status:
        keyword = status.strip().lower()
        filtered_devices = [
            device
            for device in filtered_devices
            if device["status"].lower() == keyword
        ]

    return filtered_devices
