import asyncio
import atexit
import ipaddress
import json
import logging
import os
import secrets
import socket
import sys
import threading
import time
from collections.abc import Callable
from urllib.parse import parse_qs, urlparse

from mdcx.consts import IS_PYINSTALLER

logger = logging.getLogger(__name__)
LOCAL_BYPASS_HOST = "127.0.0.1"
SERVER_START_TIMEOUT = 60
HEALTH_CHECK_INTERVAL = 0.5
BROWSER_DOWNLOAD_TIMEOUT = 300

# 本地 bypass 服务的一次性鉴权 token 通过该环境变量传递给(子进程或进程内)的 ASGI 应用
BYPASS_TOKEN_ENV = "MDCX_BYPASS_TOKEN"

# 这些端点接受 ?url= 参数, 需做 SSRF 防护(禁止回源到环回/私网/链路本地地址)
_URL_PARAM_ENDPOINTS = ("/cookies", "/solve", "/html", "/mirror")


def _is_safe_target(url: str) -> bool:
    """SSRF 防护: 仅允许 http/https, 且解析后的 IP 不能是环回/私网/链路本地/保留/多播地址。"""
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        return False
    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if addr.is_loopback or addr.is_private or addr.is_link_local or addr.is_reserved or addr.is_multicast:
            return False
    return True


async def _send_json(send, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send({"type": "http.response.body", "body": body})


def create_protected_app():
    """包裹 cf_bypasser 的 create_app, 增加一次性 token 鉴权与 SSRF 防护。

    不修改外部依赖 cf_bypasser 的源码, 仅在其外层套一层 ASGI 中间件; token 取自
    BYPASS_TOKEN_ENV 环境变量(由 LocalBypassServer.start 生成并写入)。
    """
    from cf_bypasser.server.app import create_app

    app = create_app()
    expected_token = os.environ.get(BYPASS_TOKEN_ENV, "")

    async def middleware(scope, receive, send):
        if scope["type"] != "http":
            await app(scope, receive, send)
            return

        # 0) 未配置 token 时直接拒绝(失败闭合), 避免空 token 被 compare_digest 误判通过
        if not expected_token:
            await _send_json(send, 401, {"error": "unauthorized"})
            return

        # 1) token 校验: Authorization: Bearer <tok> 或 ?token=<tok>
        headers = {k.lower(): v for k, v in scope.get("headers", [])}
        auth = headers.get(b"authorization", b"").decode("latin-1")
        token_ok = False
        if auth.startswith("Bearer "):
            token_ok = secrets.compare_digest(auth[7:].strip(), expected_token)
        if not token_ok:
            qs = parse_qs(scope.get("query_string", b"").decode("latin-1"))
            token_ok = secrets.compare_digest(qs.get("token", [""])[0], expected_token)
        if not token_ok:
            await _send_json(send, 401, {"error": "unauthorized"})
            return

        # 2) SSRF 防护: 检查 ?url= 参数
        path = scope.get("path", "")
        if any(path.startswith(p) for p in _URL_PARAM_ENDPOINTS):
            qs = parse_qs(scope.get("query_string", b"").decode("latin-1"))
            target = qs.get("url", [""])[0]
            if target and not _is_safe_target(target):
                await _send_json(send, 400, {"error": "unsafe target url"})
                return

        await app(scope, receive, send)

    return middleware


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((LOCAL_BYPASS_HOST, 0))
        return s.getsockname()[1]


class LocalBypassServer:
    def __init__(self, log_fn: Callable[[str], None] | None = None):
        self._process: asyncio.subprocess.Process | None = None
        self._thread: threading.Thread | None = None
        self._server = None  # uvicorn.Server, 仅冻结模式(in-process)使用
        self._in_process: bool = False
        self._port: int = 0
        self._url: str = ""
        self._started = False
        self._closing = False
        self._token = ""
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
    def token(self) -> str:
        return self._token

    @property
    def is_running(self) -> bool:
        if self._in_process:
            return self._started and self._server is not None and not getattr(self._server, "should_exit", True)
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

        try:
            import uvicorn  # noqa: F401
        except ImportError:
            missing.append("uvicorn")

        try:
            import fastapi  # noqa: F401
        except ImportError:
            missing.append("fastapi")

        if missing:
            self._dependency_ok = False
            if IS_PYINSTALLER:
                self._dependency_error = (
                    f"打包时缺少依赖: {', '.join(missing)}\n"
                    "请在 scripts/build.py 的 _generate_spec 中为该模块添加 --collect-all。"
                )
            else:
                self._dependency_error = f"缺少依赖: {', '.join(missing)}\n请运行: pip install {' '.join(missing)}"
        else:
            self._dependency_ok = True
            self._dependency_error = ""

        self._dependency_checked = True
        return self._dependency_ok, self._dependency_error

    async def ensure_browser(self) -> tuple[bool, str]:
        try:
            import cloakbrowser as cb

            # 冻结模式: 优先使用随包附带的 Chromium, 避免运行时下载(国内网络常因 gh-proxy 证书失败)
            if IS_PYINSTALLER and not os.environ.get("CLOAKBROWSER_BINARY_PATH"):
                meipass = getattr(sys, "_MEIPASS", "")
                candidates = [
                    os.path.join(meipass, "chromium", "chrome.exe"),
                    os.path.join(meipass, "chromium", "chrome-win64", "chrome.exe"),
                    os.path.join(meipass, "chromium", "chrome-linux", "chrome"),
                    # macOS: build.py 把 stealth Chromium 的 MacOS 目录拷入 chrome-macos/,
                    # 故二进制直接位于 chrome-macos/Chromium; 同时兜底 Chromium.app 完整包路径
                    os.path.join(meipass, "chromium", "chrome-macos", "Chromium"),
                    os.path.join(meipass, "chromium", "chrome-macos", "Chromium.app", "Contents", "MacOS", "Chromium"),
                ]
                for cand in candidates:
                    if cand and os.path.isfile(cand):
                        os.environ["CLOAKBROWSER_BINARY_PATH"] = cand
                        self._log(f"使用随附 Chromium: {cand}")
                        break

            self._log("检查 Chromium 浏览器...")
            loop = asyncio.get_running_loop()
            try:
                binary_path = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: cb.ensure_binary()),
                    timeout=BROWSER_DOWNLOAD_TIMEOUT,
                )
            except TimeoutError:
                return False, f"浏览器下载超时 (>{BROWSER_DOWNLOAD_TIMEOUT}s)"
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

        # 生成一次性鉴权 token, 通过环境变量交给(子进程或进程内)的 ASGI 应用
        self._token = secrets.token_hex(16)
        os.environ[BYPASS_TOKEN_ENV] = self._token

        os.environ.setdefault("CLOAKBROWSER_AUTO_UPDATE", "false")
        os.environ.setdefault(
            "CLOAKBROWSER_DOWNLOAD_URL",
            "https://v6.gh-proxy.com/https://github.com/CloakHQ/cloakbrowser/releases/download",
        )

        self._log(f"启动本地 Bypass 服务 {self._url} ...")

        if IS_PYINSTALLER:
            # 冻结(onefile)模式: sys.executable 指向自身, 不能用 `sys.executable -m uvicorn` 启动子进程,
            # 否则会重新拉起主程序。改为在当前进程的后台线程内运行 uvicorn。
            ok, err = await self._start_in_process()
        else:
            ok, err = await self._start_subprocess()
        if not ok:
            return False, err

        self._started = True
        self._log(f"Bypass 服务已就绪: {self._url}")
        return True, self._url

    async def _start_subprocess(self) -> tuple[bool, str]:
        try:
            # start_new_session: 让子进程自成进程组, 便于异常退出(崩溃/SIGKILL)时由 atexit 彻底清理
            self._process = await asyncio.create_subprocess_exec(
                sys.executable,
                "-m",
                "uvicorn",
                "mdcx.cf_bypass.local_server:create_protected_app",
                "--factory",
                "--host",
                LOCAL_BYPASS_HOST,
                "--port",
                str(self._port),
                "--log-level",
                "warning",
                # 子进程日志(output 可能很大)若不消费会撑满 64KB 管道导致 uvicorn 写阻塞死锁, 直接丢弃
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                start_new_session=True,
            )
        except FileNotFoundError:
            return False, "未找到 uvicorn，请安装: pip install uvicorn fastapi"
        except Exception as e:
            return False, f"启动子进程失败: {e}"

        self._register_atexit()
        ready, error = await self._wait_ready()
        if not ready:
            await self.stop()
            return False, error

        return True, ""

    def _register_atexit(self) -> None:
        """注册进程退出时的兜底清理, 避免异常退出(崩溃/SIGKILL/事件循环被拆)时 uvicorn 子进程残留。"""
        if getattr(self, "_atexit_registered", False):
            return
        self._atexit_registered = True
        atexit.register(self._atexit_cleanup)

    def _atexit_cleanup(self) -> None:
        proc = self._process
        if proc is not None and proc.returncode is None:
            try:
                proc.kill()
            except Exception:
                pass

    async def _start_in_process(self) -> tuple[bool, str]:
        try:
            import uvicorn

            from mdcx.cf_bypass.local_server import create_protected_app
        except Exception as e:
            return False, f"无法导入 bypass 服务依赖: {e}"

        try:
            config = uvicorn.Config(
                create_protected_app(),
                host=LOCAL_BYPASS_HOST,
                port=self._port,
                log_level="warning",
            )
            self._server = uvicorn.Server(config)
            self._thread = threading.Thread(target=self._server.run, daemon=True)
            self._thread.start()
        except Exception as e:
            return False, f"启动 bypass 服务线程失败: {e}"

        ready, error = await self._wait_ready()
        if not ready:
            await self.stop()
            return False, error

        self._in_process = True
        return True, ""

    async def _wait_ready(self, timeout: int = SERVER_START_TIMEOUT) -> tuple[bool, str]:
        import httpx

        deadline = time.monotonic() + timeout
        last_error = ""
        while time.monotonic() < deadline:
            # 冻结模式: uvicorn 线程若绑定失败抛异常会直接退出, 这里提前失败, 避免空转满 60s
            if self._in_process and self._thread is not None and not self._thread.is_alive():
                return False, "Bypass 服务线程已退出 (uvicorn 启动失败)"

            if not self._in_process and self._process and self._process.returncode is not None:
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
                        headers={"Authorization": f"Bearer {self._token}"} if self._token else {},
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

        if self._process is None and not self._in_process:
            self._started = False
            self._url = ""
            self._port = 0
            return

        if self._in_process and self._server is not None:
            self._log("正在停止 Bypass 服务(线程)...")
            try:
                self._server.should_exit = True
                if self._thread is not None:
                    self._thread.join(timeout=5)
            except Exception as e:
                self._log(f"停止服务异常: {e}")
            self._server = None
            self._thread = None
            self._in_process = False
        elif self._process is not None:
            self._log("正在停止 Bypass 服务...")
            try:
                self._process.terminate()
                try:
                    await asyncio.wait_for(self._process.wait(), timeout=5)
                except TimeoutError:
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
