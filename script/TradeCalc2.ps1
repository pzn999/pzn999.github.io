# TradeCalc.ps1 - Versione aggiornata con supporto ENTRY/entrata, TP1/TP2, BE
# Prodotto da Qwen3 (chat.qwen.ai)
# Identificazione: TradeCalc PowerShell Script

Add-Type -AssemblyName System.Windows.Forms

$Risk = 250          # meno di metà dello 0.5% del conto da 200K
$RiskNow = 450       # Per modalità NOW (puoi modificarlo)
$TempPath = "C:\temp"
$AhkPath = "$TempPath\trade_setup.ahk"

# Funzione che verifica le news
function Test-HighImpactNews {
    param(
        [string[]]$Currencies = @("USD", "EUR"),
        [int]$BeforeMinutes = 60,
        [int]$AfterMinutes = 15
    )

    # Percorso della cache
    $cacheDir = "C:\temp"
    if (!(Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir | Out-Null }
    $cacheFile = "$cacheDir\ff_calendar_cache.json"
    $cacheMetaFile = "$cacheDir\ff_calendar_cache.meta"  # contiene la data di creazione

    $today = (Get-Date).ToString("yyyy-MM-dd")
    $useCache = $false

    # Verifica se la cache esiste ed è di oggi
    if ((Test-Path $cacheFile) -and (Test-Path $cacheMetaFile)) {
        $cachedDate = (Get-Content $cacheMetaFile -Raw).Trim()
        if ($cachedDate -eq $today) {
            $useCache = $true
        }
    }

    try {
        if ($useCache) {
            Write-Host "✅ Utilizzo cache Forex Factory (oggi)"
            $json = Get-Content $cacheFile | ConvertFrom-Json
        } else {
            Write-Host "🌐 Scarico dati da Forex Factory..."
            $uri = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
            $json = Invoke-RestMethod -Uri $uri -TimeoutSec 10

            # Salva cache
            $json | ConvertTo-Json -Depth 5 | Set-Content $cacheFile -Encoding UTF8
            $today | Set-Content $cacheMetaFile -Encoding UTF8
        }

        $nowLocal = Get-Date
        # $nowLocal = [DateTime]"2026-03-31 14:55"  # PER TEST
        $localOffset = [TimeZoneInfo]::Local.GetUtcOffset($nowLocal)
        $nowUtc = [DateTimeOffset]::new($nowLocal, $localOffset).UtcDateTime

        foreach ($event in $json) {
            if ($event.impact -ne "High") { continue }
            if ($Currencies -notcontains $event.country) { continue }

            $eventTimeUtc = [DateTimeOffset]::Parse($event.date).UtcDateTime
            $windowStart = $eventTimeUtc.AddMinutes(-$BeforeMinutes)
            $windowEnd = $eventTimeUtc.AddMinutes($AfterMinutes)

            if ($nowUtc -ge $windowStart -and $nowUtc -le $windowEnd) {
                return $true
            }
        }
    } catch {
        $errorMessage = $_.Exception.Message
        Write-Host "⚠️ Errore nel controllo Forex Factory: $errorMessage"
        try {
            Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
            [System.Windows.Forms.MessageBox]::Show(
                "Errore nel controllo Forex Factory:`n$errorMessage",
                "Errore",
                "OK",
                "Error"
            )
        } catch {}
        return $false
    }

    return $false
}

# 🔒 Blocco sicurezza: verifica notizie High Impact su USD/EUR
if (Test-HighImpactNews) {
    [System.Windows.Forms.MessageBox]::Show(
        "Attenzione: evento High Impact in corso su USD o EUR",
        "Forex Factory Alert",
        "OK",
        "Warning"
    )
    exit 1
}

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

$Entry = $null; $SL = $null; $TP1 = $null; $TP2 = $null; $BE = $null; $Symbol = $null; $IsNow = $false

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

# Funzione per normalizzare un numero di prezzo
function Convert-PriceString {
    param([string]$str)
    if ($str -match ',') {
        return ($str -replace '\.', '' -replace ',', '.')
    } else {
        return $str
    }
}

# Estrai SL, TP1, TP2, BE come STRINGHE
$SLStrRaw = $null; $TP1StrRaw = $null; $TP2StrRaw = $null; $BEstrRaw = $null; $EntryStrRaw = $null

foreach ($line in $lines) {
    if ($line -match 'SL\s*[:\s]*([\d.,]+)') {
        $SLStrRaw = Convert-PriceString $matches[1]
    }
    if ($line -match 'TP1\s*[:\s]*([\d.,]+)') {
        $TP1StrRaw = Convert-PriceString $matches[1]
    }
    if ($line -match 'TP2\s*[:\s]*([\d.,]+)') {
        $TP2StrRaw = Convert-PriceString $matches[1]
    }
    if ($line -match '(?i)\bBE\b\s*[:\s]*([\d.,]+)') {
        $BEstrRaw = Convert-PriceString $matches[1]
    }
}

# Estrai ENTRY come ultima sequenza numerica nella riga con "ENTRY" o "entrata"
foreach ($line in $lines) {
    if ($line -match '(?i)\b(entry|entrata)\b') {
        $numberMatches = [regex]::Matches($line, '[\d.,]+')
        if ($numberMatches.Count -gt 0) {
            $lastNumber = $numberMatches[$numberMatches.Count - 1].Value
            $EntryStrRaw = Convert-PriceString $lastNumber
            break
        }
    }
}

# Validazione delle stringhe
if (!$SLStrRaw -or !$TP1StrRaw -or !$TP2StrRaw -or !$Symbol) {
    [System.Windows.Forms.MessageBox]::Show("Mancano: SL, TP1, TP2 o simbolo.", "Errore", "OK", "Error")
    exit 1
}
if ((!$IsNow -and !$EntryStrRaw) -or ($IsNow -and !$EntryStrRaw)) {
    [System.Windows.Forms.MessageBox]::Show("ENTRY non trovato.", "Errore", "OK", "Error")
    exit 1
}

# Converti in [decimal] per calcoli
try {
    $EntryNum = [decimal]$EntryStrRaw
    $SLNum = [decimal]$SLStrRaw
    $TP1Num = [decimal]$TP1StrRaw
    $TP2Num = [decimal]$TP2StrRaw
    $BENum = if ($BEstrRaw) { [decimal]$BEstrRaw } else { $null }
} catch {
    [System.Windows.Forms.MessageBox]::Show("Errore nella conversione dei numeri.`nControlla il formato di ENTRY, SL, TP1, TP2.", "Errore", "OK", "Error")
    exit 1
}

# Configurazione simboli
$SymbolConfig = @{
    "XAUUSD" = @{ UnitsPerLot = 100 }
    "XAU"    = @{ UnitsPerLot = 100 }
    "EURUSD" = @{ UnitsPerLot = 100000 }
    "EUR"    = @{ UnitsPerLot = 100000 }
    "BTCUSD" = @{ UnitsPerLot = 1 }
    "BTC"    = @{ UnitsPerLot = 1 }
    "ETHUSD" = @{ UnitsPerLot = 1 }
    "ETH"    = @{ UnitsPerLot = 1 }
    "US500"  = @{ UnitsPerLot = 100 }
    "US100"  = @{ UnitsPerLot = 100 }
    "USTEC"  = @{ UnitsPerLot = 100 }
    "US30"   = @{ UnitsPerLot = 100 }
    "DAX40"  = @{ UnitsPerLot = 100 }
    "DE40"   = @{ UnitsPerLot = 100 }
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

# Calcolo Lots
$LotsNum = [Math]::Round($Risk / ([double]($Distance * $UnitsPerLot)), 2)

# Tabella PipsPerPrezzo
$PipsPerPrezzoMap = @{
    "XAUUSD" = 100;   "XAU" = 100;
    "EURUSD" = 10000; "EUR" = 10000;
    "BTCUSD" = 1;     "BTC" = 1;
    "ETHUSD" = 1;     "ETH" = 1;
    "US500" = 1;      "US100" = 1;
    "USTEC" = 1;      "US30" = 1;
    "DE40" = 1;       "DAX40" = 1
}

if (!$PipsPerPrezzoMap.ContainsKey($Symbol)) {
    [System.Windows.Forms.MessageBox]::Show("Simbolo non supportato: $Symbol", "Errore", "OK", "Error")
    exit 1
}
$PipsPerPrezzo = $PipsPerPrezzoMap[$Symbol]

# Calcolo BEpips
if ($null -ne $BENum) {
    $BEpips = [Math]::Round([Math]::Abs($EntryNum - $BENum) * $PipsPerPrezzo, 0)
} else {
    $SLpips = [Math]::Round([Math]::Abs($EntryNum - $SLNum) * $PipsPerPrezzo, 0)
    $BEpips = $SLpips  # simmetrico
}

# Formatta valori con punto
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$LotsStr = $LotsNum.ToString($culture)
$EntryStr = $EntryStrRaw
$SLStr = $SLStrRaw
$TP1Str = $TP1StrRaw
$TP2Str = $TP2StrRaw
$BEpipsStr = $BEpips.ToString($culture)

# Genera script AHK
if ($IsNow) {
    $AhkContent = @"
#SingleInstance Force
    ^+v:: {
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($SLStr)"
    Send "+{Tab}"
    
    Sleep, 100
    Send "^a"
    Sleep, 50
    Send "^c"
    Sleep, 100
    
    CurrSLPips := Clipboard
    
    if CurrSLPips is not number
    {
        MsgBox Errore: pips non valido.
        return
    }
    
    RiskNow := $($RiskNow)
    PipsPerPrezzo := $($PipsPerPrezzo)
    Lots := Round((RiskNow * CurrSLPips) / PipsPerPrezzo, 2)
    
    Send "+{Tab}"
    SendText "%Lots%"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($TP2Str)"
    Send "{Tab}"
}
"@
} else {
    # Calcola lots/2
    $LotsHalf = [Math]::Round($LotsNum / 2, 2)
    $LotsHalfStr = $LotsHalf.ToString($culture)

    $AhkContent = @"
#SingleInstance Force
    ^+v:: {
    Send "{Tab}"
    SendText "$($EntryStr)"
    Send "{Tab}"
    SendText "$($LotsStr)"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($SLStr)"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($BEpipsStr)"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($TP1Str)"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($LotsHalfStr)"
    Send "{Tab}"
    Send "{Tab}"
    SendText "$($TP2Str)"
    Send "{Tab}"
}
"@
}

# Salva file SENZA BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($AhkPath, $AhkContent, $utf8NoBom)

# Esegui con AutoHotkey
Start-Process "C:\Portable\AutoHotkey\AutoHotkey64.exe" -ArgumentList $AhkPath

# Messaggio di successo
$mode = if ($IsNow) { " (modalità NOW)" } else { "" }
[System.Windows.Forms.MessageBox]::Show("Script AHK generato!$mode", "Successo", "OK", "Information")