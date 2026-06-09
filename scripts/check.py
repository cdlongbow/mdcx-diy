import subprocess
import sys

try:
    from scripts.install_git_hooks import install_hooks
except ModuleNotFoundError:
    from install_git_hooks import install_hooks

COMMANDS = [
    ["ruff", "format", "--check"],
    ["ruff", "check"],
    [sys.executable, "-m", "pytest", "tests/test_tmdb_actor.py", "tests/test_mapping_resources.py"],
]


def main() -> int:
    if "--skip-hook-install" not in sys.argv:
        install_hooks()

    for command in COMMANDS:
        print(f"[check] running: {' '.join(command)}")
        result = subprocess.run(command)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
