# PyQt6 迁移记录

## 背景

项目桌面端原先用的是 PyQt5/Qt5，现在已经迁到了 PyQt6。主要入口和 UI 代码在 `main.py`、`mdcx/views`、`mdcx/controllers`、`mdcx/signals.py`、`mdcx/image.py`、`mdcx/config/resources.py` 和少量核心流程弹窗里。这份文档记录迁移时的关键差别、已经做完的事和后续界面优化方向。

## PyQt6 主要差别

- `PyQt5` 包名改成了 `PyQt6`。
- Qt 的枚举和 Flag 改用标准 Python 的 `Enum`/`Flag`，需要写完整的名字，比如 `Qt.AlignmentFlag.AlignCenter`、`QMessageBox.StandardButton.Yes`。
- `exec_()` 已经没了，全部换成 `exec()`。
- `QAction` 从 `QtWidgets` 移到了 `QtGui`。
- Qt6 默认开启了高 DPI 缩放，Qt5 里的 `AA_EnableHighDpiScaling`、`AA_UseHighDpiPixmaps` 不再需要了。
- `pyrcc6` 不再提供，资源文件继续用当前的文件路径加载方式就行。

## 第一阶段做了什么

第一阶段的目的是完成 PyQt6 迁移，同时做一些风险低的 UI 统一优化：

- 把依赖更新到 PyQt6。
- 更新 `pyuic` 脚本并重新生成 UI 文件。
- 迁移手写的 Qt API、枚举、消息框、菜单、文件选择器等 PyQt6 不兼容的用法。
- 调整启动入口里的高 DPI 初始化。
- 保持现有页面结构和业务流程不变。
- 优化样式，包括基础控件边框、按钮悬停/按下、输入框焦点状态、工具提示和列表选中状态。

第一阶段已经完成。

## 后续阶段建议

- 增加主题切换：跟随系统、浅色、深色。
- 接入 `QGuiApplication.styleHints().colorScheme()`，监听系统主题变化。
- 把图标颜色、日志面板、弹窗和设置页统一到可维护的调色板。
- 针对 Windows 100%/150%/175%、macOS Retina、多显示器分别验证。
- 对主窗口布局做更深层重构时，优先改 `.ui` 源文件，不要直接手改生成后的 `mdcx/views/*.py`。

## 第二阶段进展

- 已增加浅色/暗色主题颜色变量，用统一入口刷新 `QApplication` 调色板，避免系统暗色或系统强调色污染未开启暗色模式时的弹窗、菜单和选中状态。
- 已统一概览页树控件的悬停、选中、非活动选中和分支样式，避免 Qt6/Fusion 原生选择色导致文字看不清。
- 已统一主界面右键菜单、托盘菜单和裁剪弹窗的主题样式。
- 已补充复选框、单选框、滑块、滚动条、小型说明按钮等控件的基础状态样式。
- 已继续修复 PyQt6 短枚举遗漏，包括 `QItemSelectionModel.SelectionFlag.NoUpdate`、`QEvent.Type.Wheel`、`QMessageBox.Icon.Information`。
- 已在启动入口按平台应用样式和调色板，减少系统主题对界面观感的干扰。
- 已监听系统主题变化并重新应用 MDCx 当前主题，避免运行中主题漂移。
- 已修复裁剪窗口拖拽相关 Qt6 鼠标事件 API，统一使用 `position()` / `globalPosition()`。
- 已为日志面板链接增加浅色/暗色文档级样式，提升 URL 在日志输出中的可读性。

## 验证清单

- `ruff format`
- `ruff check`
- 应用可正常启动主窗口。
- 托盘菜单：显示、隐藏、退出。
- 主界面右键菜单。
- 刮削启动、停止、删除、保存等确认弹窗。
- 文件选择器。
- 海报裁剪窗口。
- NFO 编辑窗口。
- 封面、缩略图在高 DPI 下清晰且比例正确。
