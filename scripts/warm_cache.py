"""Download cloakbrowser stealth Chromium for cache warm-up."""
import os
import shutil
from pathlib import Path

import cloakbrowser as cb


def main():
    os.environ.setdefault(
        "CLOAKBROWSER_DOWNLOAD_URL",
        "https://v6.gh-proxy.com/https://github.com/CloakHQ/cloakbrowser/releases/download",
    )
    binary = cb.ensure_binary()
    if not binary:
        print("Failed to get Chromium binary")
        return 1

    platform_sub = {"Windows": "chrome-win64", "Linux": "chrome-linux", "Darwin": "chrome-macos"}
    src = Path(binary).resolve().parent
    dest = Path("chromium") / platform_sub.get(os.name, "chrome-win64")
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    print(f"Chromium cached to {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())