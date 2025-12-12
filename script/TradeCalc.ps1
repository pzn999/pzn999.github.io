# TradeCalc.ps1
# Autore: Basato su richiesta utente
# Data: Dicembre 2025

# Configurazione
$Risk = 375
$TempPath = "C:\temp"
$AhkPath = "$TempPath\trade_setup.ahk"

# Crea cartella temp se non esiste
if (!(Test-Path $TempPath)) {
    New-Item -ItemType Directory -Path $TempPath | Out-Null
}

# Leggi clipboard
Add-Type -AssemblyName System.Windows.Forms
$clipboard = [System.Windows.Forms.Clipboard]::GetText()

if ([string]::IsNullOrWhiteSpace($clipboard)) {
    [System.Windows.Forms.MessageBox]::Show("Clipboard vuota.", "Errore", "OK", "Error")
    exit 1
}

# Pulisci e dividi in righe
$lines = $clipboard -split '\r?\n' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }

# Estrai valori
$Entry = $null; $SL = $null; $TP1 = $null; $Symbol = $null

foreach ($line in $lines) {
    if ($line -match 'ENTRY[:\s]*([\d.,]+)') { $Entry = [double]($matches[1] -replace '\.', '' -replace ',', '.') }
    if ($line -match 'SL\s*[:\s]*([\d.,]+)') { $SL = [double]($matches[1] -replace '\.', '' -replace ',', '.') }
    if ($line -match 'TP1\s*[:\s]*([\d.,]+)') { $TP1 = [double]($matches[1] -replace '\.', '' -replace ',', '.') }
    if ($line -match '\b(XAUUSD|EURUSD|BTCUSD|ETHUSD|US500|US100|US30)\b') { $Symbol = $matches[1] }
}

# Validazione
if (!$Entry -or !$SL -or !$TP1 -or !$Symbol) {
    [System.Windows.Forms.MessageBox]::Show("Dati mancanti: ENTRY, SL, TP1, simbolo.", "Errore", "OK", "Error")
    exit 1
}

# Tabella simboli
$SymbolConfig = @{
    "XAUUSD" = @{ UnitsPerLot = 100 }
    "EURUSD" = @{ UnitsPerLot = 100000 }
    "BTCUSD" = @{ UnitsPerLot = 1 }
    "ETHUSD" = @{ UnitsPerLot = 1 }
    "US500"  = @{ UnitsPerLot = 1 }
    "US100"  = @{ UnitsPerLot = 1 }
    "US30"   = @{ UnitsPerLot = 1 }
}

if (!$SymbolConfig.ContainsKey($Symbol)) {
    [System.Windows.Forms.MessageBox]::Show("Simbolo non supportato: $Symbol", "Errore", "OK", "Error")
    exit 1
}

$UnitsPerLot = $SymbolConfig[$Symbol].UnitsPerLot
$Distance = [Math]::Abs($Entry - $SL)
if ($Distance -eq 0) { exit 1 }

$Lots = [Math]::Round($Risk / ($Distance * $UnitsPerLot), 2)

# Genera script AHK
$AhkContent = @"
#SingleInstance Force
^+v:: {
    Send "{Tab}"        ; invia TAB
    SendText "$Entry"     ; Entry
    Send "{Tab}"        ; invia TAB
    SendText "$Lots"      ; Lots
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$SL"      ; SL
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    Send "{Tab}"        ; invia TAB
    SendText "$TP1"      ; TP1
    Send "{Tab}"        ; invia TAB
}
"@

# Salva file
$AhkContent | Out-File -FilePath $AhkPath -Encoding UTF8

Start-Process "C:\Portable\AutoHotkey\AutoHotkey64.exe" -ArgumentList $AhkPath

# Successo
[System.Windows.Forms.MessageBox]::Show("Script AHK generato ed eseguito!`nPremi Ctrl+Shift+V per inserire i valori.", "Successo", "OK", "Information")
