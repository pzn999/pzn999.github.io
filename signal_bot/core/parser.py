import re
from difflib import get_close_matches

# ----------------------------------------------------
# SYMBOLS
# ----------------------------------------------------

SYMBOLS = [
    "XAUUSD",
    "XAU",   
    "EURUSD",
    "EUR",   
    "GBPAUD",
    "GBPNZD",
    "USDCAD",
    "USDCHF",
    "USDJPY",
    "EURAUD",
    "EURCAD",
    "BTCUSD",
    "BTC",   
    "ETHUSD",
    "ETH",   
    "US500", 
    "US100", 
    "USTEC", 
    "US30",  
    "DAX40", 
    "DE40" 
]

# ----------------------------------------------------
# OCR FIXES
# ----------------------------------------------------

FIXES = {

    "USSOO": "US500",
    "US5OO": "US500",
    "USS00": "US500",
    "USS0O": "US500",
    "USSOO": "US500",
    
    "USI00": "US100",
    "USIOO": "US100",

    "BTCUSO": "BTCUSD",
    "BTCUS0": "BTCUSD",

    "ETHUSO": "ETHUSD",

    "TPI": "TP1",
    "TPL": "TP1",
    "TPZ": "TP2",

    "ENTRATA": "ENTRY"

}


# ----------------------------------------------------
# NORMALIZE
# ----------------------------------------------------

def normalize(text):

    t = text.upper()

    for k, v in FIXES.items():
        t = t.replace(k, v)

    return t


# ----------------------------------------------------
# NUMBER
# ----------------------------------------------------

def parse_number(s):

    if s is None:
        return None

    s = s.replace(",", ".")

    try:
        return float(s)
    except:
        return None


# ----------------------------------------------------
# VALUE
# ----------------------------------------------------

def extract_value(text, labels):

    #
    # Primo prezzo completo presente nel testo.
    # Serve come riferimento per ricostruire
    # prezzi OCR incompleti.
    #

    reference = None

    mref = re.search(r"(\d+),(\d{3,5})", text)

    if mref:

        reference = mref.group(1)

    for label in labels:

        m = re.search(
            rf"{label}\s*[:\-]?\s*([\d.,]+)",
            text
        )

        if not m:
            continue

        value = m.group(1).strip()

        #
        # Caso:
        #
        # ,60850
        #

        if value.startswith(","):

            if reference:

                value = reference + value

        #
        # Caso:
        #
        # 60850
        #
        # (5 cifre senza virgola)
        #

        elif "," not in value and "." not in value:

            if len(value) == 5 and reference:

                value = reference + "," + value

        return parse_number(value)

    return None

# ----------------------------------------------------
# SYMBOL
# ----------------------------------------------------

def extract_symbol(text):

    words = re.findall(r"[A-Z0-9]+", text)

    # match perfetto
    for w in words:

        if w in SYMBOLS:
            return w

    # fuzzy match
    for w in words:

        m = get_close_matches(
            w,
            SYMBOLS,
            n=1,
            cutoff=0.60
        )

        if m:
            return m[0]

    return None


# ----------------------------------------------------
# MAIN PARSER
# ----------------------------------------------------
    
def parse_signal(raw):

    text = normalize(raw)

    print("===== OCR TEXT =====")
    print(repr(text))
    print("====================")

    symbol = extract_symbol(text)

    if symbol is None:

        raise Exception(
            "Unable to identify trading symbol."
        )

    side = None

    if "BUY" in text:
        side = "BUY"

    elif "SELL" in text:
        side = "SELL"

    order_type = "MARKET"

    if "LIMIT" in text:
        order_type = "LIMIT"

    elif "STOP" in text:
        order_type = "STOP"

    # -------------------------------
    # TP1 / BE
    # -------------------------------

    tp1 = None
    be = None

    m = re.search(
        r"TP1\s*/\s*BE\s*[:\-]?\s*([\d.,]+)",
        text
    )

    if m:

        value = parse_number(m.group(1))

        tp1 = value
        be = value

    else:
        tp1 = extract_value(
            text,
            [
                "TP1"
            ]
        )

        be = extract_value(
            text,
            [
                "BE"
            ]
        )
        
        if not be:
            be = tp1
            
        if not tp1:
            tp1 = be
            

    entry = extract_value(
        text,
        [
            "ENTRY",
            "ENTRATA"
        ]
    )

    sl = extract_value(
        text,
        [
            "SL"
        ]
    )

    tp2 = extract_value(
        text,
        [
            "TP2"
        ]
    )

    tp3 = extract_value(
        text,
        [
            "TP3"
        ]
    )



    signal = {

        "symbol": symbol,
        "side": side,
        "order_type": order_type,

        "entry": entry,
        "sl": sl,

        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,

        "be": be

    }
    
    return signal