import math

# =====================================================
# CONFIGURAZIONE SIMBOLI
# =====================================================

SYMBOL_CONFIG = {

    "XAUUSD": {"UnitsPerLot": 100, "PipsPerPrice": 100, "USD_conversion": 1},
    "XAU":    {"UnitsPerLot": 100, "PipsPerPrice": 100, "USD_conversion": 1},

    "EURUSD": {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 1},
    "EUR":    {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 1},

    "GBPAUD": {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 0.7},
    "GBPNZD": {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 0.58},
    "USDCAD": {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 0.71},
    "EURAUD": {"UnitsPerLot": 100000, "PipsPerPrice": 10000, "USD_conversion": 0.7},

    "BTCUSD": {"UnitsPerLot": 1, "PipsPerPrice": 1, "USD_conversion": 1},
    "BTC":    {"UnitsPerLot": 1, "PipsPerPrice": 1, "USD_conversion": 1},

    "ETHUSD": {"UnitsPerLot": 1, "PipsPerPrice": 1, "USD_conversion": 1},
    "ETH":    {"UnitsPerLot": 1, "PipsPerPrice": 1, "USD_conversion": 1},

    "US500": {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1},
    "US100": {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1},
    "USTEC": {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1},
    "US30":  {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1},

    "DAX40": {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1.15},
    "DE40":  {"UnitsPerLot": 100, "PipsPerPrice": 1, "USD_conversion": 1.15},
}


# =====================================================
# VALIDAZIONE
# =====================================================

def validate(signal):

    required = [
        "symbol",
        "side",
        "order_type",
        "entry",
        "sl",
        "tp1"
    ]

    for field in required:

        if signal.get(field) is None:
            raise Exception(f"Missing field: {field}")

    symbol = signal["symbol"]

    if symbol not in SYMBOL_CONFIG:
        raise Exception(f"Invalid symbol: {symbol}")


# =====================================================
# CALCOLO
# =====================================================

def calculate(signal, risk):
    
    validate(signal)

    symbol = signal["symbol"]

    cfg = SYMBOL_CONFIG[symbol]

    units = cfg["UnitsPerLot"]

    pips_per_price = cfg["PipsPerPrice"]
    USD_conversion = cfg["USD_conversion"]

    entry = float(signal["entry"])
    sl = float(signal["sl"])

    distance = abs(entry - sl)

    if distance <= 0:
        raise Exception("SL and Entry are identical.")
        
    lots = round(
        risk / (distance * units * USD_conversion),
        2
    )
    
    print(f" calculate - risk: {risk} - distance: {distance} - units: {units} - lots: {lots}")


    # almeno 0.01
    lots = max(0.01, lots)

    # -----------------------------
    # BE Pips
    # -----------------------------

    if signal["be"] is not None:

        be_pips = abs(entry - signal["be"]) * pips_per_price

    else:

        be_pips = abs(entry - signal["tp1"]) * pips_per_price

    # -----------------------------
    # TP LOTS
    # -----------------------------

    if signal["tp3"] is None:

        tp_lots = round(lots / 2, 2)

    else:

        tp_lots = round(lots / 3, 2)

    result = signal.copy()

    result["distance"] = round(distance, 5)

    result["lots"] = round(lots, 2)

    result["tp_lots"] = round(tp_lots, 2)

    result["bepips"] = int(be_pips)

    return result