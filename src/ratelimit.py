import threading
import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    """스레드 안전 슬라이딩 윈도우 속도 제한기.

    key(예: 클라이언트 IP)별로 window 초 내 이벤트 수를 세어 max_events를
    초과하면 제한 상태로 판단한다. 관리자 로그인 무차별 대입 완화에 사용.
    """

    def __init__(self, max_events: int, window_seconds: int):
        self.max_events = max_events
        self.window = window_seconds
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def _prune(self, dq: deque, now: float):
        while dq and now - dq[0] > self.window:
            dq.popleft()

    def is_limited(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            dq = self._events[key]
            self._prune(dq, now)
            return len(dq) >= self.max_events

    def record(self, key: str):
        now = time.time()
        with self._lock:
            dq = self._events[key]
            self._prune(dq, now)
            dq.append(now)

    def reset(self, key: str):
        with self._lock:
            self._events.pop(key, None)


# 관리자 로그인 실패 제한기: 5분 내 10회 실패 시 이후 요청을 일시 차단.
# 프록시 뒤에서는 remote_addr가 프록시 IP로 공유될 수 있어 사실상 전역 제한으로
# 동작하며, 성공 로그인 시 reset으로 카운터를 비운다.
login_limiter = SlidingWindowLimiter(max_events=10, window_seconds=300)
