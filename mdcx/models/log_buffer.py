import asyncio
import threading

try:
    from warnings import deprecated
except ImportError:

    def deprecated(_message):
        def decorator(func):
            return func

        return decorator


class LogBuffer:
    _lock = threading.Lock()
    all_buffers = {}
    global_buffer = None

    @staticmethod
    def _global_buffer() -> "LogBuffer":
        if LogBuffer.global_buffer is None:
            LogBuffer.global_buffer = LogBuffer()
        return LogBuffer.global_buffer

    @staticmethod
    def _get_task_id() -> int | None:
        """获取当前协程的 Task ID，如果在协程环境下运行则返回 Task ID，否则返回线程 ID"""
        try:
            # 尝试获取当前协程
            task = asyncio.current_task()
            if task is not None:
                # 使用 Task 对象的 id 作为唯一标识符
                return id(task)
        except RuntimeError:
            # 如果不在协程环境中，会抛出 RuntimeError
            pass

        # 如果不是协程或获取失败，则回退到使用线程 ID
        return threading.current_thread().ident

    @staticmethod
    def _get_buffer(category: str) -> "LogBuffer":
        task_id = LogBuffer._get_task_id()
        if task_id is None:
            return LogBuffer._global_buffer()
        with LogBuffer._lock:
            if task_id not in LogBuffer.all_buffers:
                LogBuffer.all_buffers[task_id] = {}
            if category not in LogBuffer.all_buffers[task_id]:
                LogBuffer.all_buffers[task_id][category] = LogBuffer()
            return LogBuffer.all_buffers[task_id][category]

    @staticmethod
    def clear_task():
        task_id = LogBuffer._get_task_id()
        if task_id is not None:
            with LogBuffer._lock:
                LogBuffer.all_buffers.pop(task_id, None)

    @staticmethod
    def clear_stale_buffers(max_size: int = 200) -> int:
        if len(LogBuffer.all_buffers) <= max_size:
            return 0
        with LogBuffer._lock:
            if len(LogBuffer.all_buffers) <= max_size:
                return 0
            keys = list(LogBuffer.all_buffers.keys())
            remove_count = len(keys) // 2
            for key in keys[:remove_count]:
                LogBuffer.all_buffers.pop(key, None)
        return remove_count

    @staticmethod
    def clear_thread():
        """兼容旧版 API，实际上调用 clear_task()"""
        LogBuffer.clear_task()

    @staticmethod
    def log() -> "LogBuffer":
        return LogBuffer._get_buffer("log")

    @staticmethod
    @deprecated("仅用于向后兼容")
    def info() -> "LogBuffer":
        return LogBuffer._get_buffer("info")

    @staticmethod
    def error() -> "LogBuffer":
        return LogBuffer._get_buffer("error")

    @staticmethod
    @deprecated("内容不会被任何位置使用")
    def req() -> "LogBuffer":
        return LogBuffer._get_buffer("req")

    def __init__(self):
        self.buffer = []

    def write(self, message, with_task_name=False):
        """
        写入日志消息

        Args:
            message: 日志消息
            with_task_name: 是否在日志消息前添加任务名称
        """
        if with_task_name:
            task_name = LogBuffer.get_task_name()
            message = f"[{task_name}] {message}"
        if self.buffer and self.buffer[-1] == message:
            return
        self.buffer.append(message)

    def get(self):
        result = "".join(self.buffer)
        task_id = LogBuffer._get_task_id()
        with LogBuffer._lock:
            for tid, categories in list(LogBuffer.all_buffers.items()):
                if tid == task_id:
                    continue
                for category, buf in categories.items():
                    if isinstance(buf, LogBuffer):
                        result += "".join(buf.buffer)
        return result

    def last(self):
        if len(self.buffer) == 0:
            return ""
        return self.buffer[-1]

    def clear(self):
        self.buffer.clear()

    @staticmethod
    def get_task_name() -> str:
        """获取当前任务的名称（线程名或协程名）"""
        try:
            task = asyncio.current_task()
            if task:
                return task.get_name()
        except RuntimeError:
            pass

        return threading.current_thread().name or "unknown"
