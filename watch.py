import subprocess
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_EXTENSIONS = {".py", ".txt", ".md"}
IGNORE_DIRS = {".venv", ".git", "__pycache__"}
DEBOUNCE_SECONDS = 2


class GitAutoCommit(FileSystemEventHandler):
    def __init__(self):
        self._pending = {}

    def _should_ignore(self, path: str) -> bool:
        parts = Path(path).parts
        return any(d in parts for d in IGNORE_DIRS)

    def _schedule(self, path: str):
        if self._should_ignore(path):
            return
        if Path(path).suffix not in WATCH_EXTENSIONS:
            return
        self._pending[path] = time.time()

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(event.src_path)

    def flush(self):
        now = time.time()
        ready = [p for p, t in self._pending.items() if now - t >= DEBOUNCE_SECONDS]
        if not ready:
            return
        for path in ready:
            del self._pending[path]

        filename = Path(ready[-1]).name
        result = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[watch] git add falhou: {result.stderr.strip()}")
            return

        msg = f"auto: {filename}"
        result = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True)
        if "nothing to commit" in result.stdout:
            return
        if result.returncode != 0:
            print(f"[watch] git commit falhou: {result.stderr.strip()}")
            return

        result = subprocess.run(["git", "push"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[watch] git push falhou: {result.stderr.strip()}")
        else:
            print(f"[watch] pushed: {msg}")


if __name__ == "__main__":
    handler = GitAutoCommit()
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()
    print("[watch] Monitorando alterações... (Ctrl+C para parar)")
    try:
        while True:
            time.sleep(1)
            handler.flush()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
