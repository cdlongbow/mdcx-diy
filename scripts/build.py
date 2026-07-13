import argparse
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from contextlib import suppress
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console(color_system="truecolor", width=200, no_color=False)
handler = RichHandler(level=logging.DEBUG, console=console)
logger = logging.getLogger("build")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

EXCLUDED_MODULES = [
    "IPython",
    "ipykernel",
    "jupyter_client",
    "jupyter_core",
    "debugpy",
    "traitlets",
    "prompt_toolkit",
    "pygments",
    "tornado",
    "zmq",
    "pytest",
    "_pytest",
    "matplotlib_inline",
    "rich",
    "typer",
]


class BuildError(Exception): ...


def get_version_from_config() -> str:
    p = Path("mdcx/consts.py")
    if not p.exists():
        raise BuildError(f"版本配置文件不存在: {p}")
    try:
        content = p.read_text(encoding="utf-8")
        match = re.search(r"LOCAL_VERSION\s*=\s*(\d+)", content)
        if match:
            return match.group(1)
        raise BuildError("无法从代码中获取版本号")
    except Exception as e:
        raise BuildError("获取版本号失败") from e


class BuildManager:
    def __init__(self, app_name: str, app_version: str, create_dmg: bool, debug: bool):
        self.app_name = app_name
        self.app_version = app_version
        self.create_dmg = create_dmg
        self.platform = platform.platform()
        self.os = platform.system()
        self.is_mac = self.os == "Darwin"
        self.is_windows = self.os == "Windows"
        self.is_linux = self.os == "Linux"
        self.debug = debug

    def _app_icon_path(self) -> str:
        if self.is_windows:
            return "resources/Img/MDCx.ico"
        return "resources/Img/MDCx.icns"

    def run(self):
        """运行构建流程"""
        try:
            start_time = time.time()
            if not self.app_version:
                self.app_version = get_version_from_config()

            self._check_environment()
            self._prepare_chromium()
            self._cleanup()
            dist = Path("dist")
            if dist.exists():
                logger.info("清理现有的 dist 目录...")
                shutil.rmtree(dist)

            self._generate_spec()
            if self.is_mac:
                self._modify_spec()
            self._build_app()

            if self.create_dmg and self.is_mac:
                self._create_dmg()

            if not self.debug:
                self._cleanup()
            logger.info(f"构建完成. 耗时: {int(time.time() - start_time)}秒")
        except BuildError as e:
            logger.error(f"构建失败: {e}")
            console.print_exception()
            sys.exit(1)
        except Exception as e:
            logger.error(f"意外错误: {e}")
            console.print_exception()
            sys.exit(1)

    def _check_environment(self):
        logger.info("构建环境:")
        logger.info(f"\t操作系统: {self.platform}")
        logger.info(f"\tPython 版本: {sys.version}")
        logger.info(f"\tPython 可执行文件: {sys.executable}")

        logger.info(f"\t应用名称: {self.app_name}")
        logger.info(f"\t应用版本: {self.app_version}")

        logger.info("检查依赖...")
        # 检查 PyInstaller
        r = self._run_command([sys.executable, "-m", "PyInstaller", "-v"], error_msg="PyInstaller 未安装")
        logger.info(f"\tPyInstaller 版本: {r}")

        # 检查 create-dmg
        if self.is_mac and self.create_dmg:
            r = self._run_command(["create-dmg", "--version"])
            if not r:
                logger.warning("create-dmg 未安装, 尝试安装: brew install create-dmg ...")
                self._run_command(["brew", "install", "create-dmg"], error_msg="create-dmg 安装失败")
                r = self._run_command(["create-dmg", "--version"])
            logger.info(f"\tcreate-dmg 版本: {r}")

        logger.info("检查必要文件...")
        required_files = ["main.py", "mdcx", self._app_icon_path(), "resources", "libs"]
        for file_path in required_files:
            if not Path(file_path).exists():
                raise BuildError(f"文件检查失败: {file_path}")

    def _prepare_chromium(self):
        """为 CF Bypass 准备随附的 Chromium。

        仅使用 cloakbrowser 的 **stealth** Chromium(CloakHQ 打过补丁, 过 Cloudflare 必需)。
        CloakBrowser **免费档(无 CLOAKBROWSER_LICENSE_KEY)即可拿到过 CF 的 stealth 二进制**,
        Pro 档(需 license key)仅为可选升级。不再降级到普通 Chromium(非 stealth 过不了 CF, 无价值)。
        冻结(onefile)模式下 local_server 无法运行时下载 Chromium(国内网络常因
        gh-proxy 证书失败), 因此构建时把 Chromium 复制到 ./chromium, 由 PyInstaller 的
        --add-data 一并打入包内。
        """
        chromium_dir = Path("chromium")
        if chromium_dir.exists() and (any(chromium_dir.rglob("chrome.exe")) or any(chromium_dir.rglob("chrome"))):
            logger.info("✅ 已存在 ./chromium, 跳过准备")
            return

        ok = self._prepare_stealth_chromium(chromium_dir)
        if not ok:
            raise RuntimeError(
                "❌ 无法获取 cloakbrowser stealth Chromium, 构建中止。\n"
                "   请先 `pip install cloakbrowser` 并确保能下载 stealth 二进制\n"
                "   (构建环境可设 CLOAKBROWSER_DOWNLOAD_URL 镜像加速; 可选配置\n"
                "   CLOAKBROWSER_LICENSE_KEY 升级 Pro 档)。"
            )

    def _prepare_stealth_chromium(self, chromium_dir: Path) -> bool:
        """通过 cloakbrowser 获取过 Cloudflare 的 **stealth** Chromium。

        CloakBrowser 免费档(ensure_binary() 无参)即可拿到过 CF 的 stealth 二进制,
        **无需 CLOAKBROWSER_LICENSE_KEY**。仅当该环境变量存在时, 才下载 Pro 档作为可选升级。
        与运行期 local_server.py 一致, 这里也走国内镜像下载。
        成功则把二进制目录复制到 ./chromium/<platform>/, 返回 True; 否则返回 False。
        """
        try:
            import cloakbrowser as cb
        except ImportError:
            logger.warning("cloakbrowser 未安装, 无法获取 stealth Chromium (请先 `pip install cloakbrowser`)")
            return False

        license_key = os.environ.get("CLOAKBROWSER_LICENSE_KEY")
        try:
            if license_key:
                logger.info("检测到 CLOAKBROWSER_LICENSE_KEY, 尝试下载 Pro 档(可选升级) ...")
                try:
                    binary = cb.ensure_binary(license_key)
                except TypeError:
                    binary = cb.ensure_binary(license_key, "stable")
            else:
                # 仅免费档走国内镜像下载, 避免直连 github 失败;
                # 注意: 不能在 Pro 分支前设置 CLOAKBROWSER_DOWNLOAD_URL, 否则
                # ensure_binary(license_key) 会被强制退化为免费档 (见 P1-7)。
                os.environ.setdefault(
                    "CLOAKBROWSER_DOWNLOAD_URL",
                    "https://v6.gh-proxy.com/https://github.com/CloakHQ/cloakbrowser/releases/download",
                )
                logger.info("获取 cloakbrowser stealth Chromium (免费档, 无需 license key) ...")
                binary = cb.ensure_binary()
            if not binary or not os.path.isfile(binary):
                logger.warning(f"cloakbrowser 返回的二进制无效: {binary}")
                return False
            src_dir = Path(binary).resolve().parent
        except Exception as e:
            logger.warning(f"获取 stealth Chromium 失败: {e}")
            return False

        # 目标布局需与 local_server.py 的 CLOAKBROWSER_BINARY_PATH 候选一致
        platform_sub = {"Windows": "chrome-win64", "Linux": "chrome-linux", "Darwin": "chrome-macos"}.get(
            self.os, "chrome-win64"
        )
        dest = chromium_dir / platform_sub
        dest.mkdir(parents=True, exist_ok=True)
        logger.info(f"\t复制 stealth Chromium: {src_dir} -> {dest}")
        shutil.copytree(src_dir, dest, dirs_exist_ok=True)
        logger.info("✅ stealth Chromium 已准备, 将随包打入")
        return True

    # 注: 已移除 Playwright 普通 Chromium 降级方案 —— 非 stealth 构建过不了 Cloudflare, 保留只会增加误导。

    def _generate_spec(self):
        """生成.spec文件"""
        logger.info("生成 .spec 文件...")
        cmd = [
            sys.executable,
            "-m",
            "PyInstaller.utils.cliutils.makespec",
            "--name",
            self.app_name,
            "--noupx",
            *(["--osx-bundle-identifier", "com.mdcuniverse.mdcx"] * self.is_mac),
            *(["--onefile"] if not self.is_mac else []),
            "-w",
            "main.py",
            "-p",
            "./mdcx",
            "--add-data",
            "resources:resources",
            "--add-data",
            "libs:.",
            "--icon",
            self._app_icon_path(),
            "--hidden-import",
            "_cffi_backend",
            "--collect-all",
            "defusedxml",
            "--collect-all",
            "openpyxl",
            "--collect-all",
            "zhconv",
            "--collect-all",
            "curl_cffi",
            # CF Bypass 服务依赖: 必须随包收集, 否则打包后的 exe 无法启动 bypass 服务
            "--collect-all",
            "cf_bypasser",
            "--collect-all",
            "cloakbrowser",
            # cf_bypasser 依赖 pyvirtualdisplay(虚拟显示/Xvfb), 冻结模式(Linux/macOS)缺它会导入失败
            "--collect-all",
            "pyvirtualdisplay",
            "--collect-all",
            "easyprocess",
            "--collect-all",
            "uvicorn",
            "--collect-all",
            "fastapi",
            "--collect-all",
            "starlette",
            "--collect-all",
            "pydantic",
            # 随附 Chromium (由 _prepare_chromium 复制到 ./chromium)
            *(["--add-data", "chromium:chromium"] if Path("chromium").exists() else []),
            *[item for module in EXCLUDED_MODULES for item in ("--exclude-module", module)],
        ]
        self._run_command(cmd, "✅ 生成 .spec 文件", "spec 文件生成失败")

    def _modify_spec(self):
        """修改.spec文件添加版本信息"""
        logger.info("(macOS) 向 .spec 文件添加版本信息...")

        spec_file = Path(f"{self.app_name}.spec")
        if not spec_file.exists():
            raise BuildError("spec 文件不存在")

        try:
            content = spec_file.read_text(encoding="utf-8")

            # 查找bundle_identifier行
            lines = content.splitlines()
            new_lines = []

            for i, line in enumerate(lines, 1):
                new_lines.append(line)
                if "bundle_identifier" in line:
                    # 在下一行添加info_plist
                    indent = len(line) - len(line.lstrip())
                    info_plist = f"{' ' * indent}info_plist={{\n"
                    info_plist += f"{' ' * (indent + 4)}'CFBundleShortVersionString': '{self.app_version}',\n"
                    info_plist += f"{' ' * (indent + 4)}'CFBundleVersion': '{self.app_version}',\n"
                    info_plist += f"{' ' * indent}}},"
                    new_lines.append(info_plist)
                    logger.debug(f"在第 {i + 1} 行添加 info_plist")

            new_content = "\n".join(new_lines)
            spec_file.write_text(new_content, encoding="utf-8")

            logger.info("✅ .spec 文件修改成功，已添加版本信息")

        except Exception as e:
            raise BuildError("spec文件修改失败") from e

    def _build_app(self):
        """构建应用"""
        logger.info("开始构建应用...")
        build_start = time.time()

        cmd = [sys.executable, "-m", "PyInstaller", f"{self.app_name}.spec", "-y"]
        self._run_command(cmd, error_msg="pyinstaller 构建失败")
        build_duration = time.time() - build_start

        logger.info(f"✅ 应用构建成功! 耗时: {int(build_duration)}秒")

        # 验证构建结果
        if self.is_windows:
            app_path = Path(f"dist/{self.app_name}.exe")
        elif self.is_mac:
            app_path = Path(f"dist/{self.app_name}.app")
        else:
            app_path = Path(f"dist/{self.app_name}")
        if not app_path.exists():
            raise BuildError("构建未生成")
        logger.info(f"✅ 构建产物: {app_path}")
        with suppress(Exception):
            if app_path.is_file():
                app_size = app_path.stat().st_size
                logger.info(f"大小: {app_size / 1024 / 1024:.1f} MB")

    def _create_dmg(self):
        """创建DMG文件"""
        logger.info("(macOS) 创建 DMG 文件...")
        dmg_start = time.time()
        cmd = [
            "create-dmg",
            "--volname",
            self.app_name,
            "--volicon",
            self._app_icon_path(),
            "--window-pos",
            "200",
            "120",
            "--window-size",
            "800",
            "400",
            "--icon-size",
            "80",
            "--icon",
            f"{self.app_name}.app",
            "300",
            "36",
            "--hide-extension",
            f"{self.app_name}.app",
            "--app-drop-link",
            "500",
            "36",
            f"dist/{self.app_name}.dmg",
            f"dist/{self.app_name}.app",
        ]

        # 重试机制：解决 GitHub Actions macOS runner 中的 "Resource busy" 问题
        # 参考: https://github.com/actions/runner-images/issues/7522
        max_tries = 10
        for attempt in range(1, max_tries + 1):
            if attempt > 1:
                logger.warning(f"重试创建 DMG 文件 (尝试 {attempt}/{max_tries})...")
                time.sleep(2)  # 等待 2 秒后重试

            result = self._run_command(cmd, error_msg=None)
            if result is not False:
                logger.info(f"✅ DMG 文件创建成功! 耗时: {int(time.time() - dmg_start)}秒")
                break
        else:
            raise BuildError(f"DMG 文件创建失败: 重试 {max_tries} 次后仍然失败")

        # 验证DMG文件
        dmg_path = Path(f"dist/{self.app_name}.dmg")
        logger.info(f"✅ DMG 文件: {dmg_path}")
        with suppress(Exception):
            dmg_size = dmg_path.stat().st_size
            logger.info(f"大小: {dmg_size >> 20:.1f} MB")

    def _cleanup(self):
        """清理临时文件"""
        logger.info("清理临时文件...")
        # 清理build目录
        build_dir = Path("build")
        if build_dir.exists():
            shutil.rmtree(build_dir)
            logger.debug(build_dir)
        # 清理.spec文件
        spec_files = list(Path(".").glob("*.spec"))
        for spec_file in spec_files:
            spec_file.unlink()
            logger.debug(spec_file)

    def _run_command(self, args: list[str], success_msg: str | None = None, error_msg: str | None = None):
        """
        运行命令并检查结果

        Args:
            args (list[str]): 命令行参数列表
            success_msg (str | None): 成功时的消息. Defaults to None.
            error_msg (str ｜ None, optional): 错误时的异常消息, 若 None 则不抛出异常. Defaults to None.

        Raises:
            BuildError: 当命令执行失败且 error_msg 不为 None

        Returns:
            如果命令执行成功, 返回标准输出内容; 否则返回 False
        """
        logger.debug(f"Execute: {' '.join(args)}")
        try:
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            logger.debug(result.stdout.strip())
        except Exception:
            if error_msg is not None:
                raise BuildError(f"{error_msg}")
            return False
        if result.returncode != 0:
            if error_msg is not None:
                raise BuildError(f"{error_msg}")
            return False
        if success_msg:
            logger.info(f"{success_msg}")
        return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", "-v", help="指定版本号")
    parser.add_argument("--app-name", "-n", default="MDCx", help="指定应用名称")
    parser.add_argument("--create-dmg", "--dmg", action="store_true", help="创建 DMG 文件 (仅macOS)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--no-color", action="store_true", help="禁用颜色输出")
    args = parser.parse_args()

    if args.no_color:
        console._color_system = None
    if args.debug:
        logger.setLevel(logging.DEBUG)

    manager = BuildManager(
        app_name=args.app_name, app_version=args.version, create_dmg=args.create_dmg, debug=args.debug
    )
    manager.run()


if __name__ == "__main__":
    main()
