# ------------------------------------------------------
# Signal_bot: v1.3 - 2025-07-15
#
# programma python per elaborazione segnale di trading su Telegram
# il segnale deve essere salvato in forma grafica su file jpg (ad es. tramite Strumento di cattura)
# in una cartella e nome specificati in config.json
# purtroppo è stata inibita la copia testuale del segnale altrimenti l'elaborazione sarebbe stata più semplice senza ocr
# il file viene riconosciuto come modificato ed elaborato con ocr
# si estraggono tutti i dati per l'inserimento dell'ordine di trading (Entry, SL, TP1,2,3) e si calcolano i dati aggiuntivi di lottaggio e pips breakeven
# tramite shortcut (definito in config) viene eseguita la compilazione automatica del pannello di inserimento ordine precedentemente predisposto manualmente su ctrader web (scelta simbolo, tipo, side, presenza SL, BE, TP1,2,3)
# l'utente quindi si trova l'ordine compilato e lo può inviare col bottone Place order
# ------------------------------------------------------
from core.watcher import start_watcher
from core.ocr import read_image
from core.parser import parse_signal
from core.calculator import calculate
from core.state import state

from ui.review import ReviewWindow

from config_loader import load_config

from core.hotkey import register
from execution.ctrader import execute

import threading
import time


config = load_config()

WATCH_FILE = config["watch_file"]
ACCOUNTS = config["accounts"]

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
def process_signal():

    print(">>> PROCESS START")

    text = read_image(WATCH_FILE)

    print("===== OCR TEXT =====")
    print(repr(text))
    print("====================")

    signal = parse_signal(text)

    print(signal)

    state["last_signal"] = signal

    ReviewWindow(
        calculate(signal, ACCOUNTS[0]["risk"])
    ).show()




print("BOT STARTED")

start_watcher(WATCH_FILE, process_signal)


try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("Closing...")