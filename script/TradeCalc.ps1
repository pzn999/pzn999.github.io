# TradeCalc.ps1 - Versione corretta per prezzi con PUNTO decimale (es. EURUSD 1.03600)
# Non rimuove i punti → li tratta come decimali (corretto per trading)
# Supporta virgola solo se presente (es. 1,03600 → diventa 1.03600)
# Prodotto da Qwen3 (chat.qwen.ai)
# chat: Guida Personalizzata Excel
# Identificazione: TradeCalc PowerShell Script (oppure: "Lo script PowerShell che legge la clipboard, calcola i lotti e genera uno script AHK per AutoHotkey"

$Risk = 1500
$TempPath = "C:\temp"
$AhkPath = "$TempPath\trade_setup.ahk"

if (!(Test-Path $TempPath)) {
    New-Item -ItemType Directory -Path $TempPath | Out-Null
}

Add-Type -AssemblyName System.Windows.Forms
$clipboard = [System.Windows.Forms.Clipboard]::GetText()

if ([string]::IsNullOrWhiteSpace($clipboard)) {
    [System.Windows.Forms.MessageBox]::Show("Clipboard vuota.", "Errore", "OK", "Error")
    exit 1
}

$lines = $clipboard -split '\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }

$Entry = $null; $SL = $null; $TP2 = $null; $Symbol = $null; $IsNow = $false

# Analizza la prima riga per simbolo e NOW
if ($lines.Count -gt 0) {
    $firstLine = $lines[0]
    if ($firstLine -match '\b(XAU|XAUUSD|EUR|EURUSD|BTC|BTCUSD|ETH|ETHUSD|US500|US100|USTEC|US30|DAX40|DE40)\b') {
        $Symbol = $matches[1]
    }
    if ($firstLine -match '\b(SELL|BUY)\s+NOW\b') {
        $IsNow = $true
    }
}

# Funzione per normalizzare un numero di prezzo (mantiene il punto, sostituisce virgola con punto)
function Convert-PriceString {
    param([string]$str)
    if ($str -match ',') {
        # Se c'è una virgola, rimuovi i punti (migliaia) e sostituisci virgola con punto
        return ($str -replace '\.', '' -replace ',', '.')
    } else {
        # Se non c'è virgola, mantieni il testo così com'è (il punto è decimale)
        return $str
    }
}

# Estrai SL e TP2 come STRINGHE normalizzate (per l'output)
$SLStrRaw = $null; $TP2StrRaw = $null; $EntryStrRaw = $null

foreach ($line in $lines) {
    if ($line -match 'SL\s*[:\s]*([\d.,]+)') {
        $SLStrRaw = Convert-PriceString $matches[1]
    }
    if ($line -match 'TP2\s*[:\s]*([\d.,]+)') {
        $TP2StrRaw = Convert-PriceString $matches[1]
    }
}

# Estrai ENTRY come ultima sequenza numerica nella riga con "ENTRY"
foreach ($line in $lines) {
    if ($line -match '(?i)entry') {
        $numberMatches = [regex]::Matches($line, '[\d.,]+')
        if ($numberMatches.Count -gt 0) {
            $lastNumber = $numberMatches[$numberMatches.Count - 1].Value
            $EntryStrRaw = Convert-PriceString $lastNumber
            break
        }
    }
}

# Validazione delle stringhe
if (!$SLStrRaw -or !$TP2StrRaw -or !$Symbol) {
    [System.Windows.Forms.MessageBox]::Show("Mancano: SL, TP2 o simbolo.", "Errore", "OK", "Error")
    exit 1
}
if ((!$IsNow -and !$EntryStrRaw) -or ($IsNow -and !$EntryStrRaw)) {
    [System.Windows.Forms.MessageBox]::Show("ENTRY non trovato.", "Errore", "OK", "Error")
    exit 1
}

# Converti in [decimal] SOLO per il calcolo di Lots (più preciso di [double])
try {
    $EntryNum = [decimal]$EntryStrRaw
    $SLNum = [decimal]$SLStrRaw
    $TP2Num = [decimal]$TP2StrRaw
} catch {
    [System.Windows.Forms.MessageBox]::Show("Errore nella conversione dei numeri.`nControlla il formato di ENTRY, SL, TP2.", "Errore", "OK", "Error")
    exit 1
}

# Configurazione simboli
$SymbolConfig = @{
    "XAUUSD" = @{ UnitsPerLot = 100 }
    "XAU" = @{ UnitsPerLot = 100 }
    "EURUSD" = @{ UnitsPerLot = 100000 }
    "EUR" = @{ UnitsPerLot = 100000 }
    "BTCUSD" = @{ UnitsPerLot = 1 }
    "BTC" = @{ UnitsPerLot = 1 }
    "ETHUSD" = @{ UnitsPerLot = 1 }
    "ETH" = @{ UnitsPerLot = 1 }
    "US500"  = @{ UnitsPerLot = 100 }
    "US100"  = @{ UnitsPerLot = 100 }
    "USTEC"  = @{ UnitsPerLot = 100 }
    "US30"   = @{ UnitsPerLot = 100 }
    "DAX40"  = @{ UnitsPerLot = 100 }
    "DE40"  = @{ UnitsPerLot = 100 }
}

if (!$SymbolConfig.ContainsKey($Symbol)) {
    [System.Windows.Forms.MessageBox]::Show("Simbolo non supportato: $Symbol", "Errore", "OK", "Error")
    exit 1
}

$UnitsPerLot = $SymbolConfig[$Symbol].UnitsPerLot
$Distance = [Math]::Abs($EntryNum - $SLNum)
if ($Distance -eq 0) {
    [System.Windows.Forms.MessageBox]::Show("SL = Entry.", "Errore", "OK", "Error")
    exit 1
}

# Calcolo Lots come numero
$LotsNum = [Math]::Round($Risk / ([double]($Distance * $UnitsPerLot)), 2)

# ✅ Formatta Lots con punto, Entry/SL/TP2 usano le stringhe normalizzate (mantengono zeri finali!)
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$LotsStr = $LotsNum.ToString($culture)
# Per i prezzi, usiamo le stringhe normalizzate (non convertite in numero) per preservare 1.03600
$EntryStr = $EntryStrRaw
$SLStr = $SLStrRaw
$TP2Str = $TP2StrRaw

# Genera script AHK
if ($IsNow) {
    $AhkContent = @"
#SingleInstance Force
    ^+v:: {
    Send "{Tab}"        ; invia TAB
    SendText "$LotsStr"      ; Lots
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$SLStr"      ; SL
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$TP2Str"      ; TP2
    Send "{Tab}"        ; invia TAB
}
"@
} else {
    $AhkContent = @"
#SingleInstance Force
    ^+v:: {
    Send "{Tab}"        ; invia TAB
    SendText "$EntryStr"     ; Entry
    Send "{Tab}"        ; invia TAB
    SendText "$LotsStr"      ; Lots
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$SLStr"      ; SL
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$TP2Str"      ; TP2
    Send "{Tab}"        ; invia TAB
}
"@
}

# Salva file
$AhkContent | Out-File -FilePath $AhkPath -Encoding UTF8

# Esegui con AutoHotkey
Start-Process "C:\Portable\AutoHotkey\AutoHotkey64.exe" -ArgumentList $AhkPath

# Messaggio di successo
$mode = if ($IsNow) { " (modalità NOW)" } else { "" }
[System.Windows.Forms.MessageBox]::Show("Script AHK generato!$mode", "Successo", "OK", "Information")
