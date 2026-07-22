# Trading Signals Bot

**Trading Signals Bot** is a Python application that automates the processing of trading signals received as images.

The application continuously monitors a folder, performs OCR on newly received images, extracts trading information, calculates the correct position size according to the configured monetary risk, warns the user about nearby high-impact economic news, and assists the manual execution of trades on multiple cTrader accounts.

The philosophy of the project is:

> **Automate everything except the final trading decision.**

The trader always has the opportunity to review the signal before executing the order.

---

# Features

## Automatic image monitoring

The bot continuously watches a configured folder.

Whenever a new signal image is detected:

- OCR is executed
- the signal is parsed
- lot size is calculated
- economic news are checked
- a review popup is displayed

---

## OCR

Signal images are converted into text using OCR.

Supported information includes:

- Symbol
- BUY / SELL
- MARKET / LIMIT / STOP
- Entry
- Stop Loss
- TP1
- TP2
- TP3
- Break Even

The OCR stage is independent from the signal provider and can therefore support different image layouts.

---

## Intelligent Parser

One of the most important parts of the project.

The parser is able to automatically correct many common OCR mistakes.

Examples:

```
SL:
60850
```

becomes

```
1.60850
```

or

```
ENTRY:
,60940
```

becomes

```
1.60940
```

The parser reconstructs missing digits using contextual information extracted from the remaining prices contained in the signal.

---

## Position Size Calculator

The calculator automatically computes the trading volume according to:

- configured monetary risk
- Entry price
- Stop Loss
- instrument contract size

Supported instruments include:

- Forex
- Gold
- Bitcoin
- Ethereum
- US Indices
- DAX

Each trading account can have its own independent monetary risk.

---

## Manual Review

Before any execution the bot displays a review window containing:

- Symbol
- Side
- Entry
- Stop Loss
- TP levels
- Break Even
- Calculated Lots

The user can either:

- Confirm
- Cancel

No order is executed automatically.

---

## High Impact News Detection

The bot automatically downloads the Forex Factory economic calendar.

If a High Impact event affecting the traded instrument is scheduled:

- from 30 minutes before
- until 15 minutes after

the review window is displayed with a light red background.

Currency mapping is automatically handled for:

- Forex pairs
- Gold
- Bitcoin
- Ethereum
- US Indices
- DAX

---

## Multi Account Support

Multiple trading accounts are supported.

Each account defines:

- name
- monetary risk
- execution hotkey

The same confirmed signal can therefore be executed with different risk values depending on the selected account.

---

## Duplicate Signal Protection

Windows file notifications sometimes generate multiple events for the same image.

The bot automatically detects duplicated signals and prevents:

- duplicate OCR processing
- duplicate review windows
- duplicate trade execution

---

# Project Architecture

```
Trading Signals Bot
│
├── core
│   ├── OCR
│   ├── Parser
│   ├── Calculator
│   ├── Watcher
│   ├── News
│   ├── Hotkeys
│   └── State
│
├── execution
│   └── cTrader automation
│
├── ui
│   └── Review Window
│
├── config
│
└── main.py
```

---

# Functional Workflow

```
Signal Image
      │
      ▼
Folder Watcher
      │
      ▼
OCR
      │
      ▼
Parser
      │
      ▼
Signal Validation
      │
      ▼
Lot Size Calculation
      │
      ▼
Economic News Check
      │
      ▼
Review Popup
      │
      ▼
User Confirmation
      │
      ▼
cTrader Execution
```

---

# Technologies

The project is entirely written in Python.

Main libraries used:

- Python 3.13
- Tkinter
- Watchdog
- Pillow
- RapidOCR
- Requests
- JSON
- Threading

---

# Configuration

Application parameters are stored inside `config.json`.

Configuration includes:

- watched image
- trading accounts
- monetary risk
- hotkeys
- optional test settings

This allows changing the behaviour of the application without modifying the source code.

---

# Current Version

**Trading Signals Bot 1.0**

First stable release.

Current capabilities include:

- OCR
- Signal parsing
- OCR correction
- Position size calculation
- Economic news filtering
- Review window
- Multi-account support
- Duplicate signal protection

---

# Future Improvements

Possible future developments include:

- Telegram integration
- Automatic screenshot capture
- Trade history database
- Performance statistics
- Signal provider plugins
- Multiple execution platforms
- Executable Windows installer
- Automatic updates

---

# Disclaimer

This software is intended as a trading assistant.

Trade execution always requires user confirmation.

The author assumes no responsibility for financial losses resulting from the use of this software.
