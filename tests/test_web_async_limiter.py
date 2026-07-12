import asyncio
from types import SimpleNamespace

import pytest
from aiolimiter import AsyncLimiter

from mdcx.web_async import AsyncWebClient


def _fake_response(status_code: int = 200, content: bytes = b"ok", headers: dict | None = None, url: str = ""):
    return SimpleNamespace(status_code=status_code, headers=headers or {}, content=content, url=url)


@pytest.mark.asyncio
async def test_request_releases_per_host_limiter(monkeypatch):
    """Regression: request() must release the per-host AsyncLimiter after each call.

    AsyncLimiter.acquire() requires a matching release (or `async with`). The old code
    only called `await limiter.acquire()` without releasing, which leaks a slot and
    hard-deadlocks once the limiter's capacity is exhausted. This test forces a tiny
    real limiter (rate=2, period=100s -> no meaningful regeneration) and fires many
    concurrent requests to the same host; if the limiter is not released, the 3rd
    request deadlocks and the test times out.
    """
    client = AsyncWebClient(timeout=1)
    client.limiters.get = lambda key: AsyncLimiter(2, 100)

    call_count = 0

    async def fake_curl_request(**kwargs):
        nonlocal call_count
        call_count += 1
        return _fake_response(status_code=200, content=b"ok")

    client._curl_request = fake_curl_request

    async def one():
        resp, error = await client.request("GET", "https://example.com/page")
        return resp is not None

    results = await asyncio.wait_for(
        asyncio.gather(*[one() for _ in range(10)]),
        timeout=6,
    )
    assert all(results)
    assert call_count == 10


@pytest.mark.asyncio
async def test_call_bypass_mirror_releases_limiter(monkeypatch):
    """Regression: _call_bypass_mirror must release the 127.0.0.1 limiter after each call."""
    client = AsyncWebClient(timeout=1, cf_bypass_url="http://127.0.0.1:8000")
    client.limiters.get = lambda key: AsyncLimiter(2, 100)

    call_count = 0

    async def fake_curl_request(**kwargs):
        nonlocal call_count
        call_count += 1
        return _fake_response(status_code=200, content=b"<html>ok</html>", headers={"Content-Type": "text/html"})

    client._curl_request = fake_curl_request

    async def one():
        resp, error = await client._call_bypass_mirror(
            method="GET",
            target_url="https://missav.ws/SNOS-LIM/cn",
            headers={"Accept": "text/html"},
            cookies=None,
            use_proxy=False,
            allow_redirects=True,
        )
        return resp is not None and error == ""

    results = await asyncio.wait_for(
        asyncio.gather(*[one() for _ in range(10)]),
        timeout=6,
    )
    assert all(results)
    assert call_count == 10
