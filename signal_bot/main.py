# ------------------------------------------------------
# Trading Signals Bot v1.0
# 2025-07-22
# ------------------------------------------------------

from core.watcher import start_watcher
from core.ocr import read_image
from core.parser import parse_signal
from core.calculator import calculate
from core.state import state
from core.news import has_high_impact_news

from ui.review import ReviewWindow

from config_loader import load_config

from core.hotkey import register
from execution.ctrader import execute

import threading
import time


config = load_config()

WATCH_FILE = config["watch_file"]
WATCH_JSON_FILE = config["watch_json_file"]
ACCOUNTS = config["accounts"]
LAST_SIGNAL_KEY = None

# ------------------------------------------------------
# HOTKEY
# ------------------------------------------------------

def execute_with_account(account):

    if state["last_signal"] is None:

        print("No confirmed signal.")

        return

    calculated = calculate(

        state["last_signal"],

        account["risk"]

    )

    execute(calculated)


def on_hotkey(account):

    execute_with_account(account)


threading.Thread(

    target=register,

    args=(ACCOUNTS, on_hotkey),

    daemon=True

).start()


# ------------------------------------------------------
# PROCESS SIGNAL
# ------------------------------------------------------
import json

def write_json(path, signal):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            signal,
            f,
            indent=4,
            ensure_ascii=False
        )
        
def read_json(path):

    with open(path, "r", encoding="utf-8") as f:
        signal = json.load(f)

    return signal


from pathlib import Path

def process_signal(path):


    ext = Path(path).suffix.lower()

    if ext.strip() == ".json":

        signal = read_json(path)

    else:

        text = read_image(path)

        signal = parse_signal(text)

        global LAST_SIGNAL_KEY

        print("==============================")
        print(">>> PROCESS START")
        print("==============================")
        
        text = read_image(WATCH_FILE)

        print("===== OCR TEXT =====")
        print(repr(text))
        print("====================")

        signal = parse_signal(text)
        write_json(
            WATCH_JSON_FILE,
            signal
        )

    print(signal)
    
    #
    # Evita popup duplicati dello stesso segnale
    #

    signal_key = (
        signal["symbol"],
        signal["side"],
        signal["order_type"],
        signal["entry"],
        signal["sl"],
        signal["tp1"],
        signal["tp2"],
        signal["tp3"],
        signal["be"]
    )

    if signal_key == LAST_SIGNAL_KEY:

        print("Segnale duplicato ignorato")
        return

    LAST_SIGNAL_KEY = signal_key

    state["last_signal"] = signal
    
    #
    # High impact news
    #

    news_active, news_message, news_color = has_high_impact_news(
        signal["symbol"]
    )
    #
    # Review
    #
    
    ReviewWindow(
        calculate(
            signal,
            ACCOUNTS[0]["risk"]
        ),
        news_active,
        news_message,
        news_color
    ).show()
    
    
print("BOT STARTED")

start_watcher(
    [WATCH_FILE, WATCH_JSON_FILE],
    process_signal
)

try:

    while True:

        time.sleep(1)

except KeyboardInterrupt:

    print("Closing...")