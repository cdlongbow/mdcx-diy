# 用户指令记忆

本文件记录了用户的指令、偏好和教导，用于在未来的交互中提供参考。

## 格式

### 用户指令条目
用户指令条目应遵循以下格式：

[用户指令摘要]
- Date: [YYYY-MM-DD]
- Context: [提及的场景或时间]
- Instructions:
  - [用户教导或指示的内容，逐行描述]

### 项目知识条目
Agent 在任务执行过程中发现的条目应遵循以下格式：

[项目知识摘要]
- Date: [YYYY-MM-DD]
- Context: Agent 在执行 [具体任务描述] 时发现
- Category: [运维部署|构建方法|测试方法|排错调试|工作流协作|环境配置]
- Instructions:
  - [具体的知识点，逐行描述]

## 去重策略
- 添加新条目前，检查是否存在相似或相同的指令
- 若发现重复，跳过新条目或与已有条目合并
- 合并时，更新上下文或日期信息
- 这有助于避免冗余条目，保持记忆文件整洁

## 条目

[面向小白的细致指导风格]
- Date: 2026-06-08
- Context: 用户希望我以编程能手、审核、修改和补全代码专家的方式长期协作
- Instructions:
  - 默认从全方位、多角度、深层次的角度审查和改进代码。
  - 面向小白解释问题，给出细致、可执行、易落地的建议。
  - 在发现风险、缺陷、遗漏时主动指出，并尽量给出修复方案和进行验证。

[改动代码和提交推送前必须征得用户同意]
- Date: 2026-07-18
- Context: 用户要求每次改动代码和提交推送前必须先问过用户，不能擅自操作
- Instructions:
  - 所有代码改动（新建文件、修改代码、删除文件等）必须先向用户说明改动内容和原因，获得同意后再执行。
  - 提交推送前必须先向用户说明要提交什么、推送到哪里，获得同意后再执行 `git add` + `git commit` + `git push`。
  - 本指令优先级高于此前所有"自动执行"类指令，改动代码和提交推送这两件事必须先问后做。

[提交推送前自动运行 ruff + pytest]
- Date: 2026-07-18
- Context: 用户希望每次提交推送前自动运行测试，不要手动操作
- Category: 工作流协作
- Instructions:
  - 用户同意推送后，执行 `git push` 前必须先运行 `uv run check --skip-hook-install`（自动执行 ruff format --check + ruff check + pytest --tb=short -m "not network" -x）。
  - 如果 `uv run check` 失败，修复问题后再推送，不要强行推送。
  - 不要依赖 git hooks 或 pre-commit 来拦截，由 Agent 手动执行上述检查。
  - 注意：实际 `git add` + `git commit` + `git push` 操作必须在获得用户明确同意后才能执行。本指令仅限推送前的技术检查步骤。

[每次新会话自动安装 pre-commit 钩子]
- Date: 2026-07-17
- Context: 用户希望每次新会话开始时自动安装 pre-commit 钩子，无需手动执行
- Instructions:
  - 每次新会话开始时，自动执行 `pre-commit install` 命令安装 git hooks。
  - 如果 pre-commit 工具未安装，先执行 `pip install pre-commit --break-system-packages` 安装。
  - 安装完成后确认 `.git/hooks/pre-commit` 文件存在且可执行。

[环境 Python 版本升级到 >= 3.13.4]
- Date: 2026-07-17
- Context: 项目要求 Python >= 3.13.4（使用 type parameter defaults 语法），但沙箱环境默认只有 Python 3.11，导致无法运行测试和导入项目。
- Category: 环境配置
- Instructions:
  - 项目只能 `uv run` 执行测试（`pytest tests/ --tb=short -m "not network"`），因为 sandbox 默认 python3 是 3.11，无法解析 3.12+ 的 `class Rename[TRaw = str, TNew = TRaw]` 语法。
  - Python 3.13.14 已安装到 `/opt/python3.13`，`uv` 已安装到 `/usr/local/bin/uv`。
  - 每次新会话开始时，检查 `/opt/python3.13` 是否存在：
    - 若存在，直接使用 `uv run pytest` 跑测试。
    - 若不存在，需要下载并安装：从 `https://github.com/astral-sh/python-build-standalone` 下载最新 `cpython-3.13.x-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz`，解压到 `/opt/python3.13`，创建 `/usr/local/bin/uv` 和 `/usr/local/bin/python3.13` 软链接，然后执行 `uv sync` 安装项目依赖。
  - 依赖安装后可以运行 `uv run pytest tests/ --tb=short -m "not network"` 验证。

[Windows exe 打包依赖约束]
- Date: 2026-06-21
- Context: 用户提醒后续修改需兼容 Windows 打包发布场景
- Category: 环境配置
- Instructions:
  - 代码变更优先使用 Python 标准库，不主动引入新三方依赖。
  - 新增文件持久化路径应使用 `resources`/`userdata` 现有目录习惯，避免新增外部库。
  - 变更涉及打包入口或运行时依赖时，先确认打包脚本与 PyInstaller 打包配置仍能在 Windows 下正常启动。
