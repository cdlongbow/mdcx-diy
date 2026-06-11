import asyncio
import random
import time


class AdaptiveRequestThrottle:
    """自适应请求限流器.

    根据请求结果动态调整请求间隔和惩罚等级:
    - 正常响应: 逐步恢复到基础间隔
    - 被限流(429等): 升级惩罚等级, 增加请求间隔和冷却时间
    - 同一波限流: 维持冷却但不连续升级

    适用于任何受速率限制的 API, 如 Amazon、TMDB、翻译引擎等.
    """

    def __init__(
        self,
        *,
        base_spacing: float,
        max_spacing: float,
        cooldown_base: float,
        cooldown_max: float,
        throttle_burst_window: float = 2.2,
        same_burst_extension: float | None = None,
    ):
        self.base_spacing = max(float(base_spacing), 0.0)
        self.max_spacing = max(float(max_spacing), self.base_spacing)
        self.cooldown_base = max(float(cooldown_base), 0.0)
        self.cooldown_max = max(float(cooldown_max), self.cooldown_base)
        self.throttle_burst_window = max(float(throttle_burst_window), 0.0)
        default_extension = max(self.base_spacing * 3, self.cooldown_base * 0.5)
        extension = default_extension if same_burst_extension is None else same_burst_extension
        self.same_burst_extension = min(self.cooldown_max, max(float(extension), 0.0))
        self._lock = asyncio.Lock()
        self._next_allowed_at = 0.0
        self._request_spacing = self.base_spacing
        self._penalty_level = 0
        self._cooldown_until = 0.0
        self._burst_until = 0.0
        self._last_penalty_at = 0.0

    async def wait_turn(self) -> float:
        delay = 0.0
        async with self._lock:
            now = time.monotonic()
            delay = max(self._next_allowed_at - now, 0.0)
            scheduled_at = max(now, self._next_allowed_at)
            jitter = random.uniform(0.0, min(max(self._request_spacing * 0.15, 0.0), 0.08))
            self._next_allowed_at = scheduled_at + self._request_spacing + jitter
        if delay > 0:
            await asyncio.sleep(delay)
        return delay

    async def register_result(self, *, throttled: bool) -> tuple[float, int, bool]:
        cooldown = 0.0
        escalated = False
        async with self._lock:
            now = time.monotonic()
            if throttled:
                same_burst = now <= self._burst_until
                if same_burst:
                    cooldown = max(self._cooldown_until - now, 0.0)
                    if cooldown <= 0:
                        cooldown = self.same_burst_extension
                    self._cooldown_until = max(self._cooldown_until, now + cooldown)
                    self._burst_until = max(self._burst_until, self._cooldown_until + self.throttle_burst_window)
                    self._next_allowed_at = max(self._next_allowed_at, self._cooldown_until)
                else:
                    escalated = True
                    self._penalty_level = min(self._penalty_level + 1, 6)
                    growth_base = self._request_spacing if self._request_spacing > 0 else max(self.base_spacing, 0.12)
                    self._request_spacing = min(self.max_spacing, max(self.base_spacing, growth_base * 1.65))
                    cooldown = min(self.cooldown_max, self.cooldown_base * (1.8 ** (self._penalty_level - 1)))
                    cooldown += random.uniform(0.1, 0.5)
                    self._cooldown_until = now + cooldown
                    self._burst_until = self._cooldown_until + self.throttle_burst_window
                    self._last_penalty_at = now
                    self._next_allowed_at = max(self._next_allowed_at, self._cooldown_until)
            else:
                if self._penalty_level > 0:
                    self._penalty_level -= 1
                if self._request_spacing > self.base_spacing:
                    self._request_spacing = max(self.base_spacing, self._request_spacing * 0.82)
                else:
                    self._request_spacing = self.base_spacing
                if (
                    self._penalty_level == 0
                    and self._request_spacing == self.base_spacing
                    and now >= self._cooldown_until
                ):
                    self._cooldown_until = 0.0
                    self._burst_until = 0.0
                    self._last_penalty_at = 0.0
        return cooldown, self._penalty_level, escalated

    async def reset(self):
        async with self._lock:
            self._next_allowed_at = 0.0
            self._request_spacing = self.base_spacing
            self._penalty_level = 0
            self._cooldown_until = 0.0
            self._burst_until = 0.0
            self._last_penalty_at = 0.0
