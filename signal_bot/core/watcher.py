from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import hashlib
import os


# Hash dell'ultima versione elaborata di ciascun file
_last_hash = {}


def md5(path):

    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


class Handler(FileSystemEventHandler):

    def __init__(self, callback, targets):

        self.callback = callback

        self.targets = {
            os.path.abspath(path)
            for path in targets
            if path
        }

    def on_any_event(self, event):

        global _last_hash

        if event.is_directory:
            return

        path = os.path.abspath(event.src_path)

        if path not in self.targets:
            return

        try:

            new_hash = md5(path)

        except Exception:

            return

        old_hash = _last_hash.get(path)

        if new_hash == old_hash:
            return

        _last_hash[path] = new_hash

        print(f"SIGNAL DETECTED ({os.path.basename(path)})")

        self.callback(path)


def start_watcher(paths, callback):

    if isinstance(paths, str):
        paths = [paths]

    folders = {
        os.path.dirname(path)
        for path in paths
        if path
    }

    observer = Observer()

    handler = Handler(callback, paths)

    for folder in folders:

        observer.schedule(
            handler,
            folder,
            recursive=False
        )

    observer.start()

    return observer