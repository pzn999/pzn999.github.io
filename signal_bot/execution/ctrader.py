import pyautogui
import time

pyautogui.FAILSAFE = True

# =====================================================
# CONFIG
# =====================================================

TAB_DELAY = 0.03
TYPE_DELAY = 0.03


# =====================================================
# HELPERS
# =====================================================

def press_tab(n=1):
    for _ in range(n):
        pyautogui.press("tab")
        #print(f"TAB pressed")
        time.sleep(TAB_DELAY)


def write(value):

    if value is None:
        return

    value = str(value).replace(",", ".")

    #print(f"WRITE -> {value}")

    pyautogui.write(value, interval=TYPE_DELAY)



# =====================================================
# EXECUTION
# =====================================================
    
def execute(signal):

    print()
    print("===================================")
    print("CTRADER EXECUTION START")
    print("===================================")

    entry = signal["entry"]
    lots = signal["lots"]
    sl = signal["sl"]

    tp1 = signal["tp1"]
    tp2 = signal.get("tp2")
    tp3 = signal.get("tp3")

    bepips = signal["bepips"]

    tp_lots = signal["tp_lots"]

    #
    # CURSORE POSIZIONATO SUL BOTTONE BUY/SELL
    #

    # -------------------------------------------------
    # ENTRY
    # -------------------------------------------------

    press_tab(1)
    write(entry)

    # -------------------------------------------------
    # LOTS
    # -------------------------------------------------

    press_tab(1)
    write(lots)

    # -------------------------------------------------
    # SL
    # -------------------------------------------------

    press_tab(2)
    write(sl)

    # -------------------------------------------------
    # BE (PIPS !!)
    # -------------------------------------------------

    press_tab(4) #con SL % attivo
    write(bepips)

    # -------------------------------------------------
    # TP1
    # -------------------------------------------------

    press_tab(3)
    write(tp1)

    # -------------------------------------------------
    # TP1 LOTS
    # -------------------------------------------------

    press_tab(4)
    write(tp_lots)

    # -------------------------------------------------
    # TP2
    # -------------------------------------------------

    press_tab(2)

    if tp2 is not None:
        write(tp2)

    # -------------------------------------------------
    # TP3
    # -------------------------------------------------

    if tp3 is not None:

        press_tab(4)
        write(tp_lots)

        press_tab(2)
        write(tp3)


    print("===================================")
    print("CTRADER EXECUTION END")
    print("===================================")
    
    
