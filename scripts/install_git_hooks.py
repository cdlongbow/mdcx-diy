from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = {
    "pre-push": ROOT / "scripts" / "git-hooks" / "pre-push",
}


def install_hooks() -> None:
    git_hooks_dir = ROOT / ".git" / "hooks"
    if not git_hooks_dir.exists():
        return

    for hook_name, source in HOOKS.items():
        target = git_hooks_dir / hook_name
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        target.chmod(0o755)


def main() -> int:
    install_hooks()
    print("[hooks] Git hooks installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
