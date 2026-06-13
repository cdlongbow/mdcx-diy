"""Gfriends 本地仓库同步脚本。"""

import os
import subprocess
from pathlib import Path


def sync_gfriends(local_path: str) -> tuple[bool, str]:
    """
    执行 git pull 更新本地 Gfriends 仓库。

    Args:
        local_path: 本地仓库路径

    Returns:
        (成功, 消息)
    """
    if not local_path or not os.path.isdir(local_path):
        return False, "请先选择有效的本地仓库目录"

    git_path = Path(local_path) / ".git"
    if not git_path.exists():
        return False, f"目录 {local_path} 不是有效的 Git 仓库（缺少 .git 文件夹）"

    try:
        result = subprocess.run(
            ["git", "pull", "origin", "master"],
            cwd=local_path,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if "up to date" in output.lower() or "已经是最新" in output:
                return True, "本地仓库已是最新"
            return True, f"更新成功: {output}"
        else:
            error = result.stderr.strip()
            return False, f"更新失败: {error}"
    except subprocess.TimeoutExpired:
        return False, "更新超时（5 分钟）"
    except FileNotFoundError:
        return False, "未找到 git 命令，请确保已安装 Git"
    except Exception as e:
        return False, f"更新异常: {str(e)}"
