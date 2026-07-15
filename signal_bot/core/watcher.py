from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import hashlib
import os
import time


# Hash dell'ultima immagine elaborata
_last_hash = None


def md5(path):

    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


class Handler(FileSystemEventHandler):

    def __init__(self, callback, target):

        self.callback = callback
        self.target = os.path.abspath(target)

    def on_any_event(self, event):

        global _last_hash

        if event.is_directory:
            return

        path = os.path.abspath(event.src_path)

        if path != self.target:
            return

        # aspetta che il file sia completamente scritto
##        time.sleep(0.2)

        try:

            new_hash = md5(path)

        except Exception:

            return

        # identico all'ultima immagine
        if new_hash == _last_hash:
            return

        _last_hash = new_hash

        print("modified:", path)
        print("SIGNAL DETECTED")

        self.callback()


def start_watcher(path, callback):

    folder = os.path.dirname(path)

    observer = Observer()

    observer.schedule(
        Handler(callback, path),
        folder,
        recursive=False
    )

    observer.start()

    return observer