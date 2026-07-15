"""
Trading Signals Bot
Version 1.0

Hotkeys (pynput)
"""

import threading
import time

from pynput import keyboard

_last = 0

listener = None


def register(accounts, callback):

    global listener

    hotkeys = {}

    for account in accounts:

        hotkeys[account["hotkey"]] = account

        print(
            account["hotkey"],
            "->",
            account["name"]
        )

    print("--------------------------------------")
    print("HOTKEYS READY")
    print("--------------------------------------")

    def on_press(key):
        global _last

        now = time.time()

        if now - _last < 0.4:
            return

        _last = now
        
        try:

            if not hasattr(key, "char"):
                return

            ch = key.char

            if ch in hotkeys:

                account = hotkeys[ch]

                threading.Thread(
                    target=callback,
                    args=(account,),
                    daemon=True
                ).start()

        except Exception:
            pass

    listener = keyboard.Listener(
        on_press=on_press
    )

    listener.daemon = True

    listener.start()