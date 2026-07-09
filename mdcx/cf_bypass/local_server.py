import asyncio
import logging
import os
import socket
import sys
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)
LOCAL_BYPASS_HOST = "127.0.0.1"
LOCAL_BYPASS_PORT_RANGE = (18000, 18999)
SERVER_START_TIMEOUT = 60
HEALTH_CHECK_INTERVAL = 0.5
BROWSER_DOWNLOAD_TIMEOUT = 300


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LOCAL_BYPASS_HOST, 0))
        return s.getsockname()[1]


class LocalBypassServer:
    def __init__(self, log_fn: Callable[[str], None] | None = None):
        self._process: asyncio.subprocess.Process | None = None
        self._port: int = 0
        self._url: str = ""
        self._started = False
        self._closing = False
        self._log_fn = log_fn or (lambda msg: logger.info(msg))
        self._dependency_checked = False
        self._dependency_ok = False
        self._dependency_error = ""

    def _log(self, msg: str) -> None:
        self._log_fn(f"[本地Bypass] {msg}")

    @property
    def url(self) -> str:
        return self._url

    @property
    def is_running(self) -> bool:
        return self._started and self._process is not None and self._process.returncode is None

    def check_dependencies(self) -> tuple[bool, str]:
        if self._dependency_checked:
            return self._dependency_ok, self._dependency_error

        missing = []
        try:
            import cloakbrowser  # noqa: F401
        except ImportError:
            missing.append("cloakbrowser")

        try:
            import cf_bypasser  # noqa: F401
        except ImportError:
            missing.append("cf_bypasser")

        if missing:
            self._dependency_ok = False
            self._dependency_error = (
                f"缺少依赖: {', '.join(missing)}\n"
                f"请运行: pip install {' '.join(missing)}"
            )
        else:
            self._dependency_ok = True
            self._dependency_error = ""

        self._dependency_checked = True
        return self._dependency_ok, self._dependency_error

    async def ensure_browser(self) -> tuple[bool, str]:
        try:
            import cloakbrowser as cb
            self._log("检查 Chromium 浏览器...")
            loop = asyncio.get_running_loop()
            binary_path = await loop.run_in_executor(
                None, lambda: cb.ensure_binary()
            )
            self._log(f"Chromium 就绪: {binary_path}")
            return True, ""
        except Exception as e:
            return False, f"浏览器下载失败: {e}"

    async def start(self) -> tuple[bool, str]:
        if self.is_running:
            return True, self._url

        deps_ok, deps_error = self.check_dependencies()
        if not deps_ok:
            return False, deps_error

        browser_ok, browser_error = await self.ensure_browser()
        if not browser_ok:
            return False, browser_error

        self._port = _find_free_port()
        self._url = f"http://{LOCAL_BYPASS_HOST}:{self._port}"

        os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")
        os.environ.setdefault(
            "CLOAKBROWSER_DOWNLOAD_URL",
            "https://v6.gh-proxy.com/https://github.com/CloakHQ/cloakbrowser/releases/download",
        )

        self._log(f"启动本地 Bypass 服务 {self._url} ...")

        try:
            self._process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "uvicorn",
                "cf_bypasser.server.app:create_app",
                "--factory",
                "--host", LOCAL_BYPASS_HOST,
                "--port", str(self._port),
                "--log-level", "warning",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return False, (
                "未找到 uvicorn，请安装: pip install uvicorn fastapi"
            )
        except Exception as e:
            return False, f"启动子进程失败: {e}"

        ready, error = await self._wait_ready()
        if not ready:
            await self.stop()
            return False, error

        self._started = True
        self._log(f"Bypass 服务已就绪: {self._url}")
        return True, self._url

    async def _wait_ready(self, timeout: int = SERVER_START_TIMEOUT) -> tuple[bool, str]:
        import httpx
        deadline = time.monotonic() + timeout
        last_error = ""
        while time.monotonic() < deadline:
            if self._process and self._process.returncode is not None:
                stderr_output = ""
                if self._process.stderr:
                    try:
                        stderr_output = (await self._process.stderr.read()).decode("utf-8", errors="replace")
                    except Exception:
                        pass
                return False, f"服务进程异常退出 (code={self._process.returncode}): {stderr_output[:500]}"

            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        f"{self._url}/cache/stats",
                        timeout=5,
                    )
                    if resp.status_code == 200:
                        return True, ""
            except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
                last_error = str(e)

            await asyncio.sleep(HEALTH_CHECK_INTERVAL)

        return False, f"服务启动超时 ({SERVER_START_TIMEOUT}s): {last_error}"

    async def stop(self) -> None:
        if self._closing:
            return
        self._closing = True

        if self._process is None:
            self._started = False
            return

        self._log("正在停止 Bypass 服务...")

        try:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self._process.kill()
                await asyncio.wait_for(self._process.wait(), timeout=3)
        except ProcessLookupError:
            pass
        except Exception as e:
            self._log(f"停止服务异常: {e}")

        self._process = None
        self._started = False
        self._url = ""
        self._port = 0
        self._log("Bypass 服务已停止")
