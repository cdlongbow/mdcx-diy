import subprocess
import sys

COMMANDS = [
    ["ruff", "format", "--check"],
    ["ruff", "check"],
    ["python3", "-m", "pytest", "tests/test_tmdb_actor.py", "tests/test_mapping_resources.py"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"[check] running: {' '.join(command)}")
        result = subprocess.run(command)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
