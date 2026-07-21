"""
Trading Signals Bot
Version 1.0

Forex Factory High Impact News
"""

from pathlib import Path
import json
import requests

from datetime import datetime
from datetime import timedelta

from zoneinfo import ZoneInfo

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------

URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

CACHE_DIR = Path("cache")

CACHE_FILE = CACHE_DIR / "ff_calendar.json"

CACHE_MINUTES = 30

LOCAL_TZ = ZoneInfo("Europe/Rome")

from config_loader import load_config

config = load_config()

# -------------------------------------------------------
# CACHE
# -------------------------------------------------------

def cache_valid():

    if not CACHE_FILE.exists():

        return False

    age = datetime.now() - datetime.fromtimestamp(
        CACHE_FILE.stat().st_mtime
    )

    return age < timedelta(
        minutes=CACHE_MINUTES
    )


# -------------------------------------------------------
# DOWNLOAD
# -------------------------------------------------------

def download_calendar():

    CACHE_DIR.mkdir(
        exist_ok=True
    )

    r = requests.get(

        URL,

        timeout=15,

        headers={
            "User-Agent":
            "TradingSignalsBot/1.0"
        }

    )

    r.raise_for_status()

    CACHE_FILE.write_text(

        r.text,

        encoding="utf-8"

    )

    return r.json()


# -------------------------------------------------------
# LOAD
# -------------------------------------------------------

def load_calendar():

    if cache_valid():

        return json.loads(

            CACHE_FILE.read_text(

                encoding="utf-8"

            )

        )

    return download_calendar()


# -------------------------------------------------------
# SYMBOL
# -------------------------------------------------------

def symbol_currencies(symbol):

    symbol = symbol.upper()

    #
    # Forex (6 lettere)
    #

    if (
        len(symbol) == 6
        and symbol[:3].isalpha()
        and symbol[3:].isalpha()
    ):

        return [
            symbol[:3],
            symbol[3:]
        ]

    #
    # Oro
    #

    if symbol in (
        "XAU",
        "XAUUSD"
    ):

        return ["USD"]

    #
    # Bitcoin
    #

    if symbol in (
        "BTC",
        "BTCUSD"
    ):

        return ["USD"]

    #
    # Ethereum
    #

    if symbol in (
        "ETH",
        "ETHUSD"
    ):

        return ["USD"]

    #
    # Indici USA
    #

    if symbol in (
        "US500",
        "US100",
        "USTEC",
        "US30"
    ):

        return ["USD"]

    #
    # DAX
    #

    if symbol in (
        "DAX40",
        "DE40"
    ):

        return ["EUR"]

    return []


# -------------------------------------------------------
# IMPACT
# -------------------------------------------------------

def is_high_impact(event):

    impact = str(

        event.get(
            "impact",
            ""
        )

    ).strip().lower()

    #
    # gestisce:
    #
    # High
    # HIGH
    # High Impact
    # High Impact Expected
    #

    if impact == "high":

        return True

    if "high" in impact:

        return True

    #
    # eventuale formato numerico
    #

    try:

        impact_num = int(impact)

        if impact_num >= 3:

            return True

    except Exception:

        pass

    return False
    
# -------------------------------------------------------
# HIGH IMPACT NEWS
# -------------------------------------------------------

def has_high_impact_news(symbol):

    currencies = symbol_currencies(symbol)

    if not currencies:

        return (
            False,
            None,
            None
        )

    try:

        calendar = load_calendar()

    except Exception as ex:

        print(
            "Unable to load ForexFactory calendar:",
            ex
        )

        return (
            False,
            None,
            None
        )
        
    if config["news_test_mode"]:
        now = datetime.strptime(
            config["news_test_time"],
            "%Y-%m-%d %H:%M"
        ).replace(
            tzinfo=LOCAL_TZ
        )
    else:
        now = datetime.now(LOCAL_TZ)


    messages = []

    for event in calendar:

        #
        # COUNTRY
        #

        country = str(

            event.get(
                "country",
                ""
            )

        ).upper().strip()

        if country not in currencies:

            continue

        #
        # IMPACT
        #

        if not is_high_impact(event):

            continue

        #
        # DATE
        #

        try:

            event_time = datetime.fromisoformat(
                event["date"]
            ).astimezone(
                LOCAL_TZ
            )

        except Exception:

            continue

        #
        # TIME WINDOW
        #

        begin = event_time - timedelta(
            minutes=30
        )

        end = event_time + timedelta(
            minutes=15
        )

        if now < begin:

            continue

        if now > end:

            continue

        #
        # TITLE
        #

        title = str(

            event.get(
                "title",
                "High Impact News"
            )

        )

        #
        # DELTA
        #

        delta = int(

            (
                event_time - now
            ).total_seconds()

            / 60

        )

        if delta > 0:

            when = f"tra {delta} minuti"

        elif delta < 0:

            when = f"uscita {-delta} minuti fa"

        else:

            when = "adesso"

        messages.append(

            f"{country} - {title}\n{when}"

        )

    #
    # RESULT
    #

    if not messages:

        return (

            False,

            None,

            None

        )

    message = (

        "⚠ HIGH IMPACT NEWS\n\n"

        + "\n\n".join(messages)

    )

    return (

        True,

        message,

        "#ffcccc"

    )