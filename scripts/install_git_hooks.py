import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def install_hooks() -> int:
    hooks_dir = ROOT / ".githooks"
    if not hooks_dir.exists():
        print("[hooks] 错误：.githooks 目录不存在")
        return 1

    subprocess.run(
        ["git", "config", "core.hooksPath", ".githooks"],
        cwd=ROOT,
        check=True,
    )
    print("[hooks] Git hooks 已配置为 .githooks/")
    return 0


def main() -> int:
    return install_hooks()


if __name__ == "__main__":
    raise SystemExit(main())
